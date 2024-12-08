import os, glob
import numpy as np
import pandas as pd
import shutil
import random
from utils.randomise import generate_random_sequence_2cond_maxCons, shuffle_without_consecutive_duplicates

SESSION_NR = 3 # add loop for session repetition later
NR_LOC_RUNS = 1
NR_NF_RUNS = 3
NR_BLOCKS = 16

sub_name = input('Insert the subject name: ')
group = input('Insert group (matter or stock): ')

wdir = f'C:/Users/assun/Documents/GitHub/MatterNeurofeedbackStudy/example_data/behavioural/initial_ratings/{sub_name}'
outdir = f'C:/Users/assun/Documents/GitHub/MatterNeurofeedbackStudy/example_data/stim_prep/{sub_name}'

# make directory for the current subject in data
os.makedirs(outdir, exist_ok=True)

# get images list and prepare order files for localiser and NF runs

if group == 'stock':

    # create the session folder
    ses_folder = f'{outdir}/ses{SESSION_NR}'
    os.makedirs(ses_folder, exist_ok=True)

    # get the ratings of for the stock images
    stock_images_file = glob.glob(f'{wdir}/stock.txt')[0]
    images_list = []

    with open(stock_images_file, 'r') as file:
        for line in file:
            images_list.append(line)

    # prepare images order for the NF runs
    for run in range(NR_NF_RUNS):

        # create the run folder
        run_folder = f'{outdir}/ses{SESSION_NR}/runNF{run + 1}'
        os.makedirs(run_folder, exist_ok=True)

        # for stock pictures we can simply randomise and duplicate the frequency of each image
        images_NF_temp = images_list.copy()
        random.shuffle(images_NF_temp)

        # choose which image should be scrambled (4 per run)
        scramble_idx = np.arange(len(images_NF_temp))
        random.shuffle(scramble_idx)
        scramble_idx = scramble_idx[:4]

        images_NF = []
        for item_idx, item in enumerate(images_NF_temp):
            if item_idx not in scramble_idx:
                images_NF.extend([item] * 2)
            else:
                scramble_img_pos = np.array([0,1]) # decide if the scramble image is the first or the second presented
                random.shuffle(scramble_img_pos)
                scramble_img_pos = scramble_img_pos[0]

                if scramble_img_pos == 0:
                    images_NF.extend(['_scrambled_db/'+item, item])
                else:
                    images_NF.extend([item, '_scrambled_db/' + item])

        # save the run order file
        # the NF script looks for runNFX_group.txt
        order_filename = f'{run_folder}/runNF{run+1}_{group}.txt'

        with open(order_filename,'w') as f:
            for image in images_NF:
                f.write(f'{image}')

    # copy also the folder of the neutral images and add the names to the image list to create the order file for the localiser
    # get the ratings of for the stock images
    neutral_images = []

    with open(f'{wdir}/neutral.txt', 'r') as file:
        for line in file:
            neutral_images.append(line)

    for run in range(NR_LOC_RUNS):
        # create localiser images folder balancing the frequency that one condition follows the other
        # get balanced sequence
        seq = generate_random_sequence_2cond_maxCons('positive', 'neutral', NR_BLOCKS, balance_factor=0.5, max_consecutive = 2)
        print('Localiser condition sequence:')
        print(seq)

        idx_pos = 0
        idx_neu = 0

        images_localiser = []

        # shuffle neutral and positive images
        random.shuffle(images_list)
        random.shuffle(neutral_images)

        for cond in seq:
            if cond == 'positive' and idx_pos < NR_BLOCKS/2:
                images_localiser.append(images_list[idx_pos])
                idx_pos += 1

            elif cond == 'neutral' and idx_neu < NR_BLOCKS/2:
                images_localiser.append(f'{neutral_images[idx_neu]}')
                idx_neu += 1

        # save the run order file for the Localiser
        # the Localiser script looks for Localiser_group.txt
        order_filename = f'{ses_folder}/Localiser{run+1}_{group}.txt'

        with open(order_filename, 'w') as f:
            for image in images_localiser:
                f.write(f'{image}')


elif group == 'matter':

    pass
    '''


    for ses in range(NR_SESSIONS):

        # create the session folder
        ses_folder = f'{outdir}/{sub_name}/ses{ses+1}'
        os.makedirs(ses_folder, exist_ok=True)

        # images already contains only the image names
        images_list = images

        # copy the selected images to the current subject folder
        if ses == 0:
            shutil.rmtree(f'{outdir}/{sub_name}/matter_images/', ignore_errors=True)

            shutil.copytree(f'{wdir}/{sub_name}/{group}_ratings/{group}_images',
                        f'{outdir}/{sub_name}/matter_images/')

        # prepare images order for the NF runs
        for run in range(NR_NF_RUNS):
            # create the run folder
            run_folder = f'{outdir}/{sub_name}/ses{ses + 1}/run{run + 1}'
            os.makedirs(run_folder, exist_ok=True)

            # for matter pictures we need to randomise the emotions so tha they are not repeated twice consecutively
            # (otherwise we would have the same emotion for 4 blocks)
            images_NF_temp = images_list.copy()
            images_NF_temp = shuffle_without_consecutive_duplicates(images_NF_temp)
            images_NF = []
            for item in images_NF_temp:
                images_NF.extend([item] * 2)

            print(f'NF run{run+1} images sequence: ')
            print(images_NF)
            # save the run order file
            # the NF script looks for runNFX_group.txt
            order_filename = f'{run_folder}/runNF{run + 1}_{group}.txt'

            with open(order_filename, 'w') as f:
                for image in images_NF:
                    f.write(f'{image}\n')

        # copy also the folder of the neutral images and add the names to the image list to create the order file for the localiser
        neutral_images_dir = f'{os.path.dirname(os.getcwd())}/images/neutral'
        shutil.rmtree(f'{outdir}/{sub_name}/matter_images/neutral', ignore_errors=True)
        shutil.copytree(neutral_images_dir, f'{outdir}/{sub_name}/matter_images/neutral')

        neutral_images = [os.path.basename(image) for image in glob.glob(f'{neutral_images_dir}/*.jpg')]

        # create localiser images folder balancing the frequency that one condition follows the other
        # get balanced sequence
        seq = generate_random_sequence_2cond_maxCons('positive', 'neutral', NR_BLOCKS, balance_factor=0.5,
                                                     max_consecutive=2)
        print('Localiser condition sequence:')
        print(seq)

        idx_pos = 0
        idx_neu = 0

        images_localiser = []

        # shuffle neutral and positive images
        random.shuffle(images_list)
        random.shuffle(neutral_images)

        for cond in seq:
            if cond == 'positive' and idx_pos < NR_BLOCKS / 2:
                images_localiser.append(images_list[idx_pos])
                idx_pos += 1

            elif cond == 'neutral' and idx_neu < NR_BLOCKS / 2:
                images_localiser.append(f'/neutral/{neutral_images[idx_neu]}')
                idx_neu += 1

        # save the run order file for the Localiser
        # the Localiser script looks for Localiser_group.txt
        order_filename = f'{ses_folder}/Localiser_{group}.txt'

        with open(order_filename, 'w') as f:
            for image in images_localiser:
                f.write(f'{image}\n')
                
        '''




































# create file with the images order for the localiser
