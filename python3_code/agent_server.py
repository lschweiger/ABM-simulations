#from random import randint
import problem_space_server

class create_agent(object):
    
                      
    def __init__(self,agent_id,agent_space_parameters,N):
         self.agent_id = agent_id
         self.agent_space_parameters = agent_space_parameters
         self.N = N
         self.agent_should_explore = False
         self.temporarily_hold_agent_solution = 999999
         self.temporarily_hold_agent_score = 99999

        
    def store_new_solution_and_score(self,new_agent_solution,new_agent_score):
        self.agent_solution = new_agent_solution         
        self.agent_score = new_agent_score
        
    def hold_new_solution_and_score_until_next_round(self,new_agent_solution,new_agent_score):
        self.temporarily_hold_agent_solution = new_agent_solution         
        self.temporarily_hold_agent_score = new_agent_score
        #print self.temporarily_hold_agent_solution, new_agent_solution, self.agent_should_explore
        
    def current_agent_temporaroy_values(self):
        return [self.temporarily_hold_agent_solution,self.temporarily_hold_agent_score]
                   
    def current_agent_values(self):
        return [self.agent_id,self.agent_solution,self.agent_score]     
     
    def should_agent_explore(self):
        return self.agent_should_explore
    
    def adopt_solutions_for_next_round(self):
        temp_values = self.current_agent_temporaroy_values()
        self.agent_should_explore = False
        self.agent_solution = temp_values[0]        
        self.agent_score = temp_values[1]

    def compare_with_neighbors(self,neighbor_ids_solutions_scores):
        if self.agent_space_parameters == "NK":
            best_maximum_score = max([c for a,b,c in neighbor_ids_solutions_scores])
            best_maximum_solution = [b for a,b,c in neighbor_ids_solutions_scores if c==best_maximum_score][0]
            self.hold_new_solution_and_score_until_next_round(best_maximum_solution,best_maximum_score)     
            if best_maximum_score > self.agent_score:
                self.hold_new_solution_and_score_until_next_round(best_maximum_solution,best_maximum_score)
            else:
                self.agent_should_explore = True 
        if self.agent_space_parameters == "TSP":
            best_minimum_score = min([c for a,b,c in neighbor_ids_solutions_scores])
            best_minimum_solution = [b for a,b,c in neighbor_ids_solutions_scores if c==best_minimum_score][0]
            self.hold_new_solution_and_score_until_next_round(best_minimum_solution,best_minimum_score)     
            if best_minimum_score < self.agent_score:
                self.hold_new_solution_and_score_until_next_round(best_minimum_solution,best_minimum_score)
            else:
                self.agent_should_explore = True     
