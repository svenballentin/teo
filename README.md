# Teo Simulation

This repo contains my first work on simulating TEO using agent-based models. The agent-based modeling approach is based on a python package called [mesa] (http://mesa.readthedocs.io/en/master/ "Mesa Package") with minor adaptations.

## Getting Started

### Prerequisites

Install python3 (e.g. by following the guidelines on this [website](https://docs.python-guide.org/starting/install3/osx/ "Hitchhiker's Guide to Python").

Install all dependencies by running `pip3 install -r requirements.txt`.

In order to run the web-server that allows for setting model parameters and visualises the model output follow these steps:

1. Clone or download this repository to your machine. 
2. Run `python3 simulation/first_abm_model/run.py` to start the visualisation in the web-server.
3. A webbrowser opens. Set the model parameters to the right.
4. Click on `start` in the top right corner to start the simulation and run it until you want to stop the simulation.
5. Output data of the model is automatically saved to the directory from which you run `run.py` from.

## Model

### Agents

The model has two types of agents; customers and Teo. Usually the model is initialized with multiple customers in the system and one Teo agent, that represents the system. 

Customers are agents that are using Teo. They can perform the following actions:

* Register Contribution
* Register Sponsorship
* Register Teo->Euro Exchange
* Register Euro->Teo Exchange
* Register Withdraw
* Exit Teo

In the current version of the model we have 4 different types of customers:

1. Contributors - Contributes to receive contribution rewards
    * Has a small monthly deposit of 10
    * Contributes all available 80 hours per month
    * Always exchanges all teos for euros
    * Always all euros from euro-wallet.
2. Investors - Invests in Teo to make a surplus with exchange rewards
    * Has a monthly deposit of 400
    * Always exchanges all teos for euros
    * Always withdraws all euros for teos
    * Randomly withdraws once in 24 months/ticks
    * The withdraw amount is random between 20-80% (uniform)    
3. Charitable Sponsors - Leaves all money in the system = indirect donation  
    * deposits every month 50 euros
    * exchanges always all euros to teo
    * sponsors all teos
    * does not exchange teo->euro and does not withdraw (donates)
4. Verification Sponsors - Has always at least 100 coins for sponsoring
    * deposits 100 euro in first month
    * has always at least 100 coins in the system
    * contributes 2 hours randomly in 1 of 3 months 
    * exchanges teo->euro exceeding 100 coins (the rewards)
    * withdraws everything from euro-wallet

### Growth + Churn

Each round the system gains new users defined as a % of already existing users (set by the parameter `New User Growth`). At the same time a certain % of users churn/exit the system (set by the parameter `Churn Probability`). The overall growth of the system per tick is calculated as `New User Growth` - `Churn Probability`. 

The `New User Growth` parameter is dynamic to model stagnating growth over time. The new user growth linearly declines over X months until it reaches the `Churn Probability` (the number of months is set by the parameter `Months With Growth`). Then the number of users in the system should be stable.

### Time/Steps

Time is modelled based on rounds. Each round or tick represents a month and follows a sequence of actions:

1. All temporary variables are reset before a round is started (e.g. contributed hours per tick/month).
2. First the agents are activated. They try to register their favourite action with Teo. If the agent is allowed to perform the action, Teo accepts the action, it enters into the `Teo action-register` and the value of the action is blocked in this round (e.g. the euro-value the agent intends to exchange). Then the agent moves to the second favourite action according their preferences (and so on).
3. After all agents have registered their actions, Teo executes the registered actions. For instance, for all agents that registered a withdraw, Teo removes the withdrawn euros from their euro-wallets.
4. Teo rewards users that contributed by distributing the contribution pool according the contributed hours of the agents. The contribution pool is calculated as **(Euros in System - Coins in System) - Buffer** at the end of the round. The Buffer is set by the parameter `Buffer Share in %`.
5. Teo rewards users that exchanged euros for teos by distributing the transaction pool according the exchanged euros of the agents. The transaction pool is a percentage of the buffer and is set by the parameter `Exchange Reward Share of Buffer`.

## Interface

You can access the parameter modification and the model output in the webbrowser that opens after running `python3 run.py`. On the left side you set the parameters of the model. If the parameters are set, you can run a single step of the model by clicking on `Step` in the upper right corner or you can run the model by clicking `Start` with X steps/second (X is set by the `Frames Per Second` slider) until you click `Stop`. 

## Output

You can store the model output by toggling `Store Data` on in the webbrowser before you run the model. This will store two CSV files in the directory from which you ran `python3 run.py`. The files are:

1. agentdata_YYYY-mm-dd_HH/MM/SS.csv
    * This file contains all agents and their variable values per tick.
2. modeldata_YYYY-mm-dd_HH/MM/SS.csv
    * This file contains the model variable value per tick.

