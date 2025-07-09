import os
import argparse
import pandas as pd
import numpy as np
from owlready2 import *
from owlready2.prop import destroy_entity
from math import sqrt
import re


# returns the new summarized individual from the old individuals
def get_new_individual(ind, new_individuals, summarized_individuals):
    found = None
    for i in range(len(summarized_individuals)):
        if {ind}.issubset(summarized_individuals[i]):
            found = i
            return new_individuals[found]
  
    if found == None:
        return None
    
def get_name(individuals):
    counter = {}
    for i in range(len(individuals)):
        if individuals[i].name.split("_")[0] not in counter:
            counter[individuals[i].name.split("_")[0]] = 1
        else:
            counter[individuals[i].name.split("_")[0]] += 1
    
    name = max(counter, key=counter.get)
    #print(f"Most common name: {name} with {counter[name]} occurrences")
    return name


# summarizes the ontology by creating a new individual for each unique set of individuals
class ontologySummarizer:
    def summarize(onto, all_individuals, cams, components, output):
        summarized_individuals = list({})
        new_individuals = {}
        
        # iterate through all individuals and create a new set for each individual and its equivalent individuals
        # check if the individual is already in the summarized individuals
        for i in range(len(all_individuals)):
            individuals = all_individuals[i]
            for j in individuals:
                # create a new set with the current individual and its equivalent individuals
                new_set = set({individuals[j]})
                for k in range(len(individuals[j].equivalent_to)):
                    new_set.add(individuals[j].equivalent_to[k])

                # check if the new set is already in the summarized individuals
                found = False
                for k in range(len(summarized_individuals)):
                    # check both ways to verify, if the sets are equal
                    if summarized_individuals[k].issubset(new_set) and new_set.issubset(summarized_individuals[k]):
                        found = True

                # if not, add the new set to the summarized individuals
                if not found:
                    summarized_individuals.append(new_set)
                    
                # check if summarized individuals is empty, if so, add the new set
                if len(summarized_individuals) == 0:
                    summarized_individuals.append(new_set)
               
        # create a new ontology for the summarized individuals     
        new_onto = get_ontology("http://www.semanticweb.org/summary_maschine")
        with new_onto:
            Components = types.new_class("Components", (Thing,))
            Maschines = types.new_class("Maschines", (Thing,))
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
            
            Maschine = Maschines("Maschine")
                    
            class detection_score(Thing >> float):
                pass
            
            
            # create a new individual for each summarized individual
            for i in range(len(summarized_individuals)):
                i_individuals = list(summarized_individuals[i])
                name = get_name(i_individuals)
                with new_onto:
                    new_individuals[i] = Components(name)

            
            
            # iterate through the summarized individuals and add all relations from all individuals of the same set to the new individual
            for i in range(len(summarized_individuals)):
                for ind in summarized_individuals[i]:
                    for j in range(len(ind.above)):
                        new_individuals[i].above.append(get_new_individual(ind.above[j], new_individuals, summarized_individuals))
                    for j in range(len(ind.below)):
                        new_individuals[i].below.append(get_new_individual(ind.below[j], new_individuals, summarized_individuals))
                    for j in range(len(ind.right_to)):
                        new_individuals[i].right_to.append(get_new_individual(ind.right_to[j], new_individuals, summarized_individuals))
                    for j in range(len(ind.left_to)):
                        new_individuals[i].left_to.append(get_new_individual(ind.left_to[j], new_individuals, summarized_individuals))
                    for j in range(len(ind.inside_of)):
                        new_individuals[i].inside_of.append(get_new_individual(ind.inside_of[j], new_individuals, summarized_individuals))
                    for j in range(len(ind.outside_of)):
                        new_individuals[i].outside_of.append(get_new_individual(ind.outside_of[j], new_individuals, summarized_individuals))
                    for j in range(len(ind.in_the_middle_of)):
                        new_individuals[i].in_the_middle_of.append(Maschine)
                    

        new_onto.save(file = f"{output}_summary.owl", format = "rdfxml")