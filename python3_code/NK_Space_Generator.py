#from random import uniform
import numpy as np
#import io
#import bz2
#from shutil import copyfileobj
import pickle

def Space_Create(N,K):
    NK_numbers = range(0,2**N)
    #NK_mask = [uniform(0,1) for x in range(0,2**(K+1))] # Example of a mask for one bit (masks are the K nearest neighbors to bit i)
    #NK_masks=[[uniform(0,1) for x in range(0,2**(K+1))] for x in range(N)] # Creates a list of lists, each list is of length 2^(K+1) and there are N lists
    fNK_values = []
    binary_number_value =np.random.normal(0.6,0.08386608516010426,2**N)
    return binary_number_value

N = 20
K = 5
number_of_spaces = 1000

for iterations in range(0,number_of_spaces):

    NK_values=Space_Create(N,K)


    maximum_value = np.max(NK_values)
    scores = (NK_values.tolist()/maximum_value).tolist()

    pickle.dump(scores,open('NK_space_scores_'+str(iterations)+'.pkl',"wb"))
    #f = open("NK_space_scores.nk", "w")
    #f.writelines(["%s\n" % item  for item in scores]) #each number gets its own file
    #f.close()

        
    #with open("NK_space_scores.nk", 'rb') as input:
    #    filename = 'NK_space_scores_' + str(iterations) + '.bz2'
    #    with bz2.BZ2File(filename, 'wb', compresslevel=9) as output:
    #        copyfileobj(input, output)


#To read in nk scores
#from numpy import double
#input_file = bz2.BZ2File(filename, 'rb')
#nk_scores = [double(line.replace('\n','')) for line in input_file]

#To run on Stanford Corn cluster, qsub -cwd batch.sh
#To activate sh file, chmod +x dir.sh
#To check on cluster, qstat / delete jobs, qdel / 