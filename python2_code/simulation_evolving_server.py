# simulation_evolving_server.py
import os
import problem_space_server as ps
import agent_server as a
import agent_network_server as net
from random import randint
from numpy import average
import itertools
from itertools import chain
import sys 
from random import shuffle
from random import uniform 
from numpy import mean, std 
from numpy import array
from scipy.stats import mode

import pandas as pd

N = 20
population = 100 #Number of Agents
number_of_rounds = 300
r = 8 #NK Space 

type_of_problem_space = sys.argv[1] #ex - NK or TSP
total_simulations = int(sys.argv[2]) #ex - 1,000 spaces
type_of_simulation = sys.argv[3] # "evolving network" or "evolving communication speed"
if type_of_simulation == "evolving network":
    type_of_network = "evolving network"
    communication_speeds = [1]*population
if type_of_simulation == "evolving communication speed":
    type_of_network = "torus"
    communication_speeds = [i+1 for i in range(10)]*10


final_statistics = []
simulation_statistics = []
round_statistics = []
single_agent_round_statistics = []

global round_one_average_score
global round_one_unique_solutions

agent_rank = []

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
        agent_solution_binary = bin(test_agent_solution)[2:].zfill(N)
        test_agent_solution_binary = agent_solution_binary        
        random_bit = randint(0,len(test_agent_solution_binary)-1)
        changed_bit = str((int(agent_solution_binary[random_bit])+1)%2)
        s = list(test_agent_solution_binary) #turn string into a list 
        s[random_bit] = changed_bit #change the bit
        test_agent_solution_binary = "".join(s) #now change it back to a full string of 1s and 0s
        test_agent_solution = int(test_agent_solution_binary,2)        
        test_agent_score = problemspace[test_agent_solution]
        if test_agent_score > agent_score:
            agents[agent_id].hold_new_solution_and_score_until_next_round(test_agent_solution, test_agent_score)
        else:
            agents[agent_id].hold_new_solution_and_score_until_next_round(agent_solution, agent_score)
    if type_of_problem_space == "TSP":
        test_agent_solution = agent_solution
        random_city_1 = randint(0,len(agent_solution)-1)
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
    final_score = [sum(x)/len(x) for x in itertools.izip(*score)]
    unique_solution = [[z for x,y,z in final_statistics[i]] for i in range(len(final_statistics))]
    final_unique_solution = [sum(x)/len(x) for x in itertools.izip(*unique_solution)]
    final_round = [[x for x,y,z in final_statistics[i]] for i in range(len(final_statistics))][0]
    if type_of_problem_space == "NK":
        print [[final_round[i],final_score[i]**r,final_unique_solution[i]] for i in range(len(final_round))]    
    if type_of_problem_space == "TSP":
        print [[final_round[i],final_score[i],final_unique_solution[i]] for i in range(len(final_round))]    


#Helper function
def new_network_from_roulette_wheel_sample():
    score_sum = 0
    fitness = []
    values = []    
    for i in range(population):
        score_sum += agents[i].current_agent_values()[2] 
        values.append(agents[i].current_agent_values()[2])    
    max_values = max(values)
    min_values = min(values)
        
    if type_of_problem_space == "TSP":
        fitness = [[i,round((min_values/values[i])*1000)] for i in range(population)]        
    if type_of_problem_space == "NK":
        fitness = [[i,round((values[i]/max_values)*1000)] for i in range(population)]        

    new_population = []
        
    #construct the wheel 
    wheel = []
    for j in range(len(fitness)):
        slots = [j]*int(fitness[j][1]) #number of slots to be added to the wheel based on fitness
        wheel.extend(slots)
    
    myRange =  range(0,len(wheel)) 
    shuffle(myRange)
    shuffle(wheel)
    new_population = [ wheel[i] for i in sorted(wheel[:population]) ]    
    new_network = [network[new_population[j]] for j in range(len(new_population))]    
    return new_network     

# Helper function 
def create_new_communication_speeds():
    fitness = []
    values = []    
    
    agent_rank_array = array(agent_rank)
    agent_rank_array_mean = mean(agent_rank_array, axis=0)
    total_agent_rank_array_list = agent_rank_array_mean.tolist()

    min_value = min(total_agent_rank_array_list, key=lambda x : x[1])[1]
    max_value = max(total_agent_rank_array_list, key=lambda x : x[1])[1]

    if type_of_problem_space == "TSP":
        fitness = [[i,round((min_value/total_agent_rank_array_list[i][1])**5*100)] for i in range(population)]        
    if type_of_problem_space == "NK":
        fitness = [[i,round((total_agent_rank_array_list[i][1]/max_value)**5*100)] for i in range(population)]        

    #print fitness
    new_population = []
        
    #construct the wheel 
    wheel = []
    for j in range(len(fitness)):
        slots = [j]*int(fitness[j][1]) #number of slots to be added to the wheel based on fitness
        wheel.extend(slots)
    
    myRange =  range(0,len(wheel)) 
    shuffle(myRange)
    shuffle(wheel)
    new_population = [ wheel[i] for i in sorted(wheel[:population]) ]    
    new_communication_speeds = [communication_speeds[new_population[j]] for j in range(len(new_population))]    
    #for j in range(len(new_population)):
    #    print j, new_communication_speeds[j], agents[j].current_agent_values()[2]

    return new_communication_speeds  


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
    final_score = [sum(x)/len(x) for x in itertools.izip(*score)]
    unique_solution = [[z for x,y,z in final_statistics[i]] for i in range(len(final_statistics))]
    final_unique_solution = [sum(x)/len(x) for x in itertools.izip(*unique_solution)]
    final_round = [[x for x,y,z in final_statistics[i]] for i in range(len(final_statistics))][0]
    if type_of_problem_space == "NK":
        return final_score[len(final_round)]**r
    if type_of_problem_space == "TSP":
        return final_score[len(final_round)] 
 

if type_of_simulation == "evolving communication speed":
    total_simulation_speeds = []

    for average_generational_simulations in range(total_simulations):
        communication_speeds = [i+1 for i in range(10)]*10 #distribute the communication speeds   
        shuffle(communication_speeds)  
        one_simulation_speeds = []
   
        for simulations in range(total_simulations):
                
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
                    solution_number = randint(0,(2**N)-1)
                    agents[i].store_new_solution_and_score(solution_number,problemspace[solution_number])   
            if type_of_problem_space == "TSP":
                for i in range(population):
                    solution_number = [k for k in range(N)]
                    shuffle(solution_number)
                    agents[i].store_new_solution_and_score(solution_number,return_TSP_score(solution_number, problemspace))        
            
            # Step 3 - Each round, compare neighbors and then go to problem space
            rounds = 0
            while len(set([agents[i].current_agent_values()[2] for i in range(population)])) > 1:
                one_round(rounds)
                rounds+=1
            
            # Step 4 - Calculate the new communication speeds 
            communication_speeds = create_new_communication_speeds()
            agent_rank = []
            one_simulation_speeds.append(average(communication_speeds))
            #print simulations, average(communication_speeds), rounds, len(set([agents[i].current_agent_values()[2] for i in range(population)]))

        total_simulation_speeds.append(one_simulation_speeds)
    
    total_simulation_speeds_array = array(total_simulation_speeds)
    total_simulation_speeds_array_mean = mean(total_simulation_speeds_array, axis=0)
    total_simulation_speeds_list = list(total_simulation_speeds_array_mean)
    for i in range(len(total_simulation_speeds_list)):
        print i, total_simulation_speeds_list[i]
        
if type_of_simulation == "evolving network":
    for simulations in range(total_simulations):
        simulation_rounds = 0 
        frequency_of_mode_ = 0
                    
        while frequency_of_mode_ < population:    
            
            # Step 1 - Create the Problem Space, the network, and the agents. 
            if type_of_problem_space == "NK":
                problemspace = ps.create_problem_space(type_of_problem_space,simulations).return_NK_problem_space()
            if type_of_problem_space == "TSP":
    	       problemspace = ps.create_problem_space(type_of_problem_space,simulations).return_TSP_problem_space()
            if simulation_rounds == 0:
                network = net.create_network(type_of_network,single_agent).return_network() #Create the network for the first round
            agents = [a.create_agent(i,type_of_problem_space,N) for i in range(population)]  
    
            # Step 2 - Give each agent their initial solution and initial score
            if type_of_problem_space == "NK":
                for i in range(population):
                    solution_number = randint(0,2**N)
                    agents[i].store_new_solution_and_score(solution_number,problemspace[solution_number])   
            if type_of_problem_space == "TSP":
                for i in range(population):
                    solution_number = [k for k in range(N)]
                    shuffle(solution_number)
                    agents[i].store_new_solution_and_score(solution_number,return_TSP_score(solution_number, problemspace))
        
            # Step 3 - Each simulation/round, compare neighbors and then go to problem space
            calculate_one_round_statistics(simulation_rounds)
            one_round(simulation_rounds)
        
            network = new_network_from_roulette_wheel_sample()
            min_ = min([len(network[i]) for i in range(population)])
            mean_ = mean([len(network[i]) for i in range(population)])
            max_ = max([len(network[i]) for i in range(population)])
            mode_ = mode([len(network[i]) for i in range(population)])
            mode_ = int(mode_[0])
            frequency_of_mode_ = [len(network[i]) for i in range(population)].count(mode_)
            # print simulations, simulation_rounds, min_, mean_, max_, mode_, frequency_of_mode_ 

            simulation_rounds = simulation_rounds + 1


        # LAUNY NOTE: You'll likely need to update the code so that you can output this as a DataFrame
        # And save as a CSV in one fell swoop. 
        print simulations, simulation_rounds, mode_, calculate_final_statistics_of_one_generation()

