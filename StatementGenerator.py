from owlready2 import *
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Statement Generator from csv file')
    parser.add_argument('-o', '--owl', type=str, required=True, help='ontology file path')
    args = parser.parse_args()
    
    Statements = open("Statements.txt", "w")
    
    onto = get_ontology("file://" + args.owl).load()
    
    for i in onto.individuals():
        for e in i.is_a:
            Statements.write(i.name + " is part of " + e.name + "\n")
        for e in i.above:
            Statements.write(i.name + " above " + e.name + "\n")
        for e in i.below:
            Statements.write(i.name + " below " + e.name + "\n")
        for e in i.left_to:
            Statements.write(i.name + " left to " + e.name + "\n")
        for e in i.right_to:
            Statements.write(i.name + " right to " + e.name + "\n")
        for e in i.inside_of:
            Statements.write(i.name + " inside of " + e.name + "\n")
        for e in i.outside_of:
            Statements.write(i.name + " outside of " + e.name + "\n")
        for e in i.in_the_middle_of:
            Statements.write(i.name + " in the middle of " + e.name + "\n")
        for e in i.equivalent_to:
            Statements.write(i.name + " is equivalent to " + e.name + "\n")
        Statements.write("\n")
                
    Statements.close()
                
    