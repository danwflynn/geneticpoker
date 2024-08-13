import random
from collections import Counter
from itertools import combinations
from enum import Enum
from typing import List


class Suit(Enum):
    SPADES = "Spades"
    HEARTS = "Hearts"
    CLUBS = "Clubs"
    DIAMONDS = "Diamonds"


RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
VALUES = {rank: index for index, rank in enumerate(RANKS, start=2)}


class Card:
    def __init__(self, rank: str, suit: Suit):
        if rank not in RANKS:
            raise ValueError(f"Invalid rank: {rank}")
        self.rank = rank
        self.suit = suit
        self.value = VALUES[rank]

    def __repr__(self):
        return f"{self.rank} of {self.suit.value}"  # Use the suit's value for a cleaner output


class Deck:
    def __init__(self):
        self.cards = [Card(rank, suit) for suit in Suit for rank in RANKS]
        random.shuffle(self.cards)

    def deal(self, num):
        dealt_cards = self.cards[:num]
        self.cards = self.cards[num:]
        return dealt_cards


# Poker Hand Evaluation
def hand_rank(hand: List[Card]):
    """Return a value representing the rank of a hand."""
    ranks = sorted([card.value for card in hand], reverse=True)
    suits = [card.suit for card in hand]
    rank_counts = Counter(ranks)
    is_flush = len(set(suits)) == 1
    is_straight = len(rank_counts) == 5 and (ranks[0] - ranks[4] == 4)

    # Special case: Handling the low Ace in a straight (A, 2, 3, 4, 5)
    if ranks == [14, 5, 4, 3, 2]:
        is_straight = True
        ranks = [5, 4, 3, 2, 1]  # Adjust ranks for proper high card comparison

    rank_counts_sorted = sorted(rank_counts.values(), reverse=True)
    if is_straight and is_flush:
        return 8, ranks  # Straight flush
    elif rank_counts_sorted == [4, 1]:
        return 7, rank_counts.most_common(1)[0][0]  # Four of a kind
    elif rank_counts_sorted == [3, 2]:
        return 6, rank_counts.most_common(1)[0][0], rank_counts.most_common(2)[1][0]  # Full house
    elif is_flush:
        return 5, ranks  # Flush
    elif is_straight:
        return 4, ranks  # Straight
    elif rank_counts_sorted == [3, 1, 1]:
        return 3, rank_counts.most_common(1)[0][0], sorted(ranks, reverse=True)  # Three of a kind
    elif rank_counts_sorted == [2, 2, 1]:
        # Two pair
        return 2, rank_counts.most_common(2)[0][0], rank_counts.most_common(2)[1][0], sorted(ranks, reverse=True)
    elif rank_counts_sorted == [2, 1, 1, 1]:
        return 1, rank_counts.most_common(1)[0][0], sorted(ranks, reverse=True)  # One pair
    else:
        return 0, ranks  # High card


def best_hand(cards: List[Card]):
    """Determine the best 5-card hand from a list of 7 cards."""
    return max((comb for comb in combinations(cards, 5)), key=lambda hand: hand_rank(hand))


def hand_description(rank_tuple):
    """Return the description of the hand."""
    rank_type = rank_tuple[0]
    if rank_type == 8:
        return "Straight Flush"
    elif rank_type == 7:
        return "Four of a Kind"
    elif rank_type == 6:
        return "Full House"
    elif rank_type == 5:
        return "Flush"
    elif rank_type == 4:
        return "Straight"
    elif rank_type == 3:
        return "Three of a Kind"
    elif rank_type == 2:
        return "Two Pair"
    elif rank_type == 1:
        return "One Pair"
    else:
        return "High Card"