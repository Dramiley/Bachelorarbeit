from owlready2 import *
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Statement Generator from csv file')
    parser.add_argument('-o', '--owl', type=str, required=True, help='ontology file path')
    args = parser.parse_args()
    
    Statements = open("Statements.txt", "w")
    
    onto = get_ontology("file://" + args.owl).load()
    for i in onto.individuals():
        for j in i.is_a:
            Statements.write(i.name + " is part of " + j.name + "\n")
    #Statements.write("\n")
    
    for i in onto.individuals():
        for prop in i.get_properties():
            for value in prop[i]:
                if isinstance(value, float):
                    Statements.write(i.name + " " + prop.name + " " + str(value) + "\n")
                else:
                    Statements.write(i.name + " " + prop.name + " " + value.name + "\n")
            for e in i.equivalent_to:
                Statements.write(i.name + " is equivalent to " + e.name + "\n")
        Statements.write("\n")
                
    Statements.close()
                
    