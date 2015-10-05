# HACK ATTACK - a cyber hacking game
#
# plans:
# V 3.0 - Refactored to enable evaluation functions

import random
import numpy as np
from collections import Counter
from copy import deepcopy
from itertools import product

from header import *
# from Player import *
# from Strategy import *
# from EvaluationStrategy import *

################################################################################
# HackAttack Class
################################################################################

class HackAttack(object):
    def __init__(self, players):
        '''Create an empty board for the game with uninitialized player objects'''
        self.players = players
        self.num_players = len(players)
        self.num_hosts = Hosts_Per_Player * self.num_players
        self.players_in = range(self.num_players)  # which players are still playing

        self.board_os = [ random.choice(OS_List_Letters)
                          for i in xrange(self.num_hosts) ]
        self.board_patches = [ list(set([ pick_exp_int()
                                          for i in range(Patches_Per_OS) ]))
                                for h in xrange(self.num_hosts) ]

        starting_hosts = choose_without_replacement(
            xrange(self.num_hosts), self.num_players)
        for i in xrange(len(self.players)):
            self.players[i].register(self, starting_hosts[i], i)

        self.round = 0   # number of rounds of the game played so far
        self.whose_turn = 0  # player whose turn it is

    def play(self, max_rounds=100):
        x = np.arange(Max_Accounts)
        while True:            
            # update counters, game over if did maximum # rounds
            if self.whose_turn == 0:
                self.round += 1
                for i in self.players_in:
                    print i, '->', account_difference(self.players[i].know, i)
                if self.round == max_rounds:
                    numacc = { i:len(self.players[i].own)
                                for i in self.players_in }
                    mostacc = max(numacc.values())
                    print numacc
                    return [ i for i in numacc if numacc[i] == mostacc ]

            # if player is out, skip them
            if self.whose_turn not in self.players_in:
                self.whose_turn = (self.whose_turn + 1) % self.num_players
                continue

            # have a player move
            self.players[self.whose_turn].do_round()

            # are they out? -- if so, is game over?
            if len(self.players[self.whose_turn].own) == 0:
                self.players_in.remove(self.whose_turn)
                if len(self.players_in) == 1:
                    return self.players_in # a list with just the winner id

            # next player's turn
            self.whose_turn = (self.whose_turn + 1) % self.num_players




def account_difference(know, pid):
    x = np.arange(Max_Accounts)
    your_accounts = know['owns'][pid].dot(x).sum()
    all_accounts = know['owns'].dot(x).sum()
    return your_accounts * 2 - all_accounts

if __name__ == '__main__':
    from Player import Player
    from Strategy import *
    from EvaluationStrategy import *
    from jacobAttack import *
    
    players = [ # Player('Player', PlayerStrategy),
                # Player('Andrew', Andrews),
                # Player('Ethan', EthanAI),
                # Player('Jacob', JacobAI),
                # Player('AN', AndrewNathan),
                Player('Random', RandomStrategy),
                Player('Eval', EvaluationStrategy, {'f':account_difference,'k':3}) ]

    results = []

    for i in xrange(1, 2):
        print '-'*80
        print ('GAME ' + str(i)).center(80)
        print '-'*80    
        g=HackAttack(players)
        r = g.play(20)
        print r
        results.append(r)

    print Counter(map(tuple,results))

