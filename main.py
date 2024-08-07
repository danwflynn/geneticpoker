import random
from pokergame import PokerGame, Agent
from deck import Deck, Card, Suit, hand_description, best_hand


def play_poker_game():
    # Ask the user if they want to play as a human or have AI bots play
    player_type = input("Choose player type: 1 for Human vs AI, 2 for AI vs AI: ")
    while player_type not in ['1', '2']:
        player_type = input("Invalid input. Choose player type: 1 for Human vs AI, 2 for AI vs AI: ")

    num_players = 4  # Total players in the game
    human_player = (player_type == '1')

    # Create agents for the game
    agents = []
    if human_player:
        agents.append(Agent(stats={"name": "Human"}))  # Human player
        # Add 3 AI players
        for i in range(1, num_players):
            agents.append(Agent(stats={"name": f"AI Player {i}"}))
    else:
        # Add 4 AI players
        for i in range(num_players):
            agents.append(Agent(stats={"name": f"AI Player {i + 1}"}))

    # Initialize and start the poker game
    game = PokerGame(agents)
    game.start_game()

    def perform_betting_round():
        for agent in list(game.agents):  # Copy the list to allow safe modification
            if len(game.agents) == 1:
                # If only one player remains, they win the pot
                print(f"Only one player remains: {game.agents[0].stats['name']} wins the pot!")
                return True
            if agent.stats["name"] == "Human" and human_player:
                # Ask human player for their action
                action = input("Enter your action (bet, fold): ").strip().lower()
                if action == "bet":
                    try:
                        amount = int(input("Enter bet amount: "))
                        agent.bet(amount)
                    except ValueError:
                        print("Invalid amount. Please enter a number.")
                    except Exception as e:
                        print(e)
                elif action == "fold":
                    agent.fold()
                else:
                    print("Invalid action. Please enter 'bet' or 'fold'.")
            else:
                # AI players take random actions
                if random.choice(["bet", "fold"]) == "bet":
                    try:
                        # Random bet amount as a percentage of current balance
                        amount = random.randint(1, agent.balance)
                        agent.bet(amount)
                        print(f"{agent.stats['name']} bets {amount}")
                    except Exception as e:
                        print(f"{agent.stats['name']} could not bet: {e}")
                        agent.fold()
                else:
                    print(f"{agent.stats['name']} folds.")
                    agent.fold()
        return False

    def show_cards():
        print("\nCommunity Cards: " + ", ".join(map(str, game.community_cards)))
        for agent in game.agents:
            print(f"{agent.stats['name']} cards: {agent.cards}")

    # Game phases
    phases = ['Pre-flop', 'Flop', 'Turn', 'River', 'Showdown']

    # Deal initial cards (Pre-flop)
    print("\nStarting Pre-flop:")
    show_cards()
    if perform_betting_round():
        return

    # Deal flop
    game.deal_community_cards(3)
    print("\nFlop:")
    show_cards()
    if perform_betting_round():
        return

    # Deal turn
    game.deal_community_cards(1)
    print("\nTurn:")
    show_cards()
    if perform_betting_round():
        return

    # Deal river
    game.deal_community_cards(1)
    print("\nRiver:")
    show_cards()
    if perform_betting_round():
        return

    # Showdown
    print("\nShowdown:")
    show_cards()
    winners = game.determine_winner()
    if winners:
        for winner in winners:
            best_hand_cards = best_hand(winner.cards + game.community_cards)
            hand_desc = hand_description(hand_rank(best_hand_cards))
            print(f"Winner: {winner.stats['name']} with {hand_desc} ({', '.join(map(str, best_hand_cards))})")


if __name__ == "__main__":
    play_poker_game()
