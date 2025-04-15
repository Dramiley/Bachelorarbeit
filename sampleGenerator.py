import os
import argparse
import pandas as pd
import numpy as np
from owlready2 import *
import random
from generate_box_image import boxDrawer
import argparse
import math


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate Ontology from csv file')
    parser.add_argument('-m','--multicam', default=False, action='store_true', help='add -c for multicam mode')
    args = parser.parse_args()
    multicam = args.multicam
        
    # Create drawer object for drawing boxes and data object for saving data    
    drawer = boxDrawer(device_id=0, server_url='http://localhost:5000', box_color=(255, 0, 0), text_color=(255, 255, 255), resize=1)
    data = pd.DataFrame(columns=['detection_scores','class','x min','y min','x max','y max'])
    
    # set random values for the number of cameras
    if multicam:
        cams = random.randint(2, 4)
    else: 
        cams = 1
    
    # set random values for the number of objects and their properties
    nr = random.randint(1, 10)
    # define all possible classes
    all_classes = ['Lampe', 'Hebel', 'Motor', 'Schleifscheibe', 'Sicherung', 'Schalter', 'Ablageflaeche', 'Abdeckung', 'Anschluss', 'Gewinde']
    # create a list for each property
    sample_detection_scores = []
    sample_classes = []
    sample_x_min = []
    sample_y_min = []
    sample_x_max = []
    sample_y_max = []
    # create random values for each object property for the number of objects
    for i in range(nr):
        sample_detection_scores.append(random.uniform(0.5, 1))
        sample_classes.append(random.choice(all_classes))
        length = random.randint(10, 100)
        height = random.randint(10, 100)
        sample_x_min.append(random.randint(0,512-length))
        sample_x_max.append(sample_x_min[i] + length)
        sample_y_min.append(random.randint(0,512-height))
        sample_y_max.append(sample_y_min[i] + height)
    
    # #add lists to data frame
    data['detection_scores'] = sample_detection_scores
    data['class'] = sample_classes
    data['x min'] = sample_x_min
    data['y min'] = sample_y_min
    data['x max'] = sample_x_max
    data['y max'] = sample_y_max
    
    # sort data frame by detection scores and save to csv file
    data = data.sort_values(by=['detection_scores'], ascending=False)
    data.to_csv('output/sample.csv', index=True)
    
    # delete data object to avoid memory issues
    del data

    # draw boxes on image and save to file
    drawer.run('output/sample.csv')
    
    # if multicam mode is enabled, create multiple csv files with altered values for each camera
    if multicam:
        # create a new data frame, x_rotation, y_rotation and error for each camera
        for i in range(cams):
            data = pd.DataFrame(columns=['detection_scores','class','x min','y min','x max','y max'])
            x_rotation = random.randint(-60, 60)
            y_rotation = random.randint(-20, 20)
            error = random.uniform(0, 0.2)
            print(f'Camera {i} - x rotation: {x_rotation}, y rotation: {y_rotation}, error: {error}')
            # create new lists for each property (reset for each camera)
            # copy the values from the original lists to avoid overwriting them
            detection_scores = sample_detection_scores.copy()
            classes = sample_classes.copy()
            x_min = sample_x_min.copy()
            y_min = sample_y_min.copy()
            x_max = sample_x_max.copy()
            y_max = sample_y_max.copy()
            # for each property, alter the values based on the rotation and error 
            # rotation changes the x and y values of the boxes
            # error changes the detection score of the boxes
            # remove boxes with a detection score less than 0.5+error -> some boxes are not detected
            temp = len(detection_scores)
            j = 0
            while j < temp:
                if detection_scores[j] <= 0.5+error:
                    detection_scores.remove(detection_scores[j])
                    classes.remove(classes[j])
                    x_min.remove(x_min[j])
                    y_min.remove(y_min[j])
                    x_max.remove(x_max[j])
                    y_max.remove(y_max[j])
                    temp -= 1
                else:
                    x_min[j] = int(math.cos(math.radians(x_rotation)) * x_min[j])
                    x_max[j] = int(math.cos(math.radians(x_rotation)) * x_max[j])
                    y_min[j] = int(math.cos(math.radians(y_rotation)) * y_min[j])
                    y_max[j] = int(math.cos(math.radians(y_rotation)) * y_max[j])
                    new_score = detection_scores[j] + random.uniform(-error, error)
                    detection_scores[j] = new_score if new_score <= 1 else 1
                    j += 1
             
            # add lists to data frame       
            data['detection_scores'] = detection_scores
            data['class'] = classes
            data['x min'] = x_min
            data['y min'] = y_min
            data['x max'] = x_max
            data['y max'] = y_max
            
            # sort data frame by detection scores and save to csv file
            # data = data.sort_values(by=['detection_scores'], ascending=False) | changed to avoid flipping labels
            data.to_csv(f'output/cam{i}.csv', index=True)
            
            # draw boxes on image and save to file
            drawer.run(f'output/cam{i}.csv')
            
            # delete data object to avoid memory issues
            del data
            # draw boxes on image and save to file
            drawer.run(f'output/cam{i}.csv')
            
        # delete older cam files to avoid confusion
        for i in range(cams, 4):
            if os.path.isfile(f'output/cam{i}.csv'):
                os.remove(f'output/cam{i}.csv')
            if os.path.isfile(f'output/cam{i}.csv_out.png'):
                os.remove(f'output/cam{i}.csv_out.png')