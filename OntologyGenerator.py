import os
import argparse
import pandas as pd
import numpy as np
from owlready2 import *
from owlready2.prop import destroy_entity
from math import sqrt
import re
from OntologySummarizer import ontologySummarizer
from shapely.geometry import box
import configparser

pd.options.mode.chained_assignment = None


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
    
    # calculate the middle of the Machine    
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
    fixed_value = 0.7
    above_min = 1024
    above_class = []
    below_min = 1024
    below_class = []
    
    
    # for all individuals	
    for i in range(len(y_min)):
        if explicit:
            above_min = 1024
            below_min = 1024
        if x_cen[i] == x_cen[x] and y_cen[i] == y_cen[x]:
            continue
        # if the individual is above the current individual and the distance is smaller than the minimum distance
        if y_cen[i] < y_cen[x] and abs(y_cen[i]-y_cen[x]) < below_min:
            # check if the individual is above (for example 45° angle is not allowed), fixed_value is finetuned and can be changed
            if abs(x_cen[i] - x_cen[x])*fixed_value < abs(y_cen[x] - y_cen[i]):
                 # if explicit, add individual to list, else clear the list and add the individual (so only one can be added)
                if explicit == True:
                    below_class.append(i)
                else:
                    below_class.clear() 
                    below_class.append(i)   
                # set the minimum distance to the distance between the two individuals -> this is the new minimum distance
                below_min = abs(y_cen[i]-y_cen[x])
        # like above, but for below
        elif y_cen[i] > y_cen[x] and abs(y_cen[i]-y_cen[x]) < above_min:
            if abs(x_cen[i] - x_cen[x])*fixed_value < abs(y_cen[x] - y_cen[i]):
                if explicit == True:
                    above_class.append(i)
                else:
                    above_class.clear() 
                    above_class.append(i)   
                above_min = abs(y_cen[i]-y_cen[x])
    
    return list(set(below_class)), list(set(above_class))

def check_horizontal(x):
    fixed_value = 0.7
    left_min = 1024
    left_class = []
    right_min = 1024
    right_class = []
    
    # for all individuals	
    for i in range(len(x_min)):
        if explicit:
            right_min = 1024
            left_min = 1024
        if x_cen[i] == x_cen[x] and y_cen[i] == y_cen[x]:
            continue
          # if the individual is left the current individual and the distance is smaller than the minimum distance
        if x_cen[i] > x_cen[x] and abs(x_cen[i]-x_cen[x]) < left_min:
            # check if the individual is to the side (for example 45° angle is not allowed), fixed_value is finetuned and can be changed
            if abs(y_cen[i] - y_cen[x])*fixed_value< abs(x_cen[x] - x_cen[i]):
                # if explicit, add individual to list, else clear the list and add the individual (so only one can be added)
                if explicit == True:
                    left_class.append(i)
                else:
                    left_class.clear() 
                    left_class.append(i) 
                # set the minimum distance to the distance between the two individuals -> this is the new minimum distance  
                left_min = abs(x_cen[i]-x_cen[x])
        # like left, but for right
        elif x_cen[i] < x_cen[x] and abs(x_cen[i]-x_cen[x]) < right_min:
            if abs(y_cen[i] - y_cen[x])*fixed_value < abs(x_cen[x] - x_cen[i]):
                if explicit == True:
                    right_class.append(i)
                else:
                    right_class.clear() 
                    right_class.append(i)   
                right_min = abs(x_cen[i]-x_cen[x])
    
    return list(set(left_class)), list(set(right_class))

def rename_classes(classes, x_cen):
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
    # create a new list with the indexes of the same classes
    for i in range(len(classes)):
        same = []
        for j in range(len(classes)):
            if classes[i] == classes[j]:
                same.append(j)
                
        
        c = 0
        temp = list_count[i]
        # as long as there are more than one class with the same name, rename them    
        while temp > 1:
            c += 1
            
            # find the class with the smallest x_cen value
            min = 1000
            min_j = same[0]
            for j in same:
                if x_cen[j] < min:
                    min = x_cen[j]
                    min_j = j
                      
            # rename the class with the smallest x_cen value (1 lowest, 2 little higher, ...)
            classes[min_j] = classes[min_j] + str(c)
            
            # remove the class with the smallest x_cen value from the list of same classes
            same.remove(min_j)
            
            # set the count of the class with the smallest x_cen value to 1, so it is not renamed again   
            list_count[min_j] = 1
            
            # decrease the count of the classes with the same name
            for j in same:
                list_count[j] -= 1
            temp -= 1
            
            # if there is only one class left with the same name, rename it and break the loop
            if len(same) == 1:
                c += 1
                classes[same[0]] = classes[same[0]] + str(c)
                list_count[same[0]] = 1
    
    return classes
                
def make_float(x):
    # convert the list of strings to a list of floats
    for i in range(len(x)):
        x[i] = round(float(x[i]), 3)
    return x

def remove_end_number(string):
    # remove the number at the end of the string
    return re.sub(r'\d+$', '', string)

def get_class_names(array):
    new_array = array.copy()
    for i in range(len(array)):
        # remove the number at the end of the string
        new_array[i] = re.sub(r'\d+$', '', array[i].name.split("_")[0])
    
    return new_array

def read_csv(path):
    # Read the csv file and generate lists for each property filled with the values from the csv file
    df = pd.read_csv(path)
    try:
        df.columns = ['numbers','detection_scores','class', 'x min', 'y min', 'x max', 'y max']
    except ValueError:
        df.columns = ['detection_scores','class', 'x min', 'y min', 'x max', 'y max']

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
    det_scores = make_float(det_scores).to_list()
        
    classes = rename_classes(classes, x_cen)
        
    return df, classes, det_scores, x_min, y_min, x_max, y_max, middle, x_cen, y_cen

# used for backend, owl automatically creates the properties but the python-lists are not updated
# so we need to update the lists manually, to avoid false calculations
# so we need to add reverse properties to the individuals
def reverse_properties(onto, individuals):
    for i in range(len(individuals)):
        for j in range(len(individuals[i].above)):
            individuals[i].above[j].below.append(individuals[i]) 
        for j in range(len(individuals[i].below)):
            individuals[i].below[j].above.append(individuals[i])
        for j in range(len(individuals[i].left_to)):
            individuals[i].left_to[j].right_to.append(individuals[i])
        for j in range(len(individuals[i].right_to)):
            individuals[i].right_to[j].left_to.append(individuals[i])
        for j in range(len(individuals[i].equivalent_to)):
            individuals[i].equivalent_to[j].equivalent_to.append(individuals[i])
        for j in range(len(individuals[i].inside_of)):
            individuals[i].inside_of[j].outside_of.append(individuals[i])
        for j in range(len(individuals[i].outside_of)):
            individuals[i].outside_of[j].inside_of.append(individuals[i])
        
    onto, individuals = remove_redundant_properties(onto, individuals)
    return onto, individuals

# extension of reverse_properties for all individuals
def reverse_properties_all(onto, all_individuals):
    for i in range(len(all_individuals)):
       onto, individuals = reverse_properties(onto, all_individuals[i])
       all_individuals[i] = individuals

        
    return onto, all_individuals

# function to remove redunant properties and individuals from the ontology-list
def remove_redundant_properties(onto, individuals):
    for i in range(len(individuals)):
            # remove the redundant properties from the individuals
            individuals[i].above = list(set(individuals[i].above))
            individuals[i].below = list(set(individuals[i].below))
            individuals[i].left_to = list(set(individuals[i].left_to))
            individuals[i].right_to = list(set(individuals[i].right_to))
            individuals[i].equivalent_to = list(set(individuals[i].equivalent_to))
            individuals[i].inside_of = list(set(individuals[i].inside_of))
            individuals[i].outside_of = list(set(individuals[i].outside_of))
            
    return onto, individuals

# extension of remove_redundant_properties for all individuals
def remove_redundant_properties_all(onto, all_individuals):
    for i in range(len(all_individuals)):
        onto, individuals = remove_redundant_properties(onto, all_individuals[i])
        all_individuals[i] = individuals
        
    return onto, all_individuals


def same_individuals(onto, all_individuals):
    threshold = 0.75
    tolerance = 0.45
    # for every combination of individual-lists
    for a in range(len(all_individuals)):
        for b in range(len(all_individuals)):
            # if the lists are the same, continue
            if a == b:
                continue
            # only check lists, that are not already checked (a < b)
            if b < a:
                continue
            
            # set the lists for future reference
            individuals = all_individuals[a]
            next = all_individuals[b]
            
            # for every individual in every list
            for j in range(len(individuals)):
                for k in range(len(next)):
                    # compare names and properties of the individuals
                    propability = 0.0
                    same_next = 0
                    # [0] is the class name, remove_end_number to make Motor and Motor_1 the same
                    if remove_end_number(individuals[j].name.split("_")[0]) == remove_end_number(next[k].name.split("_")[0]):
                        for l in range(len(individuals[j].above)):
                            for m in range(len(next[k].above)):
                                if remove_end_number(individuals[j].above[l].name.split("_")[0]) == remove_end_number(next[k].above[m].name.split("_")[0]):
                                    propability += 1.0
                                if remove_end_number(individuals[j].name.split("_")[0]) == remove_end_number(individuals[j].above[l].name.split("_")[0]):
                                    same_next += 1
                        for l in range(len(individuals[j].below)):
                            for m in range(len(next[k].below)):
                                if remove_end_number(individuals[j].below[l].name.split("_")[0]) == remove_end_number(next[k].below[m].name.split("_")[0]):
                                    propability += 1.0
                                if remove_end_number(individuals[j].name.split("_")[0]) == remove_end_number(individuals[j].below[l].name.split("_")[0]):
                                    same_next += 1
                        for l in range(len(individuals[j].left_to)):
                            for m in range(len(next[k].left_to)):
                                if remove_end_number(individuals[j].left_to[l].name.split("_")[0]) == remove_end_number(next[k].left_to[m].name.split("_")[0]):
                                    propability += 1.0
                                if remove_end_number(individuals[j].name.split("_")[0]) == remove_end_number(individuals[j].left_to[l].name.split("_")[0]):
                                    same_next += 1
                        for l in range(len(individuals[j].right_to)):
                            for m in range(len(next[k].right_to)):
                                if remove_end_number(individuals[j].right_to[l].name.split("_")[0]) == remove_end_number(next[k].right_to[m].name.split("_")[0]):
                                    propability += 1.0
                                if remove_end_number(individuals[j].name.split("_")[0]) == remove_end_number(individuals[j].right_to[l].name.split("_")[0]):
                                    same_next += 1
                        for l in range(len(individuals[j].inside_of)):
                            for m in range(len(next[k].inside_of)):
                                if remove_end_number(individuals[j].inside_of[l].name.split("_")[0]) == remove_end_number(next[k].inside_of[m].name.split("_")[0]):
                                    propability += 1.0
                                if remove_end_number(individuals[j].name.split("_")[0]) == remove_end_number(individuals[j].inside_of[l].name.split("_")[0]):
                                    same_next += 1
                        for l in range(len(individuals[j].outside_of)):
                            for m in range(len(next[k].outside_of)):
                                if remove_end_number(individuals[j].outside_of[l].name.split("_")[0]) == remove_end_number(next[k].outside_of[m].name.split("_")[0]):
                                    propability += 1.0
                                if remove_end_number(individuals[j].name.split("_")[0]) == remove_end_number(individuals[j].outside_of[l].name.split("_")[0]):
                                    same_next += 1
                            
                        # calculate the propability of the individuals being the same
                        try:
                            propability = propability / ((len(individuals[j].above) + len(individuals[j].below) + len(individuals[j].left_to) + len(individuals[j].right_to) + len(individuals[j].inside_of) + len(individuals[j].outside_of)))  
                        except ZeroDivisionError:
                            propability = 0.0
                        
                        # if the individual has a object of the same class next to it
                        #TODO check if important to keep or can be removed
                        #if same_next >= 1:
                        if False:
                            check_next = 0
                            # check if the next individual is in a property of the individual and the individual is in the same property of the next individual
                            if remove_end_number(next[j].name.split("_")[0]) in get_class_names(individuals[j].above) and remove_end_number(individuals[k].name.split("_")[0]) in get_class_names(next[j].above):
                                check_next += 1
                                
                            if remove_end_number(next[j].name.split("_")[0]) in get_class_names(individuals[j].below) and remove_end_number(individuals[k].name.split("_")[0]) in get_class_names(next[j].below):
                                check_next += 1
                                
                            if remove_end_number(next[j].name.split("_")[0]) in get_class_names(individuals[j].left_to) and remove_end_number(individuals[k].name.split("_")[0]) in get_class_names(next[j].left_to):
                                check_next += 1
                                        
                            if remove_end_number(next[k].name.split("_")[0]) in get_class_names(individuals[j].right_to) and remove_end_number(individuals[j].name.split("_")[0]) in get_class_names(next[j].right_to):
                                check_next += 1
                                
                            if remove_end_number(next[k].name.split("_")[0]) in get_class_names(individuals[j].inside_of) and remove_end_number(individuals[j].name.split("_")[0]) in get_class_names(next[j].inside_of):
                                check_next += 1
                            
                            if remove_end_number(next[k].name.split("_")[0]) in get_class_names(individuals[j].outside_of) and remove_end_number(individuals[j].name.split("_")[0]) in get_class_names(next[j].outside_of):
                                check_next += 1

                            if check_next * 1.5 > same_next:
                                if next[k].name.split("_")[0] == individuals[j].name.split("_")[0] and propability > (threshold - tolerance):
                                    individuals[j].equivalent_to.append(next[k])
                                elif propability > threshold:
                                    individuals[j].equivalent_to.append(next[k])
                        else:
                            if next[k].name.split("_")[0] == individuals[j].name.split("_")[0] and propability > (threshold - tolerance):
                                individuals[j].equivalent_to.append(next[k])
                            elif propability > threshold:
                                individuals[j].equivalent_to.append(next[k])
                                

    onto, all_individuals = remove_redundant_properties_all(onto, all_individuals)
    return onto, all_individuals

def remove_false_detections(onto, all_individuals):
    threshold = 0.80
    average_same = 0.0
    total_individuals = 0.0
    for i in range(len(all_individuals)):
        individuals = all_individuals[i]
        for j in range(len(individuals)):
            average_same += len(set(individuals[j].equivalent_to))
            total_individuals += 1.0
    
    average_same = average_same / total_individuals
    
    for i in range(len(all_individuals)):
        individuals = all_individuals[i]
        for j in range(len(individuals)):
            # if the individual has less than the average number of equivalent individuals and the detection_score is low, remove it
            # print(average_same, len(set(individuals[j].equivalent_to)), individuals[j].name)
            if len(set(individuals[j].equivalent_to)) < average_same and individuals[j].detection_score[0] < threshold:
                # TODO: detroy_entity is not working, need to find a solution
                try:
                    #continue
                    destroy_entity(individuals[j])
                except Exception as e:
                    print(f"Error: {e}")
                print(f"removed {individuals[j].name} from ontology")
        
            
    return onto, all_individuals

# this function checks if the individual j is inside the individual i, if so, it adds the individual i to the inside_of property of the individual j
def check_inside(onto, individuals):
    # threshold for the inside property, if the inside-area is bigger than the treshold (70%) of the whole boxarea, it is inside
    # can be changed to fit the needs
    threshold = 0.7
    # check if the individual i is inside the individual j
    for i in range(len(individuals)):
        for j in range(len(individuals)):
            if i == j:
                continue
            
            rect1 = box(x_min[i], y_min[i], x_max[i], y_max[i])
            rect2 = box(x_min[j], y_min[j], x_max[j], y_max[j])
                
            intersection = rect1.intersection(rect2)
            
            
            if intersection.area / rect2.area >= threshold and rect2.area < rect1.area:
                individuals[j].inside_of.append(individuals[i])
      
                
    onto, individuals = remove_redundant_properties(onto, individuals)
    return onto, individuals


def check_inside_all(onto, all_individuals):
    for i in range(len(all_individuals)):
        individuals = all_individuals[i]
        onto, individuals = check_inside(onto, all_individuals[i])
        all_individuals[i] = individuals
        
    return onto, all_individuals


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate Ontology from csv file')
    parser.add_argument("-c", "--config", type=str, help="Path to the config file", default="Evaluation/config.ini")
    
    args = parser.parse_args()
    
    config = configparser.ConfigParser()
    config.read(args.config)

    output = config.get("DEFAULT","output_path")
    csv_path = config.get("DEFAULT","csv_path")
    coordinates = config.getboolean("DEFAULT","add_coordinates")
    explicit = config.getboolean("DEFAULT","explicit_mode")
    remove = config.getboolean("DEFAULT","remove_false")
    summarize = config.getboolean("DEFAULT","summarize_graph")
    
    
    
    if csv_path.endswith(".csv"):
        multicam = False
    else: 
        multicam = True
    
    # Check if the csv file exists
    print(f"Using csv file: {csv_path}")
    if not os.path.exists(csv_path):
        print("The csv file does not exist")
        exit(1)
    
    if not multicam:
    # Read the csv file
        df, classes, det_scores, x_min, y_min, x_max, y_max, middle, x_cen, y_cen = read_csv(csv_path)
     
        #onto = owl.get_ontology("file://test.rdf").load()
        onto = get_ontology("http://www.semanticweb.org/industrial_machine")
        
        # Create classes and properties
        with onto:
            Components = types.new_class("Components", (Thing,))
            Machines = types.new_class("Machines", (Thing,))
            in_the_middle_of = types.new_class("in_the_middle_of", (ObjectProperty,))
            left_to = types.new_class("left_to", (ObjectProperty,))
            right_to = types.new_class("right_to", (ObjectProperty,))
            above = types.new_class("above", (ObjectProperty,))
            below = types.new_class("below", (ObjectProperty,))
            outside_of = types.new_class("outside_of", (ObjectProperty,))
            inside_of = types.new_class("inside_of", (ObjectProperty,))
            
            left_to.inverse_property = right_to
            above.inverse_property = below
            inside_of.inverse_property = outside_of
                    
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
            class detection_score(Thing >> float):
                pass
            
            
        # Create individual of Machines
        Machine = Machines("Machine")
        
        
        individuals = {}

        
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
            
            individuals[i].detection_score = [det_scores[i]]
            
        # Create relations
        for i in range(len(x_cen)):
            below_class, above_class = check_vertical(i)
            left_class, right_class = check_horizontal(i)
            
            # Add relations to the individuals
            for j in range(len(left_class)):
                individuals[i].left_to.append(individuals[left_class[j]])
            
            for j in range(len(right_class)):
                individuals[i].right_to.append(individuals[right_class[j]])
                
            for j in range(len(above_class)):
                individuals[i].above.append(individuals[above_class[j]])
            
            for j in range(len(below_class)):
                individuals[i].below.append(individuals[below_class[j]])
            
            
        individuals[middle].in_the_middle_of = [Machine]
        
               
        onto, individuals = check_inside(onto, individuals)
                 
        onto, individuals = reverse_properties(onto, individuals)
        
        onto, individuals = remove_redundant_properties(onto, individuals)
        
        # save the ontology
        print(f"Ontology saved as {output}.owl")
        onto.save(file = f"{output}.owl", format = "rdfxml")
    
    if multicam:
        ontoSummarizer = ontologySummarizer()
        onto = get_ontology("http://www.semanticweb.org/industrial_machine")
        files = os.listdir(csv_path)
        # for every file in the directory
        for file in files:
            if not file.endswith(".csv"):
                files.remove(file)
        # print(files)
        # for every file in the directory
        cams = {}
        components = {}
        i = 0
        all_individuals = {}
        for file in files:
            # Read the csv file
            print(f'{csv_path}/{file}')
            df, classes, det_scores, x_min, y_min, x_max, y_max, middle, x_cen, y_cen = read_csv(f'{csv_path}/{file}')  
            with onto:
                name = file.removesuffix('.csv')
                cams[i] = types.new_class(f"Camera_{name}", (Thing,))
                # Create classes and properties
                components[i] = types.new_class(f"Components_{name}", (cams[i],))
                Machines = types.new_class("Machines", (cams[i],))
                # Create individual of Machines
                Machine = Machines("Machine")

                
                try: 
                    in_the_middle_of
                except NameError:
                    in_the_middle_of = types.new_class("in_the_middle_of", (ObjectProperty,))
                    left_to = types.new_class("left_to", (ObjectProperty, ))
                    right_to = types.new_class("right_to", (ObjectProperty,))
                    above = types.new_class("above", (ObjectProperty,))
                    below = types.new_class("below", (ObjectProperty,))
                    outside_of = types.new_class("outside_of", (ObjectProperty,))
                    inside_of = types.new_class("inside_of", (ObjectProperty,))
                    
                    left_to.inverse_property = right_to
                    above.inverse_property = below
                    inside_of.inverse_property = outside_of
                    
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
                    class detection_score(Thing >> float):
                        pass
                    
                else: 
                    pass
                
                individuals = {}
        
                # Create individuals
                for j in range(len(x_cen)):
                    individuals[j] = components[i](classes[j] + "_" + name)

                    # Add coordinates to the individuals
                    if coordinates:
                        individuals[j].x_center = [x_cen[j]]
                        individuals[j].y_center = [y_cen[j]]
                        individuals[j].x_minimum = [x_min[j]]
                        individuals[j].y_minimum = [y_min[j]]
                        individuals[j].x_maximum = [x_max[j]]
                        individuals[j].y_maximum = [y_max[j]]
                    
                    individuals[j].detection_score = [det_scores[j]]
            
                # Create relations
                for j in range(len(x_cen)):
                    below_class, above_class = check_vertical(j)
                    left_class, right_class = check_horizontal(j)
            
                     # Add relations to the individuals
                    for k in range(len(left_class)):
                        individuals[j].left_to.append(individuals[left_class[k]])
            
                    for k in range(len(right_class)):
                        individuals[j].right_to.append(individuals[right_class[k]])
                
                    for k in range(len(above_class)):
                        individuals[j].above.append(individuals[above_class[k]])
            
                    for k in range(len(below_class)):
                        individuals[j].below.append(individuals[below_class[k]])
            
            
                individuals[middle].in_the_middle_of = [Machine]
                  
                all_individuals[i] = individuals
                  
                i += 1

        onto, all_individuals = check_inside_all(onto, all_individuals)
        
        onto, all_individuals = reverse_properties_all(onto, all_individuals)
        
        onto, all_individuals = same_individuals(onto, all_individuals)
        
        onto, all_individuals = reverse_properties_all(onto, all_individuals)
        
        onto, all_individuals = remove_redundant_properties_all(onto, all_individuals)
            
        if remove:
            # remove false detections
            onto, all_individuals = remove_false_detections(onto, all_individuals)
            
        if summarize:
            ontologySummarizer.summarize(onto, all_individuals, cams, components, output)
        
        # save the ontology
        onto.save(file = f"{output}.owl", format = "rdfxml")
        print(f"Ontology saved as {output}.owl")
    
# to run:
# python OntologyGenerator.py -c config.ini
# for mutliple cameras, use the csv_path as a directory with multiple csv files