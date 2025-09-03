'''

Create PRT files for the Stimuli presentation

This script creates prt files that are used to define the timings of the stimuli in the presentation scripts.
This only needs to be run once at the start of the study.

'''

from utils.prt import create_prt, write_prt
import copy

prtFolder = 'C:/Users/assun/Documents/GitHub/MatterNeurofeedbackStudy/stimPCData/prt'

# create NF protocol
N_BLOCKS = 16
INITIAL_REST_DURATION = 40
REST_DURATION = 24
RECALL_DURATION = 20
FEEDBACK_DURATION = 4
PRE_FB_REST_DURATION = 8 
POST_FB_REST_DURATION = 12 
BLOCK_DURATION = RECALL_DURATION + REST_DURATION

condition_names = ['Rest', 'EmoRecall', 'Feedback']
condition_colors = [[64, 64, 64], [83, 200, 83], [255,0,0]]

# create template prt
prt_hdr, prt_data_temp = create_prt()

prt_hdr['Experiment'] = 'Neurofeedback'
prt_hdr['NrOfConditions'] = 3

timings = list()

#create timings for Rest condition
temp = {'Start':[],
        'Stop': []}
for i in range(N_BLOCKS):
    if i == 0 :

        temp['Start'] += [1, #add more seconds to the first baseline
                          INITIAL_REST_DURATION + RECALL_DURATION + 1, #first pre-feedback baseline
                          INITIAL_REST_DURATION + RECALL_DURATION + PRE_FB_REST_DURATION + FEEDBACK_DURATION + 1] #first post-feedback baseline

        temp['Stop'] += [INITIAL_REST_DURATION,
                         INITIAL_REST_DURATION  + RECALL_DURATION + PRE_FB_REST_DURATION,
                         INITIAL_REST_DURATION + RECALL_DURATION + PRE_FB_REST_DURATION + FEEDBACK_DURATION + POST_FB_REST_DURATION]
    else:

        temp['Start'] += [INITIAL_REST_DURATION + RECALL_DURATION + i * BLOCK_DURATION + 1,
                          INITIAL_REST_DURATION + RECALL_DURATION + i * BLOCK_DURATION + PRE_FB_REST_DURATION + FEEDBACK_DURATION +1]

        temp['Stop'] += [INITIAL_REST_DURATION + RECALL_DURATION + i * BLOCK_DURATION + PRE_FB_REST_DURATION,
                         INITIAL_REST_DURATION + RECALL_DURATION + i * BLOCK_DURATION + REST_DURATION]

timings.append(temp)


# create timings for EmoRecall condition
temp = {'Start': [],
        'Stop': []}
for i in range(N_BLOCKS):
    if i==0:
        temp['Start'] += [INITIAL_REST_DURATION +1 ]
        temp['Stop'] += [INITIAL_REST_DURATION + RECALL_DURATION]
    else:
        temp['Start'] += [INITIAL_REST_DURATION + i*BLOCK_DURATION +1]
        temp['Stop'] += [INITIAL_REST_DURATION + i*BLOCK_DURATION + RECALL_DURATION]

timings.append(temp)

#create timings for Feedback
temp = {'Start': [],
        'Stop': []}
for i in range(N_BLOCKS):
    if i==0:
        temp['Start'] += [INITIAL_REST_DURATION+ RECALL_DURATION + PRE_FB_REST_DURATION + 1 ]
        temp['Stop'] += [INITIAL_REST_DURATION + RECALL_DURATION + PRE_FB_REST_DURATION + FEEDBACK_DURATION]
    else:
        temp['Start'] += [INITIAL_REST_DURATION + i*BLOCK_DURATION + RECALL_DURATION + PRE_FB_REST_DURATION + 1 ]
        temp['Stop'] += [INITIAL_REST_DURATION + i*BLOCK_DURATION  + RECALL_DURATION + PRE_FB_REST_DURATION + FEEDBACK_DURATION]
timings.append(temp)

prt_data = list()
for i in range(prt_hdr['NrOfConditions']):
    temp_data = copy.deepcopy(prt_data_temp[0])
    temp_data['NameOfCondition'] = condition_names[i]
    temp_data['NrOfOccurances'] = len(timings[i]['Start'])
    temp_data['Time start'] = timings[i]['Start']
    temp_data['Time stop'] = timings[i]['Stop']
    temp_data['Color'] = condition_colors[i]

    prt_data.append(temp_data)

# save prt for stim PC
prt_file = 'Neurofeedback_stimPC.prt'
write_prt(f'{prtFolder}/{prt_file}', prt_hdr, prt_data)


# create prt for the Localiser script

N_BLOCKS = 16
INITIAL_REST_DURATION = 20
REST_DURATION = 20
RECALL_DURATION = 20
BLOCK_DURATION = RECALL_DURATION + REST_DURATION

condition_names = ['Rest', 'EmoRecall']
condition_colors = [[64, 64, 64], [83, 200, 83]]

# create template prt
prt_hdr, prt_data_temp = create_prt()

prt_hdr['Experiment'] = 'Localiser'
prt_hdr['NrOfConditions'] = 2

prt_data = []

for n, condition in enumerate(condition_names):

    temp = {'Start': [],
            'Stop': []}

    if condition == 'Rest':

        temp = {'Start': [1],
                'Stop': [INITIAL_REST_DURATION]}

        for i in range(N_BLOCKS):
            temp['Start'] += [INITIAL_REST_DURATION  + RECALL_DURATION + (BLOCK_DURATION) * i + 1]
            temp['Stop'] += [INITIAL_REST_DURATION  + RECALL_DURATION + (BLOCK_DURATION) * i + REST_DURATION]

    elif condition == 'EmoRecall':

        temp = {'Start': [],
                'Stop': []}

        for i in range(N_BLOCKS):
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

prt_file = 'Localiser_stimPC.prt'

write_prt(f'{prtFolder}/{prt_file}', prt_hdr, prt_data)


