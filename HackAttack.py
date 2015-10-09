# HACK ATTACK - a cyber hacking game
#
# plans:
# V 3.0 - Refactored to enable evaluation functions

import random
import numpy as np
from collections import Counter
from copy import deepcopy
from itertools import product
import time

from header import *

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

    def play(self, max_rounds=100, outputlog = None):
        start_time = time.time()
        while True:            
            # update counters, game over if did maximum # rounds
            if self.whose_turn == 0:
                self.round += 1
                if self.round == max_rounds:
                    break
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
                    break
                    return self.players_in # a list with just the winner id

            # next player's turn
            self.whose_turn = (self.whose_turn + 1) % self.num_players

        numacc = {i:len(self.players[i].own) for i in self.players_in}
        mostacc = max(numacc.values())
        winners = [ i for i in numacc if numacc[i] == mostacc ]
        outputstr = "RESULT {} rounds winners {} exploits {} {} time {}".format(
            self.round, winners, 
            sorted(self.players[0].exploits), sorted(self.players[1].exploits), 
            time.time() - start_time)
        print outputstr
        if outputlog != None:
            outputlog.write(outputstr + '\n')
            outputlog.flush()
            
        return winners

if __name__ == '__main__':
    from Player import Player
    from Strategy import *
    from EvaluationStrategy import *
    from EvaluationFunctions import *

    import sys
    print sys.argv

    # would be pretty easy to change to allow more than 2 strategies
    
    if len(sys.argv) != 5:
        players = [ Player('Random', RandomStrategy),
                    Player('Eval', EvaluationStrategy, {'f':nathaniscool,'k':3}) ]
    elif len(sys.argv) == 5:
        for i in [1,3]:
            assert sys.argv[i].startswith('mixture') or sys.argv[i] in globals(), \
              "Function {} undefined; choices are {}".format(
                sys.argv[i], ['your_accounts', 'net_accounts', 'your_machines',
                              'net_machines', 'clean_machines', 'security',
                              'mixtureA:B:C:D'])
            try:
                k = int(sys.argv[i+1])
            except ValueError:
                assert False, "k-ply param {} non-int".format(sys.argv[i+1])
        players = []
        for i in [1,3]:
            if sys.argv[i].lower() == 'random': # ignores the k-ply parameter
                players.append( Player('Random{}'.format(i//2), RandomStrategy) )
            elif sys.argv[i].startswith('mixture'):
                a,b,c,d = map(float, sys.argv[i][7:].split(':'))
                evalfunc = get_mixture_eval(a,b,c,d)
                players.append( Player('mixture{}'.format(i//2), EvaluationStrategy,
                                       {'f':evalfunc, 'k':int(sys.argv[i+1])} ) )
            else:
                players.append( Player('{}{}'.format(sys.argv[i], i//2),
                                       EvaluationStrategy, {'f':globals()[sys.argv[i]],
                                                            'k':int(sys.argv[i+1])} ) )
            
    results = []

    outputfile = open('output.log', 'a')
    for i in xrange(1, 2):
        print '-'*80
        print ('GAME ' + str(i)).center(80)
        print '-'*80    
        g=HackAttack(players)
        r = g.play(20, outputfile)
        print r        
        results.append(r)

    results2 = Counter(map(tuple,results))
    print results2
    outputfile.write('OUTCOME {} -> {}\n'.format(sys.argv, results2))
    
