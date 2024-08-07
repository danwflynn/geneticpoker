from typing import List
from deck import *
from collections import deque


class Agent:
    def __init__(self, stats):
        self.stats = stats
        self.balance = 10000
        self.down_for = 0
        self.cards = []
        self.game = None

    def fold(self):
        self.cards = []
        self.down_for = 0
        if self.game.last_up is self:
            remaining_agents = [agent for agent in self.game.agents if agent != self]
            if len(remaining_agents) == 1:
                self.game.round_in_play = False
            self.game.last_up = remaining_agents[-1] if remaining_agents else None
        if self.game.first_up is self:
            remaining_agents = [agent for agent in self.game.agents if agent != self]
            self.game.first_up = remaining_agents[0] if remaining_agents else None
        self.game.agents.remove(self)

    def bet(self, amount: int):
        if amount > self.balance:
            raise Exception("Not enough balance")
        if amount != self.game.call_amount - self.down_for and amount < 2 * self.game.last_raise:
            raise Exception("Must either call or raise by double previous raise")
        self.balance -= amount
        if self.game.call_amount > self.down_for:
            self.game.last_raise = amount
        self.down_for += amount
        self.game.pot += amount
        self.game.last_up = self
        if self.down_for == self.game.call_amount:
            self.game.round_in_play = False

    def call(self):
        self.bet(self.game.call_amount - self.down_for)

    def all_in(self):
        self.bet(self.balance)


class PokerGame:
    def __init__(self, agents: List[Agent]):
        self.deck = Deck()
        self.agents = deque(agents)  # Using deque for efficient rotation of players
        self.pot = 0
        self.call_amount = 0
        self.last_raise = 0
        self.round_in_play = True
        self.last_up = None
        self.first_up = None
        self.community_cards = []  # Initialize the community cards list
        for agent in agents:
            agent.game = self

    def start_game(self):
        self.deck = Deck()  # Shuffle a new deck
        self.pot = 0
        self.call_amount = 0
        self.last_raise = 0
        self.round_in_play = True
        self.community_cards = []  # Clear community cards at the start of each game

        # Deal two cards to each player
        for agent in self.agents:
            agent.cards = self.deck.deal(2)
            agent.down_for = 0

        self.first_up = self.agents[0]
        self.last_up = self.agents[-1]
        print("Game started. Players have been dealt their cards.")

    def deal_community_cards(self, num):
        self.community_cards.extend(self.deck.deal(num))

    def determine_winner(self):
        best_hands = [(agent, best_hand(agent.cards + self.community_cards)) for agent in self.agents]
        best_hands.sort(key=lambda x: hand_rank(x[1]), reverse=True)
        winning_hand = hand_rank(best_hands[0][1])
        winners = [agent for agent, hand in best_hands if hand_rank(hand) == winning_hand]
        return winners