'''

Post-scan Matter images ratings

'''

import sys

from psychopy import core, visual,event, gui
import os
import random
import glob
import pandas as pd



##########################################################################
#                            GENERAL SETTINGS                            #
##########################################################################

def showTextBox(text1="", text2=""):
    textBox = gui.Dlg(title='Insert subject info')
    textBox.addField('subject name (sub-XX): ', text1)
    textBox.addField('session number (1 to 5): ', text2)
    textBox.show()
    if textBox.OK:
        text1 = textBox.data[0]
        text2 = textBox.data[1]
        return text1, text2
    else:
        return text1, text2

wdir = os.getcwd()
#sub = input('Insert subject name (sub-XX): ')
#ses = input('Insert session number (1 to 5): ')
sub, ses = showTextBox(text1="", text2="")

image_dir = f'/Users/brainvoyager/Desktop/Matter_Neurofeedback/Matter_images/{sub}/matter_images'

sub_img_file = f'/Users/brainvoyager/Desktop/Matter_Neurofeedback/behavioural/initial_ratings/{sub}/matter.txt'

images_list = []
with open(sub_img_file, 'r') as f: 
    for line in f.readlines():
        images_list.append(f'{image_dir}/{line[:-1]}')


#images_list = glob.glob(wdir + '/images/*.jpg')
random.seed(os.urandom(2))
random.shuffle(images_list)
num_stim = len(images_list) # number of images

out_data =[]

# Define the directory paths
outdata_dir = '/Users/brainvoyager/Desktop/Matter_Neurofeedback/behavioural/post_scan_ratings'
sub_dir = os.path.join(outdata_dir, sub, f'ses-0{ses}')  # 'outdata/sub-XX/ses-0X' folder path
os.makedirs(sub_dir, exist_ok=True)

# Check and create the folders if they don't exist
if os.path.exists(f'{sub_dir}/{sub}_ses-0{ses}_ratings_matter.txt'):
    print(f'{sub_dir}/{sub}_ses-0{ses}_ratings_matter.txt already exist! Check that the current session number is correct!')
    sys.exit()

# check that the images exists
for file in images_list:
    if not os.path.exists(file + '.jpg'):
        print(f'{file} does not exist!')
        sys.exit()
    
##########################################################################
#                           PSYCHOPY SETTINGS                            #
##########################################################################


win = visual.Window(fullscr = True, color='dimgray', screen = 0,
                    size=[1024, 800], units='pix', colorSpace = 'rgb255')

x, y = win.size  # for converting norm units to pix


instr = visual.TextStim(win, text= """For each image that is shown to you, please indicate right under the image how much you could engage (0 = no engagement … 10 = very high engagement)
On the right side, indicate the valence of the image for you (1 = neutral … 10 = very positive)
And rate the emotion for the nine emotions shown (0 = no emotion …  8 = very intense emotion) 
Confirm your choices by clicking the button under the scale""", color = 'white', height=.08, units='norm')


# Adjust positions
image_left = -300 #-0.2 * x  # Left side of the screen
image_middle_y = 100  # Center vertically

#creation of the cue for the images
cur_image = visual.ImageStim(win=win, size = 450, image = None, units='pix', pos=[image_left, image_middle_y])  #pos=[0, y//7]

# Engagement scale below the image
engagement_scale_pos = (image_left - 300, image_middle_y - 550)

# Column positions
col1_x = +200  # First column x position
col2_x = +900  # Second column x position
start_y = 700  # Starting y position
y_spacing = 380  # Space between scales

# Define positions for scales
scale_positions = {
    'valence': (col1_x, start_y),
    'emotion1': (col1_x, start_y - y_spacing),
    'emotion2': (col1_x, start_y - 2 * y_spacing),
    'emotion3': (col1_x, start_y - 3 * y_spacing),
    'emotion4': (col1_x, start_y - 4 * y_spacing),
    'emotion5': (col2_x, start_y),
    'emotion6': (col2_x, start_y - y_spacing),
    'emotion7': (col2_x, start_y - 2 * y_spacing),
    'emotion8': (col2_x, start_y - 3 * y_spacing),
    'emotion9': (col2_x, start_y - 4 * y_spacing),
}


# Define scales with updated positions
myRatingScaleEngagement = visual.RatingScale(win, mouseOnly=True, pos=engagement_scale_pos,
    marker='circle', size=0.70, name='engagement',acceptText='Submit', low=0, high=10, choices=map(str, range(1, 11)))

myRatingScaleValence = visual.RatingScale(win, mouseOnly=True, pos=scale_positions['valence'],
    marker='circle', size=0.55, name='valence', low=1, high=10, choices=map(str, range(1, 11)))

myRatingScaleExcitement = visual.RatingScale(win, mouseOnly=True, pos=scale_positions['emotion1'],
    marker='circle', size=0.55, name='excitement',  low=0, high=8, choices=map(str, range(0, 9)))

myRatingScaleSexualDesire = visual.RatingScale(win, mouseOnly=True, pos=scale_positions['emotion2'],
    marker='circle', size=0.55, name='sexualDesire',  low=0, high=8, choices=map(str, range(0, 9)))

myRatingScaleRecognition = visual.RatingScale(win, mouseOnly=True, pos=scale_positions['emotion3'],
    marker='circle', size=0.55, name='recognition',  low=0, high=8, choices=map(str, range(1, 9)))

myRatingScaleFamilyLove = visual.RatingScale(win, mouseOnly=True, pos=scale_positions['emotion4'],
    marker='circle', size=0.55, name='familyLove',   low=0, high=8, choices=map(str, range(1, 9)))

myRatingScaleContentment = visual.RatingScale(win, mouseOnly=True, pos=scale_positions['emotion5'],
    marker='circle', size=0.55, name='contentment',  low=0, high=8, choices=map(str, range(1, 9)))

myRatingScaleFriendship = visual.RatingScale(win, mouseOnly=True, pos=scale_positions['emotion6'],
    marker='circle', size=0.55, name='friendship',  low=0, high=8, choices=map(str, range(1, 9)))

myRatingScaleAmusement = visual.RatingScale(win, mouseOnly=True, pos=scale_positions['emotion7'],
    marker='circle', size=0.55, name='amusement', low=0, high=8, choices=map(str, range(1, 9)))

myRatingScalePleasure = visual.RatingScale(win, mouseOnly=True, pos=scale_positions['emotion8'],
    marker='circle', size=0.55, name='pleasure', low=0, high=8, choices=map(str, range(1, 9)))

myRatingScaleGratitude = visual.RatingScale(win, mouseOnly=True, pos=scale_positions['emotion9'],
    marker='circle', size=0.55, name='gratitude', low=0, high=8, choices=map(str, range(1, 9)))



text = visual.TextStim(win, text = '', color = 'white',units = 'norm', pos = (0,0.9))



############################################################################
#                               MAIN LOOP                                  #
############################################################################

# display instruction
event.clearEvents()
instr.draw()
win.flip()

if 'escape' in event.waitKeys():
    win.close()
    core.quit()

event.clearEvents()

myRatingScaleEngagement.setDescription('0 = no engagement \n 10 = very high engagement \n')
myRatingScaleValence.setDescription('Valence \n 1 = neutral \n 10 = very positive \n') 
myRatingScaleExcitement.setDescription('Excitement \n 0 = no emotion \n 8 = very intense emotion \n') 
myRatingScaleSexualDesire.setDescription('Sexual desire')
myRatingScaleRecognition.setDescription('Recognition')
myRatingScaleFamilyLove.setDescription('Family love')
myRatingScaleContentment.setDescription('Contentment \n 0 = no emotion \n 8 = very intense emotion \n')
myRatingScaleFriendship.setDescription('Friendship')
myRatingScaleAmusement.setDescription('Amusement')
myRatingScalePleasure.setDescription('Pleasure')
myRatingScaleGratitude.setDescription('Gratitude')



for i,image in enumerate(images_list):
    text.text = str(i+1)+'/'+str(num_stim)
    cur_image.setImage(image+'.jpg')
    # reset between repeated uses of the same scale
    myRatingScaleEngagement.reset()
    myRatingScaleValence.reset() 
    myRatingScaleExcitement.reset()
    myRatingScaleSexualDesire.reset()
    myRatingScaleRecognition.reset()
    myRatingScaleFamilyLove.reset()
    myRatingScaleContentment.reset()
    myRatingScaleFriendship.reset()
    myRatingScaleAmusement.reset()
    myRatingScalePleasure.reset()
    myRatingScaleGratitude.reset()
    
    while myRatingScaleValence.noResponse or myRatingScaleEngagement.noResponse or myRatingScaleExcitement.noResponse or \
    myRatingScaleSexualDesire.noResponse or myRatingScaleRecognition.noResponse or myRatingScaleFamilyLove.noResponse or \
    myRatingScaleContentment.noResponse or myRatingScaleFriendship.noResponse or myRatingScaleAmusement.noResponse or \
    myRatingScalePleasure.noResponse or myRatingScaleGratitude.noResponse :
        cur_image.draw()
        text.draw()
        myRatingScaleEngagement.draw()
        myRatingScaleValence.draw()
        myRatingScaleExcitement.draw()
        myRatingScaleSexualDesire.draw()
        myRatingScaleRecognition.draw()
        myRatingScaleFamilyLove.draw()
        myRatingScaleContentment.draw()
        myRatingScaleFriendship.draw()
        myRatingScaleAmusement.draw()
        myRatingScalePleasure.draw()
        myRatingScaleGratitude.draw()

        win.flip()
            
    if event.getKeys(['escape']):
        win.close()
        #core.quit()
        break
    
    out_data.append((os.path.basename(image), myRatingScaleValence.getRating(), myRatingScaleValence.getRT(),
                    myRatingScaleEngagement.getRating(), myRatingScaleEngagement.getRT(),
                    myRatingScaleExcitement.getRating(), myRatingScaleExcitement.getRT(),
                    myRatingScaleSexualDesire.getRating(), myRatingScaleSexualDesire.getRT(),
                    myRatingScaleRecognition.getRating(), myRatingScaleRecognition.getRT(),
                    myRatingScaleFamilyLove.getRating(), myRatingScaleFamilyLove.getRT(),
                    myRatingScaleContentment.getRating(), myRatingScaleContentment.getRT(),
                    myRatingScaleFriendship.getRating(), myRatingScaleFriendship.getRT(),
                    myRatingScaleAmusement.getRating(), myRatingScaleAmusement.getRT(),
                    myRatingScalePleasure.getRating(), myRatingScalePleasure.getRT(),
                    myRatingScaleGratitude.getRating(), myRatingScaleGratitude.getRT(),))
    
    
data = pd.pandas.DataFrame(out_data, columns = ('image','valence', 'valence RT','engagement', 'engagement RT','excitement', 'excitement RT','sexual desire', 'sexual desire RT','recognition', 'recognition RT' 
                                               ,'family love', 'family love RT','contentment', 'contentment RT','friendship', 'friendship RT' 
                                               ,'amusement', 'amusement RT','pleasure', 'pleasure RT','gratitude', 'gratitude RT'))


# Save the data
file_path = os.path.join(sub_dir, f'{sub}_ses-0{ses}_ratings_matter.txt')
data.to_csv(file_path, index=None, sep=' ', mode='a')

#data.to_csv(os.path.join(wdir, 'outdata/'+sub +'/' +sub+'_ratings_matter.txt'), index=None, sep=' ', mode='a')

print('Data saved')

win.close()
core.quit()

    
    
