# HACK ATTACK - a cyber hacking game
#
# plans:
# V 3.0 - Refactored to enable evaluation functions

import random
import numpy as np
from collections import Counter
from copy import deepcopy
from itertools import product

try:
    from IPython import embed    # only works in ipython
except:
    pass

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
        x = np.arange(Max_Accounts)
        while True:            
            # update counters, game over if did maximum # rounds
            if self.whose_turn == 0:
                self.round += 1
                for i in self.players_in:
                    print i, '->', account_difference(self.players[i].know, i)
                if self.round == max_rounds:
                    numacc = { i:len(self.players[i].own)
                                for i in self.players_in }
                    mostacc = max(numacc.values())
                    print numacc
                    return [ i for i in numacc if numacc[i] == mostacc ]

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
                    return self.players_in # a list with just the winner id

            # next player's turn
            self.whose_turn = (self.whose_turn + 1) % self.num_players


class Player(object):
    '''Player exposes init, register, observe, and do_round.'''
    def __init__(self, name, strategy, strategy_args = {}):
        'Create a player with name (string) using a given Strategy'
        self.name     = name
        self.strategy = strategy(self, strategy_args)

        self.move_funcs = {'r':self.do_recon,    'c':self.do_clean, 'h':self.do_hack,
                           'b':self.do_backdoor, 'p':self.do_patch, # 'd':self.do_ddos,
                           's':self.do_scan}
        self.consider_funcs = {'r':self.consider_recon, 'c':self.consider_clean,
                               'h':self.consider_hack,  'b':self.consider_backdoor,
                               'p':self.consider_patch, # 'd':self.consider_ddos,
                               's':self.consider_scan}
        self.own = {}
        self.exploits = set(random_exploit() for i in xrange(Exploits_Per_Player))

        self.know = { 'notyetdefined':True }

    @staticmethod
    def knows_equal(know1, know2):
        '''Return True if they are equal and False if not; may throw exception if one
        is not a knowledge dictionary.'''
        assert know1.viewkeys() == know2.viewkeys()
        for k in know1:
            if not (know1[k] == know2[k]).all():
                return False
        return True

    def know_valid(self, know = None):
        '''Returns true if it has the right fields and matrix sizes and satisfies
        the stochasticity requirements.  With know = None (default) computes it
        for the player's self.know.'''
        if know == None:
            know = self.know

        result = True
        # check keys are good
        if know.viewkeys() != set(['OS', 'patches', 'owns', 'exploits']):
            print "Know structure has key mismatch"
            result = False

        # check shapes are good
        if 'OS' in know:
            if (know['OS'].shape != (self.game.num_hosts, len(OS_List))):
                print "Know['OS'] wrong shape"
                result = False
            else:
                s = np.abs(know['OS'].sum(1) - 1.0) < TOL
                b = (know['OS'] <= 1.0+TOL) * (know['OS'] >= -TOL)
                if not np.all( s ):
                    print "Failed sum in OS"
                    result = False
                if not np.all( b ):
                    print "Failed bounds in OS"
                    result = False

        if 'patches' in know:
            if (know['patches'].shape != (self.game.num_hosts, Max_Patch_Number)):
                print "Know['patches'] wrong shape"
                result = False
            else:
                b = (know['patches'] <= 1.0+TOL) * (know['patches'] >= -TOL)
                if not np.all( b ):
                    print "Failed bounds in patches"
                    result = False

        if 'owns' in know:
            if (know['owns'].shape != (self.game.num_players, self.game.num_hosts,
                                      Max_Accounts)):
                print "Know['owns'] wrong shape"
                result = False
            else:
                s = np.abs(know['owns'].sum(2) - 1.0) < 1e-5
                b = (know['owns'] <= 1.0+TOL) * (know['owns'] >= -TOL)
                if not np.all( s ):
                    print "Failed sum in owns"
                    result = False
                if not np.all( b ):
                    print "Failed bounds in owns"
                    result = False

        if 'exploits' in know:
            if (know['exploits'].shape != (self.game.num_players, len(OS_List),
                                           Max_Patch_Number)):
                print "Know['exploits'] wrong shape"
                result = False
            else:
                b = (know['exploits'] <= 1.0+TOL) * (know['exploits'] >= -TOL)
                if not np.all( b ):
                    print "Failed bounds in exploits"
                    result = False
                
        return result


    @staticmethod
    def knows_diff(know1, know2):
        '''Return a dictionary { key: { (i,j) : (know1_val, know2_val) } } of diffs'''
        assert know1.viewkeys() == know2.viewkeys()
        try:
            return { k : { v : (know1[k][i,j], know2[k][v])
                        for v in zip(* (know1[k] - know2[k]).nonzero()) }
                    for k in know1 }
        except:
            print '-'*80
            for k in know1:
                print k
                K = know1[k] - know2[k]
                NZ = K.nonzero()
                Z = zip(* NZ)
            assert False

            
    def knows_zeros(self):
        return { 'OS':np.zeros((self.game.num_hosts, len(OS_List))),
                 'patches':np.zeros((self.game.num_hosts, Max_Patch_Number)),
                 'owns':np.zeros((self.game.num_players,
                                  self.game.num_hosts,
                                  Max_Accounts)),
                 'exploits':np.zeros((self.game.num_players,
                                      len(OS_List),
                                      Max_Patch_Number)) }


    @staticmethod
    def add_wtd_know( know1, know2, know2_wt ):
        ''' know1 += know2 * know2_wt '''
        for k in know1:
            know1[k] += know2[k] * know2_wt

    
        
    def register(self, game, starting_machine, player_id):
        '''After the game starts, the player is registered, which sets its id in
        the game, and also the machine it starts with an account on'''
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
        self.know['owns'][self.id, :, :] = 0.0
        self.know['owns'][self.id, :, 0] = 1.0
        self.know['owns'][self.id, starting_machine, 0] = 0.0
        self.know['owns'][self.id, starting_machine, 1] = 1.0
        
        # if prob of exploit is 2^-x and pick m exploits, then chance of
        # not picking it ever is (1 - 2^-x)^m, so probability they have it
        # is 1 - (1 - 2^-x)^m
        for i in xrange(Max_Patch_Number):
            self.know['exploits'][:,:,i] = 1 - (1-0.5**(i+1))**Exploits_Per_Player
            self.know['patches'][:,i] = 1 - (1-0.5**(i+1))**Patches_Per_OS

        self.know['exploits'][self.id, :, :] = 0.0
        for e in self.exploits:
            self.know['exploits'][self.id, OS_List_Letters.index(e[0]),
                                  int(e[1:])] = 1.0
            
        # knowledge of self must be kept current for multi-ply to work right

    def do_round(self):
        assert self.know_valid()
        
        # Phase 1 - at random obtain a new exploit
        if random.random() < New_Exploit_Prob:
            self.get_new_exploit()

        # Phase 2 - start round
        assert self.know_valid()
        self.strategy.start_round()

        # Phase 3 - get moves
        assert self.know_valid()
        moves = self.strategy.get_moves()

        # Phase 4 - check validity of moves
        assert self.validate_moves(moves), "Invalid moves: {}".format(moves)

        # Phase 5 - execute moves
        assert self.know_valid()
        self.execute_moves(moves)

        # Phase 6 - report results and end round
        assert self.know_valid()
        self.strategy.end_round()
        assert self.know_valid()

    def get_new_exploit(self):
        if random.random() < New_Exploit_Prob:
            print "New exploit for {}".format(self.name)
            ne = random_exploit()
            self.exploits.add(ne)  # no check for duplicates
            self.know['exploits'][self.id, OS_List_Letters.index(ne[0]),
                                  int(ne[1:])] = 1.0

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

        # exploits used are exploits you have
        eu = [ m['exploit'] for m in moves if m['action'] == 'h' ]
        if not all([e in self.exploits for e in eu]):
            return False

        return True


    def execute_moves(self, moves):
        '''Given a list of moves, carry them out in order using the do* methods
        given by the self.move_funcs dictionary.'''
        for m in moves:
            print "Carrying out move", m
            self.know = self.move_funcs[m['action']](m, self.know)
            assert self.know_valid()
            
    def consider_moves(self, moves, startknow):
        '''Given a list of moves, consider them in order using the consider* methods
        given by the self.consider_funcs dictionary.  This does a full
        brute-force expansion of all the outcomes for each move.
        Returns new knows and probs in two (paired) lists.
        '''
        newknows = [ deepcopy(startknow) ]
        newprobs = [ 1.0 ]
        for m in moves:
            nextnewknows = []
            nextnewprobs = []
            for nk_old, pr_old in zip(newknows, newprobs):
                nk, pr = self.consider_funcs[m['action']](m, nk_old)
                nextnewknows.extend(nk)
                nextnewprobs.extend( [p * pr_old for p in pr ] )

            newknows, newprobs = nextnewknows, nextnewprobs

        return newknows, newprobs
            

    def working_attacks(self, host):
        '''return a list of the short codes for attacks this player has
        that work on machine host'''
        return [ e for e in self.exploits
                 if self.game.board_os[host] == e[0] and int(e[1:]) not in
                  self.game.board_patches[host] ]
    
    def do_scan(self, move, know):
        '''Scan a machine to see what other players are on there.'''

        print "do_scan"
        new_know = deepcopy(know)
        host = move['from']
        
        for s in xrange(self.game.num_players):
            if s == self.id:
                continue
            if host in self.game.players[s].own:
                num_accounts = self.game.players[s].own[host]
                if random.random() < Detection_Prob['s']:
                    self.game.players[s].detect( ('s', self.id, host) )
            else:
                num_accounts = 0
                
            # only impact is updated knowledge
            new_know['owns'][s, host, :] = 0.
            new_know['owns'][s, host, num_accounts] = 1.

        # test:
        nk, pr = self.consider_scan(move, know)
        if not (any(self.knows_equal(new_know, nnkk) for nnkk in nk) and
                np.allclose(sum(pr), 1.0), "prob sum = {} (not 1)".format(sum(pr))):
            print "Use models.knows_diff to compare"
            embed()
        
        return new_know


    def consider_scan(self, move, know):
        # each other player could have some number of accounts on the machine
        # we must construct the cartesian product of those possibilities
        new_knows = []
        new_probs = []
        host = move['from']
        player_accounts = [ know['owns'][P, host, :].nonzero()[0]
                            for P in xrange(self.game.num_players) ]

        for account_nums in product( *player_accounts ):
            new_probs.append( np.product( [ know['owns'][i, host, a]
                                for i,a in enumerate(account_nums) ] ) )
            new_know = deepcopy(know)
            for P in xrange(self.game.num_players):
                new_know['owns'][P, host, :] = 0.0
                new_know['owns'][P, host, account_nums[P]] = 1.0

            new_knows.append(new_know)
            
        return new_knows, new_probs
        

    def do_recon(self, move, know):
        '''Do a recon move, updating states and returning an updated knowledge'''
        print "do_recon"
        
        new_know = deepcopy(know)

        # Learn the OS
        host_os = OS_List_Letters.index(self.game.board_os[move['to']])
        self.strategy.display("Machine {} runs {} OS".format(
            move['to'], OS_List[host_os]))
        for i in xrange(len(OS_List_Letters)):
            if i == host_os:
                new_know['OS'][move['to'], i] = 1.0
            else:
                new_know['OS'][move['to'], i] = 0.0

        # Learn which exploits work
        attacks = self.working_attacks(move['to'])

        for e in self.exploits:
            if OS_List_Letters[host_os] == e[0]:
                if e in attacks:
                    self.strategy.display("Machine {} is vulnerable to {}".format(
                        move['to'], e))
                    new_know['patches'][move['to'], int(e[1])] = 0.0
                else:
                    self.strategy.display("Machine {} is patched against {}".format(
                        move['to'], e))
                    new_know['patches'][move['to'], int(e[1])] = 1.0
            else:
                self.strategy.display("No information on exploit {}".format(e))

        # Chance of detection
        for playerB in xrange(self.game.num_players):
            if random.random() < Detection_Prob['r']:
                if move['to'] in self.game.players[playerB].own:
                    self.game.players[playerB].detect(
                        ('r', self.id, move['from'], move['to']) )

        # we don't track estimates of other players' knowledge in this knowledge sys
        # other player will update their knowledge when detect is called (above)

        # test:
        nk, pr = self.consider_recon(move, know)
        if not (any(self.knows_equal(new_know, nnkk) for nnkk in nk) and
                np.allclose(sum(pr), 1.0), "prob sum = {} (not 1)".format(sum(pr))):
            print "Use models.knows_diff to compare"
            embed()
            
        return new_know

    def consider_recon(self, move, know):
        '''Like do_recon, but don't do it. Instead, return a list of new knowledges
        and their corresponding probabilities in an array.'''
        # For each OS, loop over exploits and consider the possible outcomes
        new_knows = []
        new_probs = []
        for os in xrange(len(OS_List)):
            prob_os = know['OS'][move['to'], os]
            if prob_os > 0.0:
                prob_patched = [ (int(e[1:]), know['patches'][move['to'],int(e[1:])])
                                 for e in self.exploits
                                 if e[0] == OS_List_Letters[os] ]
                outcomes = list(product(*( [[False, True]]*len(prob_patched) ) ))
                for o in outcomes:
                    # create the new_know (and append)
                    new_know = deepcopy(know)
                    prob_outcome = 1.0
                    new_know['OS'][move['to'], :] = 0.0    # learn OS
                    new_know['OS'][move['to'], os] = 1.0
                    for p,oo in zip(prob_patched, o):
                        if oo:
                            new_know['patches'][move['to'], p[0]] = 1.0
                            prob_outcome *= p[1]
                        else:
                            new_know['patches'][move['to'], p[0]] = 0.0
                            prob_outcome *= 1.0 - p[1]
                        
                    new_knows.append(new_know)
                    new_probs.append(prob_os * prob_outcome)

        return new_knows, new_probs

    def do_clean(self, move, know):
        print 'do_clean'
        new_know = deepcopy(know)

        # for each other player remove up to how many accounts this player has
        playerAaccts = self.own[move['from']]
        for playerB in xrange(self.game.num_players):
            if playerB == self.id:  # don't remove your own accounts!
                continue
            if move['from'] in self.game.players[playerB].own:
                playerBaccts = self.game.players[playerB].own[move['from']]
            else:
                playerBaccts = 0
            newBaccts = max(playerBaccts - playerAaccts, 0)
            # -- remove accts (and delete key if #acct -> 0)
            if newBaccts > 0:
                self.game.players[playerB].own[move['from']] = newBaccts
            else:
                if move['from'] in self.game.players[playerB].own:
                    self.game.players[playerB].own.pop( move['from'] )
            # -- and update knowledge
            removed = playerBaccts - newBaccts
            if playerBaccts < playerAaccts:  # then they must be off the machine
                new_know['owns'][playerB, move['from'], :] = 0.0
                new_know['owns'][playerB, move['from'], 0] = 1.0
            elif removed == playerAaccts: # may have as many as max - removed
                # new prob(m) = prob(m + removed), normalized
                print new_know['owns'][playerB,move['from'],:]
                new_know['owns'][playerB, move['from'], :Max_Accounts-removed] = \
                  new_know['owns'][playerB, move['from'], removed:]
                if new_know['owns'][playerB, move['from'], :].sum() == 0.0:
                    print "WARNING -- knowledge failure in do_clean"
                    new_know['owns'][playerB, move['from'], :] = 1.0
                new_know['owns'][playerB, move['from'], :] /= \
                  new_know['owns'][playerB, move['from'], :].sum()
            # -- and send detection notice to those players (100% chance)
            if removed > 0:
                self.game.players[playerB].detect(
                    ('c', self.id, move['from'], playerBaccts, newBaccts) )

        # test:
        nk, pr = self.consider_clean(move, know)
        if not (any(self.knows_equal(new_know, nnkk) for nnkk in nk) and
                np.allclose(sum(pr), 1.0), "prob sum = {} (not 1)".format(sum(pr))):
            print "Use models.knows_diff to compare"
            embed()
        
        return new_know
    

    def consider_clean_1(self, move, know):
        new_knows = []
        new_probs = []

        assert self.know_valid(know)
        
        host = move['from']
        # this is wrong -- it assumes you know # accounts, only good for yourself
        acct = know['owns'][self.id, host, :].nonzero()[0][0]
        # for each player think whether they have fewer or more than removed
        outcomes = list(product(*( [[False, True]]*self.game.num_players ) ))
        outcomes = [ o for o in outcomes if o[self.id] ] # avoid doubling up
        for outcome in outcomes:  # outcome is a list of T and F
            # True means removed < playerAaccts, False means equal
            new_prob = np.prod([know['owns'][p,host,:acct].sum() if o else
                                know['owns'][p,host,acct:].sum()
                                for p,o in enumerate(outcome)
                                if p != self.id])
            if new_prob > 0.0:
                new_know = deepcopy(know)
                for p,o in enumerate(outcome):
                    if p == self.id:
                        continue
                    if o: # true case: fewer than acct (incl. not on it), so goes to 0
                        new_know['owns'][p,host,:] = 0.0
                        new_know['owns'][p,host,0] = 1.0
                    else: # false case: move probs down and renormalize
                        temp = new_know['owns'][p,host,acct:]
                        ts = temp.sum()
                        if ts > 0.0:
                            new_know['owns'][p,host,:] = 0.0
                            new_know['owns'][p,host,:Max_Accounts - acct] = temp
                            new_know['owns'][p,host,:] /= ts
                        else:
                            # this is considered an impossibility
                            new_prob = 0.0

            if new_prob > 0.0:  # could have become 0.0 in previous block
                new_knows.append(new_know)
                new_probs.append(new_prob)

        assert all(self.know_valid(nk) for nk in new_knows)
        return new_knows, new_probs
    
    def consider_clean(self, move, know):
        new_knows = []
        new_probs = []

        assert self.know_valid(know)
        
        host = move['from']
        # for each number of accounts you might remove, remove that number from each
        for acct in know['owns'][self.id, host, :].nonzero()[0]:
            new_prob = know['owns'][self.id, host, acct]
            new_know = deepcopy(know)

            for p in xrange(self.game.num_players):
                if p == self.id:
                    continue
                
                # e.g., if acct = 2 and Max_Accounts = 5, then
                # -- prob of having zero is prob there was 0, 1, or 2
                new_know['owns'][p,host,0] = new_know['owns'][p,host,:acct+1].sum()
                # -- prob of having 1 is prob there was 3
                # -- prob of having 2 is prob there was 4
                new_know['owns'][p,host,1:Max_Accounts-acct] = \
                  new_know['owns'][p,host,acct+1:]
                # -- prob of having 3 or 4 is zero
                new_know['owns'][p,host,Max_Accounts-acct:] = 0.0
            
            new_knows.append(new_know)
            new_probs.append(new_prob)

        assert all(self.know_valid(nk) for nk in new_knows)
        return new_knows, new_probs
    
    def do_hack(self, move, know):
        print 'do_hack'
        new_know = deepcopy(know)
        host = move['to']        
        os_id = OS_List_Letters.index(move['exploit'][0])
        patch_id = int(move['exploit'][1:])
        
        if move['exploit'][0] == self.game.board_os[host] and \
          patch_id not in self.game.board_patches[host]:
            # it worked!
            print "Hack worked!"
            worked = True
            # -- learn how many accounts you have
            num_acc = self.own[host] if host in self.own else 0
            print "-- ", new_know['owns'][self.id, host, :]
            new_know['owns'][self.id, host, num_acc] = 0.0
            num_acc += 1
            if num_acc == Max_Accounts:
                num_acc = Max_Accounts - 1
            new_know['owns'][self.id, host, num_acc] = 1.0
            assert self.know_valid(new_know), "new_know not valid on {}".format(
                new_know['owns'][self.id, host, :])
            # -- do it for real            
            self.own[host] = num_acc
            # -- learn the OS and that the exploit works
            new_know['OS'][host, :] = 0.0
            new_know['OS'][host, os_id] = 1.0
            new_know['patches'][host, patch_id] = 0.0
        else:
            # only learn that patch was there if you knew OS
            print "Hack failed"
            worked = False
            phfos = np.array([ 1.0 if i != os_id else know['patches'][host, patch_id]
                            for i in xrange(len(OS_List)) ]) * know['OS'][host, :]
            assert phfos.sum() > 0.0, "attack failed when known to succeed"
            phfos /= phfos.sum()
            p1 = know['patches'][host, patch_id]
            p2 = (1.0 - know['OS'][host, os_id]) * (1 - know['patches'][host, patch_id])
            new_know['OS'][host, :] = phfos
            new_know['patches'][host, patch_id] = p1 / (p1 + p2)


        # detection check
        for playerB in xrange(self.game.num_players):
            if playerB == self.id:
                continue
            if random.random() < Detection_Prob['b']:
                if move['to'] in self.game.players[playerB].own:
                    self.game.players[playerB].detect(
                        ('h', self.id, move['from'], move['to'], move['exploit'],
                         worked) )
        
        nk, pr = self.consider_hack(move, know)
        if not (any(self.knows_equal(new_know, nnkk) for nnkk in nk) and
                np.allclose(sum(pr), 1.0), "prob sum = {} (not 1)".format(sum(pr))):
            print "Use models.knows_diff to compare"
            embed()
        
        return new_know

    
    def consider_hack(self, move, know):
        host = move['to']
        os_id = OS_List_Letters.index(move['exploit'][0])
        patch_id = int(move['exploit'][1:])

        # two cases: it worked or it didn't
        prob_success = know['OS'][host, os_id] * (1.0 - know['patches'][host, patch_id])

        ifworks = deepcopy(know)  # then learn OS, patches, owns
        ifworks['OS'][host, :] = 0.0
        ifworks['OS'][host, os_id] = 1.0
        ifworks['patches'][host, patch_id] = 0.0
        maxed = ifworks['owns'][self.id, host, -1]
        ifworks['owns'][self.id, host, 1:] = ifworks['owns'][self.id, host, :-1]
        ifworks['owns'][self.id, host,  0] = 0.0
        ifworks['owns'][self.id, host, -1] += maxed

        if prob_success == 1.0:
            return [ ifworks ], [ prob_success ]

        # this is wrong; need to work out Bayes rule here TODO
        # when hack fails you learn a little about OS and a little about patches
        #  P(OS = i | hack failed) = P( hack fails | OS = i ) P( OS = i ) / P(hack fails)
        phfos = np.array([ 1.0 if i != os_id else know['patches'][host, patch_id]
                          for i in xrange(len(OS_List)) ]) * know['OS'][host, :]
        if phfos.sum() == 0.0:
            # this is an attack that is known in advance it will succeed
            assert prob_success == 1.0
        else:
            phfos /= phfos.sum()

        # P( patched | hackfails ) = P( hackfails | patched ) P(patched) / P( hackfails )
        # ( know['patches'] means patched for whatever OS is right )
        # and P(hackfails | patched) = 1.0
        #     P(hackfails | not patched) = P(os used was wrong)
        #     P(hackfails) = P(hackfails | patched) P(patched) + P(fails | not) P(not)
        p1 = know['patches'][host, patch_id]
        p2 = (1.0 - know['OS'][host, os_id]) * (1 - know['patches'][host, patch_id])
        # print "HACK FAIL NUMBERS\nphfos {}\n   p1 {}\n   p2 {}\np1/p* {}".format(
        #     phfos, p1, p2, p1 / (p1 + p2))
        
        iffails = deepcopy(know)
        iffails['OS'][host, :] = phfos
        iffails['patches'][host, patch_id] = p1 / (p1 + p2)

        return [ ifworks, iffails ], [ prob_success, 1.0 - prob_success ]
    

    # this is no longer used
    def consider_hack1(self, move, know):
        '''deprecated'''
        host = move['to']
        os_id = OS_List_Letters.index(move['exploit'][0])
        patch_id = int(move['exploit'][1:])
        # wrong! -- must allow for uncertain # of accounts!
        pre_acct = know['owns'][self.id, host, :].nonzero()[0][0]
        post_acct = min(pre_acct + 1, Max_Accounts - 1)
        
        # two cases: it worked or it didn't
        prob_success = know['OS'][host, os_id] * (1.0 - know['patches'][host, patch_id])

        ifworks = deepcopy(know)  # then learn OS, patches, owns
        ifworks['OS'][host, :] = 0.0
        ifworks['OS'][host, os_id] = 1.0
        ifworks['patches'][host, patch_id] = 0.0
        ifworks['owns'][self.id, host, pre_acct] = 0.0
        ifworks['owns'][self.id, host, post_acct] = 1.0

        iffails = deepcopy(know)
        if iffails['OS'][host, os_id] == 1.0:
            iffails['patches'][host, patch_id] = 1.0

        return [ ifworks, iffails ], [ prob_success, 1.0 - prob_success ]

    def do_backdoor(self, move, know):
        print 'do_backdoor'
        new_know = deepcopy(know)

        # add an account
        if self.own[move['from']] + 1 < Max_Accounts:            
            self.own[move['from']] += 1
        
        # update in knowledge
        new_know['owns'][self.id, move['from'], :] = 0.0
        new_know['owns'][self.id, move['from'], self.own[move['from']]] = 1.0

        # detection check
        for playerB in xrange(self.game.num_players):
            if random.random() < Detection_Prob['b']:
                if move['from'] in self.game.players[playerB].own:
                    self.game.players[playerB].detect(
                        ('b', self.id, move['from']) ) # say num accounts?

        # test:
        nk, pr = self.consider_backdoor(move, know)
        if not (any(self.knows_equal(new_know, nnkk) for nnkk in nk) and
                np.allclose(sum(pr), 1.0), "prob sum = {} (not 1)".format(sum(pr))):
            print "Use models.knows_diff to compare"
            embed()
        
        return new_know

    def consider_backdoor(self, move, know):
        '''Outcome is deterministic, so only one thing in the list.'''
        new_know = deepcopy(know)

        # Max_Account - 1 <-- sum of last 2 probs
        #               0 <-- prob 0
        #               1 <-- 0.0
        #           other <-- other-1
        maxed = new_know['owns'][self.id, move['from'], -1]

        new_know['owns'][self.id, move['from'], 2:] = \
                  new_know['owns'][self.id, move['from'], 1:-1]
        new_know['owns'][self.id, move['from'], -1] += maxed
        new_know['owns'][self.id, move['from'],  1] = 0.0

        return [ new_know ], [ 1.0 ]

    def consider_backdoor1(self, move, know):
        '''Outcome is deterministic, so only one thing in the list.'''
        new_know = deepcopy(know)

        # assume information about self is deterministic
        # -- WRONG! -- must do it for uncertain # of accounts
        old_num_accounts = np.argmax(new_know['owns'][self.id, move['from'], :])
        if old_num_accounts == Max_Accounts-1:
            new_num_accounts = old_num_accounts
        else:
            new_num_accounts = old_num_accounts + 1
            
        new_know['owns'][self.id, move['from'], old_num_accounts] = 0.0
        new_know['owns'][self.id, move['from'], new_num_accounts] = 1.0

        return [ new_know ], [ 1.0 ]
            
    def do_patch(self, move, know):
        print 'do_patch'
        new_know = deepcopy(know)

        # change it for real
        if move['exploit'][0] == self.game.board_os[move['from']]:
            self.game.board_patches[move['from']].append(int(move['exploit'][1:]))

            # change your knowledge of it  -- crashes if patch too big (see known bugs)
            new_know['patches'][move['from'],int(move['exploit'][1:])] = 1.0
            
            # detection
            for playerB in xrange(self.game.num_players):
                if playerB == self.id or \
                    move['from'] not in self.game.players[playerB].own:
                    continue
                if random.random() < Detection_Prob['p']:
                    self.game.players[playerB].detect(
                        ('p', self.id, move['from'], move['exploit']) )

        # test:
        nk, pr = self.consider_backdoor(move, know)
        if not (any(self.knows_equal(new_know, nnkk) for nnkk in nk) and
                np.allclose(sum(pr), 1.0), "prob sum = {} (not 1)".format(sum(pr))):
            print "Use models.knows_diff to compare"
            embed()
        
        return new_know

    def consider_patch(self, move, know):
        # only one outcome is possible
        new_know = deepcopy(know)

        if move['exploit'][0] == self.game.board_os[move['from']]:
            # change your knowledge of it  -- crashes if patch too big (see known bugs)
            new_know['patches'][move['from'], int(move['exploit'][1:])] = 1.0
        
        return [new_know], [1.0]

    
    def detect(self, event):
        '''Called when another player's action is detected.'''
        print '{} ({}) Detected {}'.format(self.name, self.id, event)
        # really need to update know
        if event[0] not in ['r', 'b', 's', 'c', 'p', 'h']:
            raise NotImplementedError, "Detected unknown event type {}".format(event[0])

        if event[0] in ['r', 'b', 's']:  
            # detected recon, backdoor, scan => user has a an account at source
            who, fro = event[1:3]
            self.know['owns'][who, fro, 0] = 0.0
            if self.know['owns'][who, fro, :].sum() == 0.0:
                print "WARNING -- knowledge failure in {} detection".format(event[0])
                self.know['owns'][who, fro, 1:] = 1.                            
            self.know['owns'][who, fro, :] /= self.know['owns'][who, fro, :].sum()
            # -- crashes if you were sure they had no account there

        elif event[0] == 'c':
            # detected clean => something about number of accounts user has
            who, fro, pre, post = event[1:]
            if post == 0:   # user has at least pre accounts
                self.know['owns'][who, fro, :pre] = 0.0
                if self.know['owns'][who, fro, :].sum() == 0.0:
                    print "WARNING -- knowledge failure in clean detection"
                    self.know['owns'][who, fro, 1:] = 1.                
                self.know['owns'][who, fro, :] /= self.know['owns'][who, fro, :].sum()
            else:  # user has exactly pre - post accounts
                self.know['owns'][who, fro, :] = 0.0
                self.know['owns'][who, fro, pre - post] = 1.0
                
        elif event[0] == 'p':
            # detected patch => user on host, has given exploit, and exploit is patched
            who, fro, ex = event[1:]
            os_id = OS_List_Letters.index(ex[0])
            # -- user on host
            self.know['owns'][who, fro, 0] = 0.0
            if self.know['owns'][who, fro, :].sum() == 0.0:
                print "WARNING -- knowledge failure in patch detection"
                self.know['owns'][who, fro, 1:] = 1.                
            self.know['owns'][who, fro, :] /= self.know['owns'][who, fro, :].sum()
            # -- user has exploit        
            self.know['exploits'][who, os_id, int(ex[1:])] = 1.0
            # -- exploit is now patched if OS was right
            if self.know['OS'][fro, os_id] == 1.0:
                self.know['patches'][fro, int(ex[1:])] = 1.0

        elif event[0] == 'h':
            # detected hack => user on host, has given exploit, and whether it was patched
            who, fro, to, ex, worked = event[1:]
            # -- user on fro host
            self.know['owns'][who, fro, 0] = 0.0
            if self.know['owns'][who, fro, :].sum() == 0.0:
                print "WARNING -- knowledge failure in hack detection"
                self.know['owns'][who, fro, 1:] = 1.
            self.know['owns'][who, fro, :] /= self.know['owns'][who, fro, :].sum()
            # -- with success, user accts on host up by one
            if worked:
                maxed_out = self.know['owns'][who, to, Max_Accounts-1]
                self.know['owns'][who, to, 1:] = self.know['owns'][who, to, :-1]
                self.know['owns'][who, to, 0] = 0.0
                self.know['owns'][who, to, -1] += maxed_out                
            # -- user has exploit
            os_id = OS_List_Letters.index(ex[0])
            self.know['exploits'][who, os_id, int(ex[1:])] = 1.0            
            # -- if exploit worked, know OS and it's not patched
            if worked:
                self.know['OS'][to, :] = 0.0
                self.know['OS'][to, os_id] = 1.0
                self.know['patches'][to, int(ex[1:])] = 0.0
            # -- if exploit failed, know it's patched is OS was right
            else:
                if self.know['OS'][to, OS_List_Letters.index(ex[0])] == 1.0:
                    self.know['patches'][fro, int(ex[1:])] = 1.0    
        
                
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



def account_difference(know, pid):
    x = np.arange(Max_Accounts)
    your_accounts = know['owns'][pid].dot(x).sum()
    all_accounts = know['owns'].dot(x).sum()
    return your_accounts * 2 - all_accounts

# next: k-ply evaluation strategies
class EvaluationStrategy(Strategy):
    def __init__(self, player, strategy_args):
        '''Create a strategy that uses a k-ply search on an evaluation function
        where both k and the function are given.  The function takes both
        the knowledge object and the player id as inputs.'''
        Strategy.__init__(self, player, strategy_args)
        self.evaluation_function = strategy_args['f']
        self.num_ply = strategy_args['k']
        
    def set_evaluation_function(self, evaluation_function):
        '''Set the evaluation function to be something that scores 'know'
        structures with larger values being more desirable.'''
        self.evaluation_function = evaluation_function

    def set_num_ply(self, k):
        self.num_ply = k

    def tree_your_move(self, know, k, mover):
        '''
        the tree_functions do the various steps of the k-ply search:
           start with tree_your_move with a given knowledge, probability, level to go
           it constructs a tree (dictionary) of knowledges
           if k = 1, it scores each one
           otherwise, it calls tree_fuzz (with k-1) to get scores and moves
           compute the average score for each set of outcomes
           returns the max choice (move) and its score

           in tree_fuzz, it computes what happens after opponent makes a random move
           if k = 1, it then scores that result
           otherwise, it calls tree_your_move (with k-1) on it to get score
           returns the score
        '''
        pid = self.player.id
        candidates = self.candidate_moves(self.player.know, self.player.id)[mover]

        # from IPython import embed
        # embed()
        
        # candidate move --> pair (list of knows, list of probs)
        knows_and_probs = { i:self.player.consider_moves([candidates[i]], deepcopy(know))
                            for i in xrange(len(candidates)) }
        # compute score for each outcome directly or via recursion
        if k == 1:
            scores = { i: np.array([self.evaluation_function(kk,pid)
                                    for kk in kp[0]])
                       for i,kp in knows_and_probs.iteritems() }
        else:            
            scores = { i: np.array([self.tree_fuzz(kk, k-1, mover)
                                    for kk in kp[0]])
                       for i,kp in knows_and_probs.iteritems() }
        # average sores according to their probabilities
        scores = { i: np.sum(sc * np.array(knows_and_probs[i][1]))
                   for i,sc in scores.iteritems() }
        # find the best move and return that and its score
        m = max(scores.values())
        best = [ c for c in scores if scores[c] == m ]
        best_move = candidates[random.choice(best)]
        return {'bestmove':best_move, 'maxscore':m,
                'allmoves':candidates, 'allscores':scores}
    
    def tree_fuzz(self, know, k, mover):
        '''Using this implies a model where the opponent moves randomly.
        Plan to have one where it moves in its best (or your worst) interest.'''
        if k == 1:
            score = self.evaluation_function(know, self.player.id)
        else:
            result = self.tree_your_move(know, k-1, mover)
            score = result['maxscore']

        return score
    

    def get_moves(self):
        '''
        -- to avoid combinatorial explosion, pick moves one at a time:        
        choose movers in a random order
        create a k-deep tree for first mover from current know
        roll it up according to min,max,avg and select best move
          state0 --your-move-->  1ply  --outcomes-->  2ply  --fuzz-->   3ply  --your-next-move-->  4ply  --outcomes-> 5ply
          score5 <----max------ score4 <--average--- score3 <--equal-- score2 <------max------- score1 <--average-- score0
                                
        assume that move (i.e., consider it)
        from there, create k-deep tree for second mover
        continue to make trees and roll them up until all moves are picked
        '''

        # choose movers in random order
        movers = [m for m in self.player.own.keys()]
        np.random.shuffle(movers)
    
        # recursively construct and score tree to get best move
        moves = []
        knows = [deepcopy(self.player.know)]
        probs = [ 1.0 ]
        for mover in movers:
            # best_move, score = self.tree_your_move(know, self.num_ply, mover)
            # for each knowledge, get scores for all moves
            results = [ self.tree_your_move(kn, self.num_ply, mover)
                        for kn in knows ]
            
            # compute best expected score and choose that
            candidates = results[0]['allmoves']
            scores = [ sum([ pr * r['allscores'][r['allmoves'].index(c)]
                         for r, pr in zip(results, probs) ])
                       for c in candidates ]
            m = max(scores)
            best = [ candidates[i] for i in xrange(len(candidates))
                     if scores[i] == m ]
            print "best moves = ", best, "with score", m
            best_move = random.choice(best)
            moves.append(best_move)

            # now consider the best move and branch on it
            new_knows = []
            new_probs = []
            for kn, pr in zip(knows, probs):
                branch_knows, branch_probs = self.player.consider_moves([best_move], kn)
                new_knows.extend(branch_knows)
                new_probs.extend( [ bp * pr for bp in branch_probs ] )

            knows, probs = new_knows, new_probs
            print "Explored {} knowledge states after {} moves".format(len(knows),
                                                                       len(moves))
                        
        print "moves =", moves
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
    players = [ # Player('Player', PlayerStrategy),
                # Player('Andrew', Andrews),
                # Player('Ethan', EthanAI),
                # Player('Jacob', JacobAI),
                # Player('AN', AndrewNathan),
                Player('Random', RandomStrategy),
                Player('Eval', EvaluationStrategy, {'f':account_difference,'k':3}) ]

    results = []

    for i in xrange(1, 2):
        print '-'*80
        print ('GAME ' + str(i)).center(80)
        print '-'*80    
        g=HackAttack(players)
        r = g.play(20)
        print r
        results.append(r)

    print Counter(map(tuple,results))

