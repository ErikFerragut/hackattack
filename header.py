import random
import numpy as np


################################################################################
# constants
################################################################################
OS_List               = ['Linux', 'Windows', 'Mac', 'Solaris']
OS_List_Letters       = ['L', 'W', 'M', 'S']
Exploits_Per_Player   = 6   # number exploits each player starts game with
Hosts_Per_Player      = 5   # number of hosts on board is this * #players
Detection_Prob        = { 'r':0.05, 'h':0.20, 'b':0.15, 'p':0.25, 's' : 0.30 }
New_Exploit_Prob      = 0.167
Patches_Per_OS        = 3   # number each host draws to start (with repl.)
Max_Accounts          = 5   # maximum number of patches allowed (+1)
Max_Patch_Number      = 15  # maximum patch number to be kept in knowledge (+1)
TOL                   = 1e-5  # for checking 'know' is stochastic and in bounds
################################################################################
# functions
################################################################################

def pick_exp_int():
    '''Pick a non-negative integer x with probability 2^-x'''
    x = random.random()
    i = 0
    prob = .5
    while x > 0.:
        i+=1
        x -= prob
        prob *=.5
    return i-1

def random_exploit():
    return '{}{}'.format(np.random.choice(OS_List_Letters), pick_exp_int())

def choose_without_replacement2(fromthis, thismany):
    thismany = int(thismany)
    this2 = [ a for a in fromthis ]
    random.shuffle(this2)
    return this2[:thismany]

def choose_without_replacement(fromthis, thismany):
    '''Return in random order thismany samples from fromthis
    so that no two are the same.'''
    assert thismany < len(fromthis)
    choices = set([])
    while len(choices) <= thismany:
        choices.add(random.choice(fromthis))
    choices = list(choices)
    random.shuffle(choices)
    return choices
