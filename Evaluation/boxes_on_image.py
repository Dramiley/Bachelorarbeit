import numpy as np
import argparse
import os
import PIL
from PIL import Image # Pillow
import glob
import time
import pandas as pd
import matplotlib.pyplot as plt

import PIL.Image as Image
import PIL.ImageColor as ImageColor
import PIL.ImageDraw as ImageDraw
import PIL.ImageFont as ImageFont


class boxDrawer:
    def __init__(self,box_color, text_color, resize):
        self.box_color = box_color
        self.text_color = text_color
        self.resize = resize
        
# modified function from object_detection.utils.visualization_utils
    def draw_bounding_box_with_text(self,image, xmin, xmax, ymin, ymax, thickness, display_str_list):
        box=[xmin, xmax, ymin, ymax]
        draw = ImageDraw.Draw(image)
        im_width, im_height = image.size
        (left, right, top, bottom) = (xmin, xmax, ymin, ymax)
        draw.line([(left, top), (left, bottom), (right, bottom),
        (right, top), (left, top)], width=thickness, fill=self.box_color)
        try:
            font = ImageFont.truetype('arial.ttf', 18)
        except IOError:
            font = ImageFont.load_default()

        text_bottom = top
        # Reverse list and print from bottom to top.
        for display_str in display_str_list[::-1]:
            #text_width, text_height = font.getsize(display_str)
            (temp1,temp2, text_width,text_height) = font.getbbox(display_str)
            margin = np.ceil(0.05 * text_height)
            #draw.rectangle(
            #    [(left, text_bottom - text_height - 2 * margin), (left + text_width,
            #                                                  text_bottom)],
            #    fill=color)
            draw.text(
                (left + margin, text_bottom - text_height - margin),
                display_str,
                fill=self.text_color,
                font=font)
            text_bottom -= text_height - 2 * margin
            
            avg_x = (xmin + xmax) / 2
            avg_y = (ymin + ymax) / 2
            size = 2
            draw.rectangle(((avg_x - size, avg_y - size), (avg_x + size, avg_y + size)), outline=self.box_color, fill=self.box_color)


    def run(self, csv_path):
        if imagepath != '0':
            try:
                image = Image.open(imagepath)
            except PIL.UnidentifiedImageError:
                print(f"Could not open image: {imagepath}")
                return
        else:
            image = Image.new('RGB', (512, 512), (0, 0, 0))
            
        try:
            df = pd.read_csv(csvpath)
            df.columns = ['detection_scores','class', 'x min', 'y min', 'x max', 'y max']

            classes = df['class']
            det_scores = df['detection_scores']
            x_min = df['x min']
            y_min = df['y min']
            x_max = df['x max']
            y_max = df['y max']
        
            for i in range(len(classes)):
                name = classes[i]
            
                self.draw_bounding_box_with_text(image, x_min[i], x_max[i], y_min[i], y_max[i], 4, (name,''))
            
        except pd.errors.EmptyDataError:
            pass
        
        if self.resize:
            image = image.resize((1640, 1232))
            
        image.save(f'{imagepath}_boxes.png')
        
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Draw boxes on image')
    parser.add_argument('-i','--image', type=str, default='0', help='Path to image file')
    parser.add_argument('-c','--csv', type=str, default='image.csv', help='Path to csv file')
    parser.add_argument('-bc','--box_color', type=str, default='red', help='Color of the box')
    parser.add_argument('-tc','--text_color', type=str, default='white', help='Color of the text')
    parser.add_argument('-r','--resize', action='store_true', help='Resize image to 1640x1232')
    
    args = parser.parse_args()
    
    imagepath = args.image
    csvpath = args.csv
    box_color = args.box_color
    text_color = args.text_color
    resize = args.resize
    
    Drawer = boxDrawer(box_color, text_color, resize)
    Drawer.run(csvpath)
    
