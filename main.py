from pokergame import *
import copy
import csv
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def get_fitness(agent: Agent):
    return agent.balance * agent.games_won


agents_amount = 10
agents = deque([Agent(f"Agent {i+1}", [preflop_PM, flop_PM, turn_PM, river_PM]) for i in range(agents_amount)])
total_agents_used = agents_amount

policy_snapshots = []

# Function to record the current policy
def record_policy_snapshot(agent, game_number):
    hand_index = STARTING_HANDS.index("AA")  
    snapshot = {
        "game_number": game_number,
        "policy": copy.deepcopy(agent.stats[0][hand_index, :, :])  
    }
    policy_snapshots.append(snapshot)

with open('poker_simulation_results.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Game Number", "Agent Name", "Balance", "Games Won"])

    def create_mutated_agent(agent: Agent):
        stats = copy.deepcopy(agent.stats)
        choice = random.choice([1, 2])
        if choice == 1:
            for pm in stats:
                mutate_aggressive(pm, 0.05)
        else:
            for pm in stats:
                mutate_passive(pm, 0.05)
        return Agent(f"Agent {total_agents_used}", stats)

    for i in range(1000):
        print(i)
        game = PokerGame(agents)
        game.play_game()
        agents.rotate(-1)
        for a in agents.copy():
            if a.balance < 100:
                agents.remove(a)
        while len(agents) < 10:
            total_agents_used += 1
            agents.append(create_mutated_agent(max(agents, key=get_fitness)))
        
        for a in agents:
            writer.writerow([i+1, a.name, a.balance, a.games_won])

        if (i + 1) % 100 == 0:
            record_policy_snapshot(agents[0], i + 1)

num_actions = policy_snapshots[0]["policy"].shape[1] if policy_snapshots else 0

action_names = ["Fold", "Check/Call"] + [f"Raise {i}%" for i in range(num_actions - 2)]

plt.figure(figsize=(12, 6))
for idx in range(num_actions):
    probabilities = [snapshot["policy"][0, idx] for snapshot in policy_snapshots]
    plt.plot([snapshot["game_number"] for snapshot in policy_snapshots], probabilities, label=action_names[idx])

plt.xlabel('Game Number')
plt.ylabel('Probability')
plt.title('Policy Changes Over Time for Hand "AA"')
plt.legend(loc='best')
plt.show()
