from random import uniform
from numpy import average
from numpy import double
import io
import bz2
from shutil import copyfileobj

N = 20
K = 5
number_of_spaces = 1000

for iterations in range(0,number_of_spaces):

    NK_numbers = range(0,2**N)
    #NK_mask = [uniform(0,1) for x in range(0,2**(K+1))] # Example of a mask for one bit (masks are the K nearest neighbors to bit i)
    NK_masks=[[uniform(0,1) for x in range(0,2**(K+1))] for x in range(N)] # Creates a list of lists, each list is of length 2^(K+1) and there are N lists
    NK_values = []

    for r in range(0,2**N):
        binary_number = bin(NK_numbers[r])[2:].zfill(N) #return a binary number between 0 and N
        binary_number_extended = binary_number+binary_number #add the two together in order to get the K nearest neighbors (mask)
        binary_number_value = average([NK_masks[i][int(binary_number_extended[i:i+K+1],2)] for i in range(len(binary_number))])
        NK_values.append((NK_numbers[r],binary_number_value))

    maximum_value = max(NK_values,key=lambda item:item[1])[1]
    scores = [k/maximum_value for j,k in NK_values]

    f = open("NK_space_scores.nk", "w")
    f.writelines(["%s\n" % item  for item in scores]) #each number gets its own file
    f.close()

    with open('NK_space_scores.nk', 'rb') as input:
        filename = 'NK_space_scores_' + str(iterations) + '.bz2'
        with bz2.BZ2File(filename, 'wb', compresslevel=9) as output:
            copyfileobj(input, output)

#To read in nk scores
#from numpy import double
#input_file = bz2.BZ2File(filename, 'rb')
#nk_scores = [double(line.replace('\n','')) for line in input_file]

#To run on Stanford Corn cluster, qsub -cwd batch.sh
#To activate sh file, chmod +x dir.sh
#To check on cluster, qstat / delete jobs, qdel / 