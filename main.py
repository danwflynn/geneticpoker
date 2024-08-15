from pokergame import *
import copy
import csv
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


def get_fitness(agent: Agent):
    return agent.balance * agent.games_won


agents_amount = 10
agents = deque([Agent(f"Agent {i+1}", [preflop_PM, flop_PM, turn_PM, river_PM]) for i in range(agents_amount)])
total_agents_used = agents_amount

policy_snapshots_AA = []
policy_snapshots_72o = []
game_results = []
final_balances = []
game_outcomes = []
eliminated_agents = []
training_accuracy = []
agent_strategies = {} 

# Function to record the current policy for both "AA" and "72o"
def record_policy_snapshot(agent, game_number):
    hand_index_AA = STARTING_HANDS.index("AA")
    hand_index_72o = STARTING_HANDS.index("72o")
    
    snapshot_AA = {
        "game_number": game_number,
        "policy": copy.deepcopy(agent.stats[0][hand_index_AA, :, :])  
    }
    snapshot_72o = {
        "game_number": game_number,
        "policy": copy.deepcopy(agent.stats[0][hand_index_72o, :, :])  
    }
    
    policy_snapshots_AA.append(snapshot_AA)
    policy_snapshots_72o.append(snapshot_72o)

def log_game_results(game_number, agents):
    for agent in agents:
        game_results.append({
            "Game Number": game_number,
            "Agent Name": agent.name,
            "Balance": agent.balance,
            "Games Won": agent.games_won
        })
    
    agent_strategies[agent.name] = copy.deepcopy(agent.stats)

def log_game_outcome(game_number, winner, pot_size, num_players):
    game_outcomes.append({
        "Game Number": game_number,
        "Winner": winner.name,
        "Pot Size": pot_size,
        "Number of Players": num_players
    })

def calculate_accuracy(agents):
    correct_decisions = sum(agent.games_won for agent in agents)
    total_decisions = len(agents) * len(agents[0].stats)  # Just an example
    accuracy = correct_decisions / total_decisions
    training_accuracy.append(accuracy)

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

        log_game_results(i + 1, agents)
        winner = max(agents, key=lambda a: a.balance)
        log_game_outcome(i + 1, winner, game.pot, len(agents))

        for a in agents.copy():
            if a.balance < 100:
                eliminated_agents.append(a.name)
                agents.remove(a)
        while len(agents) < 10:
            total_agents_used += 1
            agents.append(create_mutated_agent(max(agents, key=get_fitness)))
        
        for a in agents:
            writer.writerow([i+1, a.name, a.balance, a.games_won])

        if (i + 1) % 100 == 0:
            record_policy_snapshot(agents[0], i + 1)

        calculate_accuracy(agents)

    for agent in agents:
        final_balances.append({
            "Agent Name": agent.name,
            "Final Balance": agent.balance
        })

num_actions_AA = policy_snapshots_AA[0]["policy"].shape[1] if policy_snapshots_AA else 0
num_actions_72o = policy_snapshots_72o[0]["policy"].shape[1] if policy_snapshots_72o else 0

action_names_AA = ["Fold", "Check/Call"] + [f"Raise {i}%" for i in range(num_actions_AA - 2)]
action_names_72o = ["Fold", "Check/Call"] + [f"Raise {i}%" for i in range(num_actions_72o - 2)]

pd.DataFrame(game_results).to_csv('game_results.csv', index=False)
pd.DataFrame(game_outcomes).to_csv('game_outcomes.csv', index=False)
pd.DataFrame(final_balances).to_csv('final_balances.csv', index=False)
pd.DataFrame(eliminated_agents, columns=['Agent Name']).to_csv('eliminated_agents.csv', index=False)

plt.figure(figsize=(12, 6))
for idx in range(num_actions_AA):
    probabilities = [snapshot["policy"][0, idx] for snapshot in policy_snapshots_AA]
    plt.plot([snapshot["game_number"] for snapshot in policy_snapshots_AA], probabilities, label=action_names_AA[idx])

plt.xlabel('Game Number')
plt.ylabel('Probability')
plt.title('Policy Changes Over Time for Hand "AA"')
plt.legend(loc='best')
plt.grid(True)
plt.savefig('policy_changes_AA.png')

plt.figure(figsize=(12, 6))
for idx in range(num_actions_72o):
    probabilities = [snapshot["policy"][0, idx] for snapshot in policy_snapshots_72o]
    plt.plot([snapshot["game_number"] for snapshot in policy_snapshots_72o], probabilities, label=action_names_72o[idx])

plt.xlabel('Game Number')
plt.ylabel('Probability')
plt.title('Policy Changes Over Time for Hand "72o"')
plt.legend(loc='best')
plt.grid(True)
plt.savefig('policy_changes_72o.png')

plt.figure(figsize=(10, 6))
plt.plot(range(len(training_accuracy)), training_accuracy, label='Training Accuracy', color='blue')
plt.xlabel('Iteration')
plt.ylabel('Accuracy')
plt.title('Training Accuracy Over Time')
plt.legend(loc='best')
plt.grid(True)
plt.savefig('training_accuracy.png')

top_agents_games_won = pd.DataFrame(game_results).groupby('Agent Name').sum().nlargest(5, 'Games Won')
top_agents_balance = pd.DataFrame(final_balances).nlargest(5, 'Final Balance')

plt.figure(figsize=(12, 6))
top_agents_games_won['Games Won'].plot(kind='bar', color='orange')
plt.xlabel('Agent Name')
plt.ylabel('Games Won')
plt.title('Top 5 Agents Based on Games Won')
plt.xticks(rotation=45)
plt.grid(True)
plt.savefig('top_5_games_won.png')

plt.figure(figsize=(12, 6))
top_agents_balance.set_index('Agent Name')['Final Balance'].plot(kind='bar', color='green')
plt.xlabel('Agent Name')
plt.ylabel('Final Balance')
plt.title('Top 5 Agents Based on Final Balance')
plt.xticks(rotation=45)
plt.grid(True)
plt.savefig('top_5_final_balance.png')

def save_agent_strategy_to_csv(agent_name, strategies_dict, filename):
    agent_strategy = strategies_dict.get(agent_name, None)
    if agent_strategy is not None:
        with open(filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            for phase, phase_name in zip(agent_strategy, ["Preflop", "Flop", "Turn", "River"]):
                writer.writerow([f"Strategy for {agent_name} during {phase_name}"])
                for row in phase:
                    writer.writerow(row)
                writer.writerow([])  # Blank line for separation

for agent_name in top_agents_balance.index:
    save_agent_strategy_to_csv(agent_name, agent_strategies, 'top_agents_strategies_balance.csv')

for agent_name in top_agents_games_won.index:
    save_agent_strategy_to_csv(agent_name, agent_strategies, 'top_agents_strategies_games_won.csv')

def plot_strategy_heatmap(agent_name, phase_data, phase_name, output_file):
    phase_data_flattened = phase_data.reshape(phase_data.shape[0] * phase_data.shape[1], phase_data.shape[2])
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(phase_data_flattened, annot=False, cmap='coolwarm', cbar=True)
    plt.title(f"{agent_name} Strategy Heatmap during {phase_name}")
    plt.xlabel("Action Index")
    plt.ylabel("Hand/Wealth State Index")
    plt.savefig(output_file)
    plt.close()

for agent_name in top_agents_balance.index:
    if agent_name in agent_strategies:
        for phase_data, phase_name in zip(agent_strategies[agent_name], ["Preflop", "Flop", "Turn", "River"]):
            output_file = f"{agent_name}_{phase_name}_heatmap.png"
            plot_strategy_heatmap(agent_name, phase_data, phase_name, output_file)

for agent_name in top_agents_games_won.index:
    if agent_name in agent_strategies:
        for phase_data, phase_name in zip(agent_strategies[agent_name], ["Preflop", "Flop", "Turn", "River"]):
            output_file = f"{agent_name}_{phase_name}_heatmap.png"
            plot_strategy_heatmap(agent_name, phase_data, phase_name, output_file)
