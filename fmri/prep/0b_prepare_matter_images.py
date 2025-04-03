import shutil

import numpy as np
from PIL import Image, ImageDraw
import random
import os
import glob


def scramble_image_variable_blocks(image_path, block_size, output_path):
    # Load image
    img = Image.open(image_path)
    img = img.convert("RGB")
    img_array = np.array(img)

    # Get image dimensions
    height, width, channels = img_array.shape

    # Create a list of blocks with variable sizes
    blocks = []
    block_positions = []
    for y in range(0, height, block_size):
        for x in range(0, width, block_size):
            # Determine the actual block size (adjust for edges)
            y_end = min(y + block_size, height)
            x_end = min(x + block_size, width)
            block = img_array[y:y_end, x:x_end]
            blocks.append(block)
            block_positions.append((y, x, y_end, x_end))  # Keep track of positions

    # Shuffle the blocks
    random.shuffle(blocks)

    # Reconstruct the scrambled image
    scrambled_array = np.zeros_like(img_array)
    for (y, x, y_end, x_end), block in zip(block_positions, blocks):
        scrambled_array[y:y_end, x:x_end] = block

    # Save the scrambled image
    scrambled_img = Image.fromarray(scrambled_array)
    scrambled_img.save(output_path)


def scramble_image_variable_blocks_dashed_border(image_path, block_size, output_path):
    # Load image
    img = Image.open(image_path)
    img = img.convert("RGB")
    img_array = np.array(img)

    # Get image dimensions
    height, width, channels = img_array.shape

    # Create a list of blocks with variable sizes
    blocks = []
    block_positions = []
    for y in range(0, height, block_size):
        for x in range(0, width, block_size):
            # Determine the actual block size (adjust for edges)
            y_end = min(y + block_size, height)
            x_end = min(x + block_size, width)
            block = img_array[y:y_end, x:x_end]
            blocks.append(block)
            block_positions.append((y, x, y_end, x_end))  # Keep track of positions

    # Shuffle the blocks
    random.shuffle(blocks)

    # Reconstruct the scrambled image
    scrambled_array = np.zeros_like(img_array)
    for (y, x, y_end, x_end), block in zip(block_positions, blocks):
        scrambled_array[y:y_end, x:x_end] = block

    # Convert scrambled array back to a PIL image
    scrambled_img = Image.fromarray(scrambled_array)

    # Define the dashed border thickness
    border_thickness = 10  # Thickness of the border area
    dash_length = 20  # Length of each dash
    gap_length = 10  # Gap between dashes
    line_thickness = border_thickness  # Thickness of the dashed lines
    color = (255, 0, 0)  # Red color

    # Create a new canvas larger than the image to include the border
    new_width = width + 2 * border_thickness
    new_height = height + 2 * border_thickness
    canvas = Image.new("RGB", (new_width, new_height), (60, 60, 60))  # same background of the stimulus pc

    # Paste the scrambled image onto the canvas at the center
    canvas.paste(scrambled_img, (border_thickness, border_thickness))

    # Draw the dashed red border around the image (outside the image area)
    draw = ImageDraw.Draw(canvas)

    # Top border
    for x in range(border_thickness, new_width - border_thickness, dash_length + gap_length):
        draw.line([(x, border_thickness - line_thickness // 2),
                   (x + dash_length, border_thickness - line_thickness // 2)], fill=color, width=line_thickness)
    # Bottom border
    for x in range(border_thickness, new_width - border_thickness, dash_length + gap_length):
        draw.line([(x, new_height - border_thickness + line_thickness // 2),
                   (x + dash_length, new_height - border_thickness + line_thickness // 2)], fill=color,
                  width=line_thickness)
    # Left border
    for y in range(border_thickness, new_height - border_thickness, dash_length + gap_length):
        draw.line([(border_thickness - line_thickness // 2, y),
                   (border_thickness - line_thickness // 2, y + dash_length)], fill=color, width=line_thickness)
    # Right border
    for y in range(border_thickness, new_height - border_thickness, dash_length + gap_length):
        draw.line([(new_width - border_thickness + line_thickness // 2, y),
                   (new_width - border_thickness + line_thickness // 2, y + dash_length)], fill=color,
                  width=line_thickness)

    # Save the final image with the border
    canvas.save(output_path)

# create scramble images from the stim pc script folder
sub_name = input('Insert the subject name: ')
wdir = f'/Users/brainvoyager/Desktop/Matter_Neurofeedback/Matter_images/{sub_name}/photos'

outdir1 = f'/Users/brainvoyager/Desktop/Matter_Neurofeedback/Matter_images/{sub_name}/matter_images'
os.makedirs(outdir1, exist_ok=True)

# copy the neutral folder
shutil.copytree('/Users/brainvoyager/Desktop/Matter_Neurofeedback/Matter_images/neutral',outdir1, dirs_exist_ok=True)

sub_img_file = f'/Users/brainvoyager/Desktop/Matter_Neurofeedback/behavioural/initial_ratings/{sub_name}/matter.txt'

images_list = []
with open(sub_img_file, 'r') as f:
    for line in f.readlines():
        image = f'{wdir}/{line[:-1]}.jpg'
        images_list.append(image)

        if not os.path.exists(image):
            print(f'Image {line[:-1]}.jpg not found')
        else:
            shutil.copyfile(image, f'{outdir1}/{line[:-1]}.jpg')

outdir2 = f'{outdir1}_scrambled_db'
os.makedirs(outdir2, exist_ok=True)

for img in images_list:
    img = img.replace('\\', '/')
    # Example usage
    img_name = img.split('/')[-1]

    scramble_image_variable_blocks_dashed_border(img, 50, f"{outdir2}/{img_name}")


