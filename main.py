from pokergame import *
import copy
import csv
import pandas as pd
import matplotlib.pyplot as plt


def get_fitness(agent: Agent):
    return agent.balance * agent.games_won


agents_amount = 10
agents = deque([Agent(f"Agent {i+1}", [preflop_PM, flop_PM, turn_PM, river_PM]) for i in range(agents_amount)])
total_agents_used = agents_amount


# Open a file to write the data
with open('poker_simulation_results.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    # Write the header
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
        
        # Record the data after each game
        for a in agents:
            writer.writerow([i+1, a.name, a.balance, a.games_won])

    # Print the final results
    for a in agents:
        print(f"{a.name}: {a.balance}")

    winner = max(agents, key=get_fitness)

    for i in range(3):
        for j in range(9):
            print(winner.stats[i+1][j][0])


data = pd.read_csv('poker_simulation_results.csv')

plt.figure(figsize=(10, 6))
for agent_name in data['Agent Name'].unique():
    agent_data = data[data['Agent Name'] == agent_name]
    plt.plot(agent_data['Game Number'], agent_data['Balance'], label=agent_name)

plt.xlabel('Game Number')
plt.ylabel('Balance')
plt.title('Agent Balance Over Time')
plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
plt.show()

games_won_summary = data.groupby('Agent Name')['Games Won'].sum()

plt.figure(figsize=(10, 6))
games_won_summary.plot(kind='bar')
plt.xlabel('Agent Name')
plt.ylabel('Total Games Won')
plt.title('Total Games Won by Each Agent')
plt.show()
