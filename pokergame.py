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
        if len(self.game.sidepots.values()) == 0:
            self.game.pot += amount
        else:
            self.game.sidepots[self.game.current_sidepot] += amount
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
            self.game.pot += self.balance
            self.down_for += self.balance
            self.balance = 0
            sp = []
            for a in self.game.agents:
                if a.balance > 0:
                    sp.append(a)
            self.game.current_sidepot = sp
            self.game.sidepots[sp] = 0
            if self.game.last_up is self:
                self.game.round_in_play = False
        else:
            self.bet(self.game.call_amount - self.down_for)

    def take_action(self):
        if self.balance == 0:
            self.game.agents.rotate(-1)
            if self.game.last_up is self:
                self.game.round_in_play = False
        else:
            # agent policy
            pass


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
        self.current_sidepot = None
        self.sidepots = {}
        self.call_amount = 0
        self.last_raise = 0
        self.round_in_play = False
        self.first_up = agents[0]
        self.last_up = agents[-1]
    
    def __get_players_with_winning_hand(self):
        agent_ranks = {agent : hand for (agent, hand) in zip(self.agents, [hand_rank(best_hand(a.hand)) for a in self.agents])}
        max_rank = max(agent_ranks.values())
        return [a for a in agent_ranks.keys() if agent_ranks[a] == max_rank]
    
    def play_game(self):
        self.agents[0].bet(50)
        self.agents[0].bet(100)
        for agent in self.agents:
            agent.cards = self.deck.deal(2)
        self.round_in_play = True
        while self.round_in_play():
            self.agents[0].take_action()
        if len(self.agents == 1):
            self.agents[0].balance += self.pot
            for sidepot in self.sidepots.keys():
                if self.agents[0] in sidepot:
                    self.agents[0].balance += self.sidepots[sidepot]
            return
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
                if len(self.agents == 1):
                    self.agents[0].balance += self.pot
                    for sidepot in self.sidepots.keys():
                        if self.agents[0] in sidepot:
                            self.agents[0].balance += self.sidepots[sidepot]
                    return
                self.last_raise = 0
                self.community_cards += self.deck.deal(1)
        winners = self.__get_players_with_winning_hand()
        winnings = {}
        for a in winners:
            winnings[a] = self.pot // len(winners)
            for sidepot in self.sidepots.keys():
                if a in sidepot:
                    winnings[a] += self.sidepots[sidepot] // len([x for x in sidepot if x in winners])
        for winner in winners:
            winner.balance += winnings[winner]
        for a in self.agents:
            a.cards = []
            a.down_for = 0
