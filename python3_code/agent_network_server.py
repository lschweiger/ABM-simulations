# network.py
import random


class create_network(object):
        
    def __init__(self,type_of_network,single_agent):
         self.type_of_network = type_of_network 
         self.single_agent = single_agent
         self.population = 100
     
    def return_network(self):
        if self.type_of_network == "linear": # wont use
            return [[(i-1)%self.population,(i+1)%self.population] for i in range(self.population)]
        if self.type_of_network == "fully connected": # wont use
            return [[j for j in range(self.population) if j!=i] for i in range(self.population)]
        if self.type_of_network == "torus": 
            return [[(i-2)%self.population,(i-1)%self.population,(i+1)%self.population,(i+2)%self.population] for i in range(self.population)]
        if self.type_of_network == "torus_w_error": 
            return [[(i-2)%self.population,(i-1)%self.population,(i+1)%self.population,(i+2)%self.population] for i in range(self.population)]
        if self.type_of_network == "single fully connected agent on torus":
            # single_agent (one agent between 0 and 99 inclusive) is the agent who is fully connected to everyone else, but everyone else is not connected to single_agent. 
            single_agent_torus = [[(i-2)%self.population,(i-1)%self.population,(i+1)%self.population,(i+2)%self.population] for i in range(self.population)]
            single_agent_torus[self.single_agent] = [j for j in range(self.population) if j!=self.single_agent]
            return single_agent_torus
        if self.type_of_network == "single fast communicator agent on torus":
            return [[(i-2)%self.population,(i-1)%self.population,(i+1)%self.population,(i+2)%self.population] for i in range(self.population)]
        if self.type_of_network == "evolving network":
            shuffled_range = random.sample(range(0,self.population),self.population)
            evolving_network = [random.sample(list(range(0,i))+list(range(i+1,self.population)),i+1) for i in range(0,self.population-1)]
            evolving_network[0] = [int(round(random.random()*(self.population-1)))+1]
            while evolving_network[0] == [100]:
                evolving_network[0] = [int(round(random.random()*(self.population-1)))+1]
            temp=list(range(self.population-1))
            random.shuffle(temp)
            evolving_network.append(temp)
            random.shuffle(evolving_network)
            # for agent_i in range(self.population):
            #     for link in range(len(evolving_network[agent_i])):
            #         # Check to see if there are any duplicate links
            #         if len(evolving_network[agent_i])!=len(set(evolving_network[agent_i])):
            #             length = len(evolving_network[agent_i])
            #             evolving_network[agent_i] = list(set(evolving_network[agent_i]))
            #             while len(evolving_network[agent_i]) < length:
            #                 evolving_network[agent_i].append(randint(0,99))
            #         #Remove any self links                            
            #         if evolving_network[agent_i][link] == agent_i:
            #             random_link = randint(0,99)
            #             while random_link == agent_i:
            #                 random_link = randint(0,99)
            #             evolving_network[agent_i][link] = random_link
            return evolving_network
        else:
            print("error") 
 
        
        