import numpy as np
import pandas as pd
import glob
import matplotlib.pyplot as plt
import random

NR_SEL_IMAGES = 8
emotions = ['EXCITEMENT','SEXUAL DESIRE','RECOGNITION', 'FAMILY LOVE', 'CONTENTMENT', 'FRIENDSHIP','AMUSEMENT' , 'PLEASURE','GRATITUDE']
# corresponding emotion names from the Matter App
emo_MatterAp = ['enthusiasm', 'sexualDesire', 'pride', 'nurturantLove','contentment', 'attachmentLove', 'amusement', 'pleasure', 'gratitude']

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

	for _, image in ratings.iterrows():

		max_score = np.max(image.values[1:])
		max_idx = np.where(image.values[1:] == max_score)[0]

		temp_labels = []
		peak_labels = col_name[max_idx]
		for i,label in enumerate(col_name):
			if i in max_idx:
				peak_label_dict[label] += [image['id']]
				temp_labels.append(label)


		image_labels.append(temp_labels)

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

	# compute peak ratios
	#ratings['Peak Ratio'] = peak_ratios

	return ratings


def compute_peak_ratio_matter(ratings):


	#ratings['Peak Ratio'][i] = ratings.values[i][idx_emo]/np.mean(ratings.values[i][idx_other_emo])
	pass




if __name__ == '__main__':

	

	wdir = 'C:/Users/assun/Documents/GitHub/MatterNeurofeedbackStudy/example_data/behavioural/initial_ratings'

	sub = input('Insert subject ID (subxx): ')

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

		# write positive images to a text file
		filename = f'{wdir}/{sub}/matter.txt'
		with open(filename,'w') as f:

			for img in positive_images:
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
		plt.show()

	except Exception as e:

		if not rating_file_matter:
			print('No matter ratings found!')

		else:
			print(e)






