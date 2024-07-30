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
            if self.game.agents[1].down_for == self.game.call_amount:
                self.game.round_in_play = False
            self.game.last_up = self.game.agents[-1]
        if self.game.first_up is self:
            self.game.first_up = self.game.agents[1]
        self.game.agents.remove(self)

    def bet(self, amount: int):
        if amount > self.balance:
            raise Exception("Not enough balance")
        if amount != self.game.call_amount - self.down_for and amount < 2 * self.game.last_raise:
            raise Exception("Must either call or raise by double previous raise")
        self.balance -= amount
        self.game.pot += amount
        self.down_for += amount
        prev_call_amount = self.game.call_amount
        self.game.call_amount = self.down_for
        if self.game.call_amount > prev_call_amount:
            self.game.last_raise = amount
            self.game.last_up = self.game.agents[-1]
        if self.game.last_up is self and self.game.call_amount == prev_call_amount:
            self.game.round_in_play = False
        self.game.agents.rotate(-1)
    
    def check_call(self):
        if self.game.call_amount - self.down_for > self.balance:
            # side pot case
            # implement the side pot logic in other places as well
            pass
        else:
            self.bet(self.game.call_amount - self.down_for)

    def take_action(self):
        if self.balance == 0:
            return
        action = input("Action: ")
        while action.lower() != "call" and action.lower() != "fold":
            action = input("Action: ")
        if action.lower() == "call":
            self.check_call()
        else:
            self.fold()
        # I just put call and fold as user actions for now


class PokerGame:
    def __init__(self, agents: List[Agent]):
        if len(agents) > 22 or len(agents) < 2:
            raise Exception("Max of 22 players min of 2 players per game")
        for agent in agents:
            if agent.balance < 100:
                raise Exception("Players must have at least 100")
        self.agents = deque(agents)
        self.deck = Deck()
        self.community_cards = []
        self.pot = 0
        self.sidepots = {}
        self.call_amount = 0
        self.last_raise = 0
        self.round_in_play = False
        self.first_up = agents[0]
        self.last_up = agents[-1]
    
    def __get_player_with_winning_hand(self):
        hands = {agent : hand for (agent, hand) in zip(self.agents, [best_hand(a.hand) for a in self.agents])}
        # also account for 2 players in a tie
        return max(hands, key=lambda player: hand_rank(best_hand(hands[player])))
    
    def play_game(self):
        self.agents[0].bet(50)
        self.agents[0].bet(100)
        for agent in self.agents:
            agent.cards = self.deck.deal(2)
        self.round_in_play = True
        while self.round_in_play():
            self.agents[0].take_action()
        self.last_raise = 0
        self.community_cards += self.deck.deal(3)
        for i in range(3):
            while self.agents[0] is not self.first_up:
                self.agents.rotate(-1)
            self.last_up = self.agents[-1]
            self.round_in_play = True
            while self.round_in_play():
                self.agents[0].take_action()
            if i < 2:
                self.last_raise = 0
                self.community_cards += self.deck.deal(1)
        winner = self.__get_player_with_winning_hand()
        winner.balance += self.pot
        # account for draw case
