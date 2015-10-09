from header import *
from Player import Player
from Strategy import *
from EvaluationStrategy import *
from EvaluationFunctions import *
from collections import Counter

outputfile = open('output.log', 'a')


methods = [('random', RandomStrategy, {})] + \
          [(ef.__name__, EvaluationStrategy, {'f':ef, 'k':k}) for k in [1,2,-2,-3]
           for ef in [net_accounts, net_machines, clean_machines, security] ]

for i1, m1 in enumerate(methods):
    for m2 in methods[i1+1:]:
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

