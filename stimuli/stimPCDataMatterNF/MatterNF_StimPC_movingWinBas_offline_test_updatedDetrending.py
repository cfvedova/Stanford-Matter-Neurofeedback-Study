'''

Neurofeedback script for Matter Project

This script can be used for the Matter Neurofeedback groups.
The timing of the stimulation is locked with the scanner trigger and the data are 
requested to TBV with some delay (set the TBV_REQUEST_DELAY flag). 

For each subject, the images should be provided in advance and copied in the ./images/ folder.
The images order for the localiser and the NF runs should also be provided in the ./data/sub-XX/ses-XX folder.

The ./data/sub-XX/ses-XX should contain:

LocaliserX_group.txt (optional)
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

A log file will be saved also for interrupted runs.

Outup data will be also saved as pickle files


Important settings:
-------------------------------------------------------------------

    TBV_REQUEST_DELAY = 2 # ask TBV for data with a bit of delay (in TR)


    NR_BLOCKS = 16 # number of trials within the run, it has to match the number of images in the image order file

    FEEDBACK_AVG = 3 # compute the feedback as the average of the FEEDBACK_AVG last time point of the RECALL block

    BASELINE_AVG = 5 # compute a local baseline level for the feedback PSC using  BASELINE_AVG time points around the IMAGE block

    BASELINE_END_SHIFT = 2 # for the local baseline, BASELINE_END_SHIFT time points within the IMAGE block are also considered


    SHOW_TARGET_LEVEL = False # whether to show arrows for the target level

    ADDITIONAL_LEVELS = 0.5 # in PSC units, set this to a value > 0 if you want to leave the participants the possibility 
    to have feedback for activity higher than the max PSC of the localiser 

    THERMOMETER_SEGMENTS = 10 # number of levels displayed on the themometer


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
#                              TCP/IP SETTINGS                                 #
################################################################################

# HOST = "192.168.173.3"
# HOST = "192.168.1.95"
HOST = "10.8.76.21"  # TBV pc ip
#HOST = 'localhost'
PORT = 55555

# try to connect to TBV
try:
    TBV = TbvNetworkInterface(HOST, PORT)
except:
    print('TBV network plugin is not active!')
    exit(1)

# ask TBV for data with a bit of delay (in TR)
TBV_REQUEST_DELAY = 2

################################################################################
#                              DISPLAY SETTINGS                                #
################################################################################

# control.set_develop_mode(True)
control.defaults.window_mode = False
control.defaults.window_size = (1900,800)
design.defaults.experiment_background_colour = [60,60,60]
design.defaults.experiment_foreground_colour = misc.constants.C_WHITE


# INSTRUCTIONS
instructions_header = "You are about to start the Neurofeedback Run {0}"

# NOTE: Please feel free to change the instructions
instructions_content = \
    """   
    Always keep your gaze on the central dot!
    
    The REST condition is indicated by a black dot.
    Just relax and try to disengage with previous emotions.

    In the EMOTION RECALL period an image will be displayed.
    Try to feel the emotion suggested by the image as much as possible.

    In the FEEDBACK, period a thermometer is presented.
    The light grey filling will reflect your brain activation.

    """
end_header = "The Neurofeedback Run {0} is now finished"
end_content = "Thank you!" 


# control.defaults.open_gl=3 # to run on GPU if available, but check compatibility first!

################################################################################
#                              DESIGN SETTINGS                                 #
################################################################################

control.defaults.auto_create_subject_id = False
control.defaults.event_logging = 0 # use custome logging file instead
io.DataFile.logging = False

# DESIGN
exp = design.Experiment("Neurofeedback")
exp.set_log_level(0)
control.initialize(exp)


# SCANNER SETTINGS
ROI = 0  # 0 if only 1 ROI
TR = 1000
PREP_SCANS = 0  # adapt
FEEDBACK_AVG = 10 # compute the feedback as the average of the last 3 time points of the RECALL block
BASELINE_AVG = 15 # compute a local baseline level for the feedback PSC using  BASELINE_AVG time points
BASELINE_BLOCK_POINTS = 5 
BASELINE_END_SHIFT = 2 # for the local baseline, BASELINE_END_SHIFT time points within the EMO block are also considered
SCAN_TRIGGER = misc.constants.K_5


# TRIGGER IO
trigger = exp.keyboard


# IMAGES
# Get images path
images_folder = f'{wdir}/images/matter_images' 

# CONDITION CUES
fixcircle = stimuli.Circle(radius = 8, colour=misc.constants.C_BLACK, position = (0,0), anti_aliasing =10)


# FEEDBACK SETTINGS
SHOW_TARGET_LEVEL = False
ADDITIONAL_LEVELS = 0.5 # in PSC unit, set this to a value > 0 if you want to leave the participants the possibility have feedback for activity higher than the max PSC of the localiser 
GO_COLOUR = [60,60,60] # hide refrence level indication by default
FRAME_COLOUR = [60,60,60]
ACTIVE_COLOUR = [150, 150, 150]
THERMOMETER_SEGMENTS = 10
INACTIVE_COLOUR = [60,60,60]
feedback_display = []

if SHOW_TARGET_LEVEL:
    GO_COLOUR = [0,255,0]

################################################################################
#                              RUN NEUROFEEDBACK                               #
################################################################################

# USER INPUTs

# TO DO: check whether other controls for these user inputs are needed

i = io.TextInput("Subject: ")
sub = i.get()

i = io.TextInput("Session: ")
session = int(i.get())

i = io.TextInput("NF Run: ")
run = int(i.get())

# Ask the user of the maximum PSC level for the thermometer, as derived from the localiser run
PSC_ok = False
while not PSC_ok:   
    i = io.TextInput("Max PSC: ")  
    _max = float(i.get())

    if _max < 10:
        PSC_ok =True

# PROTOCOL TIMING
# Get condition name and timings from prt file
hdr, prt_data = prt.read_prt(f'{wdir}/data/{sub}/ses-0{session}/runNF{run}/runNF{run}_matter.prt')

condition_names = []

# NOTE: the script assumes the following conditions in the protocol
# Rest - Recall - Feedback - Control
#

for i, condition in enumerate(prt_data):
    condition_names += [condition['NameOfCondition']] # these are needed to check the current condition in TBV
    if 'Recall' in condition['NameOfCondition']:
        RECALL_TIMINGS = np.array([prt_data[i]['Time start'], prt_data[i]['Time stop']])

    if 'Feedback' in condition['NameOfCondition']:
        FEEDBACK_TIMINGS = np.array([prt_data[i]['Time start'], prt_data[i]['Time stop']])

    if 'Control' in condition['NameOfCondition']:
        CONTROL_TIMINGS = np.array([prt_data[i]['Time start'], prt_data[i]['Time stop']])

REST_TIMINGS = np.array([prt_data[0]['Time start'],prt_data[0]['Time stop']])

NR_BLOCKS = 16

NR_VOLUMES = max(prt_data[0]['Time stop']) #last rest time point

print('Number of Volumes', NR_VOLUMES)

# preallocate blocks from protocol file
for i in range(NR_VOLUMES):

    if i+1 in REST_TIMINGS[0]: #since prt is in volumes starting from 1
        idx = np.where(REST_TIMINGS[0] == i+1)[0]
        block = design.Block()
        block.set_factor("Condition", "Rest")
        for length in range(int(REST_TIMINGS[1,idx] - REST_TIMINGS[0,idx]+1)):
            trial = design.Trial()
            block.add_trial(trial)
        exp.add_block(block)

    elif i+1 in RECALL_TIMINGS[0]:
        idx = np.where(RECALL_TIMINGS[0] == i+1)[0]
        block = design.Block()
        block.set_factor("Condition", "EmoRecall")
        for length in range(int(RECALL_TIMINGS[1][idx] - RECALL_TIMINGS[0][idx] + 1)):
            trial = design.Trial()
            block.add_trial(trial)
        exp.add_block(block)

    elif i+1 in FEEDBACK_TIMINGS[0]:
        idx = np.where(FEEDBACK_TIMINGS[0] == i+1)[0]
        block = design.Block()
        block.set_factor("Condition", "Feedback")
        for length in range(int(FEEDBACK_TIMINGS[1][idx] - FEEDBACK_TIMINGS[0][idx] + 1)):
            trial = design.Trial()
            block.add_trial(trial)
        exp.add_block(block)

    elif i+1 in CONTROL_TIMINGS[0]:
        idx = np.where(CONTROL_TIMINGS[0] == i+1)[0]
        block = design.Block()
        block.set_factor("Condition", "Control")
        for length in range(int(CONTROL_TIMINGS[1][idx] - CONTROL_TIMINGS[0][idx] + 1)):
            trial = design.Trial()
            block.add_trial(trial)
        exp.add_block(block)



# Check that the inputs are correct for the current subject

image_file = glob.glob(f'{wdir}/data/{sub}/ses-0{session}/runNF{run}/runNF{run}*.txt')[0]
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
    print(images_list)
    exit(1)

# Get group name for logging
group = os.path.basename(image_file).split('_')[1][:-4]

# THERMOMITER SETTINGS
# Rescale the thermometer level based on the PSC settings
for x in range(THERMOMETER_SEGMENTS + 1):
    stim = ThermometerDisplay(x * 10,
                              _max/(_max+ADDITIONAL_LEVELS)*100, # set reference level in percentage, it considers also the case of additional levels above _max
                              nr_segments=THERMOMETER_SEGMENTS,
                              active_colour=ACTIVE_COLOUR,
                              goal_colour=GO_COLOUR,
                              frame_colour=FRAME_COLOUR,
                              inactive_colour= INACTIVE_COLOUR )
    feedback_display.append(stim)
feedback_display.append(feedback_display)




# OUTPUT DATA

#create output folder 
outdir = f'{wdir}/data/{sub}/ses-0{session}/runNF{run}'
os.makedirs(outdir, exist_ok=True)

outdata ={'Condition': [],
          'Volume': [],
          'TBV Detrended Mean': [],
          'Local PSC Detrended Mean': [],
          'All FB corrected PSC': [],
          'TBV request time': [],
          'Baseline time points': [],
          'FB Signal time points': [],
          'Point-wise Baseline List': [],
          'Block baselines': [], 
          'Block feedback values': [],
          'TBV Detrended Mean End': []
          }


# LOGGING SETTINGS
# Save a log file and set level for msg to be received
timestamp = time.strftime("%Y-%m-%d_%H-%M", exp.clock.init_localtime)

logging.basicConfig(filename = f'{outdir}/runNF{run}_{timestamp}.log', 
                                level=logging.INFO,
                                filemode = 'w',
                                format ='%(message)s')


# start logging the experiment information
logging.info('Neuroscience of Happiness - Neurofeedback\n')
logging.info(f'SUBJECT INFO')
logging.info('-----------')
logging.info(f'Subject ID: {sub}')
logging.info(f'Session: {session}')
logging.info(f'Run: {run}')
logging.info(f'Group: {group}\n')

logging.info(f'DESIGN INFO')
logging.info('-----------')
logging.info(f'Conditions:')
for condition in prt_data:
    logging.info(f'\t{condition["NameOfCondition"]}') 
logging.info(f'Max PSC: {_max}')
logging.info(f'Additional PSC: {ADDITIONAL_LEVELS}')
logging.info(f'Thermometer levels: {THERMOMETER_SEGMENTS}\n')


# START THE ESPERIMENT
baselines = []
mean_list = []
means_list_block = []
block_baseline_time_point = []
block_fb_signal_time_points = []
all_fb_psc = []
baseline = 0
idx_bas = 0
loc_bas_block = 0
current_trigger = 0
image_count = 0
thermometer_level = 0
updated_feedback = 0
feedback = 0
mean = None
updated_psc =0
updated_baseline =0
updated_baselines = []
tbv_request_time_point = 0 # seems 0-based check
start_time = 0
# 3 was not enough, I put 5 12/04
values_request_time = np.array(FEEDBACK_TIMINGS[0]) - 5 # ask for the deternded time series 3 time point before the feedback since we are asking TBV values with some delay this is just for safety
bas_ready_time = np.array(RECALL_TIMINGS[0]) + 3

# define baseline and task time points 
baseline_time_points = ([[int(i)] for i in np.arange(1,38)] +
                        [[int(elem) for elem in np.arange(RECALL_TIMINGS[0, i] - BASELINE_BLOCK_POINTS + BASELINE_END_SHIFT, RECALL_TIMINGS[0, i] + BASELINE_END_SHIFT)] for i in range(RECALL_TIMINGS.shape[1])] +
                        [[int(elem) for elem in np.arange(CONTROL_TIMINGS[0, i] - BASELINE_BLOCK_POINTS + BASELINE_END_SHIFT, CONTROL_TIMINGS[0, i] + BASELINE_END_SHIFT)] for i in range(CONTROL_TIMINGS.shape[1])]
                        )

baseline_time_points = np.array(sorted([item for sublist in baseline_time_points for item in sublist]))
print('baseline_time_points: ', baseline_time_points)


fb_signal_time_points = [[int(elem) for elem in np.arange(int(RECALL_TIMINGS[1,i]) - FEEDBACK_AVG +1, int(RECALL_TIMINGS[1,i])+1)] for i in range(RECALL_TIMINGS.shape[1])]
fb_signal_time_points = np.array([item for sublist in fb_signal_time_points for item in sublist])
print('fb_signal_time_points: ', fb_signal_time_points)

print('Request extisting values at time: ', values_request_time)


# log timings where to get dtaa from TBV
logging.info(f'Baseline time points: {baseline_time_points}')
logging.info(f'FB singal time points: {fb_signal_time_points}')
logging.info(f'TBV request existing means time points: {values_request_time}')

logging.info('START')
logging.info('-----------')

# used afterward for the computation of the thermometer level
_max = _max+ADDITIONAL_LEVELS


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

try:

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
                if block.get_factor("Condition") == "Rest":  # Rest
     
                    print(f'\nRest')
                    fixcircle.present()
                    logging.info(f'\nRest')


                elif block.get_factor("Condition") == "EmoRecall":  # Emo

                    print(f'\nEmoRecall')
                    #present a new cue
                    image = stimuli.Picture(f'{images_folder}/{images_list[image_count]}'.replace('\\','/'))  
                    image.present()

                    image_count += 1
                    logging.info(f'\nEmoRecall')

                     # reset the thermomiter level to reaccumulate values
                    thermometer_level = 0
                    mean_list = []
                    means_list_block = []

                elif block.get_factor("Condition") == "Control":  # Control scrambled image

                    print(f'\nControl')
                    #present a new cue
                    image = stimuli.Picture(f'{images_folder}{images_list[image_count]}'.replace('\\','/'))
                    image.present()

                    image_count += 1
                    logging.info(f'\nControl')

                     # reset the thermomiter level to reaccumulate values
                    thermometer_level = 0
                    mean_list = []
                    means_list_block = []
      

                elif block.get_factor("Condition") == "Feedback":  # Feedback

                    print(f'\nFeedback')
                    logging.info(f'\nFeedback')

                    baseline = np.median(baselines[-BASELINE_AVG:])

                    try: 
                        psc = np.mean(mean_list) - baseline

                        if psc is not None or not np.isnan(psc):
                            feedback = int(round((psc/ _max) * 10.0))

                        else:
                            feedback = 0
                            psc = 0
                            print(f'Feedback time point: {current_trigger+1}, Feedback data not ready')
                            logging.info(f'Feedback time point: {current_trigger+1}, Feedback data not ready')

                        if feedback > 10:
                            feedback = 10
                        elif feedback < 0:
                            feedback = 0

                        print(f'Feedback time point: {current_trigger+1}, PSC (local Baseline): {psc}, Baseline: {baseline}, Thermometer level: {feedback}')
                        logging.info(f'Feedback time point: {current_trigger+1}, PSC (local Baseline): {psc}, Baseline: {baseline}, Thermometer level: {feedback}')
                    
                    except Exception as e:
                    
                        print(str(e))
                        feedback = 0
                        psc=0
                        print(f'Feedback time point: {current_trigger+1}, Feedback point data not ready')
                        logging.info(f'Feedback time point: {current_trigger+1}, Feedback point data not ready')
                        
                    try:

                        updated_baseline = np.median(updated_baselines)
                        updated_psc = np.mean(means_list_block) - updated_baseline
                        all_fb_psc.append(updated_psc)

                        updated_feedback = int(round((updated_psc/ _max) * 10.0))

                        if updated_feedback > 10:
                            updated_feedback = 10
                        elif updated_feedback < 0:
                            updated_feedback = 0

                    except Exception as e:

                        updated_feedback = feedback
                        updated_psc = psc
                        logging.info('Block FB not ready, replaced with point FB')
                        logging.info(str(e))

                    print(f'Feedback time point (Block): {current_trigger+1}, PSC (local Baseline): {updated_psc}, Baseline: {updated_baseline}, Thermometer level: {updated_feedback}')
                    logging.info(f'Feedback time point (Block): {current_trigger+1}, PSC (local Baseline): {updated_psc}, Baseline: {updated_baseline}, Thermometer level: {updated_feedback}')

                    feedback_display[updated_feedback].present()

                    # save feedback image to outdir
                    exp.screen.update()
                    exp.screen.save(f'{outdir}/Feedback{image_count}.jpg') 
                    # it's deleted after due to the screen update 
                    #TO DO: search for another solution this is suboptimal, eventually add method to the ThermometerDisplay class to save pygame surface images    
                    feedback_display[updated_feedback].present()

            # The trigger count is updated here to present the condition name before 
            current_trigger += 1 
            print(f'Current Volume: {current_trigger}')
            logging.info(f'Current Volume: {current_trigger}, Time [s] {(trigger_time-start_time)/1000:.3f}')


            if current_trigger >= TBV_REQUEST_DELAY:

                while tbv_request_time_point <= current_trigger - TBV_REQUEST_DELAY:
                
                    exp.keyboard.check()

                    try:
                        mean, rt = TBV.get_detrended_mean_of_roi_at_time_point(ROI, tbv_request_time_point) # tbv_request_time_point must be 0-based
                        t = (exp.clock.time - start_time)/1000 

                    except Exception as e:
                        #print(e)
                        t = (exp.clock.time - start_time)/1000 
                        print(f'Waiting TBV Time point {tbv_request_time_point +1}, Time [s] {t:.3f}')
                        logging.info(f'Waiting TBV Time point: {tbv_request_time_point +1},  Time [s] {t:.3f}')
                        break
                        
                            
                    if mean is not None:  # (In case of a timeout it could be None)

                        tbv_request_time_point += 1 #update tbv request time point here for the next time, hence below tbv_request_time_point could be treated as 1-based

                        if tbv_request_time_point in baseline_time_points:  # Rest

                            # take only baseline values from the longer baseline (before the recall)

                            baselines.append(mean)
                          
                            logging.info(f'Baseline list: {baselines}')
                            print(f'Baseline list: {baselines}')

                        elif tbv_request_time_point in fb_signal_time_points:  # Task

                            mean_list.append(mean)


                        elif tbv_request_time_point in values_request_time:

                            # get all existing mean up to that time point
                            exist_means, rt = TBV.get_existing_detrended_means_of_roi(ROI, tbv_request_time_point-1) # since it was updated before
                            exist_means = np.array(exist_means)

                            # take the last 3 values available for fb
                            cur_fb_points = fb_signal_time_points[fb_signal_time_points<tbv_request_time_point][-FEEDBACK_AVG:] -1
                            block_fb_signal_time_points.append(cur_fb_points + 1)
                            means_list_block = exist_means[cur_fb_points]

                            cur_bas_points = baseline_time_points[baseline_time_points<tbv_request_time_point][-BASELINE_AVG:] -1
                            block_baseline_time_point.append(cur_bas_points + 1)
                            updated_baselines = exist_means[cur_bas_points]
                            outdata['Block baselines'] += [updated_baselines]
                            outdata['Block feedback values'] += [means_list_block]

                        elif tbv_request_time_point in bas_ready_time:

                            baseline = np.median(baselines[-BASELINE_AVG:])


                        print(f'TBV Time point {tbv_request_time_point}, Mean {mean:.4f}, FB Value list point-wise: {mean_list}, FB Value list block-wise: {means_list_block}' )
                        logging.info(f'TBV Time point: {tbv_request_time_point},  Time [s] {t:.3f}, Mean: {mean:.4f}, FB Value list point-wise: {mean_list}, FB Value list block-wise: {means_list_block}')

                        # update outputs
                        outdata['Volume'] += [tbv_request_time_point]
                        outdata['TBV Detrended Mean'] += [mean]
                        outdata['Local PSC Detrended Mean'] += [mean - baseline]
                        outdata['TBV request time'] += [t]
                        outdata['Condition'] += [block.get_factor("Condition")]
                    
                    time.sleep(0.01)    

                        

    # store all the remaining data from TBV
    while tbv_request_time_point < current_trigger: # check this
        start = exp.clock.time
        exp.keyboard.check()  # check to quit
        try:
            mean, rt2 = TBV.get_detrended_mean_of_roi_at_time_point(ROI, tbv_request_time_point)  # tbv_request_time_point must be 0-based
            t = (exp.clock.time - start_time)/1000 

        except:
            time.sleep(0.3)

        if mean is not None:

             # update outputs
            outdata['Volume'] += [tbv_request_time_point+1]
            outdata['TBV Detrended Mean'] += [mean]
            outdata['Local PSC Detrended Mean'] += [mean - baseline]
            outdata['TBV request time'] += [t]
            outdata['Condition'] += [block.get_factor("Condition")]
            
            print(f'TBV Time point {tbv_request_time_point+1}, Mean: {mean:.4f}')
            logging.info(f'TBV Time point: {tbv_request_time_point+1},  Time [s] {t:.3f}, Mean: {mean:.4f}')

            tbv_request_time_point += 1

except Exception as e:
    print(e)

exist_means = []

stimuli.TextScreen(end_header.format(run), end_content).present()

outdata['Baseline time points'] = block_baseline_time_point
outdata['FB Signal time points'] = block_fb_signal_time_points
outdata['Point-wise Baseline List'] = baselines
outdata['TBV Detrended Mean End'] = exist_means
outdata['All FB corrected PSC'] = all_fb_psc

# SAVE OUTDATA
# save log files and outdata


timestamp = time.strftime("%Y-%m-%d_%H-%M", exp.clock.init_localtime)

# save this for safety
outfile = f'{wdir}/data/{sub}/ses-0{session}/runNF{run}/outdata_noend_{timestamp}.pkl'
pickle.dump(outdata, open(outfile,'wb'))

exp.keyboard.wait()


try:
    # get full detrended time series at the last time point
    exist_means, rt = TBV.get_existing_detrended_means_of_roi(ROI, NR_VOLUMES-1) # this is 0-based
except Exception as e:

    print('Problems saving the full average detrended time series')
    print('Requested Roi', ROI)
    print('Requested time point', NR_VOLUMES)
    print(e)
    pass
    
outdata['TBV Detrended Mean End'] = exist_means


timestamp = time.strftime("%Y-%m-%d   %H:%M", exp.clock.init_localtime)
logging.info(f'\n{timestamp}')

timestamp = time.strftime("%Y-%m-%d_%H-%M", exp.clock.init_localtime)

outfile = f'{wdir}/data/{sub}/ses-0{session}/runNF{run}/outdata_{timestamp}.pkl'
pickle.dump(outdata, open(outfile,'wb'))


#print(outdata)

control.end()
