# simulation_evolving_server.py
import os
import problem_space_server as ps
import agent_server as a
import agent_network_server as net
from random import randint
from numpy import average
import sys 
from random import shuffle
from random import uniform 
from numpy import mean, std 
from numpy import array
from scipy.stats import mode
from random import random
from random import uniform 
import pandas as pd
import argparse
N = 20
population = 100 #Number of Agents
number_of_rounds = 300
r = 8 #NK Space 

parser = argparse.ArgumentParser(description='Paramters for simulation')
parser.add_argument('--TPS', type = str,
                    help = 'type of problem_space NK or TSP',required = True)
parser.add_argument('--Total',type = int,help = 'Total number of spaces to run',required = True)
parser.add_argument('--TN',type = str,required = True,
                    help = "Type of network:  'evolving network', 'evolving communication speed', or 'evolving error '")
args=parser.parse_args()

type_of_problem_space=args.TPS
type_of_simulation=args.TN
total_simulations=args.Total
if type_of_simulation == "evolving network":
    type_of_network = "evolving network"
    communication_speeds = [1]*population
if type_of_simulation == "evolving communication speed":
    type_of_network = "torus"
    communication_speeds = [i+1 for i in range(10)]*10
if(type_of_simulation=="evolving error"):
    type_of_network = "torus"
final_statistics = []
simulation_statistics = []
round_statistics = []
single_agent_round_statistics = []

global round_one_average_score
global round_one_unique_solutions

agent_rank = [] #

single_agent = 99999 # default value 


#Helper Functions - TSP
def return_TSP_score(agent_solution,problemspace):
    tsp_score = 0
    for j in range(20):
        tsp_score = tsp_score + problemspace[agent_solution[j]][agent_solution[(j+1)%20]]
    return tsp_score
        
# Helper Functions
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
        try:
            test_agent_solution_binary[random_bit]=str(int((int(test_agent_solution_binary[random_bit])+1)%2))
        except:
            print(test_agent_solution_binary[random_bit]," ",test_agent_solution_binary)
        test_agent_solution_binary = "".join(test_agent_solution_binary) #convert back to string
        
        try:
            test_agent_solution = int(test_agent_solution_binary,2) # converts back to number        
        except:
            adding1=int(round(random()*(len(test_agent_solution_binary)-1)))%2
            adding2=int(round(random()*(len(test_agent_solution_binary)-1)))%2
            final_add=str(adding1)+str(adding2)
            test_agent_solution=int(test_agent_solution_binary[:-2]+final_add,2)
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
def one_round(current_round):
    for i in range(population):
        neighbors = [agents[negh].current_agent_values() for negh in network[i]]
        if current_round%communication_speeds[i]==0 or current_round==0:         
            agents[i].compare_with_neighbors(neighbors)
            if agents[i].should_agent_explore():
                explore_space(*agents[i].current_agent_values())    
        else:
            explore_space(*agents[i].current_agent_values())    
    for i in range(population):
        agents[i].adopt_solutions_for_next_round()
    
    agent_rank_values_one_simulation = rank_and_sort_agent_values()
    agent_rank.append(agent_rank_values_one_simulation)

def one_round_com(current_round, agents,com_speed):
    for i in range(len(com_speed)):
        if((current_round+1)%com_speed[i]==0):
            neighbors = [agents[negh].current_agent_values() for negh in network[i]]
            if (current_round+1)%com_speed[i]==0 or current_round==0:        
                agents[i].compare_with_neighbors(neighbors)
                #agents[i].avgscore = agents[i].avgscore+((agents[i].agent_score-agents[i].avgscore)/(current_round+1))
                if agents[i].should_agent_explore():
                    explore_space(*agents[i].current_agent_values())    
            else:
                explore_space(*agents[i].current_agent_values())    
    for i in range(population):
        agents[i].adopt_solutions_for_next_round()

def one_round_error(current_round, agents,error_rate,problem_space):
    for i in range(len(error_rate)):
            neighbors = [agents[negh].current_agent_values() for negh in network[i]]       
            agents[i].compare_with_neighbors_with_error(neighbors,error_rate[i],problem_space)
            if agents[i].should_agent_explore():
                explore_space(*agents[i].current_agent_values())  
    for i in range(population):
        agents[i].adopt_solutions_for_next_round()
    
    agent_rank_values_one_simulation = rank_and_sort_agent_values()
    agent_rank.append(agent_rank_values_one_simulation)
# Helper function
def rank_and_sort_agent_values():
   t1 = [agents[i].current_agent_values()[2] for i in range(population)]
   t2 = [[i,t1[i]] for i in range(population)]
   t3 = sorted(t2, key=lambda x: x[0])
   return t3     
    
# Helper function 
def calculate_one_round_statistics(rounds):
    if type_of_problem_space == "NK":
        values = [rounds, average([agents[i].current_agent_values()[2] for i in range(population)]), len(set([agents[i].current_agent_values()[1] for i in range(population)]))]
    if type_of_problem_space == "TSP":
        values = [rounds, average([agents[i].current_agent_values()[2] for i in range(population)]), len(set([agents[i].current_agent_values()[2] for i in range(population)]))]
    round_statistics.append(values)
                    
# Helper function
def calculate_final_statistics():
    final_statistics = []
    for j in range(0, len(round_statistics), number_of_rounds):
        final_statistics.append(round_statistics[j:j+number_of_rounds])
    score = [[y for x,y,z in final_statistics[i]] for i in range(len(final_statistics))]
    final_score = [sum(x)/len(x) for x in zip(*score)]
    unique_solution = [[z for x,y,z in final_statistics[i]] for i in range(len(final_statistics))]
    final_unique_solution = [sum(x)/len(x) for x in zip(*unique_solution)]
    final_round = [[x for x,y,z in final_statistics[i]] for i in range(len(final_statistics))][0]
    if type_of_problem_space == "NK":
        print([[final_round[i],final_score[i]**r,final_unique_solution[i]] for i in range(len(final_round))])   
    if type_of_problem_space == "TSP":
        print([[final_round[i],final_score[i],final_unique_solution[i]] for i in range(len(final_round))])


#Helper function
def new_network_connection_from_roulette_wheel_sample(agents,network): # rewrite connection
    score_sum = 0
    fitness = []
    values = []    
    for i in range(population):
        score_sum += agents[i].current_agent_values()[2] 
        values.append(agents[i].current_agent_values()[2])    
    max_values = max(values)
    min_values = min(values)
    rel_fit=[agents[i].current_agent_values()[2]/score_sum for i in range(population)]
    probs = [sum(rel_fit[:i+1]) for i in range(len(rel_fit))] 
    new_network =[]
    for n in range(population):
        r = random()
        for i in range(population):
            if r <= probs[i]:
                new_network.append(network[i])
                break
    #new_network=[network[wheel[int(round(random()*(leng)-1))]] for i in range(population)]
    #print("len",len(new_network))
    return new_network     

# Helper function 
def create_new_communication_speeds(agents,com_speed):
    score_sum = 0
    fitness = []
    values = []    
    for i in range(population):
        score_sum += agents[i].current_agent_values()[2] 
        values.append(agents[i].current_agent_values()[2])    
    max_values = max(values)
    min_values = min(values)
    rel_fit=[agents[i].current_agent_values()[2]/score_sum for i in range(population)]
    probs = [sum(rel_fit[:i+1]) for i in range(len(rel_fit))] 
    new_communication_speeds =[]
    for n in range(population):
        r = random()
        for i in range(population):
            if r <= probs[i]:
                new_communication_speeds.append(com_speed[i])
                break

    return new_communication_speeds

def create_new_error_rates(agents,com_speed):
    score_sum = 0
    fitness = []
    values = []    
    for i in range(population):
        score_sum += agents[i].current_agent_values()[2] 
        values.append(agents[i].current_agent_values()[2])    
    max_values = max(values)
    min_values = min(values)
    rel_fit=[agents[i].current_agent_values()[2]/score_sum for i in range(population)]
    probs = [sum(rel_fit[:i+1]) for i in range(len(rel_fit))] 
    new_error_rates =[]
    for n in range(population):
        r = random()
        for i in range(population):
            if r <= probs[i]:
                new_error_rates.append(com_speed[i])
                break

    return new_error_rates   


# Helper function 
def calculate_one_round_statistics_for_communication(rounds):
    if type_of_problem_space == "NK":
        values = [rounds, average([agents[i].current_agent_values()[2] for i in range(population)]), len(set([agents[i].current_agent_values()[1] for i in range(population)]))]
    if type_of_problem_space == "TSP":
        values = [rounds, average([agents[i].current_agent_values()[2] for i in range(population)]), len(set([agents[i].current_agent_values()[2] for i in range(population)]))]
    round_statistics.append(values)

# Helper function
def calculate_final_statistics_of_one_generation():
    final_statistics = []
    for j in range(0, len(round_statistics), number_of_rounds):
        final_statistics.append(round_statistics[j:j+number_of_rounds])
    score = [[y for x,y,z in final_statistics[i]] for i in range(len(final_statistics))]
    final_score = [sum(x)/len(x) for x in zip(*score)]
    unique_solution = [[z for x,y,z in final_statistics[i]] for i in range(len(final_statistics))]
    final_unique_solution = [sum(x)/len(x) for x in zip(*unique_solution)]
    final_round = [[x for x,y,z in final_statistics[i]] for i in range(len(final_statistics))][0]
    if type_of_problem_space == "NK":
        return final_score[-1]
    if type_of_problem_space == "TSP":
        return final_score[-1] 

def calculate_final_statistics_of_one_generation_com(number_of_rounds):
    final_statistics = []
    for j in range(0, len(round_statistics), number_of_rounds):
        final_statistics.append(round_statistics[j:j+number_of_rounds])
    score = [[y for x,y,z in final_statistics[i]] for i in range(len(final_statistics))]
    final_score = [sum(x)/len(x) for x in zip(*score)]
    unique_solution = [[z for x,y,z in final_statistics[i]] for i in range(len(final_statistics))]
    final_unique_solution = [sum(x)/len(x) for x in zip(*unique_solution)]
    final_round = [[x for x,y,z in final_statistics[i]] for i in range(len(final_statistics))][0]
    if type_of_problem_space == "NK":
        return final_score[-1]
    if type_of_problem_space == "TSP":
        return final_score[-1] 
 
# needs to finished and update, to include com speeds, roulette wheel,
if type_of_simulation == "evolving communication speed":
    total_simulation_speeds = []
    score=[]
    collection=[]

    for simulations in range(total_simulations):
        communication_speeds = [i+1 for i in range(5)]*20 #distribute the communication speeds 
        #communication_speeds=[int(i) for x in range(20)  for i in [1,2,5,10,20]]
        one_simulation_speeds = []   
        shuffle(communication_speeds)  
        collection_min=[]
        collection_max=[]
        collection_mode=[]  
        # Step 1 - Create the Problem Space, the network, and the agents. 
        if type_of_problem_space == "NK":
            problemspace = ps.create_problem_space(type_of_problem_space,simulations).return_NK_problem_space()
        if type_of_problem_space == "TSP":
            problemspace = ps.create_problem_space(type_of_problem_space,simulations).return_TSP_problem_space()
        network = net.create_network(type_of_network,single_agent).return_network() #Create the network for the first round
        agents = [a.create_agent(i,type_of_problem_space,N) for i in range(population)]    

        # Step 2 - Give each agent their initial solution and initial score
        if type_of_problem_space == "NK":
            for i in range(population):
                solution_number = int(round(random()*(2**N)-1))
                agents[i].store_new_solution_and_score(solution_number,problemspace[solution_number])
                agents[i].hold_new_solution_and_score_until_next_round(solution_number,problemspace[solution_number])   
        if type_of_problem_space == "TSP":
            for i in range(population):
                solution_number = [k for k in range(N)]
                shuffle(solution_number)
                agents[i].store_new_solution_and_score(solution_number,return_TSP_score(solution_number, problemspace))        
        
        # Step 3 - Each round, compare neighbors and then go to problem space
        gen = 0
        while(len(set(communication_speeds))!=1):
            one_round_com(gen,agents,communication_speeds)
            gen+=1
        # Step 4 - Calculate the new communication speeds 
            communication_speeds = create_new_communication_speeds(agents,communication_speeds)
            one_simulation_speeds.append(average(communication_speeds))
            calculate_one_round_statistics_for_communication(gen)
            collection_min.append(min(communication_speeds))
            collection_max.append(max(communication_speeds))
            mode_com = mode(communication_speeds)
            collection_mode.append(int(mode_com[0]))

        score.append(calculate_final_statistics_of_one_generation_com(gen))
        round_statistics=[]
        #agent_rank = []
        #print(communication_speeds)
        #print simulations, average(communication_speeds), rounds, len(set([agents[i].current_agent_values()[2] for i in range(population)]))
        #calculate_final_statistics_of_one_generation()
        total_simulation_speeds.append(one_simulation_speeds)

        collection.append([simulations,gen,total_simulation_speeds[simulations],mean(total_simulation_speeds[simulations]),collection_min,collection_max,collection_mode,total_simulation_speeds[simulations][-1],score[simulations]])
    en_output=pd.DataFrame(data=collection,columns=["simulation #","# of generations","simulation com speed value ","com speed mean","min","max","mode","com speed final value","final score"])
    en_output.to_csv(type_of_simulation+"_"+type_of_network+".csv",index=False)

if type_of_simulation == "evolving network":
    collection=[]
    for simulations in range(total_simulations):
        simulation_rounds = 0 
        frequency_of_mode_ = 0
        if type_of_problem_space == "NK":
            problemspace = ps.create_problem_space(type_of_problem_space,simulations).return_NK_problem_space()
        if type_of_problem_space == "TSP":
            problemspace = ps.create_problem_space(type_of_problem_space,simulations).return_TSP_problem_space()

        while frequency_of_mode_ < population:    
            
            # Step 1 - Create the Problem Space, the network, and the agents. 
            
            if simulation_rounds == 0:
                network = net.create_network(type_of_network,single_agent).return_network() #Create the network for the first round
            agents = [a.create_agent(i,type_of_problem_space,N) for i in range(population)]  
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
        
            # Step 3 - Each simulation/round, compare neighbors and then go to problem space
            calculate_one_round_statistics(simulation_rounds)
            try:
                one_round(simulation_rounds)
            except:
                print(network)
                print("old round", simulation_rounds)
                break
            network = new_network_connection_from_roulette_wheel_sample(agents,network)
            min_ = min([len(network[i]) for i in range(population)])
            mean_ = mean([len(network[i]) for i in range(population)])
            max_ = max([len(network[i]) for i in range(population)])
            mode_ = mode([len(network[i]) for i in range(population)])
            mode_ = int(mode_[0])
            frequency_of_mode_ = [len(network[i]) for i in range(population)].count(mode_)
            #print(simulations, simulation_rounds, min_, mean_, max_, mode_, frequency_of_mode_)

            simulation_rounds = simulation_rounds + 1
            #round_statistics=[]
# third if statment for evoling error 

        # LAUNY NOTE: You'll likely need to update the code so that you can output this as a DataFrame
        # And save as a CSV in one fell swoop. 
        collection.append([simulations, simulation_rounds, mode_, calculate_final_statistics_of_one_generation()])
    en_output=pd.DataFrame(data=collection,columns=["simulation #","simulation_rounds ","mode_","final score"])
    en_output.to_csv(type_of_network+".csv",index=False)

if type_of_simulation == "evolving error":
    total_simulation_speeds = []
    score=[]
    collection=[]

    for simulations in range(total_simulations): 
        error_rate =  [round(10-i/10,4) for i in range(100)]
        one_simulation_speeds = [] 
        collection_min=[]
        collection_max=[]
        collection_mode=[]  
        # Step 1 - Create the Problem Space, the network, and the agents. 
        if type_of_problem_space == "NK":
            problemspace = ps.create_problem_space(type_of_problem_space,simulations).return_NK_problem_space()
        if type_of_problem_space == "TSP":
            problemspace = ps.create_problem_space(type_of_problem_space,simulations).return_TSP_problem_space()
        network = net.create_network(type_of_network,single_agent).return_network() #Create the network for the first round
        agents = [a.create_agent(i,type_of_problem_space,N) for i in range(population)]    

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
        gen = 0
        while(len(set(error_rate))!=1):
            one_round_error(gen,agents,error_rate,problemspace)
            gen+=1
        # Step 4 - Calculate the new communication speeds 
            error_rate = create_new_error_rates(agents,error_rate)
            one_simulation_speeds.append(average(error_rate))
            calculate_one_round_statistics_for_communication(gen)
            collection_min.append(min(error_rate))
            collection_max.append(max(error_rate))
            mode_com = mode(error_rate)
            collection_mode.append(int(mode_com[0]))

        score.append(calculate_final_statistics_of_one_generation_com(gen))
        round_statistics=[]
        #agent_rank = []
        #print simulations, average(error_rate), rounds, len(set([agents[i].current_agent_values()[2] for i in range(population)]))
        #calculate_final_statistics_of_one_generation()
        total_simulation_speeds.append(one_simulation_speeds)

        collection.append([simulations,gen,total_simulation_speeds[simulations],mean(total_simulation_speeds[simulations]),collection_min,collection_max,collection_mode,total_simulation_speeds[simulations][-1],score[simulations]])
    en_output=pd.DataFrame(data=collection,columns=["simulation #","# of generations","simulation com speed value ","error rate mean","min","max","mode","error rate final value","final score"])
    en_output.to_csv(type_of_simulation+"_"+type_of_network+".csv",index=False)