# create_problem_space.py
import os
import bz2
from shutil import copyfileobj
from numpy import double
from random import randint
from random import uniform
import numpy as np
from numpy import loadtxt


class create_problem_space(object):
    
    def __init__(self,problem_space,simulation_number):
        self.problem_space = problem_space
        self.simulation_number = simulation_number
        
    def return_NK_problem_space(self):
            os.chdir('/Users/macuser/Documents/Stanford Research/Lazer - Tragedy of the Network/NK_Spaces')
            ## os.chdir('/afs/ir.stanford.edu/users/c/j/cjgomez/Lazer_Tragedy_of_the_Networks/NK_Spaces')
            filename = "NK_space_scores_" + str(self.simulation_number) + ".bz2"
            input_file = bz2.BZ2File(filename, 'rb')
            os.chdir('/Users/macuser/Documents/Stanford Research/Lazer - Tragedy of the Network/')
            ## os.chdir('/afs/ir.stanford.edu/users/c/j/cjgomez/Lazer_Tragedy_of_the_Networks/')
            return [double(line.replace('\n','')) for line in input_file]

    def return_TSP_problem_space(self):    
            #a = np.zeros(shape=(20,20))
            #for i in range(20):
            #    for j in range(i):
            #        a[i][j] = round(uniform(0, 100), 6)
            #b = a + a.T - np.diag(a.diagonal())
            #self.TSP_space = b.tolist()
            
            os.chdir('/Users/macuser/Documents/Stanford Research/Lazer - Tragedy of the Network/TSP_Spaces')
            #os.chdir('/afs/ir.stanford.edu/users/c/j/cjgomez/Lazer_Tragedy_of_the_Networks/TSP_Spaces')
            filename = "TSP_Space_"+str(self.simulation_number)+".txt"
            TSP_space = loadtxt(filename,delimiter=" ",unpack=False)
            os.chdir('/Users/macuser/Documents/Stanford Research/Lazer - Tragedy of the Network/')
            #os.chdir('/afs/ir.stanford.edu/users/c/j/cjgomez/Lazer_Tragedy_of_the_Networks/')
            
            TSP_space = TSP_space.tolist()
            return TSP_space
    
