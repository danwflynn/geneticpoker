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
RANKED_STARTING_HANDS = ["AA", "KK", "QQ", "AKs", "JJ", "AQs", "KQs", "AJs", "KJs", "TT", "AKo", "ATs", "QJs", "KTs", "QTs",
                         "JTs", "99", "AQo", "A9s", "KQo", "88", "K9s", "T9s", "A8s", "Q9s", "J9s", "AJo", "A5s", "77", "A7s",
                         "KJo", "A4s", "A3s", "A6s", "QJo", "66", "K8s", "T8s", "A2s", "98s", "J8s", "ATo", "Q8s", "K7s", "KTo",
                         "55", "JTo", "87s", "QTo", "44", "33", "22", "K6s", "97s", "K5s", "76s", "T7s", "K4s", "K3s", "K2s",
                         "Q7s", "86s", "65s", "J7s", "54s", "Q6s", "75s", "96s", "Q5s", "64s", "Q4s", "Q3s", "T9o", "T6s", "Q2s",
                         "A9o", "53s", "85s", "J6s", "J9o", "K9o", "J5s", "Q9o", "43s", "74s", "J4s", "J3s", "95s", "J2s", "63s",
                         "A8o", "52s", "T5s", "84s", "T4s", "T3s", "42s", "T2s", "98o", "T8o", "A5o", "A7o", "73s", "A4o", "32s",
                         "94s", "93s", "J8o", "A3o", "62s", "92s", "K8o", "A6o", "87o", "Q8o", "83s", "A2o", "82s", "97o", "72s",
                         "76o", "K7o", "65o", "T7o", "K6o", "86o", "54o", "K5o", "J7o", "75o", "Q7o", "K4o", "K3o", "K2o", "96o",
                         "64o", "Q6o", "53o", "85o", "T6o", "Q5o", "43o", "Q4o", "Q3o", "Q2o", "74o", "J6o", "63o", "J5o", "95o",
                         "52o", "J4o", "J3o", "42o", "J2o", "84o", "T5o", "T4o", "32o", "T3o", "73o", "T2o", "62o", "94o", "93o",
                         "92o", "83o", "82o", "72o"]

assert sorted(STARTING_HANDS) == sorted(RANKED_STARTING_HANDS)

# Always fold action space
always_fold = np.zeros(13)
always_fold[0] = 1

# Always call action space
always_call = np.zeros(13)
always_call[1] = 1

# Action space for super strong hand
early_strong_hand_actions = np.array([0, 0.1, 0.025, 0.025, 0.05, 0.05, 0.15, 0.3, 0.15, 0.05, 0.05, 0.025, 0.025])

def consolidate_to_action(action_space: np.ndarray, action: int, alpha=1):
    new_action_space = action_space.copy()
    new_action_space[action] = alpha
    sum_all_else = np.sum(action_space) - action_space[action]
    mask = np.ones(new_action_space.shape, dtype=bool)
    mask[action] = False
    new_action_space[mask] -= (sum_all_else - 1 + alpha) * (action_space[mask] / sum_all_else)
    if np.sum(new_action_space) != 1:
        new_action_space[action] += 1 - np.sum(new_action_space)
    assert np.sum(new_action_space) == 1
    return new_action_space

# By default, set all hands to fold
preflop_PM[:, :] = always_fold

for starting_rank in range(169):
    hand_str = RANKED_STARTING_HANDS[starting_rank]
    hand_ind = STARTING_HANDS.index(hand_str)

    if starting_rank == RANKED_STARTING_HANDS.index("AA"):
        preflop_PM[hand_ind, :] = early_strong_hand_actions.copy()
    elif starting_rank <= RANKED_STARTING_HANDS.index("TT"):
        preflop_PM[hand_ind, :5] = consolidate_to_action(early_strong_hand_actions, 1, 0.2)
        preflop_PM[hand_ind, 5:10] = consolidate_to_action(early_strong_hand_actions, 1, 0.9)
    elif starting_rank <= RANKED_STARTING_HANDS.index("99"):
        preflop_PM[hand_ind, :5] = consolidate_to_action(consolidate_to_action(early_strong_hand_actions, 2, 0.5), 1, 0.5)
        preflop_PM[5:10] = always_call

assert np.sum(preflop_PM) == 1690
