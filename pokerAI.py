import random
from collections import Counter
from itertools import combinations

# Constants for the poker game
SUITS = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
VALUES = {rank: index for index, rank in enumerate(RANKS, start=2)}

# Card and Deck Classes
class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
        self.value = VALUES[rank]

    def __repr__(self):
        return f"{self.rank} of {self.suit}"

class Deck:
    def __init__(self):
        self.cards = [Card(suit, rank) for suit in SUITS for rank in RANKS]
        random.shuffle(self.cards)

    def deal(self, num):
        dealt_cards = self.cards[:num]
        self.cards = self.cards[num:]
        return dealt_cards

# Poker Hand Evaluation
def hand_rank(hand):
    ranks = sorted((card.value for card in hand), reverse=True)
    suits = [card.suit for card in hand]
    rank_counts = Counter(ranks)
    is_flush = len(set(suits)) == 1
    is_straight = len(rank_counts) == 5 and (ranks[0] - ranks[4] == 4)

    if ranks == [14, 5, 4, 3, 2]:
        is_straight = True
        ranks = [5, 4, 3, 2, 1]

    rank_counts_sorted = sorted(rank_counts.values(), reverse=True)
    if is_straight and is_flush:
        return (8, ranks)
    elif rank_counts_sorted == [4, 1]:
        return (7, rank_counts.most_common(1)[0][0])
    elif rank_counts_sorted == [3, 2]:
        return (6, rank_counts.most_common(1)[0][0], rank_counts.most_common(2)[1][0])
    elif is_flush:
        return (5, ranks)
    elif is_straight:
        return (4, ranks)
    elif rank_counts_sorted == [3, 1, 1]:
        return (3, rank_counts.most_common(1)[0][0], ranks)
    elif rank_counts_sorted == [2, 2, 1]:
        return (2, rank_counts.most_common(2)[0][0], rank_counts.most_common(2)[1][0], ranks)
    elif rank_counts_sorted == [2, 1, 1, 1]:
        return (1, rank_counts.most_common(1)[0][0], ranks)
    else:
        return (0, ranks)

def best_hand(cards):
    return max((comb for comb in combinations(cards, 5)), key=hand_rank)

def hand_description(rank_tuple):
    descriptions = ["High Card", "One Pair", "Two Pair", "Three of a Kind", "Straight", "Flush", "Full House", "Four of a Kind", "Straight Flush"]
    return descriptions[rank_tuple[0]]

class PokerAgent:
    def __init__(self):
        self.strategy = {
            "Bet Aggressively": random.random(),
            "Fold in Weak Situations": random.random(),
            "Bluffing Tendency": random.random(),
            "Response to Other Players' Actions": random.random(),
            "Importance of High-Ranked Cards": random.random(),
            "Tendency to Check": random.random(),
            "Consideration of Potential Hands": random.random(),
            "Response to a Strong Hand": random.random(),
            "Risk Appetite": random.random(),
            "Likelihood of Calling a Bet": random.random(),
        }
        self.score = 0

    def decide_action(self, hand, community_cards, other_players_actions):
        return random.choice(["bet", "call", "check", "fold"])

def play_game(agents):
    deck = Deck()
    players_hands = {agent: deck.deal(2) for agent in agents}
    community_cards = deck.deal(5)

    hands = {agent: hand + community_cards for agent, hand in players_hands.items()}
    best_player = max(hands, key=lambda agent: hand_rank(best_hand(hands[agent])))

    for agent in agents:
        if agent == best_player:
            agent.score += 1

def evaluate_agents(agents):
    for agent in agents:
        agent.score = 0
    for _ in range(100):  
        play_game(agents)
    agents.sort(key=lambda agent: agent.score, reverse=True)

def select_parents(agents):
    return random.choices(agents, k=2, weights=[agent.score for agent in agents])

def crossover(parent1, parent2):
    crossover_point = random.randint(1, len(parent1.strategy) - 1)
    child_strategy = dict(list(parent1.strategy.items())[:crossover_point] + list(parent2.strategy.items())[crossover_point:])
    child = PokerAgent()
    child.strategy = child_strategy
    return child

def mutate(agent):
    mutation_rate = 0.1
    for key in agent.strategy:
        if random.random() < mutation_rate:
            agent.strategy[key] += random.uniform(-mutation_rate, mutation_rate)

def genetic_algorithm():
    population_size = 5
    generations = 100
    agents = [PokerAgent() for _ in range(population_size)]
    
    best_overall_strategy = None
    best_overall_score = 0
    best_generation = 0

    for generation in range(generations):
        print(f"Generation {generation + 1}")
        evaluate_agents(agents)
        
        # Track the best strategy of this generation
        best_strategy = agents[0].strategy
        best_score = agents[0].score
        
        # Update the overall best strategy if the current one is better
        if best_score > best_overall_score:
            best_overall_strategy = best_strategy
            best_overall_score = best_score
            best_generation = generation + 1
        
        new_agents = []
        for _ in range(population_size // 2):
            parent1, parent2 = select_parents(agents)
            child1 = crossover(parent1, parent2)
            child2 = crossover(parent2, parent1)
            mutate(child1)
            mutate(child2)
            new_agents.extend([child1, child2])
        agents = new_agents
        
    
    # Print final best strategy and the generation it came from
    print(f"Best strategy found in Generation {best_generation} with score {best_overall_score}:")
    print(best_overall_strategy)

if __name__ == "__main__":
    genetic_algorithm()
