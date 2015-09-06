import random
from collections import Counter
import numpy as np

################################################################################
# constants
################################################################################
OS_List               = ['Linux', 'Windows', 'Mac', 'Solaris']
OS_List_Letters       = ['L', 'W', 'M', 'S']
Exploits_Per_Player   = 4   # number exploits each player starts game with
Hosts_Per_Player      = 5   # number of hosts on board is this * #players
Detection_Prob        = { 'r':0.05, 'h':0.20, 'b':0.15, 'p':0.25, 's' : 0.30 }
New_Exploit_Prob      = 0.167
# deprecated -- remove these
Patches_Per_OS        = 5   # number each host draws to start (with repl.)
Max_Accounts          = 5   # maximum number of patches allowed (+1)
Max_Patch_Number      = 15  # maximum patch number to be kept in knowledge (+1)

################################################################################
# functions
################################################################################

def pick_exp_int():
    '''Pick a non-negative integer x with probability 2^-x'''
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

def random_exploit():
    return '{}{}'.format(np.random.choice(OS_List_Letters), pick_exp_int())

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
        while True:
            # update counters, game over if did maximum # rounds
            if self.whose_turn == 0:
                self.round += 1
                if self.round == max_rounds:
                    return [self.players[i].name for i in self.players_in]

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
                    return [ self.players[self.players_in[0]].name ]

            # next player's turn
            self.whose_turn = (self.whose_turn + 1) % self.num_players


class Player(object):
    '''Player exposes init, register, observe, and do_round.'''
    def __init__(self, name, strategy):
        self.name     = name
        self.strategy = strategy(self)
        
        self.move_funcs = {'r':self.do_recon,    'c':self.do_clean, 'h':self.do_hack,
                           'b':self.do_backdoor, 'p':self.do_patch, 'd':self.do_ddos,
                           's':self.do_scan}
        self.own = {}
        self.exploits = set(random_exploit() for i in xrange(Exploits_Per_Player))
        
        self.know = { 'notyetdefined':True }
        
    def register(self, game, starting_machine, player_id):
        self.game = game
        self.id   = player_id
        self.own[starting_machine] = 1
        
        # The fields are:
        # {
        #  'OS':array(#machines, #OSs),  
        #  'patches':array(#machines, max-patch-number)
        #  'owns':array(#players, #machines, #accounts)
        #  'exploits':array(#players, #OSs, max-patch-number)
        # }

        self.know = {
            'OS':np.empty((self.game.num_hosts, len(OS_List))),
            'patches':np.empty((self.game.num_hosts, Max_Patch_Number)),
            'owns':np.empty((self.game.num_players,
                                      self.game.num_hosts,
                                      Max_Accounts)),
            'exploits':np.empty((self.game.num_players,
                                          len(OS_List),
                                          Max_Patch_Number)) }
        self.know['OS'].fill(1./len(OS_List))
        self.know['owns'][:,:,0].fill(1. - 1./self.game.num_hosts)
        self.know['owns'][:,:,1].fill(1./self.game.num_hosts)
        self.know['owns'][:,:,2:].fill(0.0)
        # if prob of exploit is 2^-x and pick m exploits, then chance of
        # not picking it ever is (1 - 2^-x)^m, so probability they have it
        # is 1 - (1 - 2^-x)^m
        for i in xrange(Max_Patch_Number):
            self.know['exploits'][:,:,i] = 1 - (1-0.5**i)**Exploits_Per_Player
            self.know['patches'][:,i] = 1 - (1-0.5**i)**Patches_Per_OS

    def do_round(self):
        # Phase 1 - at random obtain a new exploit
        if random.random() < New_Exploit_Prob:
            self.get_new_exploit()
            
        # Phase 2 - start round
        self.strategy.start_round()

        # Phase 3 - get moves
        moves = self.strategy.get_moves()
        
        # Phase 4 - check validity of moves
        assert self.validate_moves(moves), "Invalid moves: {}".format(moves)
        
        # Phase 5 - execute moves
        self.execute_moves(moves)
        
        # Phase 6 - report results and end round
        self.strategy.end_round()

    def get_new_exploit(self):
        pass

    def validate_moves(self, moves):
        '''A valid set of moves obeys the following rules:
        1. No machine is assigned two moves
        2. A machine action is taken from 'rsbhcpd', stored in 'action' field
        3. If a move is 'd' (ddos) it must be the only move and no machine is involved
        4. Except for 'd', each move has a 'from' field, which is an owned acting machine
        5. For 'b', 's', and 'c', no other fields are used
        6. For 'r' and 'h', must also specify 'to' field
        7. For 'h' and 'p', must specify 'exploit' field
        '''
        # special case: empty list of moves is okay
        if len(moves) == 0:
            return True
        
        # every move has an action
        if not all(['action' in m for m in moves]):
            return False

        # in a ddos, only 1 move and specify a valid user
        if 'd' in [m['action'] for m in moves]:  # DDOS case
            return ((len(moves) == 1) and ('user' in moves[0]) and
                    (moves[0]['user'] != self.id) and
                    (moves[0]['user'] in xrange(self.game.num_players)))

        # if not ddos, every move has a from, which must not repeat and be owned
        if not all(['from' in m for m in moves]):
            return False
        movers = Counter([m['from'] for m in moves])
        if set(movers.values()) != set([1]):
            return False
        if any([m['from'] not in self.own]):
            return False
        
        # all actions are valid
        if not all([m['action'] in 'rsbhcpd' for m in moves]):
            return False

        # Recon and Hack specify a target 'to', which must be an actual machine number
        if any([m['action'] in 'rh' and 'to' not in m for m in moves]):
            return False
        if any([m['action'] in 'rh' and m['to'] not in xrange(self.game.num_hosts)]):
            return False
        
        # Hack and Patch specify an exploit
        if any([m['action'] in 'hp' and 'exploit' not in m for m in moves]):
            return False

        return True

    
    def execute_moves(self, moves):
        # each move should return a probability distribution of knowledge states
        # and if it uses "omniscience" then it gives what actually happens (prob distr.)
        pass
    
    def observe(self):
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
        self.player = player

    def start_round(self):
        print self.player.name, self.player.id, "Round", self.player.game.round
        print self.player.own

    def get_moves(self):
        return []

    def end_round(self):
        pass

    def output(self):
        pass

    def display(self, message):
        pass

class AI(Strategy):
    def __init__(self, player):
        pass

    def get_moves(self):
        pass
    
class PlayerStrategy(Strategy):
    def start_round(self):
        print 'Round', self.player.game.round
        print 'name', self.player.name, self.player.id
        print 'own', self.player.own
        print 'exploits', self.player.exploits
        print 'know', self.player.know
        
    def get_moves(self):        
        print("<acting-machine> (R)econ <machine>")
        print("<acting-machine> (C)lean")
        print("<acting-machine> (H)ack <machine> <exploit>")
        print("<acting-machine> (B)ackdoor")
        print("<acting-machine> (P)atch <exploit>")
        print("<acting-machine> (S)can")
        print("(D)DoS <user>")
        
        moves = []  # a list of moves, each is a dictionaries
        # std move format: acting-maching player action parameters (machine/exploit/user)
        while len(moves) < len(self.player.own.keys()):
            move = None
            while move == None:
                move_str = raw_input("\nSelect a move: ")
                move_words = move_str.split()
                if move_words[0] == 'd':
                    return [ {'action':'d', 'user':int(move_words[1])} ]
                if move_words[1] not in 'rchbps':
                    continue
                move = {'from':int(move_words[0]), 'action':move_words[1]}
                if move['action'] in 'rh':
                    move['to'] = int(move_words[2])
                if move['action'] in 'hp':
                    move['exploit'] = move_words[-1]
                moves.append(move)

        print "Moves chosen:", moves
        return moves

    
class Andrews(Strategy):
    pass

class EthanAI(Strategy):
    pass

class JacobAI(Strategy):
    pass

class AndrewNathan(Strategy):
    pass

if __name__ == '__main__':
    players = [ Player('Player', PlayerStrategy),
                Player('Andrew', Andrews),
                Player('Ethan', EthanAI),
                Player('Jacob', JacobAI),
                Player('AN', AndrewNathan) ]
    g=HackAttack(players)
    r = g.play(10)
    print r


'''
    Get off at crab orchard, turn right at end of ramp, left at liberty market.  Just after you go under the bridge, turn left on Cox Valley Rd at Meadow Creek Baptist Church sign.  Turn right at the end (a T).  Turn left at elementary
school at water tower on South 127.

Turn right 
    '''
