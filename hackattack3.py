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
# deprecated -- remove these
Patches_Per_OS        = 3   # number each host draws to start (with repl.)
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
        'Create a player with name (string) using a given Strategy'
        self.name     = name
        self.strategy = strategy(self)

        self.move_funcs = {'r':self.do_recon,    'c':self.do_clean, 'h':self.do_hack,
                           'b':self.do_backdoor, 'p':self.do_patch, # 'd':self.do_ddos,
                           's':self.do_scan}
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

    @staticmethod
    def knows_diff(know1, know2):
        '''Return a dictionary { key: { (i,j) : (know1_val, know2_val) } } of diffs'''
        assert know1.viewkeys() == know2.viewkeys()
        return { k : { (i,j) : (know1[k][i,j], know2[k][i,j])
                       for i,j in zip(* (know1[k] - know2[k]).nonzero()) }
                 for k in know1 }
    
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
            self.know = self.move_funcs[m['action']](m, self.know)
            

    def working_attacks(self, host):
        '''return a list of the short codes for attacks this player has
        that work on machine host'''
        return [ e for e in self.exploits
                 if self.game.board_os[host] == e[0] and int(e[1:]) not in
                  self.game.board_patches[host] ]
    
    def do_scan(self, move, know):
        '''Scan a machine to see what other players are on there.'''

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
        assert any(self.knows_equal(new_know, nnkk) for nnkk in nk)
        assert np.allclose(sum(pr), 1.0), "prob sum = {} (not 1)".format(sum(pr))
        
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
        assert any(self.knows_equal(new_know, nnkk) for nnkk in nk)
        assert sum(pr) == 1.0
        
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
            removed = playerBaccts - newBaccts
            # -- remove accts
            self.game.players[playerB].own[move['from']] = newBaccts
            # -- and update knowledge
            if removed < playerAaccts:  # then they must be off the machine
                new_know['owns'][playerB, move['from'], :] = 0.0
                new_know['owns'][playerB, move['from'], 0] = 1.0
            elif removed == playerAaccts: # may have as many as max - removed
                # new prob(m) = prob(m + removed), normalized
                new_know['owns'][playerB, move['from'], :Max_Accounts-removed] = \
                  new_know['owns'][playerB, move['from'], removed:]
                new_know['owns'][playerB, move['from'], :] /= \
                  new_know['owns'][playerB, move['from'], :].sum()
            # -- and send detection notice to those players (100% chance)
            if removed > 0:
                self.game.players[playerB].detect(
                    ('c', self.id, move['from'], removed) )

        # test:
        nk, pr = self.consider_clean(move, know)
        assert any(self.knows_equal(new_know, nnkk) for nnkk in nk)
        assert sum(pr) == 1.0
        
        return new_know
    

    def consider_clean(self, move, know):
        new_knows = []
        new_probs = []
        
        host = move['from']
        acct = know['owns'][self.id, host, :].nonzero()[0][0]
        # for each player think whether they have fewer or more than removed
        outcomes = list(product(*( [[False, True]]*self.game.num_players ) ))
        outcomes = [ o for o in outcomes if o[self.id] ] # avoid doubling up
        for outcome in outcomes:
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
                    if o: # true case: fewer than acct, so goes to 0
                        new_know['owns'][p,host,:] = 0.0
                        new_know['owns'][p,host,0] = 1.0
                    else: # false case: move probs down and renormalize
                        temp = new_know['owns'][p,host,acct:]
                        new_know['owns'][p,host,:] = 0.0
                        if temp.sum() > 0.0:
                            new_know['owns'][p,host,:Max_Accounts - acct] = temp
                            new_know['owns'][p,host,:] /= temp.sum()
                            
                new_knows.append(new_know)
                new_probs.append(new_prob)

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
            # -- learn how many accounts you have
            num_acc = self.own[host] if host in self.own else 0
            new_know['owns'][self.id, host, num_acc] = 0.0
            num_acc += 1
            if num_acc == Max_Accounts:
                num_acc = Max_Accounts - 1
            new_know['owns'][self.id, host, num_acc] = 1.0
            # -- do it for real            
            self.own[host] = num_acc
            # -- learn the OS and that the exploit works
            new_know['OS'][host, :] = 0.0
            new_know['OS'][host, os_id] = 1.0
            new_know['patches'][host, patch_id] = 0.0
        else:
            # only learn that patch was there if you knew OS
            print "Hack failed"
            if new_know['OS'][host, os_id] == 1.0:
                new_know['patches'][host, patch_id] = 1.0

        # detection check
        for playerB in xrange(self.game.num_players):
            if random.random() < Detection_Prob['b']:
                if move['to'] in self.game.players[playerB].own:
                    self.game.players[playerB].detect(
                        ('h', self.id, move['from'], move['to'], move['exploit']) )
        
        nk, pr = self.consider_hack(move, know)
        if not any([self.knows_equal(new_know, nnkk) for nnkk in nk]):
            print "Knowledge mismatch.  Here's the diffs."
            for nnkk in nk:
                print self.knows_diff(new_know, nnkk)
                
        assert any([self.knows_equal(new_know, nnkk) for nnkk in nk])
        assert sum(pr) == 1.0
        
        return new_know

    
    def consider_hack(self, move, know):
        host = move['to']
        os_id = OS_List_Letters.index(move['exploit'][0])
        patch_id = int(move['exploit'][1:])
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

        nk, pr = self.consider_backdoor(move, know)
        assert any(self.knows_equal(new_know, nnkk) for nnkk in nk)
        assert sum(pr) == 1.0
        
        return new_know

    def consider_backdoor(self, move, know):
        '''Outcome is deterministic, so only one thing in the list.'''
        new_know = deepcopy(know)

        # assume information about self is deterministic
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
        print '{} Detected {}'.format(self.name, event)
        # really need to update know


class Strategy(object):
    '''The Strategy class represents the player logic or the methods for getting to the
    human player to communicate status and get moves.  It's called Strategy because you
    query it and it gives you the next moves.  Anticipated interfaces are terminal-style,
    gui, and networked.  Also, the AI classes will be Strategies.'''
    def __init__(self, player):
        self.player = player

    def start_round(self):
        print self.player.name, self.player.id, "Round", self.player.game.round
        # print self.player.own

    def get_moves(self):
        return []

    def end_round(self):
        pass

    def display(self, message):
        print message

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
                        embed()  # brings up repl
                        continue

                    move_words = move_str.split()
                    if move_words[0] == 'd':
                        if len(move_words) < 2:
                            continue
                        return [ {'action':'d', 'user':int(move_words[1])} ]
                    elif move_words[0] == 'k':     # show the knowledge tables
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
