'''

Transfer run script script for Matter Project

This script can be used for Standard Neurofeedback groups.
The timing of the stimulation is locked with the scanner trigger.

For each subject, the images should be provided in advance and copied in the ./images/ folder.
The images order for the Localiser and the NF runs should also be provided in the ./data/sub-XX/ses-XX folder.

The ./data/sub-XX/ses-XX should contain:

LocaliserX_group.txt
TransferX_group.txt
/runNF1/
    runNF1_group.txt
    runNF1_group.prt
/runNF2/
    runNF2_group.txt
    runNF2_group.prt
...

 
After loading the files for the current run, the script checks that the all the requested images are in the 
./images/ folder.

Please delete the images at the end of each session!


Outup data will be also saved as pickle files


Important settings:
-------------------------------------------------------------------

    NR_BLOCKS = 16 # number of trials within the run, it has to match the number of images in the image order file

    # set the prt file to define the condition timings
    hdr, prt_data = prt.read_prt(wdir + '/prt/Transfer_stimPC.prt')


'''


import os
import time
import glob
import random
import numpy as np
from packages.bvbabel import prt
from expyriment import control, stimuli, misc, design, io
from packages.expyriment_stimuli_extras.thermometerdisplay import ThermometerDisplay
from packages.expyriment_io_extras.tbvnetworkinterface import TbvNetworkInterface
# import pdb; pdb.set_trace() eventually for debugging
import time
import logging
import pickle

wdir = os.getcwd()


################################################################################
#                              DISPLAY SETTINGS                                #
################################################################################

# control.set_develop_mode(True)
control.defaults.window_mode = False
#control.defaults.window_size = (1920,1200)
control.defaults.window_size = (1920,800)
design.defaults.experiment_background_colour = [60,60,60]
design.defaults.experiment_foreground_colour = misc.constants.C_WHITE


# INSTRUCTIONS
instructions_header = "You are about to start the Transfer Run {0}"

# NOTE: Please feel free to change the instructions
instructions_content = \
    """   
    Always keep your gaze on the central dot!
    
    The REST condition is indicated by a BLACK dot.
    Just relax and try to disengage with previous emotions.

    In the EMOTION RECALL period an image will be displayed.
    Try to feel the emotion suggested by the image as much as possible.
    Try to not engage when viewing scrambled images.

    """
end_header = "Run is now finished"
end_content = "Thank you!" 


# control.defaults.open_gl=3 # to run on GPU if available, but check compatibility first!

################################################################################
#                              DESIGN SETTINGS                                 #
################################################################################

control.defaults.auto_create_subject_id = False
control.defaults.event_logging = 0 # use custome logging file instead
io.DataFile.logging = False



# DESIGN
exp = design.Experiment("Transfer")
exp.set_log_level(0)


control.initialize(exp)


# SCANNER SETTINGS
ROI = 0  # 0 if only 1 ROI
TR = 1000
PREP_SCANS = 0  # adapt
SCAN_TRIGGER = misc.constants.K_5
NR_BLOCKS = 16


# TRIGGER IO
trigger = exp.keyboard


# PROTOCOL TIMING
# Get condition name and timings from prt file
hdr, prt_data = prt.read_prt(wdir + '/prt/Transfer_stimPC.prt')
condition_names = []

# NOTE: the script assumes that the condition order is fixed in the protocol
# 0 - Rest
# 1 - Recall


for condition in prt_data:
    condition_names += [condition['NameOfCondition']] # these are needed to check the current condition in TBV

REST_TIMINGS = np.array([prt_data[0]['Time start'],prt_data[0]['Time stop']])
RECALL_TIMINGS = np.array([prt_data[1]['Time start'], prt_data[1]['Time stop']])

NR_VOLUMES = max(prt_data[0]['Time stop']) #last rest time point

# preallocate blocks from protocol file
for i in range(NR_VOLUMES):

    if i+1 in REST_TIMINGS[0]: #since prt is in volumes starting from 
        idx = np.where(REST_TIMINGS[0] == i+1)[0]
        block = design.Block()
        block.set_factor("Condition", condition_names[0])
        for length in range(int(REST_TIMINGS[1,idx] - REST_TIMINGS[0,idx]+1)):
            trial = design.Trial()
            block.add_trial(trial)
        exp.add_block(block)

    elif i+1 in RECALL_TIMINGS[0]:
        idx = np.where(RECALL_TIMINGS[0] == i+1)[0]
        block = design.Block()
        block.set_factor("Condition", condition_names[1])
        for length in range(int(RECALL_TIMINGS[1][idx] - RECALL_TIMINGS[0][idx] + 1)):
            trial = design.Trial()
            block.add_trial(trial)
        exp.add_block(block)



# IMAGES
# Get images path
images_folder = f'{wdir}/images/stock_images' 

# CONDITION CUES
#fixcross = stimuli.FixCross(colour=misc.constants.C_WHITE)  # Create fixation cross
#fixcross_recall = stimuli.FixCross(colour=misc.constants.C_RED)  # Create fixation
fixcircle = stimuli.Circle(radius = 8, colour=misc.constants.C_BLACK, position = (0,0), anti_aliasing =10)


################################################################################
#                              RUN LOCALISER                                   #
################################################################################

# USER INPUTs

# TO DO: check whether other controls for these user inputs are needed

i = io.TextInput("Subject: ")
sub = i.get()

i = io.TextInput("Session: ")
session = int(i.get())

i = io.TextInput("Transfer Run: ")
run = int(i.get())


# Check that the inputs are correct for the current subject

image_file = glob.glob(f'{wdir}/data/{sub}/ses-0{session}/Transfer{run}*.txt')[0]
if not os.path.exists(image_file):
    print(f'Image order file {image_file} missing!')
    exit(1)


# Get image names and check that all the images are present in the ./images folder
images_list =[]
with open(image_file) as f:
    for line in f:
        images_list.append(line[:-1]) #remove '\n'

        if not os.path.exists(f'{images_folder}/{line[:-1]}') and not os.path.exists(f'{images_folder}{line[:-1]}'):
            print(f'Missing image {line[:-1]} in the images folder\n')
            print('Currently available images: \n')
            cur_images = glob.glob(f'{images_folder}/*jpg')

            for img in cur_images:
                print(os.path.basename(img))
            exit(1)


# Check that the order file contains the expected number of images
if len(images_list) != NR_BLOCKS:
    print(f'Wrong number of images in the file {image_file}!\n Expected {NR_BLOCKS}. Please check.')
    exit(1)

# Get group name for logging
group = os.path.basename(image_file).split('_')[1][:-4]


# OUTPUT DATA

#create output folder 
outdir = f'{wdir}/data/{sub}/ses-0{session}'
os.makedirs(outdir, exist_ok=True)


# LOGGING SETTINGS
# Save a log file and set level for msg to be received
logging.basicConfig(filename = f'{outdir}/Transfer{run}_{group}.log', 
                                level=logging.INFO,
                                filemode = 'w',
                                format ='%(message)s')


# start logging the esperiment informations
logging.info('Neuroscience of Happiness - Transfer\n')
logging.info(f'SUBJECT INFO')
logging.info('-----------')
logging.info(f'Subject ID: {sub}')
logging.info(f'Session: {session}')
logging.info(f'Transfer Run: {run}')
logging.info(f'Group: {group}\n')

logging.info(f'DESIGN INFO')
logging.info('-----------')
logging.info(f'Conditions:')
for condition in prt_data:
    logging.info(f'\t{condition["NameOfCondition"]}') 
logging.info('-----------')

# START THE ESPERIMENT

current_trigger = 0
image_count = 0


# present intructions
stimuli.TextScreen(instructions_header.format(run), instructions_content, \
                    heading_size = 36, position = (0,0), text_size = 36).present()


start = False


exp.keyboard.wait()
stimuli.TextLine("Waiting for first MR trigger...").present()

for prep_scan in range(PREP_SCANS):  # Skip preparation scans! not needed for now unless we want to change this
    trigger.wait(SCAN_TRIGGER)
    print('Dummy trigger...')

trigger_time = exp.clock.time

for block in exp.blocks:

    for trial in block.trials:

        if exp.clock.time - trigger_time < TR:

            trigger.wait(SCAN_TRIGGER)  # check scanner trigger
            trigger_time = exp.clock.time

            if not start:
                start_time = trigger_time # to store the timing of the events in seconds (first volume -> 0s)
                start = True

        else:
            trigger_time += TR # just update the trigger time by 1TR in case a trigger was missing

            # NOTE: it should not happen in our case, but in case of missing more triggers (e.g., for very short TR) 
            # we could use the start time as reference for the trigger count


        if trial.id == 0:

            exp.keyboard.check() # check quit button pressed

            # Present a new condition!
            if block.get_factor("Condition") == condition_names[0]:  # Rest
 
                print(f'\n{condition_names[0]}')
                fixcircle.present()
                logging.info(f'\n{condition_names[0]}')


            elif block.get_factor("Condition") == condition_names[1]:  # recall

                print(f'\n{condition_names[1]}')
                #present a new cue
                if 'scrambled' in images_list[image_count]:
                    img_path = f'{images_folder}{images_list[image_count]}'.replace('\\','/')
                else:
                    img_path = f'{images_folder}/{images_list[image_count]}'.replace('\\','/')
                image = stimuli.Picture(img_path)  
                image.present()

                image_count += 1
                logging.info(f'\n{condition_names[1]}')

        # The trigger count is updated here to present the condition name before 
        current_trigger += 1 
        print(f'Current Volume: {current_trigger}')
        logging.info(f'Current Volume: {current_trigger}, Time [s] {(trigger_time-start_time)/1000:.3f}')



stimuli.TextScreen(end_header.format(run), end_content).present()


exp.keyboard.wait()


timestamp = time.strftime("%Y/%m/%d   %H:%M", exp.clock.init_localtime)
logging.info(f'\n{timestamp}')

# SAVE OUTDATA
# save log files and outdata

control.end()
