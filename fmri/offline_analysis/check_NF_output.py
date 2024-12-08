import matplotlib.pyplot as plt
import pickle, os
import matplotlib
from bvbabel import prt
from matplotlib.patches import Rectangle, Patch
import numpy as np
matplotlib.use('Qt5Agg')

def add_prt_plot(protocol,ax):
    for cond in protocol:
        for event in range(cond['NrOfOccurances']):
            ax.add_patch(Rectangle((cond['Time start'][event],-3),
                                       cond['Time stop'][event] - cond['Time start'][event], 6,
                                       facecolor=np.array(cond['Color']) / 255,
                                       edgecolor='none',
                                       alpha=0.3,label='_nolegend_'))
    return ax

wdir = 'D:/NFData/raw_data/StandardNF/sub00/ses2/sub00_online_stim/ses2/runNF1'
#data = pickle.load(open(f'{wdir}/data/sub01/ses1/run2/outdata.pkl','rb'))
data = pickle.load(open(f'{wdir}/outdata_2024-12-04_11-40.pkl','rb'))

#hdr, prt_data = prt.read_prt(wdir + '/prt/Neurofeedback_Run_offline_test_v2_short.prt')
hdr, prt_data = prt.read_prt(f'{wdir}/runNF1_stock.prt')


fig,ax=plt.subplots()
handles = []
ax = add_prt_plot(prt_data,ax)
ax.plot(data['Volume'],data['TBV Detrended Mean'], 'k--', linewidth = 0.8)
ax.plot(data['Volume'],np.array(data['TBV Detrended Mean'])-np.array(data['Local PSC Detrended Mean']),'grey', linewidth = 0.8)
ax.plot(data['Volume'],data['Local PSC Detrended Mean'],'k', linewidth = 0.8)
ax.legend(['TBV Detrended Mean','Baseline','Local PSC Detrended Mean'])

fig, ax =plt.subplots()

ax.plot(data['All FB corrected PSC'])

wdir = 'D:/NFData/raw_data/StandardNF/sub00/ses2/sub00_online_stim/ses2/runNF2'
data = pickle.load(open(f'{wdir}/outdata_2024-12-04_11-57.pkl','rb'))

ax.plot(data['All FB corrected PSC'])

wdir = 'D:/NFData/raw_data/StandardNF/sub00/ses2/sub00_online_stim/ses2/runNF3'
data = pickle.load(open(f'{wdir}/outdata_2024-12-04_12-16.pkl','rb'))

ax.plot(data['All FB corrected PSC'])

wdir = 'D:/NFData/raw_data/StandardNF/sub00/ses2/sub00_online_stim/ses2/runNF4'
data = pickle.load(open(f'{wdir}/outdata_2024-12-04_13-02.pkl','rb'))

ax.plot(data['All FB corrected PSC'])
ax.legend(['NFrun1', 'NFrun2', 'NFrun3', 'NFrun4'])




import os, pickle
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
import numpy as np
matplotlib.use('Qt5Agg')

# plot results for the stock NF run
data_dir = 'E:/Matter_project/NF_project/NFPilot1Data/output/Pilot1NF_outputStimPC/sub01/ses1/run1'
outdata = pickle.load(open(f'{data_dir}/outdata.pkl','rb'))

# for the stock images there are only positive

# plot PSC of 1st and second occurence of the image
FB_data = outdata['Feedback Info']
first_second_label = ['First time','Second time']* 8

sample_data = pd.DataFrame({'Order': first_second_label,
                            'PSC value': FB_data['Local PSC Detrended Mean']
                            })
fig, ax = plt.subplots()
ax = sns.swarmplot(x='Order', y='PSC value', data=sample_data, s=10, palette='tab10', ax=ax)
for (x0, y0), (x1, y1) in zip(ax.collections[0].get_offsets(), ax.collections[1].get_offsets()):
    ax.plot([x0, x1], [y0, y1], color='black', ls=':', zorder=0)
plt.show()


FB_data_online = FB_data.copy()

#offline NF run stock images

data_dir = 'E:/Matter_project/NF_project/7TPCtests/NF_scripts_pilot1/data/sub01/ses1/run1'
outdata = pickle.load(open(f'{data_dir}/outdata.pkl','rb'))

# for the stock images there are only positive

# plot PSC of 1st and second occurence of the image
FB_data = outdata['Feedback Info']
first_second_label = ['First time','Second time']* 8

sample_data = pd.DataFrame({'Order': first_second_label,
                            'PSC value': np.array(FB_data['Local PSC Detrended Mean']) #+ np.array(FB_data['Baseline'])
                            })

fig, ax = plt.subplots()
ax = sns.swarmplot(x='Order', y='PSC value', data=sample_data, s=10, palette='tab10',ax=ax)
for (x0, y0), (x1, y1) in zip(ax.collections[0].get_offsets(), ax.collections[1].get_offsets()):
    ax.plot([x0, x1], [y0, y1], color='black', ls=':', zorder=0)
plt.show()

fig, ax = plt.subplots()
ax = sns.pointplot(x='Order', y='PSC value', data=sample_data,ax=ax, errorbar="sd", linestyle='--')

#offline NF run matter images

data_dir = 'E:/Matter_project/NF_project/7TPCtests/NF_scripts_pilot1/data/sub01/ses2/run1'
outdata = pickle.load(open(f'{data_dir}/outdata.pkl','rb'))

# for the stock images there are only positive

# plot PSC of 1st and second occurence of the image
FB_data = outdata['Feedback Info']
first_second_label = ['First time','Second time']* 8

sample_data = pd.DataFrame({'Order': first_second_label,
                            'PSC value': np.array(FB_data['Local PSC Detrended Mean']) #+ np.array(FB_data['Baseline'])
                            })

fig, ax = plt.subplots()
ax = sns.swarmplot(x='Order', y='PSC value', data=sample_data, s=10, palette='tab10',ax=ax)
for (x0, y0), (x1, y1) in zip(ax.collections[0].get_offsets(), ax.collections[1].get_offsets()):
    ax.plot([x0, x1], [y0, y1], color='black', ls=':', zorder=0)
plt.show()

fig, ax = plt.subplots()
ax = sns.pointplot(x='Order', y='PSC value', data=sample_data,ax=ax, errorbar="sd", linestyle='--')

NF_conditions = []
order_file = 'E:/Matter_project/NF_project/7TPCtests/NF_scripts_pilot1/data/sub01/ses2/run1/runNF1_matter.txt'

emo = ['Amusement','Contentment','Friendship','Recognition']

with open(order_file, 'r') as f:
    for line in f.readlines():

        if emo[0] in line:
            NF_conditions.append(emo[0])
        elif emo[1] in line:
            NF_conditions.append(emo[1])
        elif emo[2] in line:
            NF_conditions.append(emo[2])
        elif emo[3] in line:
            NF_conditions.append(emo[3])

fig, ax = plt.subplots()
ax = sns.pointplot(x='Order', y='PSC value', hue = NF_conditions, data=sample_data,ax=ax, errorbar="sd", linestyle='--')

fig, ax = plt.subplots()
ax = sns.swarmplot(x='Order', y='PSC value', hue = NF_conditions, data=sample_data, s=10, palette='tab10',ax=ax)
for (x0, y0), (x1, y1) in zip(ax.collections[0].get_offsets(), ax.collections[1].get_offsets()):
    ax.plot([x0, x1], [y0, y1], color='black', ls=':', zorder=0)
plt.show()







