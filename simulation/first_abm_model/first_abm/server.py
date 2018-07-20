from mesa.visualization.ModularVisualization import ModularServer
from .model import TeoModel

from mesa.visualization.modules import ChartModule
from mesa.visualization.UserParam import UserSettableParameter

chart_totals = ChartModule([
    {"Label": "Total Euros", "Color": "#3498DB"},
    {"Label": "Total Teos", "Color": "#E74C3C"},
    {"Label": "Contributed Hours", "Color": "#2ECC71"}],
    data_collector_name='datacollector'
)

chart_rewards = ChartModule([
    {"Label": "Reward per Contrib Hour", "Color": "#3498DB"},
    {"Label": "Reward per Exchanged Euro", "Color": "#E74C3C"}],
    data_collector_name='datacollector'
)

chart_agents = ChartModule([
    {"Label": "Number of Agents", "Color": "#3498DB"},
    {"Label": "Number of Contributors", "Color": "#E74C3C"},
    {"Label": "Number of Investors", "Color": "#2ECC71"},
    {"Label": "Number of Charitable Sponsors", "Color": "#ffff00"},
    {"Label": "Number of Verification Sponsors", "Color": "#ff00ff"}],
    data_collector_name='datacollector'
)


model_params = {
    "store_data": UserSettableParameter('checkbox', 'Store Data', value=True),
    "n_contributors": UserSettableParameter('slider', "Number of contributors", 60, 0, 100, 1,
                               description="Choose how many contributors to include in the model"),
    "n_investors": UserSettableParameter('slider', "Number of investors", 10, 0, 100, 1,
                               description="Choose how many investors to include in the model"),
    "n_ver_sponsors": UserSettableParameter('slider', "Number of verification sponsors", 10, 0, 100, 1,
                               description="Choose how many verification sponsors to include in the model"),
    "n_char_sponsors": UserSettableParameter('slider', "Number of charitable sponsors", 20, 0, 100, 1,
                               description="Choose how many charitable sponsors to include in the model"),
    "buffer_share": UserSettableParameter('slider', "Buffer Share in %", 20, 0, 100, 1,
                               description="Choose how much buffer should be hold back in % of Euro Pool"),
    "exchange_reward_share": UserSettableParameter('slider', "Exchange Reward Share of Buffer", 20, 0, 100, 1,
                               description="Choose how much % of the buffer should be used for exchange rewards"),
    "new_user_growth": UserSettableParameter('slider', "New user growth", 10, 0, 100, 1,
                               description="Choose % of new users relative to existing"),
    "churn_prob": UserSettableParameter('slider', "Churn probability", 5, 0, 100, 1,
                               description="Choose how many % churn each tick."),
    "months_with_growth": UserSettableParameter('slider', "Months with growth", 96, 0, 100, 1,
                               description="Choose how many months the system grows until churn = new users")
}

server = ModularServer(TeoModel, [chart_totals, chart_rewards, chart_agents], "Teo Model", model_params)
server.port = 8521
