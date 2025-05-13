import os
import argparse
import pandas as pd
import numpy as np
from owlready2 import *
from owlready2.prop import destroy_entity
from math import sqrt
import re

def get_new_individual(indname, new_individuals, ind_dict):
    found = None
    for key, value in ind_dict.items():
        indname = str(re.sub(r'\d+$', '', indname.split("_")[0]))
        if value.startswith(f"Summary_"+ indname):
            found = key
            return new_individuals[found]
        
    if found == None:
        return None


class ontologySummarizer:
    def summarize(onto, all_individuals, cams, components):
        with onto:
            cams[len(cams)] = (types.new_class(f"Summary", (Thing,)))
            components[len(components)] = (types.new_class(f"Components_Summary", (cams[len(cams) - 1],)))
        
            count = 0
            summarized_individuals = list({})
            new_individuals = {}
        
            for i in range(len(all_individuals)):
                individuals = all_individuals[i]
                for j in individuals:
                    new_set = set({individuals[j]})
                    for k in range(len(individuals[j].equivalent_to)):
                        new_set.add(individuals[j].equivalent_to[k])
                
                    found = False
                    for k in range(len(summarized_individuals)):
                        if summarized_individuals[k].issubset(new_set) and new_set.issubset(summarized_individuals[k]):
                            found = True
                
                    if not found:
                        summarized_individuals.append(new_set)
                        count += 1
                    
                    if len(summarized_individuals) == 0:
                        summarized_individuals.append(new_set)
                        count += 1
                    
          
        
            ind_dict = {}

            for i in range(len(summarized_individuals)):
                i_individuals = list(summarized_individuals[i])
                name = i_individuals[0].name.split("_")[0]
                ind_dict.update({i: "Summary_" + name})
                with onto:
                    new_individuals[i] = components[len(components) - 1]("Summary_" + name)

            
            
            print(new_individuals)
            print(ind_dict)
            print(get_new_individual("Summary_Gewinde", new_individuals, ind_dict))
            
            for i in range(len(summarized_individuals)):
                for ind in summarized_individuals[i]:
                    for j in range(len(ind.above)):
                        new_individuals[i].above.append(get_new_individual((ind.above[j].name), new_individuals, ind_dict))
                    for j in range(len(ind.below)):
                        new_individuals[i].below.append(get_new_individual((ind.below[j].name), new_individuals, ind_dict))
                    for j in range(len(ind.right_to)):
                        new_individuals[i].right_to.append(get_new_individual((ind.right_to[j].name), new_individuals, ind_dict))
                    for j in range(len(ind.left_to)):
                        new_individuals[i].left_to.append(get_new_individual((ind.left_to[j].name), new_individuals, ind_dict))
                    for j in range(len(ind.inside_of)):
                        new_individuals[i].inside_of.append(get_new_individual((ind.inside_of[j].name), new_individuals, ind_dict))
                    for j in range(len(ind.outside_of)):
                        new_individuals[i].outside_of.append(get_new_individual((ind.outside_of[j].name), new_individuals, ind_dict))
                    

        all_individuals[len(all_individuals)] = new_individuals
        return onto, all_individuals, cams, components