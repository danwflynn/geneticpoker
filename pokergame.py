from typing import List
from deck import *
from collections import deque
from policy import *


class Agent:
    def __init__(self, name: str, stats: List[np.ndarray]):
        self.name = name
        self.stats = stats
        self.balance = 10000
        self.down_for = 0
        self.cards = []
        self.game = None
        self.games_won = 0

    def fold(self):
        print(f"{self.name}: fold")
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
        print(f"{self.name}: bet {amount}")
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
        print(f"{self.name}: check/call")
        if self.game.call_amount - self.down_for > self.balance:
            self.game.pot += self.balance
            self.down_for += self.balance
            self.balance = 0
            sp = []
            for a in self.game.agents:
                if a.balance > 0:
                    sp.append(a)
            self.game.current_sidepot = tuple(sp)
            self.game.sidepots[self.game.current_sidepot] = 0
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
            hand_ind = get_hand_index(self.cards[0], self.cards[1]) if len(self.game.community_cards) == 0 else \
            hand_rank(best_hand(self.cards + self.game.community_cards))[0]
            wealth_ind = 0
            if (self.game.call_amount - self.down_for) / self.balance > 0.9:
                wealth_ind = 9
            elif (self.game.call_amount - self.down_for) / self.balance > 0.8:
                wealth_ind = 8
            elif (self.game.call_amount - self.down_for) / self.balance > 0.7:
                wealth_ind = 7
            elif (self.game.call_amount - self.down_for) / self.balance > 0.6:
                wealth_ind = 6
            elif (self.game.call_amount - self.down_for) / self.balance > 0.5:
                wealth_ind = 5
            elif (self.game.call_amount - self.down_for) / self.balance > 0.4:
                wealth_ind = 4
            elif (self.game.call_amount - self.down_for) / self.balance > 0.3:
                wealth_ind = 3
            elif (self.game.call_amount - self.down_for) / self.balance > 0.2:
                wealth_ind = 2
            elif (self.game.call_amount - self.down_for) / self.balance > 0.1:
                wealth_ind = 1
            action_space = None
            if len(self.game.community_cards) == 0:
                action_space = self.stats[0][hand_ind][wealth_ind]
            elif len(self.game.community_cards) == 3:
                action_space = self.stats[1][hand_ind][wealth_ind]
            elif len(self.game.community_cards) == 4:
                action_space = self.stats[2][hand_ind][wealth_ind]
            else:
                action_space = self.stats[3][hand_ind][wealth_ind]
            action = np.random.choice(np.arange(13), p=action_space)
            if self.game.call_amount - self.down_for == 0 and action == 0:
                action = 1
            if action == 0:
                self.fold()
            elif action == 1 or self.balance < 2 * self.game.last_raise:
                self.check_call()
            else:
                self.bet((2 * self.game.last_raise) + (((action - 2) / 10) * (self.balance - (2 * self.game.last_raise))))


class PokerGame:
    def __init__(self, agents: deque[Agent]):
        if len(agents) > 22 or len(agents) < 2:
            raise Exception("Max of 22 players min of 2 players per game")
        for agent in agents:
            if agent.balance < 100:
                raise Exception("Players must have at least 100")
            agent.game = self
        self.agents = agents
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
        agent_ranks = {agent : hand for (agent, hand) in 
                       zip(self.agents, [hand_rank(best_hand(a.cards + self.community_cards)) for a in self.agents])}
        max_rank = max(agent_ranks.values())
        return [a for a in agent_ranks.keys() if agent_ranks[a] == max_rank]
    
    def play_game(self):
        def end_early():
            self.agents[0].games_won += 1
            self.agents[0].balance += self.pot
            for sidepot in self.sidepots.keys():
                if self.agents[0] in sidepot:
                    self.agents[0].balance += self.sidepots[sidepot]
            for a in self.agents:
                a.cards = []
                a.down_for = 0
        self.agents[0].bet(50)
        self.agents[0].bet(100)
        for agent in self.agents:
            agent.cards = self.deck.deal(2)
        self.round_in_play = True
        while self.round_in_play:
            self.agents[0].take_action()
        if len(self.agents) == 1:
            end_early()
            return
        self.last_raise = 0
        self.community_cards += self.deck.deal(3)
        for i in range(3):
            while self.agents[0] is not self.first_up:
                self.agents.rotate(-1)
            self.last_up = self.agents[-1]
            self.round_in_play = True
            while self.round_in_play:
                self.agents[0].take_action()
            if i < 2:
                if len(self.agents) == 1:
                    end_early()
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
            winner.games_won += 1
            winner.balance += winnings[winner]
        for a in self.agents:
            a.cards = []
            a.down_for = 0