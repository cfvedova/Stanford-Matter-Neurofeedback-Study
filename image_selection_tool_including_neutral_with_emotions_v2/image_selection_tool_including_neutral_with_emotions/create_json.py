# create json file with a list of the images

import glob, os

wdir = os.getcwd()

images_list = glob.glob(f'{wdir}/images/*/*jpg')

file = f'{wdir}/images.json'

with open(file, 'w') as f:

	for image in images_list:
		im = image.split("/")[-1][7:].replace("\\","/")
		print(im)
		f.write(f'"{im}",\n')