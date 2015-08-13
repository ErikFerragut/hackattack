import random
from hackattack_util import *  # OS_List_Letters & pick_exp_int
from collections import defaultdict as ddict


class Player(object):
    '''Handle all server-side interactions with the user'''

    def __init__(self, name):
        self.name = name
        self.status = 'in'  # other status values are 'out' and 'won'
        self.own = {}
        self.log = []
        self.news   = []

        # knowledge system
        self.min_accounts = ddict(lambda :ddict(str)) # [machine][player] = #
        self.max_accounts = ddict(lambda :ddict(str))
        # replace min/max_accounts with others_own
        
        # True = Patched, False = Vulnerable, undef = unknown
        self.traced = []   # list of players
        
        E = set([])
        while len(E) < Exploits_Per_Player:
            E.add(random.choice(OS_List_Letters) + str(pick_exp_int()))
        self.expl   = list(E)

    def knowledge_dict(self):
        return { 'own': self.own, 'others_own':self.others_own,
                 'patches': self.patches, 'vuln':self.vuln,
                 'traced': self.traced, 'expl':self.expl  }
        
    def start_player(self, game, start, position):
        self.own[start] = 1
        self.id = position
        self.game = game
        self.oss = ddict(str, {start:self.game.board_os[start]})
        self.others_own = { i: { start: 0 } for i in xrange(game.num_players) if i != position }
        self.patches = { i: [] for i in xrange(game.num_hosts) }  # known patches
        self.vuln = { i: [] for i in xrange(game.num_hosts) }     # known vulnerabilities
        
    def display(self, string):
        print string
        
    def parse_move(self,move_str):
        """Return move {'from':from_machine, 'to':to_machine, 'player':player,
        'exploit':exploit, 'user':target_user, 'action':action} based on an input
        of the form 'machine action parameters' and for player (global variable)"""
        words = move_str.lower().split()

        if len(words) == 0:
            return
         
        if words[0].lower() == 'd':        
            if len(words) != 2:
                self.display("Follow format: (D)DoS <user>")
                return
            try:
                user = int(words[1])
            except:
                self.display("Must specify a user by number")
                return
            if user not in self.traced:
                self.display("You can only DDoS a player after you have traced them")
                return
            return {'action':'d', 'user':user, 'player':self.id}

        if words[0].lower() == 'q':
            if len(words) != 2:
                self.display("Follow format: (Q)uit <save_file>")
                return
            return {'action':'q', 'filename':words[1]}
                                        
        if len(words) < 2:
            self.display("Follow format: <acting-machine> <action> ... --or-- (D)DoS <user>")
            return

        try:
            move = { 'from': int(words[0]), 'action': words[1][0], 'player':self.id  }
        except:
            self.display("Must indicate source of move first (as int) and then action (by letter)")
            return

        if move['from'] not in self.own:#new change
            self.display("You must specify only a machine that you own")
            return
        
        if move['action'] == 'r':
            if len(words) != 3:
                self.display("Follow format: <acting-machine> (R)econ <machine>")
                return
            try:
                mac2 = int(words[2])
            except:
                self.display("Target machine must be an integer")
                return
            if mac2 not in xrange(self.game.num_hosts):
                self.display("Invalid target")
                return
            move['to'] = mac2
            return move
        elif move['action'] == 'updownupdownleftrightleftrightabab':
            self.display('password accepted')
            return
        elif move['action'] == 'c':
            return move
        elif move['action'] == 'h':
            if len(words) != 4:
                self.display("Follow format: <acting-machine> (H)ack <machine> <exploit>")
                return
            
            if not words[2].isdigit():
                self.display("Target machine must be an integer")
                return
            else:
                mac2 = int(words[2])

            if mac2 not in xrange(self.game.num_hosts):
                self.display("Invalid target")
                return

            if words[3][1:].isdigit():
                if not words[3].upper() in self.expl:
                    self.display("Not your exploit")
                    return
            else:
                self.display("Third word must be letter followed by number (no space)")
                return
                #:)
            
            move['to'] = mac2
            move['exploit'] = words[3].upper()
            return move
        elif move['action'] == 'b':
            return move
        elif move['action'] == 'p':
            move['exploit'] = words[2].upper()
            if len(words) != 3:
                self.display("Follow format: <acting-machine> (P)atch <exploit>")
                return
            elif words[2][1:].isdigit() and (not words[2].upper() in self.expl):
                self.display("Must apply a patch for an exploit you have")
                return
            else:
                return move
        elif move['action'] == 's':
            return move
                
        else:
            self.display("Invalid action")
            return

    def update_status(self):
        if sum(self.own.values()) == 0:
            self.status = 'out'
        elif all( [ sum(p.own.values()) == 0 for p in self.game.players if p.name != self.name] ):
            self.status = 'won'

    def start_round(self):
        # for each player (if they haven't lost)
        ## are you ready? screen
        raw_input("\n"*100 + "Ready {}? ".format(self.name)) 
            
        
        ## check for a new exploit
        if random.random() <= 1. / 6:        
            ne = random.choice(OS_List_Letters) + str(pick_exp_int())
                
            while ne in self.expl:
                ne = random.choice(OS_List_Letters) + str(pick_exp_int())
                
            self.expl.append(ne)
            self.say({'text':'You found a new exploit! ' + ne, 'type':'new exploit',
                      'exploit':ne})
    
    def update_output(self):
        ### output stuff to update the player
        if self.status == 'out':
            self.display("{} is out".format(self.name))
            return
        if self.status == 'won':
            self.display("You won!")
            return

        if len(self.news) == 0:
            self.display("No news to report on round {}".format(self.game.round))
        else:
            self.display("\n   ".join(["ROUND {} NEWS!".format(self.game.round)] +
                                      self.news))
            self.news = []

        ## show them what they have
        self.display("Your access:")
        for k,v in self.own.iteritems(): #self.own = {start:1} at start
            if v > 0:
                self.display("{} account{} on machine {}, which runs the {} OS".format(
                    v, 's' if v > 1 else '', k, self.game.board_os[k]))
            
        self.display(("Your exploits:", ", ".join(sorted(self.expl))))

        self.display("Traced players: {}".format( "None" if len(self.traced) == 0
                                             else " ".join(map(str, self.traced)) ))

        # new knowledge system...
        self.display(("Known accounts:", "None" if len(self.others_own) == 0 else ""))
        for m in self.min_accounts:
            self.display('Machine {}:'.format(m))
            for p in self.min_accounts[m]:
                self.display(('   Player {} has {} accounts'.format(p,
                    self.min_accounts[m][p] if self.min_accounts[m][p] == self.max_accounts[m][p]
                    else 'maybe some')))
                
        self.display(("Known OSes:", "None" if len(self.oss) == 0 else ""))
        for m,os in self.oss.iteritems():
            self.display(('   Machine {} runs {}'.format(m, os)))

        if len(self.patches) == 0:
            self.display("Known Patches: None")
        for m in self.patches:
            patched = [ str(p) for p in self.patches[m] if self.patches[m][p] ]
            vuln    = [ str(p) for p in self.patches[m] if self.patches[m][p] == False ]
            if len(patched) + len(vuln) == 0:
                continue
            self.display("Machine {} Patches:".format(m))
            if len(patched) > 0:
                self.display(("   Patched: " + ', '.join(patched)))
            if len(vuln) > 0:
                self.display(("   Vulnerabilities: " + ', '.join(vuln)))

    def get_moves(self):
        ## have them assign a move to each owned machine (or do DDoS)
        self.display("<acting-machine> (R)econ <machine>")
        self.display("<acting-machine> (C)lean")
        self.display("<acting-machine> (H)ack <machine> <exploit>")
        self.display("<acting-machine> (B)ackdoor")
        self.display("<acting-machine> (P)atch <exploit>")
        self.display("<acting-machine> (S)can")
        self.display("(L)ogreview")
        self.display("(D)DoS <user>")
        self.display("(Q)uitAfterSave <filename>")
        
        moves = []  # a list of moves, each is a dictionaries
        # std move format: acting-maching player action parameters (machine/exploit/user)
        while len(moves) < len(self.own.keys()):
            move = None
            while move == None:
                move_str = raw_input("\nSelect a move: ")
                if len(move_str) > 0 and move_str[0].upper() == 'L':
                    self.display("LOG".center(30,'='))
                    self.display(("\n".join(map(str, self.log))))
                    continue
                move = self.parse_move(move_str)
                if move != None and move['action'] not in 'dq' and move['from'] in [ m['from'] for m in moves]:
                    self.display("Each machine can only have one move")
                    killed = [ m for m in moves if m['from'] == move['from'] ][0]
                    self.display("Replacing {} with {}".format(killed, move))
                    moves.remove(killed)
            if move['action'] == 'd':
                moves = [move]
                self.display("DDoS is your only move this turn")
                break
            elif move['action'] == 'q':
                moves = [move]
                self.display("Saving and quitting")
                break
            else:
                moves.append(move)
        return moves

    def turn_done(self):
        pass

    def say(self, said):
        '''How the player class receives messages from the game.'''
        self.display(said['text'])

        if 'type' not in said:
            said['type'] = 'not_given'
        elif said['type'] == 'accounts':
            self.min_accounts[said['machine']][said['player']] = said['has accounts']
            self.max_accounts[said['machine']][said['player']] = said['has accounts']
        elif said['type'] == 'os':
            self.oss[said['machine']] = said['OS']
        elif said['type'] == 'exploits':
            for e in self.expl:
                if e[0] == self.oss[int(said['machine'])][0]:
                    if e in said['exploitable with']:
                        self.patches[said['machine']][int(e[1:])] = False
                    else:
                        self.patches[said['machine']][int(e[1:])] = True
        elif said['type'] == 'clean':
            if said['accounts removed'] == self.own[said['machine']]:
                self.min_accounts[said['machine']][said['player']] = 0
                self.max_accounts[said['machine']][said['player']] = 0
            else:
                self.min_accounts[said['machine']][said['player']] = 0
                self.max_accounts[said['machine']][said['player']] = 100
        elif said['type'] == 'trace':
            self.traced.append(said['player'])
        elif said['type'] == 'failed hack':
            self.patches[said['machine']][int(said['with'][1:])] = True
        elif said['type'] == 'patch':
            self.patches[said['machine']][said['patched']] = True
        # to do -- say's for ddos moves

        self.log.append(said['text'])
        # add it to a list for machines that are involved
        # store inferred information
