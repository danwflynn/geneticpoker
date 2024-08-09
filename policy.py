from deck import *
import numpy as np


'''
There are 169 starting hands. 13 pocket pairs. 78 suited. 78 unsuited (13 choose 2 is 78).

Since the state space for percentage of wealth forced to call is continuous, 
we will have 10 increments of 10%

Since raising is continuous in the action space, it will be split up into 11 increments

State space: starting hand and percentage of wealth forced to call
Action space: fold, check/call, raise by 100% of pot, raise by 100% of pot + 10% of remaining wealth, etc.

- If you can't afford to raise, those probabilites get folded into check/call
- If you can't afford to raise by a certain percentage of remaining wealth,
  those probabilities get folded into the highest amount you can raise possible
'''

preflop_PM = np.zeros((169, 10, 13))

# List of starting hands indexed from 0 to 168
STARTING_HANDS = [
    # Pocket Pairs
    "AA", "KK", "QQ", "JJ", "TT", "99", "88", "77", "66", "55", "44", "33", "22",
    # Suited Hands
    "AKs", "AQs", "AJs", "ATs", "A9s", "A8s", "A7s", "A6s", "A5s", "A4s", "A3s", "A2s",
    "KQs", "KJs", "KTs", "K9s", "K8s", "K7s", "K6s", "K5s", "K4s", "K3s", "K2s",
    "QJs", "QTs", "Q9s", "Q8s", "Q7s", "Q6s", "Q5s", "Q4s", "Q3s", "Q2s",
    "JTs", "J9s", "J8s", "J7s", "J6s", "J5s", "J4s", "J3s", "J2s",
    "T9s", "T8s", "T7s", "T6s", "T5s", "T4s", "T3s", "T2s",
    "98s", "97s", "96s", "95s", "94s", "93s", "92s",
    "87s", "86s", "85s", "84s", "83s", "82s",
    "76s", "75s", "74s", "73s", "72s",
    "65s", "64s", "63s", "62s",
    "54s", "53s", "52s",
    "43s", "42s", "32s",
    # Offsuit Hands
    "AKo", "AQo", "AJo", "ATo", "A9o", "A8o", "A7o", "A6o", "A5o", "A4o", "A3o", "A2o",
    "KQo", "KJo", "KTo", "K9o", "K8o", "K7o", "K6o", "K5o", "K4o", "K3o", "K2o",
    "QJo", "QTo", "Q9o", "Q8o", "Q7o", "Q6o", "Q5o", "Q4o", "Q3o", "Q2o",
    "JTo", "J9o", "J8o", "J7o", "J6o", "J5o", "J4o", "J3o", "J2o",
    "T9o", "T8o", "T7o", "T6o", "T5o", "T4o", "T3o", "T2o",
    "98o", "97o", "96o", "95o", "94o", "93o", "92o",
    "87o", "86o", "85o", "84o", "83o", "82o",
    "76o", "75o", "74o", "73o", "72o",
    "65o", "64o", "63o", "62o",
    "54o", "53o", "52o",
    "43o", "42o", "32o"
]

# Function to get the index of a starting hand
def get_hand_index(card1: Card, card2: Card) -> int:
    # Ensure cards are in correct order (higher rank first)
    if VALUES[card1.rank] < VALUES[card2.rank] or (VALUES[card1.rank] == VALUES[card2.rank] and card1.suit < card2.suit):
        card1, card2 = card2, card1

    # Determine hand type
    if card1.rank == card2.rank:
        # Pocket pair
        hand_str = card1.rank + card2.rank
        return STARTING_HANDS.index(hand_str)
    else:
        # Suited or offsuit
        is_suited = card1.suit == card2.suit
        hand_str = f"{card1.rank}{card2.rank}{'s' if is_suited else 'o'}"
        return STARTING_HANDS.index(hand_str)

# Starting hands but in ranked order

RANKED_STARTING_HANDS = []

# Pocket Aces
preflop_PM[12, :, 1] = 0.1
preflop_PM[12, :, 12] = 0.1
preflop_PM[12, :, 2:12] = 0.08

# Pocket Kings, Queens, Jacks, 10s, Suited Royals (minus queen-jack)
preflop_PM[8:12, 0:8, 1] = 0.2
preflop_PM[8:12, 0:8, 2:8] = 0.1
preflop_PM[8:12, 0:8, 8:13] = 0.04
preflop_PM[8:12, 8:10, 1] = 1

preflop_PM[13:16, 0:8, 1] = 0.2
preflop_PM[13:16, 0:8, 2:8] = 0.1
preflop_PM[13:16, 0:8, 8:13] = 0.04
preflop_PM[13:16, 8:10, 1] = 1

preflop_PM[25:27, 0:8, 1] = 0.2
preflop_PM[25:27, 0:8, 2:8] = 0.1
preflop_PM[25:27, 0:8, 8:13] = 0.04
preflop_PM[25:27, 8:10, 1] = 1

# Ace-King offsuit, Ace-10 suited, Queen-Jack suited, Royals-Ten suited, Pocket 9s


preflop_PM[36, 0:8, 1] = 0.2
preflop_PM[36, 0:8, 2:8] = 0.1
preflop_PM[36, 0:8, 8:13] = 0.04
preflop_PM[36, 8:10, 1] = 1

# Ace-Queen offsuit, Ace-9 suited, King-Queen, Pocket 8s

# 10->Ace-9 suited

# Ace-Jack offsuit, 