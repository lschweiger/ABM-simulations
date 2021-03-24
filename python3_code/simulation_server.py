# simulation_server.py
#import os
import problem_space_server as ps
import agent_server as a
import agent_network_server as net
#from random import randint
from numpy import std
from numpy import average
from math import sqrt
from numpy import mean
import itertools
from itertools import chain
import sys
from numpy import unique
from random import shuffle
from random import random 
import pandas as pd
import argparse



def check_prob(prob):
    prob = float(prob)
    if prob <0 or prob>1 :
        raise argparse.ArgumentTypeError("%s is an invalid probability value" % prob)
    return prob


parser = argparse.ArgumentParser(description='Paramters for simulation')
parser.add_argument('--TPS', type = str,
                    help = 'type of problem_space',required = True)
parser.add_argument('--Total',type = int,help = 'Total number of spaces to run',required = True)
parser.add_argument('--TN',type = str,required = True,
                    help = "Type of network:  'torus', 'single fully connected agent on torus', or 'single fast communicator agent on torus' or 'torus_w_error'")
parser.add_argument('--IV', type = int,
                    help ='Info Velocity value',required = True)
parser.add_argument('--prob', type = check_prob, default = 0.0)
args=parser.parse_args()


#print(args.prob)
N = 20
population = 100
number_of_rounds = 250
r = 8

type_of_problem_space = args.TPS #ex - NK or TSP
total_simulations = args.Total #ex - 1,000 spaces
type_of_network = args.TN #ex - linear, fully connected, torus, single fully connected agent on torus, or single fast communicator agent on torus
probability=args.prob
global round_one_average_score
global round_one_unique_solutions


# Choose the single fully connected agent in the torus, if applicable. 
if type_of_network == 'single fully connected agent on torus' or type_of_network == 'single fast communicator agent on torus' or "torus_w_error": #upodate with torus error
    single_agent = int(round(random()*(population-1))) # 0 through 99, inclusive
else: 
    single_agent = 99999 # default value means no prop agent



#Helper Functions - TSP
def return_TSP_score(agent_solution,problemspace):
    tsp_score = 0
    for j in range(N):
        tsp_score = tsp_score + problemspace[agent_solution[j]][agent_solution[(j+1)%N]]
    return tsp_score
        
# Helper Functions
#@profile
def explore_space(agent_id,agent_solution,agent_score):
    if type_of_problem_space == "NK":
        test_agent_solution = agent_solution        
        agent_solution_binary = bin(test_agent_solution)[2:].zfill(N) #converts to binary for bit manipulation padded to length N
        test_agent_solution_binary = list(agent_solution_binary) #converts to list to be manipulated         
        random_bit = int(round(random()*(len(test_agent_solution_binary)-1))) #bit manipulation, picks random number in binary sequence
        #changed_bit = str((int(agent_solution_binary[random_bit])+1)%2) #bit man
        #s = list(test_agent_solution_binary) #turn string into a list 
        #if(test_agent_solution_binary[random_bit]=='0'): #flips selected bit
        #    test_agent_solution_binary[random_bit]='1'
        #else:
        #    test_agent_solution_binary[random_bit]='0'
        #s[random_bit] = changed_bit
        test_agent_solution_binary[random_bit]=str((int(test_agent_solution_binary[random_bit])+1)%2)
        test_agent_solution_binary = "".join(test_agent_solution_binary) #convert back to string
        
        try:
            test_agent_solution = int(test_agent_solution_binary,2) # converts back to number        
        except:
            print(test_agent_solution_binary)
        test_agent_score = problemspace[test_agent_solution] # finds score using int version of string
        if test_agent_score > agent_score:
            agents[agent_id].hold_new_solution_and_score_until_next_round(test_agent_solution, test_agent_score)
        else:
            agents[agent_id].hold_new_solution_and_score_until_next_round(agent_solution, agent_score)
    if type_of_problem_space == "TSP":
        test_agent_solution = agent_solution
        random_city_1 = int(round(random()*(len(agent_solution)-1)))
        random_city_2 = (random_city_1+N/2)%N
        #random_city_2 = randint(0,len(agent_solution)-1)
        #while random_city_1 == random_city_2:
        #    random_city_2 = randint(0,len(agent_solution)-1)       
        
        test_agent_solution[random_city_1], test_agent_solution[random_city_2] = test_agent_solution[random_city_2], test_agent_solution[random_city_1]
        test_agent_score = return_TSP_score(test_agent_solution, problemspace)
        if test_agent_score < agent_score:
            agents[agent_id].hold_new_solution_and_score_until_next_round(test_agent_solution, test_agent_score)
        else:
            agents[agent_id].hold_new_solution_and_score_until_next_round(agent_solution, agent_score)
        
# Helper function - Each round, compare neighbors and then go to problem space
#@profile
def one_round(current_round,prob,problem_space):
    for i in range(population): #runs through population
        neighbors = [agents[negh].current_agent_values() for negh in network[i]]
        # if type_of_network != "torus_w_error":
        #     if (current_round%info_velocity==0 or current_round==0):
        #         agents[i].compare_with_neighbors(neighbors)
        #         if agents[i].should_agent_explore(): 
        #             explore_space(*agents[i].current_agent_values())
        #     else:
        #         explore_space(*agents[i].current_agent_values())
        #if type_of_network == "single fast communicator agent on torus" or type_of_network == 'single fully connected agent on torus' or type_of_network == 'torus_w_error': #added 2 more types single full and torus with error
        if (current_round%info_velocity == 0 or current_round == 0 or i==single_agent): # update with single no error and torus
            if(i==single_agent or type_of_network != 'torus_w_error'):
                agents[i].compare_with_neighbors(neighbors)
            elif(type_of_network == 'torus_w_error' and i!=single_agent):
                #print("inside")
                agents[i].compare_with_neighbors_with_error(neighbors,prob,problem_space)
            if agents[i].should_agent_explore(): # will run if the above failed to find better solutions
                explore_space(*agents[i].current_agent_values())
        else:
            explore_space(*agents[i].current_agent_values())    
    for i in range(population):
        agents[i].adopt_solutions_for_next_round()
    

# Helper function 
def calculate_one_round_statistics(rounds):
    if type_of_problem_space == "NK":
        values = [rounds, average([agents[i].current_agent_values()[2] for i in range(population)]), len(set([agents[i].current_agent_values()[1] for i in range(population)]))]
    if type_of_problem_space == "TSP":
        values = [rounds, average([agents[i].current_agent_values()[2] for i in range(population)]), len(set([agents[i].current_agent_values()[2] for i in range(population)]))]
    round_statistics.append(values) #global
    if type_of_network == 'single fully connected agent on torus' or type_of_network == 'single fast communicator agent on torus' or type_of_network == 'torus_w_error':
        single_agent_values =  [rounds, agents[single_agent].current_agent_values()[2]]
        single_agent_round_statistics.append(single_agent_values)


if(probability>0):
        info_velocity=1
else:
    info_velocity = args.IV #ex - 1 (every turn), 2 (every two turns, communicatioon allowed), 5 (every fifth turn, communication allowed), or 10
# Reduce communication to every tenth round if "single fast communiator agent on torus"
#if type_of_network == 'single fast communicator agent on torus':
#    info_velocity = 10
if(info_velocity==1 or info_velocity==2):
    number_of_rounds=100
if(info_velocity==5):
    number_of_rounds=250
if(info_velocity==10):
    number_of_rounds=350
if(type_of_network=='torus_w_error'):
    number_of_rounds=500
print(info_velocity,probability)
final_statistics = []
simulation_statistics = []
round_statistics = []
single_agent_round_statistics = []

for simulations in range(total_simulations):   #setups network and agents 
    # Step 1 - Create the Problem Space, the network, and the agents. 
    if type_of_problem_space == "NK":
        problemspace = ps.create_problem_space(type_of_problem_space,simulations).return_NK_problem_space() #loads NK space file
    if type_of_problem_space == "TSP":
        problemspace = ps.create_problem_space(type_of_problem_space,simulations).return_TSP_problem_space()
    network = net.create_network(type_of_network,single_agent).return_network() #creates network with propities
    agents = [a.create_agent(i,type_of_problem_space,N) for i in range(population)]  #creates agents

    # Step 2 - Give each agent their initial solution and initial score
    if type_of_problem_space == "NK":
        for i in range(population):
            solution_number = int(round(random()*(2**N)-1))
            agents[i].store_new_solution_and_score(solution_number,problemspace[solution_number])   
    if type_of_problem_space == "TSP":
        for i in range(population):
            solution_number = [k for k in range(N)]
            shuffle(solution_number)
            agents[i].store_new_solution_and_score(solution_number,return_TSP_score(solution_number, problemspace))

    # Step 3 - Each round, compare neighbors and then go to problem space
    for rounds in range(number_of_rounds): #runs a full simultations
        calculate_one_round_statistics(rounds)
        one_round(rounds,probability,problemspace)

############################
#### Main Function That Calculates Statistics 
############################
final_statistics = []
for j in range(0, len(round_statistics), number_of_rounds):
    final_statistics.append(round_statistics[j:j+number_of_rounds])
score = [[y for x,y,z in final_statistics[i]] for i in range(len(final_statistics))]
final_score = [sum(x)/len(x) for x in zip(*score)]
final_score_sem = [std(x)/sqrt(len(x)) for x in zip(*score)]
unique_solution = [[z for x,y,z in final_statistics[i]] for i in range(len(final_statistics))]
final_unique_solution = [sum(x)/len(x) for x in zip(*unique_solution)]
final_round = [[x for x,y,z in final_statistics[i]] for i in range(len(final_statistics))][0]
if type_of_problem_space == "NK":
    #NK_final_list=[]
    #for i in range(len(final_round)):
    #    NK_final_list.append([final_round[i],final_score[i]**r,final_unique_solution[i]])
    NK_final_list = [[a,b,c,d ] for a,b,c,d in zip(final_round,final_score,final_unique_solution,final_score_sem)]
    NK = pd.DataFrame(data=NK_final_list,columns=["round","final Score","final unique solution","SEM"])
    NK.to_csv("NK_"+type_of_network+"_P"+str(probability)+"_V"+str(info_velocity)+".csv",index=False)
if type_of_problem_space == "TSP":
    #TSP_final_list=[]
    #for i in range(len(final_round)):
    #    TSP_final_list.append([final_round[i],final_score[i],final_unique_solution[i]])
    TSP_final_list = [[a,b,c,d] for a,b,c,d in zip(final_round,final_score,final_unique_solution,final_score_sem)]
    TSP=pd.DataFrame(data=TSP_final_list,columns=["round","final Score","final unique solution","SEM"])   
    TSP.to_csv("TSP_"+type_of_network+"_P"+str(probability)+"_V"+str(info_velocity)+".csv",index=False)
if type_of_network == 'single fully connected agent on torus' or type_of_network == 'single fast communicator agent on torus'or type_of_network == 'torus_w_error':
    single_agent_final_statistics = []
    for j in range(0, len(single_agent_round_statistics), number_of_rounds):
        single_agent_final_statistics.append(single_agent_round_statistics[j:j+number_of_rounds])
    single_agent_score = [[y for x,y in single_agent_final_statistics[i]] for i in range(len(single_agent_final_statistics))]    
    single_agent_final_score = [sum(x)/len(x) for x in zip(*single_agent_score)]
    single_agent_final_score_sem = [std(x)/sqrt(len(x)) for x in zip(*single_agent_score)]
    single_agent_final_round = [[x for x,y in single_agent_final_statistics[i]] for i in range(len(single_agent_final_statistics))][0]
    
     
    if type_of_problem_space == "NK":
        #single_final_list=[]
        #for i in range(len(final_round)):
        #    single_final_list.append([single_agent_final_round[i], single_agent_final_score[i]**r,single_agent_final__score_sem])
        single_final_list = [[a,b,c] for a,b,c in zip(single_agent_final_round, single_agent_final_score,single_agent_final_score_sem) ]
        Single_final=pd.DataFrame(data=single_final_list,columns=["round","final Score","SEM"])
        Single_final.to_csv("Singleagent_NK"+type_of_network+"_P"+str(probability)+"_V"+str(info_velocity)+".csv",index=False)
    if type_of_problem_space == "TSP":
        
        #for i in range(len(final_round)):
        #    single_final_list.append([single_agent_final_round[i], single_agent_final_score[i],single_agent_final__score_sem])
        single_final_list = [[a,b,c] for a,b,c in zip(single_agent_final_round, single_agent_final_score,single_agent_final_score_sem) ]
        Single_final=pd.DataFrame(data=single_final_list,columns=["round","final Score","SEM"])
        Single_final.to_csv("Singleagent_TSP"+type_of_network+"_P"+str(probability)+"_V"+str(info_velocity)+".csv",index=False)

