from mesa import Agent
from .model import get_exchange_reward_per_euro, get_contribution_reward_per_hour, get_exchanged_euros
from .model import get_total_teos, get_total_euros, get_total_hours
import random
import numpy as np

EXIT_PROBABILITY = 0.05

class Teo(Agent):
    
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.model = model
        self.action_register = []
        
    def register_deposit(self, agent, value):
        """Registers intended deposit value of an agent in the action-register.

        Args:
            agent (Agent): Agent instance.
            value (int): Intendend deposit value in euro.

        """
        action = {
            'unique_id': agent.unique_id,
            'action': 'deposit',
            'value': value
        }
        self.action_register.append(action)
        
    def execute_deposits(self):
        """Executes all deposit actions from the action-register.
      
        """
        deposits = [v for v in self.action_register if v['action'] == 'deposit']
        for deposit in deposits:
            self.model.schedule.agents_by_type['Customer'][deposit['unique_id']].euro_wallet += deposit['value']

    def register_sponsorship(self, agent, value):
        """Registers the intended sponsorship teos of an agent in the action-register
        if the agent is allowed to register the intended amount.

        Args:
            agent (Agent): Agent instance.
            value (int): Intendend sponsorship amount in teos.

        """
        if value <= agent.teo_wallet - agent.staged_teo:
            action = {
                'unique_id': agent.unique_id,
                'action': 'sponsorship',
                'value': value
            }
            self.action_register.append(action)
            agent.staged_teo += value       
            
    def execute_sponsorship(self):
        """Executes all sponsorship actions from the action-register.
      
        """
        sponsorships = [v for v in self.action_register if v['action'] == 'sponsorship']
        for sponsorship in sponsorships:
            self.model.schedule.agents_by_type['Customer'][sponsorship['unique_id']].staged_teo += sponsorship['value']
            
    def register_contribution(self, agent, value):
        """Registers the intended contribution hours of an agent in the action-register
        if the agent is allowed to register the intended amount.

        Args:
            agent (Agent): Agent instance.
            value (int): Intendend contribution hours.

        """
        if value <= agent.hour_wallet:
            action = {
                'unique_id': agent.unique_id,
                'action': 'contribution',
                'value': value
            }
            self.action_register.append(action)
            
    def execute_contribution(self):
        """Executes all contribution actions from the action-register.
        
        """
        contributions = [v for v in self.action_register if v['action'] == 'contribution']
        for contribution in contributions:
            self.model.schedule.agents_by_type['Customer'][contribution['unique_id']].hour_wallet -= contribution['value']
            self.model.schedule.agents_by_type['Customer'][contribution['unique_id']].contributed_hours += contribution['value']

    def register_withdraw(self, agent, value):
        """Registers the intended withdraw value of an agent in the action-register
        if the agent is allowed to register the intended amount.

        Args:
            agent (Agent): Agent instance.
            value (int): Intendend withdraw value in euros.

        """
        if value <= agent.euro_wallet - agent.staged_euro and self.model.schedule.steps - agent.last_withdraw_tick >= 2:
            action = {
                'unique_id': agent.unique_id,
                'action': 'withdraw',
                'value': value
            }
            self.action_register.append(action)
            agent.staged_euro += value
        
    def execute_withdraws(self):
        """Executes all withdraw actions from the action-register.
        
        """
        withdraws = [v for v in self.action_register if v['action'] == 'withdraw']
        for withdraw in withdraws:
            self.model.schedule.agents_by_type['Customer'][withdraw['unique_id']].euro_wallet -= withdraw['value']
            self.model.schedule.agents_by_type['Customer'][withdraw['unique_id']].withdrawn_euros += withdraw['value']
            self.model.schedule.agents_by_type['Customer'][withdraw['unique_id']].last_withdraw_tick = self.model.schedule.steps

    def register_euro_exchange(self, agent, value):
        """Registers the intended euro->teo exchange value of an agent in the action-register
        if the agent is allowed to register the intended amount.

        Args:
            agent (Agent): Agent instance.
            value (int): Intendend exchange value in euros.

        """
        if value <= agent.euro_wallet - agent.staged_euro:
            action = {
                'unique_id': agent.unique_id,
                'action': 'euro_exchange',
                'value': value
            }
            self.action_register.append(action)
            agent.staged_euro += value
            
    def register_teo_exchange(self, agent, value):
        """Registers the intended teo->euro exchange value of an agent in the action-register
        if the agent is allowed to register the intended amount.

        Args:
            agent (Agent): Agent instance.
            value (int): Intendend exchange value in teos.

        """
        if value <= agent.teo_wallet - agent.staged_teo:
            action = {
                'unique_id': agent.unique_id,
                'action': 'teo_exchange',
                'value': value
            }
            self.action_register.append(action)
            agent.staged_teo += value
            
    def execute_exchanges(self):
        """Executes all exchanges from the action-register. 
        
        If the teo-exchange amount > euro-exchange amount, first all euro-to-teo exchanges are
        executed, then teo-to-euro exchanges are executed randomly until the exchanged amount exceeds
        the exchangeable euro amount. The last exchange is potentially done only partially. 
        
        """
        #TODO: make this nicer and less verbose!
        exchanged_euros = 0
        exchanged_teos = 0
        
        euro_exchanges = [v for v in self.action_register if v['action'] == 'euro_exchange']
        teo_exchanges = [v for v in self.action_register if v['action'] == 'teo_exchange']
    
        if len(teo_exchanges) == 0 or len(euro_exchanges) == 0 or \
        (sum([v['value'] for v in teo_exchanges]) == 0 and sum([v['value'] for v in euro_exchanges]) == 0):
            return
        else:
            teo_exchange_volume = sum([v['value'] for v in teo_exchanges])
            euro_exchange_volume = sum([v['value'] for v in euro_exchanges])
            #in the case that euro register is larger, fullfill euro exchanges in random order until teo amount reached
            if euro_exchange_volume >= teo_exchange_volume:
                # transfer money for all agents in teo register
                for exchange in teo_exchanges:
                    self.model.schedule.agents_by_type['Customer'][exchange['unique_id']].teo_wallet -= exchange['value']
                    self.model.schedule.agents_by_type['Customer'][exchange['unique_id']].euro_wallet += exchange['value']
                    self.model.schedule.agents_by_type['Customer'][exchange['unique_id']].exchanged_teos += exchange['value']
                # fullfill euro exchanges in random order until total teo amount is reached
                random.shuffle(euro_exchanges)
                for exchange in euro_exchanges:
                    if exchanged_euros + exchange['value'] > teo_exchange_volume:
                        remaining_euros = teo_exchange_volume - exchanged_euros
                        self.model.schedule.agents_by_type['Customer'][exchange['unique_id']].euro_wallet -= remaining_euros
                        self.model.schedule.agents_by_type['Customer'][exchange['unique_id']].teo_wallet += remaining_euros
                        self.model.schedule.agents_by_type['Customer'][exchange['unique_id']].exchanged_euros += remaining_euros
                        break
                    self.model.schedule.agents_by_type['Customer'][exchange['unique_id']].euro_wallet -= exchange['value']
                    self.model.schedule.agents_by_type['Customer'][exchange['unique_id']].teo_wallet += exchange['value']
                    self.model.schedule.agents_by_type['Customer'][exchange['unique_id']].exchanged_euros += exchange['value']
                    exchanged_euros += exchange['value']
            #in the case that teo register is larger, fullfill teo exchanges in random order until euro amount reached      
            else:
                # transfer money for all agents in euro register
                for exchange in euro_exchanges:
                    self.model.schedule.agents_by_type['Customer'][exchange['unique_id']].euro_wallet -= exchange['value']
                    self.model.schedule.agents_by_type['Customer'][exchange['unique_id']].teo_wallet += exchange['value']
                    self.model.schedule.agents_by_type['Customer'][exchange['unique_id']].exchanged_euros += exchange['value']
                # fullfill euro exchanges in random order until total teo amount is reached
                random.shuffle(teo_exchanges)
                for exchange in teo_exchanges:
                    if exchanged_teos + exchange['value'] > euro_exchange_volume:
                        remaining_teos = euro_exchange_volume - exchanged_teos
                        self.model.schedule.agents_by_type['Customer'][exchange['unique_id']].teo_wallet -= remaining_teos
                        self.model.schedule.agents_by_type['Customer'][exchange['unique_id']].euro_wallet += remaining_teos
                        self.model.schedule.agents_by_type['Customer'][exchange['unique_id']].exchanged_teos += remaining_teos

                        break
                    self.model.schedule.agents_by_type['Customer'][exchange['unique_id']].teo_wallet -= exchange['value']
                    self.model.schedule.agents_by_type['Customer'][exchange['unique_id']].euro_wallet += exchange['value']
                    self.model.schedule.agents_by_type['Customer'][exchange['unique_id']].exchanged_teos += exchange['value']

                    exchanged_teos += exchange['value']
    
    def reward_contributions(self):
        """Method that rewards agents that contributed in the current tick.

        """        
        contribution_reward_per_hour = get_contribution_reward_per_hour(self.model)
        #payout to agents according to the number of hours they contributed
        for agent_id, agent in self.model.schedule.agents_by_type['Customer'].items():
            agent.teo_wallet += agent.contributed_hours * contribution_reward_per_hour
            agent.contribution_surplus += agent.contributed_hours * contribution_reward_per_hour

    def reward_exchanges(self):
        """Method that rewards agents that exchanged euros for teos in the current tick.

        """
        exchange_reward_per_euro = get_exchange_reward_per_euro(self.model)
        #payout to agents according to the number of hours they contributed
        for agent_id, agent in self.model.schedule.agents_by_type['Customer'].items():
            agent.teo_wallet += agent.exchanged_euros * exchange_reward_per_euro
            agent.exchange_surplus += agent.exchanged_euros * exchange_reward_per_euro

    
    def reset_parameters(self):
        self.action_register = []
    
    def step(self):
        self.execute_deposits()
        self.execute_contribution()
        self.execute_sponsorship()
        self.execute_exchanges()
        self.execute_withdraws()
        self.reward_contributions()
        self.reward_exchanges()
        self.reset_parameters()
        
class Customer(Agent):
    """Customer agent base class."""
    
    def __init__(self, unique_id, model, teo):
        super().__init__(unique_id, model)
        self.model = model
        self.unique_id = unique_id
        
        self.monthly_deposit = 0
        self.monthly_hours = 0
        
        self.euro_wallet = 0
        self.teo_wallet = 0

        self.contribution_surplus = 0
        self.exchange_surplus = 0
        
        self.deposit_intent = 0
        self.contribution_intent = 0
        self.sponsor_intent = 0
        self.teo_exchange_intent = 0
        self.euro_exchange_intent = 0
        self.withdraw_intent = 0
        
        self.hour_wallet = self.monthly_hours
        self.staged_euro = 0
        self.staged_teo = 0
        self.contributed_hours = 0
        self.exchanged_euros = 0
        self.exchanged_teos = 0
        self.withdrawn_euros = 0
               
        self.teo = teo

        self.last_withdraw_tick = -1
        self.exit_triggered = False
    
         
    def register_deposit(self, deposit_intent):
        """Registers the intended deposit amount with TEO.

        Args:
            deposit_intent (int): Indended deposit euros.

        """
        if deposit_intent > 0:
            self.teo.register_deposit(self, deposit_intent)
        
    def register_sponsorship(self, sponsor_intent):
        """Registers the intended sponsorship amount with TEO.

        Args:
            sponsor_intent (int): Indended sponsoring teos.

        """
        if sponsor_intent > 0:
            self.teo.register_sponsorship(self, sponsor_intent)  
        
    def register_contribution(self, contribution_intent):
        """Registers the intended contribution amount with TEO.

        Args:
            contribution_intent (int): Indended contribution hours.

        """
        if contribution_intent > 0:
            self.teo.register_contribution(self, contribution_intent)  
                     
    def register_withdraw(self, withdraw_intent):
        """Registers the intended withdraw amount with TEO.

        Args:
            withdraw_intent (int): Indended withdraw euros.

        """        
        if withdraw_intent > 0:
            self.teo.register_withdraw(self, withdraw_intent)
        
    def register_euro_exchange(self, exchange_intent):
        """Registers the intended euro->teo exchange amount with TEO.

        Args:
            exchange_intent (int): Indended euros to exchange for teos.

        """
        if exchange_intent > 0:
            self.teo.register_euro_exchange(self, exchange_intent)  
        
    def register_teo_exchange(self, exchange_intent):
        """Registers the intended teo->euro exchange amount with TEO.

        Args:
            exchange_intent (int): Indended teos to exchange for euros.

        """        
        if exchange_intent > 0:
            self.teo.register_teo_exchange(self, exchange_intent)  

    def exit(self):
        """Handles the exit of a user.

        The user stops depositing, sponsoring and contributing. She exchanges all teos 
        and withdraws remaining euros. If all money is removed from the system. The user
        is removed from the system by Teo.

        """     
        self.teo_exchange_intent = self.teo_wallet
        self.withdraw_intent = self.euro_wallet

        self.register_teo_exchange(self.teo_exchange_intent)
        self.register_withdraw(self.withdraw_intent)

        if self.teo_wallet + self.euro_wallet == 0:
            print('Agent exited: ', self.__class__.__name__)
            self.model.schedule.remove(self)

    def reset_parameters(self):
        """Resets temporary parameters at the beginning of a new tick.

        """       
        self.deposit_intent = 0
        self.contribution_intent = 0
        self.sponsor_intent = 0
        self.teo_exchange_intent = 0
        self.euro_exchange_intent = 0
        self.withdraw_intent = 0
        
        self.hour_wallet = self.monthly_hours
        self.staged_euro = 0
        self.staged_teo = 0
        self.contributed_hours = 0
        self.exchanged_euros = 0
        self.exchanged_teos = 0
        self.withdrawn_euros = 0


    def step(self):
        """Step method defining the ordered action to be taken each step.

        """      
        self.reset_parameters()

        if np.random.uniform(0, 1) < self.model.churn_prob: self.exit_triggered = True       
        if self.exit_triggered:
            self.exit()
        else:
            self.register_deposit(self.deposit_intent)
            self.register_contribution(self.contribution_intent)
            self.register_sponsorship(self.sponsor_intent)
            self.register_euro_exchange(self.euro_exchange_intent)
            self.register_teo_exchange(self.teo_exchange_intent)
            self.register_withdraw(self.withdraw_intent)

class VerificationSponsor(Customer):
    """Class describing the verfication sponsor. 
    
    A verification sponsor deposits 100 euro once and sponsors 100 teos each round. 
    She contributes occassionally and withdraws all rewards from the system.
    She has the following properties:
        - deposits 100 euro in first month
        - mininum coins in system: 100
        - contributes 2 hours randomly in 1 of 3 months 
        - exchanges teo->euro exceeding 100 coins (the rewards)
        - withdraws everything from euro-wallet
    """

    def __init__(self, unique_id, model, teo):
        print(model)
        super().__init__(unique_id, model, teo)
        # self.model = model
        self.monthly_deposit = 100
        self.monthly_hours = 2
            
    
    def step(self):
        self.reset_parameters()

        # exit randomly
        if np.random.uniform(0, 1) < self.model.churn_prob: self.exit_triggered = True       
        if self.exit_triggered:
            self.exit()
        else:
            self.sponsor_intent = min([self.teo_wallet, self.monthly_deposit]) #always sponsor max 100
            self.teo_exchange_intent = max([self.teo_wallet - self.sponsor_intent, 0]) #exchange non-sponsored teos back
            self.euro_exchange_intent = max([self.monthly_deposit - self.teo_wallet, 0]) #only exchange euros if teos < 100
            self.withdraw_intent = max([self.teo_wallet + self.euro_wallet - self.monthly_deposit, 0]) #always withdraw rewards
                
            if self.model.schedule.steps == 0:
                self.deposit_intent = self.monthly_hours
                self.register_deposit(self.deposit_intent)
            if np.random.uniform(0, 1) < 1/3:
                self.contribution_intent = self.monthly_hours
                self.register_contribution(self.contribution_intent)
            
            self.register_sponsorship(self.sponsor_intent) 
            self.register_euro_exchange(self.euro_exchange_intent) 
            self.register_teo_exchange(self.teo_exchange_intent)
            self.register_withdraw(self.withdraw_intent)
        

class CharitableSponsor(Customer):
    """Class describing the charitable sponsor.
    
    A charitable sponsor leaves all money within the system and has 
    the following properties:    
        - deposits every month
        - exchanges always all euros to teo
        - sponsors all teos
        - does not exchange teo->euro and does not withdraw
    """

    def __init__(self, unique_id, model, teo):
        super().__init__(unique_id, model, teo)
        self.monthly_deposit = 50
        self.monthly_hours = 0

    def step(self):
        self.reset_parameters()

        # exit randomly
        if np.random.uniform(0, 1) < self.model.churn_prob: self.exit_triggered = True       
        if self.exit_triggered:
            self.exit()
        else:
            self.deposit_intent = self.monthly_deposit
            self.sponsor_intent = self.teo_wallet #sponsors all teos
            self.euro_exchange_intent = self.euro_wallet #always exchange all euros->teos
            
            self.register_deposit(self.deposit_intent)
            self.register_contribution(self.contribution_intent)
            self.register_sponsorship(self.sponsor_intent) 
            self.register_euro_exchange(self.euro_exchange_intent) 
            self.register_teo_exchange(self.teo_exchange_intent)
            self.register_withdraw(self.withdraw_intent)
        
class Contributor(Customer):
    """Class describing the contributor agent.

    A contributor that has the following properties:
        - Has a monthly deposit of 10
        - Has 80 monthly hours
        - Contributes all monthly hours
        - Always exchanges all teos for euros
        - Always withdraws all euros from euro-wallet

    """
    
    def __init__(self, unique_id, model, teo):
        super().__init__(unique_id, model, teo)
        self.monthly_deposit = 10
        self.monthly_hours = 80
    
    def step(self):
        self.reset_parameters()

        # exit randomly
        if np.random.uniform(0, 1) < self.model.churn_prob: self.exit_triggered = True       
        if self.exit_triggered:
            print('Agent wants to exit: ', self.__class__.__name__)
            self.exit()
        else:
            self.deposit_intent = self.monthly_deposit
            self.contribution_intent = self.monthly_hours
            self.teo_exchange_intent = self.teo_wallet #always exchanges all teos to euros
            self.withdraw_intent = self.euro_wallet
            
            self.register_deposit(self.deposit_intent)
            self.register_contribution(self.contribution_intent)
            self.register_sponsorship(self.sponsor_intent) 
            self.register_euro_exchange(self.euro_exchange_intent) 
            self.register_teo_exchange(self.teo_exchange_intent)
            self.register_withdraw(self.withdraw_intent)
        

class Investor(Customer):
    """Class describing the investor agent.

    An investor that has the following properties:
    - Has a monthly deposit of 400
    - Always exchanges all teos for euros
    - Always withdraws all euros for teos
    - Randomly withdraws once in 24 months/ticks
    - The withdraw amount is random between 20-80% (uniform)
    """

    def __init__(self, unique_id, model, teo):
        super().__init__(unique_id, model, teo)
        self.monthly_deposit = 400
        self.monthly_hours = 0
    
    def step(self):
        self.reset_parameters()

        # exit randomly, stay in Teo until all funds are withdrawn
        if np.random.uniform(0, 1) <  self.model.churn_prob: self.exit_triggered = True       
        if self.exit_triggered:
            self.exit()
            return   
        # withdraw randomly once in 24 months and exchange before if euro-wallet < withdraw_intent      
        if np.random.uniform(0, 1) < 1/24:
            self.withdraw_intent = np.random.uniform(0.2, 0.8) * self.euro_wallet
            if self.euro_wallet < self.withdraw_intent:
                self.teo_exchange_intent = self.withdraw_intent - self.euro_wallet
                self.register_teo_exchange(self.teo_exchange_intent)
            self.withdraw_intent = min(self.euro_wallet, self.withdraw_intent)
            self.register_withdraw(self.withdraw_intent)
            return

        self.deposit_intent = self.monthly_deposit
        self.teo_exchange_intent = self.teo_wallet #always exchanges all teos to euros
        self.euro_exchange_intent = self.euro_wallet #always exchanges all euros to teos

        self.register_deposit(self.deposit_intent)
        self.register_contribution(self.contribution_intent)
        self.register_sponsorship(self.sponsor_intent) 
        self.register_euro_exchange(self.euro_exchange_intent) 
        self.register_teo_exchange(self.teo_exchange_intent)
        self.register_withdraw(self.withdraw_intent)