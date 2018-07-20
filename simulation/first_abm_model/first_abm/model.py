import numpy as np
from mesa import Model
from .schedule import ActivationByType
from .datacollection import DataCollector
from time import time
import itertools
import datetime


def get_exchange_reward_per_euro(model):
    """Method that returns the reward per exchanged euro for the current tick.

    Args:
        model (Model): Instance of the model class.
        
    """
    exchanged_euros = get_exchanged_euros(model)
    total_euros = get_total_euros(model) 
    total_teos = get_total_teos(model)
    exchange_pool = (total_euros - total_teos)*model.buffer_share*model.exchange_reward_share
    if exchanged_euros == 0 or exchange_pool <= 0:
        return 0
    exchange_reward_per_euro = exchange_pool / exchanged_euros 
    return round(float(exchange_reward_per_euro),4)


def get_contribution_reward_per_hour(model):
    """Method that returns the reward per contributed hour for the current tick.

    Args:
        model (Model): Instance of the model class.

    """
    contributed_hours = get_total_hours(model)
    total_teos = get_total_teos(model)
    total_euros = get_total_euros(model)
    contribution_pool = (total_euros - total_teos)*(1-model.buffer_share)

    if contributed_hours == 0 or contribution_pool <= 0:
        return 0

    contribution_reward_per_hour = contribution_pool / contributed_hours
    return round(float(contribution_reward_per_hour), 4)

def get_exchanged_euros(model):
    """Method that returns all euros that were exchanged in the current tick.

    Args:
        model (Model): Instance of the model class.

    """
    exchanged_euros = np.sum([v.exchanged_euros for k, v in model.schedule.agents_by_type['Customer'].items()])
    return round(float(np.sum(exchanged_euros)), 2)

def get_total_teos(model):
    """Method that returns all teos in the system at the end of the current tick.

    Args:
        model (Model): Instance of the model class.

    """
    total_teos = [v.teo_wallet for k, v in model.schedule.agents_by_type['Customer'].items()]
    return round(float(np.sum(total_teos)), 2)

def get_total_euros(model):
    """Method that returns all euros in the system at the end of the current tick.

    Args:
        model (Model): Instance of the model class.

    """
    total_euros = [v.euro_wallet for k, v in model.schedule.agents_by_type['Customer'].items()]
    return round(float(np.sum(total_euros)), 2)

def get_total_hours(model):
    """Method that returns all hours that were contributed in the current tick.

    Args:
        model (Model): Instance of the model class.

    """
    total_hours = [v.contributed_hours for k, v in model.schedule.agents_by_type['Customer'].items()]
    return round(float(np.sum(total_hours)), 2)

def get_number_of_agents(model):
    """Method that returns the number of agents in the system.

    Args:
        model (Model): Instance of the model class.

    """

    n_agents = len(model.schedule.agents_by_type['Customer'])
    return n_agents

def get_number_of_contributors(model):
    """Method that returns the number of contributors in the system.

    Args:
        model (Model): Instance of the model class.

    """
    n_agents = len([k for k, v in model.schedule.agents_by_type['Customer'].items() if v.__class__.__name__ == 'Contributor'])
    return n_agents

def get_number_of_ver_sponsors(model):
    """Method that returns the number of verification sponsors in the system.

    Args:
        model (Model): Instance of the model class.

    """
    n_agents = len([k for k, v in model.schedule.agents_by_type['Customer'].items() if v.__class__.__name__ == 'VerificationSponsor'])
    return n_agents

def get_number_of_char_sponsors(model):
    """Method that returns the number of charitable sponsors in the system.

    Args:
        model (Model): Instance of the model class.

    """
    n_agents = len([k for k, v in model.schedule.agents_by_type['Customer'].items() if v.__class__.__name__ == 'CharitableSponsor'])
    return n_agents

def get_number_of_investors(model):
    """Method that returns the number of investors in the system.

    Args:
        model (Model): Instance of the model class.

    """
    n_agents = len([k for k, v in model.schedule.agents_by_type['Customer'].items() if v.__class__.__name__ == 'Investor'])
    return n_agents


from .agents import Contributor, VerificationSponsor, CharitableSponsor, Investor, Teo

class TeoModel(Model):
    """A model simulating the TEO mechanics.
    """

    def __init__(self, n_contributors, n_char_sponsors, n_ver_sponsors, n_investors,
        buffer_share, exchange_reward_share, new_user_growth, churn_prob, months_with_growth,
        store_data):

        """Initializes a new TEO model with a certain number of agents of each type.
               
        Args:
            n_contributors (int): Number of contributors.
            n_char_sponsors (int): Number of charitable sponsors.
            n_ver_sponsors (int): Number of verification sponsors.
            n_investors (int): Number of contributors.
            buffer_share (float): Buffer size in % of euro pool.
            exchange_reward_share (float): Share of buffer for rewarding transactions.
            new_user_growth (float): Growth of new users in %.
            churn_prob (float): Probability to churn.
            months_with_growth (int): Number of months until new users=churn.
            store_data (bool): True if datacollector output should be stored.


        """
        self.step_id = 0
        self.n_contributors = n_contributors
        self.n_char_sponsors = n_char_sponsors
        self.n_ver_sponsors = n_ver_sponsors
        self.n_investors = n_investors
        self.buffer_share = buffer_share/100
        self.exchange_reward_share = exchange_reward_share/100
        self.new_user_growth = new_user_growth/100
        self.churn_prob = churn_prob/100
        self.months_with_growth = months_with_growth
        self.store_data = store_data
        self.init_datetime = datetime.datetime.now()
        self.schedule = ActivationByType(self)
        self.datacollector = DataCollector(model_reporters={
                                              "Total Euros": get_total_euros,
                                              "Total Teos": get_total_teos,
                                              "Contributed Hours": get_total_hours,
                                              "Reward per Contrib Hour": get_contribution_reward_per_hour,
                                              "Reward per Exchanged Euro": get_exchange_reward_per_euro,
                                              "Number of Agents": get_number_of_agents,
                                              "Number of Investors": get_number_of_investors,
                                              "Number of Contributors": get_number_of_contributors,
                                              "Number of Charitable Sponsors": get_number_of_char_sponsors,
                                              "Number of Verification Sponsors": get_number_of_ver_sponsors
                                          },
                                          agent_reporters={
                                              "Euro Wallet": lambda a: a.euro_wallet,
                                              "Teo Wallet": lambda a: a.teo_wallet,
                                              "Contribution Surplus": lambda a: a.contribution_surplus,
                                              "Exchange Surplus": lambda a: a.exchange_surplus,     
                                              "Registered Sponsored Teos": lambda a: a.sponsor_intent,
                                              "Registered Exchange Teos": lambda a: a.teo_exchange_intent,
                                              "Exchanged Teos": lambda a: a.exchanged_teos,
                                              "Registered Exchange Euros": lambda a: a.euro_exchange_intent,                                              
                                              "Exchanged Euros": lambda a: a.exchanged_euros,                                              
                                              "Contributed Hours": lambda a: a.contributed_hours,
                                              "Registered Withdraw Euros": lambda a: a.withdraw_intent,
                                              "Withdrawn Euros": lambda a: a.withdrawn_euros,
                                              "Last withdraw tick": lambda a: a.last_withdraw_tick,
                                              "Exit triggered bool": lambda a: a.exit_triggered 
                                          })

        # Create agents
        self.teo = Teo(0, self)
        self.schedule.add(self.teo)
        
        for _ in itertools.repeat(None, self.n_contributors):
            a = Contributor('Contributor_'+self.uniqid(), self, self.teo)
            self.schedule.add(a)
            
        for _ in itertools.repeat(None, self.n_ver_sponsors):
            a = VerificationSponsor('Ver_Sponsor_'+self.uniqid(), self, self.teo)
            self.schedule.add(a)
            
        for _ in itertools.repeat(None, self.n_char_sponsors):
            a = CharitableSponsor('Char_Sponsor_'+self.uniqid(), self, self.teo)
            self.schedule.add(a)
            
        for _ in itertools.repeat(None, self.n_investors):
            a = Investor('Investor_'+self.uniqid(), self, self.teo)
            self.schedule.add(a)

        self.running = True

    def uniqid(self):
        return hex(int(time()*10000000))[2:]

    def step(self):
        new_user_growth_adjusted = self.new_user_growth - (self.new_user_growth - self.churn_prob)/self.months_with_growth * min([self.months_with_growth, self.schedule.steps])

        # generate new users
        self.n_contributors = len([k for k, v in self.schedule.agents_by_type['Customer'].items() if v.__class__.__name__ == 'Contributor'])
        for _ in itertools.repeat(None, self.n_contributors):
            if np.random.uniform(0, 1) < new_user_growth_adjusted:
                a = Contributor('Contributor_'+self.uniqid(), self, self.teo)
                self.schedule.add(a)

        self.n_ver_sponsors = len([k for k, v in self.schedule.agents_by_type['Customer'].items() if v.__class__.__name__ == 'VerificationSponsor'])
        for _ in itertools.repeat(None, self.n_contributors):
            if np.random.uniform(0, 1) < new_user_growth_adjusted:
                a = VerificationSponsor('Ver_Sponsor_'+self.uniqid(), self, self.teo)
                self.schedule.add(a)    

        self.n_char_sponsors = len([k for k, v in self.schedule.agents_by_type['Customer'].items() if v.__class__.__name__ == 'CharitableSponsor'])  
        for _ in itertools.repeat(None, self.n_contributors):
            if np.random.uniform(0, 1) < new_user_growth_adjusted:
                a = CharitableSponsor('Char_Sponsor'+self.uniqid(), self, self.teo)
                self.schedule.add(a)    

        self.n_investors = len([k for k, v in self.schedule.agents_by_type['Customer'].items() if v.__class__.__name__ == 'Investor'])    
        for _ in itertools.repeat(None, self.n_contributors):
            if np.random.uniform(0, 1) < new_user_growth_adjusted:
                a = Investor('Investor_'+self.uniqid(), self, self.teo)
                self.schedule.add(a)    

        self.schedule.step()
 
        # collect data
        self.datacollector.collect(self, self.store_data)
        # store data if store_data is True
        #results = model.datacollector.get_agent_vars_dataframe().reset_index()
        #results = results.rename(columns={'level_0': 'tick', 'level_1': 'agent_id'})

