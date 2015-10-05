from header import *
from copy import deepcopy
from HackAttack import *
from Player import *

class Strategy(object):
    '''The Strategy class represents the player logic or the methods for getting to the
    human player to communicate status and get moves.  It's called Strategy because you
    query it and it gives you the next moves.  Anticipated interfaces are terminal-style,
    gui, and networked.  Also, the AI classes will be Strategies.'''
    def __init__(self, player, strategy_args):
        self.player = player
        self.args = strategy_args

    def know_fuzz(self, playerB, startknow):
        '''Given a know structure fuzz it (i.e., average over possible moves) for
        moves by playerB and return that.'''
        print "debug: know_fuzz"
        new_know = self.player.knows_zeros()
        # all_moves is dict of what each host can do
        all_moves = self.candidate_moves(self.player.know, playerB)
        PB = self.player.game.players[playerB] # use playerB's consider methods
        prob_wt = 1./ sum(map(len, all_moves.values()))
        for host_moving in all_moves:
            for the_move in all_moves[host_moving]:
                nk, pr = PB.consider_moves([the_move], startknow)
                for outcome, prob in zip(nk, pr):
                    if prob == 0.0:
                        continue
                    assert self.player.know_valid(outcome)
                    self.player.add_wtd_know(new_know, outcome, prob * prob_wt)

        assert self.player.know_valid(new_know)
        return new_know
    
        
    def start_round(self):
        '''Start the round, including updating of knowledge to account for other
        players' actions.'''
        print self.player.name, self.player.id, "Round", self.player.game.round

        assert self.player.know_valid(self.player.know)

        print "Starting round"
        
        # update knowledge according to a uniformly random chosen move
        startknow = deepcopy(self.player.know)
        
        assert self.player.know_valid(startknow)
        
        if self.player.game.round > 0:  # or is it 1?
            for i in xrange(self.player.id+1, self.player.game.num_players):
                startknow = self.know_fuzz(i, startknow)
                assert self.player.know_valid(startknow)
        for i in xrange(self.player.id):
            startknow = self.know_fuzz(i, startknow)
            assert self.player.know_valid(startknow)

        # should only do fuzzes consistent with what you *really* know
        # instead, we reset the known stuff (own)
        startknow['owns'][self.player.id, :, :] = 0.0
        for h in xrange(self.player.game.num_hosts):
            a = self.player.own[h] if h in self.player.own else 0
            startknow['owns'][self.player.id, h, a] = 1.0
            
        self.player.know = startknow

    def get_moves(self):
        return []

    def end_round(self):
        pass

    def display(self, message):
        print message

    @staticmethod
    def candidate_moves(know, p):
        '''Return a dictionary of lists of moves to consider given a knowledge
        structure know and the player id (int) p.  The dictionary is sorted by
        the from field in the moves.
        '''
        num_hosts = know['OS'].shape[0]

        all_moves = { }
        # or know['owns'][p, :, 1:].nonzero()[0]
        for F in know['owns'][p,:,1:].nonzero()[0]:
            F_moves = []
            F_moves.append( {'from':F, 'action':'c'} )
            F_moves.append( {'from':F, 'action':'b'} )
            F_moves.append( {'from':F, 'action':'s'} )
            for T in xrange(num_hosts):
                F_moves.append( {'from':F, 'action':'r', 'to':T} )
                for E in zip(*know['exploits'][p,:,:].nonzero()):
                    ex = OS_List_Letters[E[0]] + str(E[1])
                    F_moves.append( {'from':F, 'action':'h', 'to':T, 'exploit':ex} )
                    if T == 0:  # i.e., only do this one time
                        F_moves.append( {'from':F, 'action':'p', 'exploit':ex} )
            all_moves[F] = F_moves
                    
        return all_moves


class RandomStrategy(Strategy):
    def get_moves(self):
        all_moves = self.candidate_moves(self.player.know, self.player.id)
        moves = [ np.random.choice(all_moves[f]) for f in self.player.own ]
        # debug:
        print "Random strategy moves = ", moves
        return moves

class PlayerStrategy(Strategy):
    def start_round(self):
        print 'Round', self.player.game.round
        print 'name', self.player.name, self.player.id
        print 'own', self.player.own
        print 'exploits', self.player.exploits
        # print 'know', self.player.know

    def get_moves(self):
        done = False
        while not done:
            print("<acting-machine> (R)econ <machine>")
            print("<acting-machine> (C)lean")
            print("<acting-machine> (H)ack <machine> <exploit>")
            print("<acting-machine> (B)ackdoor")
            print("<acting-machine> (P)atch <exploit>")
            print("<acting-machine> (S)can")
            # print("(D)DoS <user>")
            print("or e, k, q")

            moves = []  # a list of moves, each is a dictionary
            # std format: acting-maching player action-parameters (machine/exploit/user)
            while len(moves) < len(self.player.own.keys()):
                move = None
                while move == None:
                    move_str = raw_input("\nSelect a move: ")

                    if move_str[0] == 'e':
                        try:
                            embed()  # brings up repl
                        except:
                            pass
                        continue

                    move_words = move_str.split()
                    if move_words[0] == 'k':     # show the knowledge tables
                        print "knowledge\n", self.player.know
                        move = None
                        continue
                    elif move_words[0] == 'q':
                        assert False
                    elif len(move_words) < 2:
                        continue
  
                    if move_words[1] not in 'rchbps':
                        continue
                    move = {'from':int(move_words[0]), 'action':move_words[1]}
                    if move['action'] in 'rh':
                        move['to'] = int(move_words[2])
                    if move['action'] in 'hp':
                        move['exploit'] = move_words[-1]
                    moves.append(move)

            print "Moves chosen:", moves

            done = self.player.validate_moves(moves)
            if not done:
                print "moves were invalid"

        return moves


class Andrews(Strategy):
    pass

class EthanAI(Strategy):
    pass

class JacobAI(Strategy):
    pass

class AndrewNathan(Strategy):
    pass
class MaxEval(Strategy):
	pass
