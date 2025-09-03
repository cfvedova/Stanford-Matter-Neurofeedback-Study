'''

Create PRT files for TBV

This script creates protocols files for the TBV PC based on the stimuli order (only when dealing with Matter images).

Practically, it loads the stimuli order files (of the Matter images runs) for the current participant and session and creates
the corresponding protocol files, saving them to a template TBVFiles folder to be used during the real-time scanning session.

'''


import copy
import os, glob, shutil
import numpy as np
import pandas as pd

from utils.prt import create_prt, write_prt

sub_name = input('Insert the subject name: ')
ses = input('Insert the session number: ')

subdir_stim = f'C:/Users/assun/Documents/GitHub/MatterNeurofeedbackStudy/example_data/stim_prep/{sub_name}/ses-0{ses}'
ratings_dir = f'C:/Users/assun/Documents/GitHub/MatterNeurofeedbackStudy/example_data/behavioural/initial_ratings/{sub_name}'

outdir = f'C:/Users/assun/Documents/GitHub/MatterNeurofeedbackStudy/example_data/tbv_prep/{sub_name}'
# Create a folder for this subject in data_TBV
subdir_tbv = f'{outdir}/ses-0{ses}'
os.makedirs(subdir_tbv, exist_ok=True)

# Copy the template TBV file to subdir_tbv
shutil.rmtree(f'{subdir_tbv}/TBVFiles', ignore_errors=True)
shutil.copytree(f'C:/Users/assun/Documents/GitHub/MatterNeurofeedbackStudy/TBVData/TBVFiles', f'{subdir_tbv}/TBVFiles')

# Get NF images order
runs = glob.glob(f'{subdir_stim}/runNF*/runNF*.txt')
runs.sort()
print(runs)

### create NF protocol

N_BLOCKS = 16
INITIAL_REST_DURATION = 40
REST_DURATION = 24
NO_FB_REST_DURATION = 20
RECALL_DURATION = 20
FEEDBACK_DURATION = 4
PRE_FB_REST_DURATION = 8
POST_FB_REST_DURATION = 12
BLOCK_DURATION = RECALL_DURATION + REST_DURATION

# read emotion information for each image
images_emo_info = pd.read_excel(f'{ratings_dir}/selected_matter_ratings_info.xlsx')

# for stock images there are only positive and only 1 recall predictor is needed
# the images order file is only created to name the prt file
# 1 predictor for Positive Recall

for run, order_file in enumerate(runs):

    # create template prt
    prt_hdr, prt_data_temp = create_prt()

    prt_hdr['Experiment'] = 'Neurofeedback'
    prt_hdr['NrOfConditions'] = 4

    # read condition list to get the order of the control images
    images_list = []
    emo_order = []
    with open(order_file, 'r') as f:
        for line in f.readlines():
            images_list.append(line)
            if not 'scrambled' in line:
                emo_order.append(images_emo_info['Peak Labels'][images_emo_info['Image ID'] == line[:-5].split('/')[-1]].values[0])
            else:
                emo_order.append('Control')

    print(images_list)
    timings = list()


    # define here the emotion names
    emo = ['RECOGNITION', 'FAMILY LOVE', 'FRIENDSHIP', 'PLEASURE', 'Control']

    emo_colors = [[76, 0, 153], [0, 255, 0], [0, 0, 255], [255, 255, 0], [143, 143, 143]]
    rest_color = [64, 64, 64]
    img_color = [83, 125, 188]
    fb_color = [255, 0, 0]


    # create timings for Rest condition
    temp_rest = {'Start': [],
                 'Stop': []}
    temp_recall = {'Start': [],
                   'Stop': []}
    temp_feedback = {'Start': [],
                     'Stop': []}
    temp_control = {'Start': [],
                    'Stop': []}

    for i in range(N_BLOCKS):
        if i == 0 and 'scrambled' not in images_list[i]:

            temp_rest['Start'] += [1,  # add 10 seconds more to the first baseline
                                   INITIAL_REST_DURATION + RECALL_DURATION + 1,  # first pre-feedback baseline
                                   INITIAL_REST_DURATION + RECALL_DURATION + PRE_FB_REST_DURATION + FEEDBACK_DURATION + 1]  # first post-feedback baseline

            temp_rest['Stop'] += [INITIAL_REST_DURATION,
                                  INITIAL_REST_DURATION + RECALL_DURATION + PRE_FB_REST_DURATION,
                                  INITIAL_REST_DURATION + RECALL_DURATION + PRE_FB_REST_DURATION + FEEDBACK_DURATION + POST_FB_REST_DURATION]

            temp_recall['Start'] += [temp_rest['Stop'][-3] + 1]
            temp_recall['Stop'] += [temp_rest['Stop'][-3] + RECALL_DURATION]

            temp_feedback['Start'] += [temp_rest['Stop'][-2] + 1]
            temp_feedback['Stop'] += [temp_rest['Stop'][-2] + FEEDBACK_DURATION]

        elif i == 0 and 'scrambled' in images_list[i]:

            temp_rest['Start'] += [1,
                                   INITIAL_REST_DURATION + RECALL_DURATION + 1]

            temp_rest['Stop'] += [INITIAL_REST_DURATION,
                                  INITIAL_REST_DURATION + RECALL_DURATION + NO_FB_REST_DURATION]

            temp_control['Start'] += [temp_rest['Stop'][-2] + 1]
            temp_control['Stop'] += [temp_rest['Stop'][-2] + RECALL_DURATION]

        elif i > 0 and 'scrambled' not in images_list[i]:

            temp_recall['Start'] += [temp_rest['Stop'][-1] + 1]
            temp_recall['Stop'] += [temp_rest['Stop'][-1] + RECALL_DURATION]

            temp_rest['Start'] += [temp_recall['Stop'][-1] + 1,
                                   temp_recall['Stop'][-1] + PRE_FB_REST_DURATION + FEEDBACK_DURATION + 1]

            temp_rest['Stop'] += [temp_recall['Stop'][-1] + PRE_FB_REST_DURATION,
                                  temp_recall['Stop'][
                                      -1] + PRE_FB_REST_DURATION + FEEDBACK_DURATION + POST_FB_REST_DURATION]

            temp_feedback['Start'] += [temp_rest['Stop'][-2] + 1]
            temp_feedback['Stop'] += [temp_rest['Stop'][-2] + FEEDBACK_DURATION]

        elif i > 0 and 'scrambled' in images_list[i]:

            temp_control['Start'] += [temp_rest['Stop'][-1] + 1]
            temp_control['Stop'] += [temp_rest['Stop'][-1] + RECALL_DURATION]

            temp_rest['Start'] += [temp_control['Stop'][-1] + 1]

            temp_rest['Stop'] += [temp_control['Stop'][-1] + NO_FB_REST_DURATION]

    # check condition order to append the timings to the prt file

    if 'scrambled' in images_list[0]:

        timings.append(temp_rest)
        timings.append(temp_control)
        timings.append(temp_recall)
        timings.append(temp_feedback)

        condition_names = ['Rest', 'Control', 'EmoRecall', 'Feedback']
        condition_colors = [[64, 64, 64], [143, 143, 143], [83, 200, 83], [255, 0, 0]]

    else:

        timings.append(temp_rest)
        timings.append(temp_recall)
        timings.append(temp_feedback)
        timings.append(temp_control)

        condition_names = ['Rest', 'EmoRecall', 'Feedback', 'Control']
        condition_colors = [[64, 64, 64], [83, 200, 83], [255, 0, 0], [143, 143, 143]]

    prt_data = list()
    for i in range(prt_hdr['NrOfConditions']):
        temp_data = copy.deepcopy(prt_data_temp[0])
        temp_data['NameOfCondition'] = condition_names[i]
        temp_data['NrOfOccurances'] = len(timings[i]['Start'])
        temp_data['Time start'] = timings[i]['Start']
        temp_data['Time stop'] = timings[i]['Stop']
        temp_data['Color'] = condition_colors[i]

        prt_data.append(temp_data)

    # write the prt file to the stim folder for the stimulation script
    prt_file = f'{os.path.basename(order_file)[:-4]}.prt'
    write_prt(f'{subdir_stim}/runNF{run + 1}/{prt_file}', prt_hdr, prt_data)

    # separate timings for different emotions
    prtFolder = f'{subdir_tbv}/TBVFiles/prt/'
    prt_hdr['NrOfConditions'] = 7

    # check the first occurrence of each emotion to create the prt correctly
    emo_first_occurrence_order = sorted(set(emo_order), key=emo_order.index)
    first_occurence_indices = [emo.index(emo_sort) for emo_sort in emo_first_occurrence_order]
    # define condition names for the prt creation
    if emo_first_occurrence_order[0] != 'Control':
        condition_names = ['Rest', emo_first_occurrence_order[0], 'Feedback',
                           emo_first_occurrence_order[1], emo_first_occurrence_order[2],
                           emo_first_occurrence_order[3], emo_first_occurrence_order[4]]


        colors = [rest_color,
                  emo_colors[first_occurence_indices[0]],
                  fb_color,
                  emo_colors[first_occurence_indices[1]],
                  emo_colors[first_occurence_indices[2]],
                  emo_colors[first_occurence_indices[3]],
                  emo_colors[first_occurence_indices[4]]]
    else:
        condition_names = ['Rest', emo_first_occurrence_order[0],
                           emo_first_occurrence_order[1],  'Feedback',emo_first_occurrence_order[2],
                           emo_first_occurrence_order[3], emo_first_occurrence_order[4]]

        colors = [rest_color,
                  emo_colors[first_occurence_indices[0]],
                  emo_colors[first_occurence_indices[1]],
                  fb_color,
                  emo_colors[first_occurence_indices[2]],
                  emo_colors[first_occurence_indices[3]],
                  emo_colors[first_occurence_indices[4]]]

    prt_data = list()
    for i in range(len(condition_names)):
        temp_data = copy.deepcopy(prt_data_temp[0])
        temp_data['NameOfCondition'] = condition_names[i]

        if condition_names[i]=='Rest':
            temp_data['NrOfOccurances'] = len(timings[0]['Start'])
            temp_data['Time start'] = timings[0]['Start']
            temp_data['Time stop'] = timings[0]['Stop']
            temp_data['Color'] = colors[i]

        elif condition_names[i]=='Control':
            temp_data['NrOfOccurances'] = len(temp_control['Start'])
            temp_data['Time start'] = temp_control['Start']
            temp_data['Time stop'] = temp_control['Stop']
            temp_data['Color'] = colors[i]

        elif condition_names[i]=='Feedback':
            temp_data['NrOfOccurances'] = len(temp_feedback['Start'])
            temp_data['Time start'] = temp_feedback['Start']
            temp_data['Time stop'] = temp_feedback['Stop']
            temp_data['Color'] = colors[i]

        else:
            # check index for the current emotion and corresponding timings in temp_recall
            # remove control from order
            emo_order_noControl = [item for item in emo_order if item!='Control']
            emo_index = [idx for idx,item in enumerate(emo_order_noControl) if item == condition_names[i]]
            temp_data['NrOfOccurances'] = len(emo_index)
            temp_data['Time start'] = [temp_recall['Start'][idx] for idx in np.array(emo_index)]
            temp_data['Time stop'] = [temp_recall['Stop'][idx] for idx in np.array(emo_index)]
            temp_data['Color'] = colors[i]

        prt_data.append(temp_data)


    prt_file = f'{os.path.basename(order_file)[:-4]}.prt'
    write_prt(f'{prtFolder}/{prt_file}', prt_hdr, prt_data)

# create Localiser script

# for the Localiser, there are Positive and Neutral images, two recall predictors are needed
# 1 predictor for Image
# 1 predictor for Neutral
# 1 predicotr for Positive

N_BLOCKS = 16
INITIAL_REST_DURATION = 20
REST_DURATION = 20
RECALL_DURATION = 20
BLOCK_DURATION = RECALL_DURATION + REST_DURATION


# load the Localiser images order and create a condition
localiser_files = glob.glob(f'{subdir_stim}/Localiser*matter.txt')

for run, localiser_order in enumerate(localiser_files):

    localiser_conditions = []
    with open(localiser_order,'r') as f:

        for line in f.readlines():

            if 'neutral' in line:
                localiser_conditions.append('Neutral')
            else:
                localiser_conditions.append('Positive')

    print('Localiser condition order:')
    print(localiser_conditions)

    condition_names = ['Rest']
    condition_colors = [[64, 64, 64]]

    # define the condition order in the prt file based on occurrence
    if localiser_conditions[0] == 'Positive':
        condition_names += ['EmoRecall-Positive', 'EmoRecall-Neutral']
        condition_colors += [[83, 200, 83], [150, 150, 150]]

    else:
        condition_names += ['EmoRecall-Neutral', 'EmoRecall-Positive']
        condition_colors += [[150, 150, 150], [83, 200, 83]]

    # create template prt
    prt_hdr, prt_data_temp = create_prt()
    prt_hdr['Experiment'] = 'Localiser'
    prt_hdr['NrOfConditions'] = 3

    prt_data = list()

    for n,condition in enumerate(condition_names):

        temp = {'Start': [],
                'Stop': []}

        if condition == 'Rest':
            temp = {'Start': [1],
                    'Stop': [INITIAL_REST_DURATION]}

            for i in range(N_BLOCKS ):
                temp['Start'] += [INITIAL_REST_DURATION  + RECALL_DURATION + (BLOCK_DURATION)*i + 1]
                temp['Stop'] += [INITIAL_REST_DURATION  + RECALL_DURATION + (BLOCK_DURATION)*i + REST_DURATION]


        elif condition == 'EmoRecall-Positive':

            temp = {'Start': [],
                    'Stop': []}

            idx_pos = [i for i, cond in enumerate(localiser_conditions) if cond == 'Positive']

            for i in idx_pos:
                if i == 0:
                    temp['Start'] += [INITIAL_REST_DURATION  +1]
                    temp['Stop'] += [INITIAL_REST_DURATION  + RECALL_DURATION]
                else:
                    temp['Start'] += [INITIAL_REST_DURATION + i*BLOCK_DURATION  +1]
                    temp['Stop'] += [INITIAL_REST_DURATION + i*BLOCK_DURATION  + RECALL_DURATION]

        elif condition == 'EmoRecall-Neutral':

            temp = {'Start': [],
                    'Stop': []}

            idx_neu = [i for i, cond in enumerate(localiser_conditions) if cond == 'Neutral']

            for i in idx_neu:
                if i == 0:
                    temp['Start'] += [INITIAL_REST_DURATION  + 1]
                    temp['Stop'] += [INITIAL_REST_DURATION  + RECALL_DURATION]
                else:
                    temp['Start'] += [INITIAL_REST_DURATION + i * BLOCK_DURATION  + 1]
                    temp['Stop'] += [INITIAL_REST_DURATION + i * BLOCK_DURATION  + RECALL_DURATION]

        temp_data = copy.deepcopy(prt_data_temp[0])
        temp_data['NameOfCondition'] = condition_names[n]
        temp_data['NrOfOccurances'] = len(temp['Start'])
        temp_data['Time start'] = temp['Start']
        temp_data['Time stop'] = temp['Stop']
        temp_data['Color'] = condition_colors[n]

        prt_data.append(temp_data)


    prtFolder = f'{subdir_tbv}/TBVFiles/prt/'
    prt_file =f'{os.path.basename(localiser_order)[:-4]}.prt'
    write_prt(f'{prtFolder}/{prt_file}', prt_hdr, prt_data)

# load the Localiser images order and create a condition
transfer_files = glob.glob(f'{subdir_stim}/Transfer*.txt')

for run, transfer_order in enumerate(transfer_files):

    localiser_conditions = []
    with open(transfer_order, 'r') as f:

        for line in f.readlines():

            if 'scrambled' in line:
                localiser_conditions.append('Control')
            else:
                localiser_conditions.append('EmoRecall')

    print('Transfer condition order:')
    print(localiser_conditions)

    condition_names = ['Rest']
    condition_colors = [[64, 64, 64]]

    # define the condition order in the prt file based on occurrence
    if localiser_conditions[0] == 'EmoRecall':
        condition_names += ['EmoRecall', 'Control']
        condition_colors += [[83, 200, 83], [150, 150, 150]]

    else:
        condition_names += ['Control', 'EmoRecall']
        condition_colors += [[150, 150, 150], [83, 200, 83]]

    # create template prt
    prt_hdr, prt_data_temp = create_prt()
    prt_hdr['Experiment'] = 'Transfer'
    prt_hdr['NrOfConditions'] = 3

    prt_data = list()

    for n, condition in enumerate(condition_names):

        temp = {'Start': [],
                'Stop': []}

        if condition == 'Rest':
            temp = {'Start': [1],
                    'Stop': [INITIAL_REST_DURATION]}

            for i in range(N_BLOCKS):
                temp['Start'] += [INITIAL_REST_DURATION + RECALL_DURATION + (BLOCK_DURATION) * i + 1]
                temp['Stop'] += [INITIAL_REST_DURATION + RECALL_DURATION + (BLOCK_DURATION) * i + REST_DURATION]


        elif condition == 'EmoRecall':

            temp = {'Start': [],
                    'Stop': []}

            idx_pos = [i for i, cond in enumerate(localiser_conditions) if cond == 'EmoRecall']

            for i in idx_pos:
                if i == 0:
                    temp['Start'] += [INITIAL_REST_DURATION + 1]
                    temp['Stop'] += [INITIAL_REST_DURATION + RECALL_DURATION]
                else:
                    temp['Start'] += [INITIAL_REST_DURATION + i * BLOCK_DURATION + 1]
                    temp['Stop'] += [INITIAL_REST_DURATION + i * BLOCK_DURATION + RECALL_DURATION]

        elif condition == 'Control':

            temp = {'Start': [],
                    'Stop': []}

            idx_neu = [i for i, cond in enumerate(localiser_conditions) if cond == 'Control']

            for i in idx_neu:
                if i == 0:
                    temp['Start'] += [INITIAL_REST_DURATION + 1]
                    temp['Stop'] += [INITIAL_REST_DURATION + RECALL_DURATION]
                else:
                    temp['Start'] += [INITIAL_REST_DURATION + i * BLOCK_DURATION + 1]
                    temp['Stop'] += [INITIAL_REST_DURATION + i * BLOCK_DURATION + RECALL_DURATION]

        temp_data = copy.deepcopy(prt_data_temp[0])
        temp_data['NameOfCondition'] = condition_names[n]
        temp_data['NrOfOccurances'] = len(temp['Start'])
        temp_data['Time start'] = temp['Start']
        temp_data['Time stop'] = temp['Stop']
        temp_data['Color'] = condition_colors[n]

        prt_data.append(temp_data)

    prtFolder = f'{subdir_tbv}/TBVFiles/prt/'
    prt_file = f'{os.path.basename(transfer_order)[:-4]}.prt'
    write_prt(f'{prtFolder}/{prt_file}', prt_hdr, prt_data)