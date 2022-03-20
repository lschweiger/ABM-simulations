# create_problem_space.py
import os
import bz2
import pickle
from numpy import loadtxt


class create_problem_space(object):
    
    def __init__(self,simulation_number):
        self.simulation_number = simulation_number
       
    def return_NK_problem_space(self):
            cwd = os.getcwd()
            os.chdir('/mnt/fe296d38-f1f4-4735-8745-7bd587944d6d/Tragedy_of_the_Network_New/NK_Spaces')
            ## os.chdir('/afs/ir.stanford.edu/users/c/j/cjgomez/Lazer_Tragedy_of_the_Networks/NK_Spaces')
            #filename = "NK_space_scores_" + str(self.simulation_number) + ".bz2"
            filename = "NK_space_scores_" + str(self.simulation_number) + ".pkl"
            #with bz2.open(cwd+"/NK_Spaces/"+filename, "rt",newline='\n') as bz_file:
            NK_score=pickle.load(open(filename,'rb'))
            os.chdir(cwd)
            ## os.chdir('/afs/ir.stanford.edu/users/c/j/cjgomez/Lazer_Tragedy_of_the_Networks/')
            return NK_score
    def return_TSP_problem_space(self):
            cwd = os.getcwd()    
            
            os.chdir(cwd+'/TSP_Spaces')
            #os.chdir('/afs/ir.stanford.edu/users/c/j/cjgomez/Lazer_Tragedy_of_the_Networks/TSP_Spaces')
            filename = "TSP_Space_"+str(self.simulation_number)+".txt"
            TSP_space = loadtxt(filename,delimiter=" ",unpack=False)
            os.chdir(cwd)
            #os.chdir('/afs/ir.stanford.edu/users/c/j/cjgomez/Lazer_Tragedy_of_the_Networks/')
            
            TSP_space = TSP_space.tolist()
            return TSP_space
    
