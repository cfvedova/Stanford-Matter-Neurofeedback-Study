'''

Prepare scramble Stock images

This script creates scrambled version of the stock pictures to be used as control condition during the NF runs of the
Standard NF group. It needs to run only one time at the beginning of the study!

'''


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

wdir = 'C:/Users/assun/Documents/GitHub/MatterNeurofeedbackStudy/stimPCData/images/stock_images'
outdir1 = f'{wdir}_scrambled'
outdir2 = f'{wdir}_scrambled_db'

os.makedirs(outdir1, exist_ok=True)
os.makedirs(outdir2, exist_ok=True)

img_list = glob.glob(f'{wdir}/*/*.jpg')

for img in img_list:
    img = img.replace('\\', '/')
    # Example usage
    category = img.split('/')[-2]
    img_name = img.split('/')[-1]
    os.makedirs(f'{outdir1}/{category}', exist_ok=True)
    os.makedirs(f'{outdir2}/{category}', exist_ok=True)

    scramble_image_variable_blocks(img, 50, f"{outdir1}/{category}/{img_name}")
    scramble_image_variable_blocks_dashed_border(img, 50, f"{outdir2}/{category}/{img_name}")


