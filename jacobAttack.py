from header import *

def jacobAttack(know,pid):
    num_computers = know['owns'].shape[1]
    howmanycomputersyouhave = 0
    for computer in xrange(num_computers):
        howmanycomputersyouhave += know['owns'][pid, computer, 1:].sum()
    return howmanycomputersyouhave