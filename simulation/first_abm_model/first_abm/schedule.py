from collections import defaultdict
from mesa.time import RandomActivation


class ActivationByType(RandomActivation):
    """A scheduler which activates each type of agent once per step.
    Assumes that all agents have a step() method.
    
    """

    def __init__(self, model):
        super().__init__(model)
        self.agents_by_type = defaultdict(dict)

    def add(self, agent):
        """Add an Agent object to the schedule
        
        Args:
            agent: An Agent to be added to the schedule.
        
        """

        self._agents[agent.unique_id] = agent
        agent_type = agent.__class__.__name__
        if agent_type in ['Investor', 
                          'Contributor', 
                          'VerificationSponsor',
                          'CharitableSponsor']: agent_type = 'Customer'
        self.agents_by_type[agent_type][agent.unique_id] = agent

    def remove(self, agent):
        """Remove all instances of a given agent from the schedule.
        
        """
        del self._agents[agent.unique_id]

        agent_type = self.__class__.__name__
        del self.agents_by_type['Customer'][agent.unique_id]

    def step(self):
        """Executes the step of each agent type, one at a time.
        
        """
        for agent_type in ['Customer', 'Teo']:
            self.step_type(agent_type)
        self.steps += 1
        self.time += 1


    def step_type(self, type):
        """Run all agents of a given type.
        
        Args:
            type: Class name of the type to run.
            
        """
        for agent_key in list(self.agents_by_type[type].keys()):
            self.agents_by_type[type][agent_key].step()
