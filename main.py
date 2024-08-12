from pokergame import *


def get_balance(agent: Agent):
    return agent.balance


def create_mutated_agent(agent: Agent):
    # Implement the mutations here
    return agent


agents_amount = 10
agents = [Agent(f"Agent {i+1}", [preflop_PM, flop_PM, turn_PM, river_PM]) for i in range(agents_amount)]
total_agents_used = agents_amount

for i in range(1000):
    game = PokerGame(agents)
    game.play_game()
    agents = game.agents
    while len(agents) < 10:
        agents.append(create_mutated_agent(max(agents, key=get_balance)))