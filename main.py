from pokergame import *
import copy


def get_fitness(agent: Agent):
    return agent.balance * agent.games_won


agents_amount = 10
agents = deque([Agent(f"Agent {i+1}", [preflop_PM, flop_PM, turn_PM, river_PM]) for i in range(agents_amount)])
total_agents_used = agents_amount


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
    print(f"{a.name}: {a.balance}")

winner = max(agents, key=get_fitness)

for i in range(3):
    for j in range(9):
        print(winner.stats[i+1][j][0])