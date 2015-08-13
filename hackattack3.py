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
Patches_Per_OS       = 5

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


################################################################################
# Game Class
################################################################################

class Game(object):    
    def __init__(self, players):
        '''Create an empty board for the game with uninitialized player objects'''
        self.players = players
        self.num_players = len(players)
        self.num_hosts = Hosts_Per_Player * self.num_players

        self.board_os = [ random.choice(OS_List_Letters) for i in xrange(self.num_hosts) ]
        self.board_patches = [ list(set([ pick_exp_int() for i in range(Patches_Per_OS) ])) 
                                for h in xrange(self.num_hosts) ]
        
        starting_hosts = choose_without_replacement(xrange(self.num_hosts), self.num_players)
        for i in xrange(len(self.players)):
            self.players[i].start_player(self, starting_hosts[i], i)

        self.round = 0   # number of rounds of the game played so far
        self.whose_turn = 0  # player whose turn it is
        
    def play(self):
        pass

class Player(object):
    def __init__(self, name, interface):
        self.move_funcs = {'r':self.do_recon,    'c':self.do_clean, 'h':self.do_hack,
                           'b':self.do_backdoor, 'p':self.do_patch, 'd':self.do_ddos,
                           's':self.do_scan}
        pass

    def register(self, game, player_id, starting_machine):
        pass

    def observe(self):
        pass

    def do_round(self):
        pass

    def do_scan(self, move):
        pass
    
    def do_recon(self,move):
        pass
    
    def do_clean(self,move):
        pass
    
    def do_hack(self,move):
        pass
    
    def do_backdoor(self,move):
        pass
    
    def do_patch(self,move):
        pass
    
    def do_ddos(self,move):
        pass

class Strategy(object):
    '''The Strategy class represents the player logic or the methods for getting to the
    human player to communicate status and get moves.  It's called Strategy because you
    query it and it gives you the next moves.  Anticipated interfaces are terminal-style,
    gui, and networked.  Also, the AI classes will be Strategies.'''
    def __init__(self, player):
        pass

    def start_round(self):
        pass
    
    def display(self, message):
        pass

    def get_moves(self):
        pass

    def output(self):
        pass

    def end_round(self):
        pass

class AI(Strategy):
    def __init__(self, player):
        pass

    def get_moves(self):
        pass
    

if __name__ == '__main__':
    players = [ Player('Player', PlayerStrategy),
                Player('Andrew', Andrews),
                Player('Ethan', EthanAI),
                Player('Jacob', JacobAI),
                Player('AN', AndrewNathan) ]
    g=Game(players)
    r = g.play()
    print r
