import matplotlib.pyplot as plt
import pickle, os
import matplotlib
from bvbabel import prt
from matplotlib.patches import Rectangle, Patch
import numpy as np
import seaborn as sns
import pandas as pd
matplotlib.use('Qt5Agg')

# session 2
nr_nf_runs=4
outdata_list = ['_2024-12-04_11-40.pkl', '_2024-12-04_11-57.pkl', '_2024-12-04_12-16.pkl','_2024-12-04_13-02.pkl']
online_psc = []
offline_psc= []
ctrl_psc = []
df2 = {'data':[],
      'type':[],
      'Run':[]}

for run in range(1,nr_nf_runs+1):

    wdir = f'D:/NFData/raw_data/StandardNF/sub-00/ses-02/stim/runNF{run}'
    data = pickle.load(open(f'{wdir}/outdata{outdata_list[run-1]}','rb'))

    #load end of run data that was saved separately
    data_end = np.array(pickle.load(open(f'{wdir}/end_run_time_series.pkl','rb')))
    data['TBV Detrended Mean End'] = data_end

    hdr, prt_data = prt.read_prt(f'{wdir}/runNF{run}_stock.prt')
    ctrl_pts =[]
    for i, condition in enumerate(prt_data):
        if 'Control' in condition['NameOfCondition']:
            CONTROL_TIMINGS = np.array([prt_data[i]['Time start'], prt_data[i]['Time stop']])
    for pt in  CONTROL_TIMINGS[1,:]:
        ctrl_pts.append(np.arange(pt-9, pt+1))

    online_psc.append(data['All FB corrected PSC'])

    bas = np.unique(np.concatenate(data['Baseline time points']))
    bas_val = np.mean(data['TBV Detrended Mean End'][bas])
    temp=[]
    for i in range(len(data['FB Signal time points'])):
        fb_values = np.mean(data['TBV Detrended Mean End'][data['FB Signal time points'][i]])
        temp.append(fb_values-bas_val)
    offline_psc.append(temp)
    temp =[]
    for i in range(4):
        temp.append(np.mean(data['TBV Detrended Mean End'][ctrl_pts[i]])-bas_val)
    ctrl_psc.append(temp)

    df2['data'] += online_psc[-1]
    df2['data'] += offline_psc[-1]
    df2['data'] +=  ctrl_psc[-1]
    df2['type'] += ['Online PSC']*12 + ['Offline PSC']*12 + ['Control PSC']*4
    df2['Run'] += [run]*28

    fig, ax = plt.subplots()
    ax.plot(np.arange(12),online_psc[run-1])
    ax.plot(np.arange(12),offline_psc[run-1])

df2 = pd.DataFrame(df2)
fig, ax = plt.subplots()
s = sns.barplot(data=df2,x='Run',y='data', hue='type',  errorbar='sd', ax=ax )
ax.legend().remove()
ax.set_ylim([-0.5,2.2])
ax.set_title('Session 2')

# session 3
nr_nf_runs=3
outdata_list = ['_2024-12-09_17-00.pkl','_2024-12-09_17-24.pkl','_2024-12-09_17-39.pkl']
online_psc = []
offline_psc = []
ctrl_psc = []
df3 = {'data':[],
      'type':[],
      'Run':[]}
for run in range(1,nr_nf_runs+1):
    wdir = f'D:/NFData/raw_data/StandardNF/sub-00/ses-03/stim/runNF{run}'
    data = pickle.load(open(f'{wdir}/outdata{outdata_list[run-1]}','rb'))
    data['TBV Detrended Mean End'] = np.array(data['TBV Detrended Mean End'])

    hdr, prt_data = prt.read_prt(f'{wdir}/runNF{run}_stock.prt')

    ctrl_pts =[]
    for i, condition in enumerate(prt_data):
        if 'Control' in condition['NameOfCondition']:
            CONTROL_TIMINGS = np.array([prt_data[i]['Time start'], prt_data[i]['Time stop']])
    for pt in  CONTROL_TIMINGS[1,:]:
        ctrl_pts.append(np.arange(pt-9, pt+1))

    online_psc.append(data['All FB corrected PSC'])

    bas = np.unique(np.concatenate(data['Baseline time points']))
    bas_val = np.mean(data['TBV Detrended Mean End'][bas])
    temp=[]
    for i in range(len(data['FB Signal time points'])):
        fb_values = np.mean(data['TBV Detrended Mean End'][data['FB Signal time points'][i]])
        temp.append(fb_values-bas_val)
    offline_psc.append(temp)
    temp =[]
    for i in range(4):
        temp.append(np.mean(data['TBV Detrended Mean End'][ctrl_pts[i]])-bas_val)
    ctrl_psc.append(temp)

    df3['data'] += online_psc[-1]
    df3['data'] += offline_psc[-1]
    df3['data'] += ctrl_psc[-1]
    df3['type'] += ['Online PSC']*12 + ['Offline PSC']*12 + ['Control PSC']*4
    df3['Run'] += [run]*28

    fig, ax = plt.subplots()
    ax.plot(np.arange(12),online_psc[run-1])
    ax.plot(np.arange(12),offline_psc[run-1])

df3 = pd.DataFrame(df3)
fig, ax = plt.subplots()
s = sns.barplot(data=df3,x='Run',y='data', hue='type',  errorbar='sd', ax=ax )
ax.legend().remove()
ax.set_ylim([-0.5,2.2])
ax.set_title('Session 3')

# session 4
nr_nf_runs=4
outdata_list = ['_2024-12-13_15-40.pkl','_2024-12-13_15-55.pkl','_2024-12-13_16-32.pkl','_2024-12-13_17-03.pkl']
online_psc = []
offline_psc = []
ctrl_psc = []
df4 = {'data':[],
      'type':[],
      'Run':[]}
for run in range(1,nr_nf_runs+1):
    wdir = f'D:/NFData/raw_data/StandardNF/sub-00/ses-04/stim/runNF{run}'
    data = pickle.load(open(f'{wdir}/outdata_noend{outdata_list[run-1]}','rb'))

    data_end = np.array(pickle.load(open(f'{wdir}/end_run_time_series.pkl', 'rb')))
    data['TBV Detrended Mean End'] = data_end

    hdr, prt_data = prt.read_prt(f'{wdir}/runNF{run}_stock.prt')

    ctrl_pts = []
    for i, condition in enumerate(prt_data):
        if 'Control' in condition['NameOfCondition']:
            CONTROL_TIMINGS = np.array([prt_data[i]['Time start'], prt_data[i]['Time stop']])
    for pt in CONTROL_TIMINGS[1, :]:
        ctrl_pts.append(np.arange(pt - 9, pt + 1))

    online_psc.append(data['All FB corrected PSC'])

    bas = np.unique(np.concatenate(data['Baseline time points']))
    bas_val = np.mean(data['TBV Detrended Mean End'][bas])
    temp = []
    for i in range(len(data['FB Signal time points'])):
        fb_values = np.mean(data['TBV Detrended Mean End'][data['FB Signal time points'][i]])
        temp.append(fb_values - bas_val)
    offline_psc.append(temp)
    temp = []
    for i in range(4):
        temp.append(np.mean(data['TBV Detrended Mean End'][ctrl_pts[i]]) - bas_val)
    ctrl_psc.append(temp)

    df4['data'] += online_psc[-1]
    df4['data'] += offline_psc[-1]
    df4['data'] += ctrl_psc[-1]
    df4['type'] += ['Online PSC'] * 12 + ['Offline PSC'] * 12 + ['Control PSC'] * 4
    df4['Run'] += [run] * 28

    fig, ax = plt.subplots()
    ax.plot(np.arange(12), online_psc[run - 1])
    ax.plot(np.arange(12), offline_psc[run - 1])

df4 = pd.DataFrame(df4)
fig, ax = plt.subplots()
s = sns.barplot(data=df4, x='Run', y='data', hue='type', errorbar='sd', ax=ax)
ax.set_ylim([-0.5,2.2])
ax.legend().remove()
ax.set_title('Session 4')

# session 5
nr_nf_runs=3
offline_psc = []
ctrl_psc = []
BASELINE_BLOCK_POINTS = 5
BASELINE_END_SHIFT = 2
df5 = {'data':[],
      'type':[],
      'Run':[]}
for run in range(1,nr_nf_runs+1):
    wdir = f'D:/NFData/raw_data/StandardNF/sub-00/ses-05/stim/'
    data = np.array(pickle.load(open(f'{wdir}/Transfer{run}.pkl','rb')))
    #data_end = pickle.load(open(f'{wdir}/end_run_time_series3.pkl','rb'))
    #data['TBV Detrended Mean End'] = data_end
    hdr, prt_data = prt.read_prt(f'{wdir}/Transfer{run}_stock.prt')

    for i, condition in enumerate(prt_data):
        if 'EmoRecall' in condition['NameOfCondition']:
            RECALL_TIMINGS = np.array([prt_data[i]['Time start'], prt_data[i]['Time stop']])

        if 'Control' in condition['NameOfCondition']:
            CONTROL_TIMINGS = np.array([prt_data[i]['Time start'], prt_data[i]['Time stop']])

    REST_TIMINGS = np.array([prt_data[0]['Time start'], prt_data[0]['Time stop']])

    ctrl_pts = []
    recall_pts = []
    for pt in CONTROL_TIMINGS[1, :]:
        ctrl_pts.append(np.arange(pt - 9, pt + 1))

    for pt in RECALL_TIMINGS[1, :]:
        recall_pts.append(np.arange(pt - 9, pt + 1))

    baseline_time_points = ([[int(i)] for i in np.arange(1, 18)] +
                            [[int(elem) for elem in
                              np.arange(RECALL_TIMINGS[0, i] - BASELINE_BLOCK_POINTS + BASELINE_END_SHIFT,
                                        RECALL_TIMINGS[0, i] + BASELINE_END_SHIFT)] for i in
                             range(RECALL_TIMINGS.shape[1])] +
                            [[int(elem) for elem in
                              np.arange(CONTROL_TIMINGS[0, i] - BASELINE_BLOCK_POINTS + BASELINE_END_SHIFT,
                                        CONTROL_TIMINGS[0, i] + BASELINE_END_SHIFT)] for i in
                             range(CONTROL_TIMINGS.shape[1])]
                            )

    baseline_time_points = np.array(sorted([item for sublist in baseline_time_points for item in sublist]))

    bas_val = np.mean(data[baseline_time_points])
    temp = []
    for i in range(12):
        fb_values = np.mean(data[recall_pts[i]])
        temp.append(fb_values - bas_val)
    offline_psc.append(temp)
    temp = []
    for i in range(4):
        temp.append(np.mean(data[ctrl_pts[i]]) - bas_val)
    ctrl_psc.append(temp)

    df5['data'] += offline_psc[-1]
    df5['data'] += ctrl_psc[-1]
    df5['type'] += ['Offline PSC'] * 12 + ['Control PSC'] * 4
    df5['Run'] += [run] * 16

    fig, ax = plt.subplots()
    ax.plot(np.arange(12), offline_psc[run - 1])

df5 = pd.DataFrame(df5)
fig, ax = plt.subplots()
# Get the second color from the default 'deep' palette

# Set the palette to use the second color for one category and default for the other
custom_palette = {'Offline PSC': (1,129/255,44/255), 'Control PSC': (58/255,146/255,58/255)}

# Plot with the custom palette
sns.barplot(data=df5, x='Run', y='data', hue='type', errorbar='sd', ax=ax, palette=custom_palette)
ax.set_ylim([-0.5,2.2])
ax.legend().remove()
ax.set_title('Session 5')

