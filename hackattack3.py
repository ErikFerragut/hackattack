import random

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

def choose_without_replacement(fromthis, thismany):
    '''Return in random order thismany samples from fromthis so that no two are the same.'''
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

        self.board_os = [ random.choice(OS_List_Letters) for i in xrange(self.num_hosts) ]
        self.board_patches = [ list(set([ pick_exp_int() for i in range(Patches_Per_OS) ])) 
                                for h in xrange(self.num_hosts) ]
        
        starting_hosts = choose_without_replacement(xrange(self.num_hosts), self.num_players)
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

    def register(self, game, starting_machine, player_id):
        self.game = game
        self.id   = player_id
        self.own[starting_machine] = 1

    def do_round(self):
        # Phase 1 - at random obtain a new exploit
        if random.random() < New_Exploit_Prob:
            self.get_new_exploit()
            
        # Phase 2 - start round
        self.strategy.start_round()
        
        # Phase 3 - get moves
        moves = self.strategy.get_moves()
        
        # Phase 4 - check validity of moves
        assert self.validate_moves(moves)
        
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
        4. Except for 'd', each move has a 'from' field, which is the acting machine
        5. For 'b', 's', and 'c', no other fields are used
        6. For 'r' and 'h', must also specify 'to' field
        7. For 'h', must specify 'exploit' field
        8. For 'p', must specify 'patch' field
        '''
        HERE HERE HERE
        return True

    def execute_moves(self, moves):
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
    pass

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
