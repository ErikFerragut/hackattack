from header import *
from Player import Player
from Strategy import *
from EvaluationStrategy import *
from EvaluationFunctions import *
from collections import Counter

import sys

if len(sys.argv) < 3:
    print "Usage: python Experiment.py <number_of_parts> <which_part>"
    print "\nRuns over all pairs of algorithms and k values, doing only one part of many"
    print "(parts are counted 0-up)"
    
outputfile = open('output.log', 'a')

methods = [('random', RandomStrategy, {})] + \
          [(ef.__name__, EvaluationStrategy, {'f':ef, 'k':k}) for k in [1,2,-2,-3]
           for ef in [net_accounts, net_machines, clean_machines, security] ]

experiments = [ (i1, i2) for i1 in xrange(len(methods)-1)
                for i2 in xrange(i1+1, len(methods)) ]

num_parts  = int(sys.argv[1])
part_starts = [ (len(experiments) * i) / num_parts for i in xrange(num_parts+1) ]
which_part = int(sys.argv[2])

for i in xrange(part_starts[which_part], part_starts[which_part+1]):
    experiment = experiments[i]
    m1, m2 = methods[experiment[0]], methods[experiment[1]]
    print "Pair {}".format(experiment)
    
    case = '{} {} {} {}'.format(m1[0], m1[2], m2[0], m2[2])
    outputfile.write('STARTCASE {}\n'.format(case))
    results = []
    for i in xrange(1, 11):
        print '-'*80
        print ('GAME ' + str(i)).center(80)
        print '-'*80    
        print case
        players = [ Player('player1', m1[1], m1[2]), Player('player2', m2[1], m2[2]) ]
        g = HackAttack(players)
        r = g.play(20, outputfile)
        print r
        results.append(r)

    results2 = Counter(map(tuple, results))
    print results2
    outputfile.write('SUMMARY {} -> {}\n'.format(case, results2))
    outputfile.write('ENDCASE {}\n'.format(case))

