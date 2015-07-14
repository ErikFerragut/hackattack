import random

def pick_exp_int():
    x = random.random()
    i = 0
    prob = .5
    while x > 0.:
        i+=1
        x -= prob
        prob *=.5
    return i-1
#pick_exp_int()