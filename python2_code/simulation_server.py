# simulation_server.py
import os
#os.chdir("/Users/macuser/Documents/Stanford Research/Lazer - Tragedy of the Network/Python_Scripts_for_Server")
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

N = 20
population = 100
number_of_rounds = 300
r = 8

type_of_problem_space = sys.argv[1] #ex - NK or TSP
total_simulations = int(sys.argv[2]) #ex - 1,000 spaces
type_of_network = sys.argv[3] #ex - linear, fully connected, torus, single fully connected agent on torus, or single fast communicator agent on torus
info_velocity = int(sys.argv[4]) #ex - 1 (every turn), 2 (every two turns, communicatioon allowed), 5 (every fifth turn, communication allowed), or 10


final_statistics = []
simulation_statistics = []
round_statistics = []
single_agent_round_statistics = []

global round_one_average_score
global round_one_unique_solutions


# Choose the single fully connected agent in the torus, if applicable. 
if type_of_network == 'single fully connected agent on torus' or type_of_network == 'single fast communicator agent on torus':
    single_agent = randint(0,99) # 0 through 99, inclusive
else: 
    single_agent = 99999 # default value 

# Reduce communication to every tenth round if "single fast communiator agent on torus"
if type_of_network == 'single fast communicator agent on torus':
    info_velocity = 10 # 0 through 99, inclusive

#Helper Functions - TSP
def return_TSP_score(agent_solution,problemspace):
    tsp_score = 0
    for j in range(N):
        tsp_score = tsp_score + problemspace[agent_solution[j]][agent_solution[(j+1)%N]]
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
        #print current_round, i, agents[i].current_agent_values()[2]
        neighbors = [agents[negh].current_agent_values() for negh in network[i]]
        if type_of_network != "single fast communicator agent on torus":
            if current_round%info_velocity==0 or current_round==0:
                agents[i].compare_with_neighbors(neighbors)
                if agents[i].should_agent_explore(): 
                    explore_space(*agents[i].current_agent_values())
            else:
                explore_space(*agents[i].current_agent_values())
        if type_of_network == "single fast communicator agent on torus":
            if (current_round%info_velocity==0 or current_round == 0) or i==single_agent:
                agents[i].compare_with_neighbors(neighbors)
                if agents[i].should_agent_explore(): 
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
    round_statistics.append(values)
    if type_of_network == 'single fully connected agent on torus' or type_of_network == 'single fast communicator agent on torus':
        single_agent_values =  [rounds, agents[single_agent].current_agent_values()[2]]
        single_agent_round_statistics.append(single_agent_values)

               
for simulations in range(total_simulations):    
    # Step 1 - Create the Problem Space, the network, and the agents. 
    if type_of_problem_space == "NK":
        problemspace = ps.create_problem_space(type_of_problem_space,simulations).return_NK_problem_space()
    if type_of_problem_space == "TSP":
        problemspace = ps.create_problem_space(type_of_problem_space,simulations).return_TSP_problem_space()
    network = net.create_network(type_of_network,single_agent).return_network()
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

    # Step 3 - Each round, compare neighbors and then go to problem space
    for rounds in range(number_of_rounds):
        calculate_one_round_statistics(rounds)
        one_round(rounds)

############################
#### Main Function That Calculates Statistics 
############################
final_statistics = []
for j in range(0, len(round_statistics), number_of_rounds):
    final_statistics.append(round_statistics[j:j+number_of_rounds])
score = [[y for x,y,z in final_statistics[i]] for i in range(len(final_statistics))]
final_score = [sum(x)/len(x) for x in itertools.izip(*score)]
unique_solution = [[z for x,y,z in final_statistics[i]] for i in range(len(final_statistics))]
final_unique_solution = [sum(x)/len(x) for x in itertools.izip(*unique_solution)]
final_round = [[x for x,y,z in final_statistics[i]] for i in range(len(final_statistics))][0]
if type_of_problem_space == "NK":
    for i in range(len(final_round)):
        print final_round[i],final_score[i]**r,final_unique_solution[i]
if type_of_problem_space == "TSP":
    for i in range(len(final_round)):
        print final_round[i],final_score[i],final_unique_solution[i]   

if type_of_network == 'single fully connected agent on torus' or type_of_network == 'single fast communicator agent on torus':
    single_agent_final_statistics = []
    for j in range(0, len(single_agent_round_statistics), number_of_rounds):
        single_agent_final_statistics.append(single_agent_round_statistics[j:j+number_of_rounds])
    single_agent_score = [[y for x,y in single_agent_final_statistics[i]] for i in range(len(single_agent_final_statistics))]    
    single_agent_final_score = [sum(x)/len(x) for x in itertools.izip(*single_agent_score)]
    single_agent_final_round = [[x for x,y in single_agent_final_statistics[i]] for i in range(len(single_agent_final_statistics))][0]
    
    # LAUNY NOTE: You'll likely need to update the code so that you can output this as a DataFrame
    # And save as a CSV. 
    if type_of_problem_space == "NK":
        print "\t"
        for i in range(len(final_round)):
            print single_agent_final_round[i], single_agent_final_score[i]**r 
    if type_of_problem_space == "TSP":
        print "\t"
        for i in range(len(final_round)):
            print single_agent_final_round[i], single_agent_final_score[i]