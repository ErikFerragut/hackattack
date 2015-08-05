import random

################################################################################
# constants
################################################################################
OS_List               = ['Linux', 'Windows', 'Mac', 'Solaris']
OS_List_Letters       = ['L', 'W', 'M', 'S']
Exploits_Per_Player   = 4   # number exploits each player starts game with
Hosts_Per_Player      = 5   # number of hosts on board is this * #players
Detection_Prob        = { 'r':0.05, 'h':0.20, 'b':0.15, 'p':0.25, 's' : 0.30 }

# deprecated -- remove these
Vuln_Prob             = 0.2
Exploits_Per_OS       = 5




################################################################################
# functions
################################################################################

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
