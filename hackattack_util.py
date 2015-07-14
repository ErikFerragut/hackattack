import random

def pick_exp_int():
    x = random.random()
    #print x
    i = 0
    prob = .5
    while x > 0.:
        i+=1
        x -= prob
        #print x
        prob *=.5
    return i-1
#pick_exp_int()