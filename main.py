from pokergame import *
import numpy as np
import random

def get_fitness(agent: Agent):
    return agent.balance * agent.games_won


agents_amount = 10
agents = deque([Agent(f"Agent {i+1}", [preflop_PM, flop_PM, turn_PM, river_PM]) for i in range(agents_amount)])
total_agents_used = agents_amount


def create_mutated_agent(agent: Agent):
    stats = [np.copy(pm) for pm in agent.stats]  # Deep copy of the policy matrices

    for i in range(len(stats)):
        flat_stats = stats[i].flatten()

        # Ensure the initial sum is exactly 1
        flat_stats /= np.sum(flat_stats)
        
        # Select one index to modify
        idx1 = random.randint(0, len(flat_stats) - 1)

        # Calculate a small adjustment
        adjustment = random.uniform(-0.01, 0.01)
        
        # Apply the adjustment
        flat_stats[idx1] += adjustment

        # Make sure the probabilities remain valid
        flat_stats = np.clip(flat_stats, 0, 1)

        # Re-normalize to sum to 1
        total = np.sum(flat_stats)
        if total != 1:
            flat_stats /= total  # Ensure the sum is exactly 1

        stats[i] = flat_stats.reshape(stats[i].shape)

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
    print(f"{a.name}: {a.balance}")