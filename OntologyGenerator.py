import os
import argparse
import pandas as pd
import numpy as np
from owlready2 import *
from math import sqrt



def check_middle(x_min, y_min, x_max, y_max):
    x_mid = 0
    y_mid = 0
    x_cen = list()
    y_cen = list()
    # for every individual, calculate the middle of the coordinates
    for i in range(len(x_min)):
        x_mid += (x_max[i] + x_min[i]) /2
        y_mid += (y_max[i] + y_min[i]) /2
        x_cen.append((x_max[i] + x_min[i]) /2)
        y_cen.append((y_max[i] + y_min[i]) /2)
    
    # calculate the middle of the maschine    
    x_mid = x_mid / len(x_min)
    y_mid = y_mid / len(y_min)
    lowest_diff = 1000000
    middle = 0
    for i in range(len(x_min)):
        diff = ((x_max[i] + x_min[i]) /2 - x_mid)**2 + ((y_max[i] + y_min[i]) /2 - y_mid)**2
        if diff < lowest_diff:
            lowest_diff = diff
            middle = i
        
    return middle, x_cen, y_cen

def check_vertical(x):
    above_min = 1000
    above_class = None
    below_min = 1000
    below_class = None
    
    
    # for all individuals	
    for i in range(len(y_min)):
        # if the individual is above the current individual and the distance is smaller than the minimum distance
        if y_cen[i] < y_cen[x] and abs(y_cen[i]-y_cen[x]) < below_min:
            # check if the individual is above (for example 45° angle is not allowed), 1.5 is finetuned and can be changed
            if abs(x_cen[i] - x_cen[x])*1.5 < abs(y_cen[x] - y_cen[i]):
                # set the minimum distance to the distance between the two individuals -> this is the new minimum distance
                below_min = abs(y_cen[i]-y_cen[x])
                # set the below class to the current individual
                below_class = i
        # like above, but for below
        elif y_cen[i] > y_cen[x] and abs(y_cen[i]-y_cen[x]) < above_min:
            if abs(x_cen[i] - x_cen[x])*1.5 < abs(y_cen[x] - y_cen[i]):
                above_min = abs(y_cen[i]-y_cen[x])
                above_class = i
    
    return below_class, above_class

def check_horizontal(x):
    left_min = 1000
    left_class = None
    right_min = 1000
    right_class = None
    
    # for all individuals	
    for i in range(len(x_min)):
          # if the individual is left the current individual and the distance is smaller than the minimum distance
        if x_cen[i] > x_cen[x] and abs(x_cen[i]-x_cen[x]) < left_min:
            # check if the individual is to the side (for example 45° angle is not allowed), 1.5 is finetuned and can be changed
            if abs(y_cen[i] - y_cen[x])*1.5 < abs(x_cen[x] - x_cen[i]):
                # set the minimum distance to the distance between the two individuals -> this is the new minimum distance
                left_min = abs(x_cen[i]-x_cen[x])
                # set the left class to the current individual
                left_class = i
        # like left, but for right
        elif x_cen[i] < x_cen[x] and abs(x_cen[i]-x_cen[x]) < right_min:
            if abs(y_cen[i] - y_cen[x])*1.5 < abs(x_cen[x] - x_cen[i]):
                right_min = abs(x_cen[i]-x_cen[x])
                right_class = i
    
    return left_class, right_class

def rename_classes(classes):
    list_count = list()
    # Count the number of classes with the same name
    for i in range(len(classes)):
        count = 1
        for j in range(len(classes)):
            if i == j:
                continue
            if classes[i] == classes[j]:
                count += 1
        list_count.append(count)
        
    # Rename classes with the same name and decreasing the counter of every duplicate class
    for i in range(len(classes)):
        if list_count[i] > 1:
            for j in range(len(classes)):
                if i == j: continue
                if classes[i] == classes[j]:
                    list_count[j] -= 1
            classes[i] = classes[i] + str(list_count[i])
            list_count[i] -= 1
    
    return classes
                
def make_float(x):
    # convert the list of strings to a list of floats
    for i in range(len(x)):
        x[i] = float(x[i])
    return x

def read_csv(path):
    # Read the csv file and generate lists for each property filled with the values from the csv file
    df = pd.read_csv(path)
    df.columns = ['numbers','detection_scores','class', 'x min', 'y min', 'x max', 'y max']

    classes = df['class']
    det_scores = df['detection_scores']
    x_min = list(df['x min'])
    y_min = list(df['y min'])
    x_max = list(df['x max'])
    y_max = list(df['y max'])
            
    middle, x_cen, y_cen = check_middle(x_min, y_min, x_max, y_max)
            
    x_cen = make_float(x_cen)
    y_cen = make_float(y_cen)
    x_min = make_float(x_min)
    y_min = make_float(y_min)
    x_max = make_float(x_max)
    y_max = make_float(y_max)
        
    classes = rename_classes(classes)
        
    return df, classes, det_scores, x_min, y_min, x_max, y_max, middle, x_cen, y_cen

def explicit_mode(onto, individuals):
    # TODO implement explicit mode
    changed = True
    # it's possible that all individuals depend on each other, so we need to repeat the process for every individual
    for p in range(len(individuals)):
        # if no changes were made, break the loop
        if not changed:
            break
        changed = False
        # for every individual
        for i in range(len(individuals)):
            # get all properties of the individual
            for prop in individuals[i].get_properties():
                # get all values of the property
                for value in prop[individuals[i]]:
                    # if the value is a float, continue (keep only classes, not coordinates)
                    if isinstance(value, float):
                        continue
                    # get all properties of the value (next individual)
                    next = value.get_properties()
                    # for every property of the value
                    for prop2 in next:
                        # if the property is not the same as the property of the individual, continue (keep only the same properties)
                        if prop != prop2:
                            continue
                        # get all values of the property of the value
                        for value2 in prop2[value]:
                            # get the key of the individual from the value of the value (3rd individual)
                            for key2, values in individuals.items():
                                if value2  == values:
                                    # get the key of the individual from the value of the individual (2nd individual)
                                    for key, values in individuals.items():
                                        if values == value:
                                            # add the explicit relation
                                            # TODO only 2 relations possible, meed to change for more relations
                                            if individuals[key2] in prop[individuals[i]]:
                                                continue
                                            changed = True
                                            if prop.name == "above":
                                                individuals[i].above = [values, individuals[key2]]
                                            elif prop.name == "below":
                                                individuals[i].below = [values, individuals[key2]]
                                            elif prop.name == "left_to":
                                                individuals[i].left_to = [values, individuals[key2]]
                                            elif prop.name == "right_to":
                                                individuals[i].right_to = [values, individuals[key2]]
                                            else: print(prop.name)
    return onto, individuals


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate Ontology from csv file')
    parser.add_argument('-f', '--file', type=str, required=True, help='csv file path')
    parser.add_argument('-e','--explicit', default=False, action='store_true', help='add -e for explicit mode')
    parser.add_argument('-c','--coordinates', default=False, action='store_true', help='add -c to add coordinates to the individuals')
    parser.add_argument('-m','--multicam', default=False, action='store_true', help='add -m for multicam mode')
    
    args = parser.parse_args()
    csv_path = args.file
    explicit = args.explicit
    coordinates = args.coordinates
    multicam = args.multicam
    
    # Check if the csv file exists
    if not os.path.exists(csv_path):
        print("The csv file does not exist")
        exit(1)
    
    if not multicam:
    # Read the csv file
        df, classes, det_scores, x_min, y_min, x_max, y_max, middle, x_cen, y_cen = read_csv(csv_path)
     
        classes = rename_classes(classes)
        #onto = owl.get_ontology("file://test.rdf").load()
        onto = get_ontology("http://www.semanticweb.org/industrial_maschine")
        
        # Create classes and properties
        with onto:
            Components = types.new_class("Components", (Thing,))
            Maschines = types.new_class("Maschines", (Thing,))
            in_the_middle_of = types.new_class("in_the_middle_of", (ObjectProperty,))
            left_to = types.new_class("left_to", (ObjectProperty,))
            right_to = types.new_class("right_to", (ObjectProperty,))
            above = types.new_class("above", (ObjectProperty,))
            below = types.new_class("below", (ObjectProperty,))
            class x_center(Thing >> float):
                pass
            class y_center(Thing >> float):
                pass
            class x_minimum(Thing >> float):
                pass
            class y_minimum(Thing >> float):
                pass
            class x_maximum(Thing >> float):
                pass
            class y_maximum(Thing >> float):
                pass
            
            
        # Create individual of maschines
        Schleifmaschine = Maschines("Schleifmaschine")
        
        
        individuals = {}
        
        print(abs(x_cen[1] - x_cen[0]), abs(y_cen[1]-y_cen[0]))
        
        # Create individuals
        for i in range(len(x_cen)):
            individuals[i] = Components(classes[i])
            
            # Add coordinates to the individuals
            if coordinates:
                individuals[i].x_center = [x_cen[i]]
                individuals[i].y_center = [y_cen[i]]
                individuals[i].x_minimum = [x_min[i]]
                individuals[i].y_minimum = [y_min[i]]
                individuals[i].x_maximum = [x_max[i]]
                individuals[i].y_maximum = [y_max[i]]
            
        # Create relations
        for i in range(len(x_cen)):
            below_class, above_class = check_vertical(i)
            left_class, right_class = check_horizontal(i)
            
            # Add relations to the individuals
            if below_class != None:
                individuals[i].below = [individuals[below_class]]
            if above_class != None:
                individuals[i].above = [individuals[above_class]]
            if left_class != None:
                individuals[i].left_to = [individuals[left_class]]
            if right_class != None:
                individuals[i].right_to = [individuals[right_class]]
            
            
        individuals[middle].in_the_middle_of = [Schleifmaschine]
        
        
        # Create explicit relations
        if explicit:
            onto, individuals = explicit_mode(onto, individuals)
                                                    
                                                    
                    
                            
        
        # save the ontology
        onto.save(file = "output.rdf", format = "rdfxml")
    
    if multicam:
        onto = get_ontology("http://www.semanticweb.org/industrial_maschine")
        files = os.listdir(csv_path)
        # for every file in the directory
        for file in files:
            if not file.endswith(".csv"):
                files.remove(file)
        print(files)
        # for every file in the directory
        cams = {}
        i = 0
        for file in files:
            # Read the csv file
            df, classes, det_scores, x_min, y_min, x_max, y_max, middle, x_cen, y_cen = read_csv(f'{csv_path}/{file}')  
            with onto:
                cams[i] = types.new_class(f"Camera_{file.removesuffix('.csv')}", (Thing,))
                # Create classes and properties
                Components = types.new_class("Components", (cams[i],))
                Maschines = types.new_class("Maschines", (cams[i],))
                
                try: 
                    in_the_middle_of
                except NameError:
                    in_the_middle_of = types.new_class("in_the_middle_of", (ObjectProperty,))
                    left_to = types.new_class("left_to", (ObjectProperty,))
                    right_to = types.new_class("right_to", (ObjectProperty,))
                    above = types.new_class("above", (ObjectProperty,))
                    below = types.new_class("below", (ObjectProperty,))
                    class x_center(Thing >> float):
                        pass
                    class y_center(Thing >> float):
                        pass
                    class x_minimum(Thing >> float):
                        pass
                    class y_minimum(Thing >> float):
                        pass
                    class x_maximum(Thing >> float):
                        pass
                    class y_maximum(Thing >> float):
                        pass
                else: 
                    pass
            
            # Create individual of maschines
        Schleifmaschine = Maschines("Schleifmaschine")
        
        
        individuals = {}
        
        print(abs(x_cen[1] - x_cen[0]), abs(y_cen[1]-y_cen[0]))
        
        # Create individuals
        for i in range(len(x_cen)):
            individuals[i] = Components(classes[i])
            
            # Add coordinates to the individuals
            if coordinates:
                individuals[i].x_center = [x_cen[i]]
                individuals[i].y_center = [y_cen[i]]
                individuals[i].x_minimum = [x_min[i]]
                individuals[i].y_minimum = [y_min[i]]
                individuals[i].x_maximum = [x_max[i]]
                individuals[i].y_maximum = [y_max[i]]
            
        # Create relations
        for i in range(len(x_cen)):
            below_class, above_class = check_vertical(i)
            left_class, right_class = check_horizontal(i)
            
            # Add relations to the individuals
            if below_class != None:
                individuals[i].below = [individuals[below_class]]
            if above_class != None:
                individuals[i].above = [individuals[above_class]]
            if left_class != None:
                individuals[i].left_to = [individuals[left_class]]
            if right_class != None:
                individuals[i].right_to = [individuals[right_class]]
            
            
        individuals[middle].in_the_middle_of = [Schleifmaschine]
        
        
        # Create explicit relations
        if explicit:
            onto, individuals = explicit_mode(onto, individuals)
        # save the ontology
        onto.save(file = "output.rdf", format = "rdfxml")
    
# to run:
# python OntologyGenerator.py -f test.csv -e -c (-e for explicit mode, -c for added coordinates)