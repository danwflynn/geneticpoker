from pokergame import *


agents = [Agent(f"Agent {i+1}", [preflop_PM, flop_PM, turn_PM, river_PM]) for i in range(10)]
max_agent_number = 10

game = PokerGame(agents)
game.play_game()