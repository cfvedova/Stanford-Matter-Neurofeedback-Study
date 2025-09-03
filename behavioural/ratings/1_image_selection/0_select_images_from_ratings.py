'''

Image Selection

This script selects images to be used in the experiment based on Matter ratings and Standard images ratings.

Inputs:
- ratings_*.csv file from the standard rating tool
- memories.csv file from the Matter Download App (only for the Matter and Matter NF groups)

For Standard images:
- it will select 8 positive images with the highest valence score and 8 neutral images with the lowest valence score;
- IDs of the selected images will be stored in the stock.txt and neutral.txt files.

For Matter images:
- it will select 2 memories for each emotion listed in the sel_matter_emotions list, based on the highest score for each
  emotion and the peak ratio (which defines how much a specific emotion rating is extreme with respect to the average of the others);
- IDs of the selected images will be stored in the matter.txt, IDs+emotion type will be stored in the matter_EMOinfo.txt.

'''


import numpy as np
import pandas as pd
import glob
import matplotlib.pyplot as plt
import random

NR_SEL_IMAGES = 8
emotions = ['EXCITEMENT','SEXUAL DESIRE','RECOGNITION', 'FAMILY LOVE', 'CONTENTMENT', 'FRIENDSHIP','AMUSEMENT' , 'PLEASURE','GRATITUDE']
# corresponding emotion names from the Matter App
emo_MatterAp = ['enthusiasm', 'sexualDesire', 'pride', 'nurturantLove','contentment', 'attachmentLove', 'amusement', 'pleasure', 'gratitude']

sel_matter_emotions = ['RECOGNITION', 'FAMILY LOVE', 'FRIENDSHIP','PLEASURE']
def read_ratings_stock(file_name):

	images = []

	ratings = pd.read_csv(file_name)

	# get neutral images, the last 12
	ratings_neutral = ratings[12:]
	# get positive images, first 12
	ratings_positive = ratings[:12]

	return ratings_neutral, ratings_positive


def select_images_stock(ratings_neutral, ratings_positive):

	ratings_sorted = ratings_neutral.sort_values(by = 'VALENCE')
	neutral_images = np.array(ratings_sorted['Image ID'][:NR_SEL_IMAGES]) # select the neutral images with lower valence

	# choose randomly among the neutral images with the higher score if more then needed
	max_neutral = np.max(ratings_sorted['VALENCE'][:NR_SEL_IMAGES])
	idx_sel_max_neutral = np.where(ratings_sorted['VALENCE'][:NR_SEL_IMAGES]==max_neutral)[0]
	idx_max_neutral = np.where(ratings_sorted['VALENCE']==max_neutral)[0]

	if len(idx_sel_max_neutral)!=len(idx_max_neutral):
		random.shuffle(idx_max_neutral)
		images = np.array(ratings_sorted['Image ID'])
		neutral_images[idx_sel_max_neutral] = images[idx_max_neutral[:len(idx_sel_max_neutral)]]

	ratings_sorted = ratings_positive.sort_values(by = 'VALENCE')[::-1]
	positive_images = np.array(ratings_sorted['Image ID'][:NR_SEL_IMAGES]) # select the positive images with higher valence

	# choose randomly among the positive images with the lowest score if more there needed
	min_positive = np.min(ratings_sorted['VALENCE'][:NR_SEL_IMAGES])
	idx_sel_min_positive = np.where(ratings_sorted['VALENCE'][:NR_SEL_IMAGES]==min_positive)[0]
	idx_min_positive = np.where(ratings_sorted['VALENCE']==min_positive)[0]

	if len(idx_sel_min_positive)!=len(idx_min_positive):
		random.shuffle(idx_min_positive)
		images = np.array(ratings_sorted['Image ID'])
		positive_images[idx_sel_min_positive] = images[idx_min_positive[:len(idx_sel_min_positive)]]

	return neutral_images, positive_images

def read_ratings_matter(file_name):

	images = []
	data = pd.read_csv(file_name)
	# take only the emotion ratings
	ratings = pd.concat([data.iloc[:,0],data.iloc[:,4:13]],axis=1)
	# (optional) reorder the columns based on the emo_MatterAp list order
	# ratings.reindex(columns=emo_MatterAp)
	return ratings

def assign_peak_label_matter(ratings):

	# get emo order the dataframe
	col_name = ratings.columns.values[1:]

	peak_label_dict = {key: [] for key in col_name}

	image_labels = []
	image_label_idx = []
	peak_ratios = []
	peak_value = []

	for _, image in ratings.iterrows():

		max_score = np.max(image.values[1:])
		peak_value.append(max_score)
		max_idx = np.where(image.values[1:] == max_score)[0]

		idx_other_emo = list(np.arange(9))
		idx_other_emo.remove([max_idx[0]])
		idx_other_emo = np.array(idx_other_emo)
		peak_ratios.append(max_score/np.mean(image.values[1:][idx_other_emo]))
		temp_labels = []
		peak_labels = col_name[max_idx]
		for i,label in enumerate(col_name):
			if i in max_idx:
				peak_label_dict[label] += [image['id']]
				temp_labels.append(label)


		image_labels.append(temp_labels)
	'''
	orig_image_labels = image_labels.copy()
	for i,labels in enumerate(image_labels):

		if len(labels)>1:
			emo_group_len = []
			for lb in labels:
				emo_group_len.append(len(peak_label_dict[lb]))
			idx_lb = np.argmin(emo_group_len)
			# assign to the image the label of the emo group with less images
			image_labels[i] = emotions[emo_MatterAp.index(labels[idx_lb])] # replace with the name that will be used in the study
		else:
			image_labels[i] = emotions[emo_MatterAp.index(labels[0])] # replace with the name that will be used in the study

	ratings['Label'] = image_labels
	'''
	study_labels = []
	for items in image_labels:
		temp = []
		for lb in items:
			temp.append(emotions[emo_MatterAp.index(lb)])
		study_labels.append(temp)


	outdict = pd.DataFrame({'Image ID': ratings['id'].values,
			   'Peak Labels': [", ".join(items) for items in study_labels],
			   'Peak Value': peak_value,
			   'Peak Ratio': peak_ratios})

	return outdict

def select_images_matter(outdict):

	seldict=[]

	for emo in sel_matter_emotions:
		cur_emo_dict_idx=outdict['Peak Labels'].isin([emo])
		cur_emo_dict = outdict[cur_emo_dict_idx]
		cur_emo_dict=cur_emo_dict.sort_values(by=['Peak Value', 'Peak Ratio'], ascending=[False, False])
		seldict.append(cur_emo_dict[:2])

	seldict = pd.concat(seldict, ignore_index=True)

	return seldict




if __name__ == '__main__':


	wdir = 'C:/Users/assun/Documents/GitHub/MatterNeurofeedbackStudy/example_data/behavioural/initial_ratings'

	sub = input('Insert subject ID (sub-xx): ')

	rating_file_stock = glob.glob(f'{wdir}/{sub}/ratings*csv')

	try:

		ratings_neutral, ratings_positive = read_ratings_stock(rating_file_stock[0])

		neutral_images, positive_images = select_images_stock(ratings_neutral, ratings_positive)

		# write positive images to a text file
		filename = f'{wdir}/{sub}/stock.txt'
		with open(filename,'w') as f:

			for img in positive_images:
				f.write(f'{img}\n')

		filename = f'{wdir}/{sub}/neutral.txt'
		with open(filename,'w') as f:

			for img in neutral_images:
				f.write(f'{img}\n')


		# write summary graphs for positive and neutral images
		#bar plot of the valence score
		ratings_sorted = ratings_positive.sort_values(by = 'VALENCE')
		fig, ax = plt.subplots(2,1, figsize=(10,5))
		ax[0].barh(ratings_sorted['Image ID'],ratings_sorted['VALENCE'], alpha=0.8)
		ax[0].set_title('Valence Score')
		for emo in emotions:
			ax[1].plot(np.arange(1,len(ratings_sorted)+1), ratings_sorted[emo])
		ax[1].set_xticks(np.arange(1,len(ratings_sorted)+1))
		ax[1].set_ylabel('Emotion Ratings')
		ax[1].legend(emotions, loc=(-0.3,0))
		plt.tight_layout()
		fig.savefig(f'{wdir}/{sub}/stock_images_summary.jpg',bbox_inches='tight')
		plt.show()

	except Exception as e:
		print(e)
		print('Stock rating file not created')

	rating_file_matter = glob.glob(f'{wdir}/{sub}/memories.csv')

	try:

		orig_ratings = read_ratings_matter(rating_file_matter[0])

		ratings = assign_peak_label_matter(orig_ratings)

		ratings.to_excel(f'{wdir}/{sub}/matter_ratings_info.xlsx')

		matter_images_dict = select_images_matter(ratings)

		matter_images_dict.to_excel(f'{wdir}/{sub}/selected_matter_ratings_info.xlsx')
		# write positive images to a text file
		filename = f'{wdir}/{sub}/matter.txt'
		with open(filename,'w') as f:
			for img in matter_images_dict['Image ID']:
				f.write(f'{img}\n')

		filename = f'{wdir}/{sub}/matter_EMOinfo.txt'
		with open(filename, 'w') as f:
			for i,img in enumerate(matter_images_dict['Image ID']):
				f.write(f'{matter_images_dict["Peak Labels"][i]}_{img}\n')


	except Exception as e:

		if not rating_file_matter:
			print('No matter ratings found!')

		else:
			print(e)






