from pokergame import *


agents_amount = 10
agents = [Agent(f"Agent {i+1}", [preflop_PM, flop_PM, turn_PM, river_PM]) for i in range(agents_amount)]

game = PokerGame(agents)
game.play_game()