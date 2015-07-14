import random
import hackattack_util

from collections import defaultdict as ddict


class Player(object):
    '''Handle all server-side interactions with the user'''

    def __init__(self, game, name, start):
        self.game = game
        self.name = name
        self.status = 'in'  # other status values are 'out' and 'won'
        self.own = {start:1}
        self.log = []

        # knowledge system
        self.min_accounts = ddict(lambda :ddict(str)) # [machine][player] = #
        self.max_accounts = ddict(lambda :ddict(str)) 
        self.oss = ddict(str)      # [machine] = OS string
        # True = Patched, False = Vulnerable, undef = unknown
        self.patches = ddict(lambda :ddict(str)) # patches[machine][expl#] = True, False, undef
        self.traced = []   # list of players
        
        E = set([])
        while len(E)<20:
            E.add(random.choice(self.game.state.OSs)[0]+str(hackattack_util.pick_exp_int()))
        self.players_expl = list(E)
        
        
        
        
        

        if self.name == 'Player 0':
            # show title screen until someone hits a key
            print "HACK ATTACK!\n\n"

            # look at http://www.network-science.de/ascii/ for more fonts
            # I like o8, poison.  This is smslant
            
            print '''
               __ __         __     ___  __  __           __  
              / // /__ _____/ /__  / _ |/ /_/ /____ _____/ /__
             / _  / _ `/ __/  '_/ / __ / __/ __/ _ `/ __/  '_/
            /_//_/\_,_/\__/_/\_\ /_/ |_\__/\__/\_,_/\__/_/\_\ 
            '''

            raw_input("\n\n\nPress enter to begin.")
            # give players names.  PROBLEM: commands and data still use numbers to specify players!
            # players_names = [ raw_input("Enter name for player {} of {}: ".format(i+1, num_players)).strip() for i in xrange(num_players) ]

    def parse_move(self,move_str):
        
        """Return move {'from':from_machine, 'to':to_machine, 'player':player,
        'exploit':exploit, 'user':target_user, 'action':action} based on an input
        of the form 'machine action parameters' and for player (global variable)"""
        s=self.game.state
        words = move_str.lower().split()

        if len(words) == 0:
            return
         
        if words[0].lower() == 'd':        
            if len(words) != 2:
                print "Follow format: (D)DoS <user>"
                return
            try:
                user = int(words[1])
            except:
                print "Must specify a user by number"
                return
            if user not in s.players_traced[s.player]:
                print "You can only DDoS a player after you have traced them"
                return
            return {'action':'d', 'user':user, 'player':s.player}

        if words[0].lower() == 'q':
            if len(words) != 2:
                print "Follow format: (Q)uit <save_file>"
                return
            return {'action':'q', 'filename':words[1]}
                                        
        if len(words) < 2:
            print "Follow format: <acting-machine> <action> ... --or-- (D)DoS <user>"
            return

        try:
            move = { 'from': int(words[0]), 'action': words[1][0], 'player':s.player,  }
        except:
            print "Must indicate source of move first (as int) and then action (by letter)"
            return

        if move['from'] not in self.own:#new change
            print "You must specify only a machine that you own"
            return
        
        if move['action'] == 'r':
            if len(words) != 3:
                print "Follow format: <acting-machine> (R)econ <machine>"
                return
            try:
                mac2 = int(words[2])
            except:
                print "Target machine must be an integer"
                return
            if mac2 not in xrange(s.num_hosts):
                print "Invalid target"
                return
            move['to'] = mac2
            return move
        elif move['action'] == 'updownupdownleftrightleftrightabab':
            print 'password accepted'
            return
        elif move['action'] == 'c':
            return move
        elif move['action'] == 'h':
            if len(words) != 4:
                print "Follow format: <acting-machine> (H)ack <machine> <exploit>"
                return
            
            if not words[2].isdigit():
                print "Target machine must be an integer"
                return
            else:
                mac2 = int(words[2])

            if mac2 not in xrange(s.num_hosts):
                print "Invalid target"
                return

            if words[3][1:].isdigit():
                if not words[3].upper() in self.players_expl:
                    print "Not your exploit"
                    return
            else:
                print "Third word must be letter followed by number (no space)"
                return
                #:)
            
            move['to'] = mac2
            move['exploit'] = words[3].upper()
            return move
        elif move['action'] == 'b':
            return move
        elif move['action'] == 'p':
            if len(words) != 3:
                print "Follow format: <acting-machine> (P)atch <exploit>"
                return
            if words[2][1:].isdigit() and (not words[2].upper() in self.players_expl):
                print "Must apply a patch for an exploit you have"
                return
            else:
                print "Third word must be a letter followed by a number (no space)"
                return
            
            move['exploit'] = words[2].upper()
            #if words[2].lower() == words[0][self.boardOSs]:
            return move
        elif move['action'] == 's':
            return move
                
        else:
            print "Invalid action"
            return

    def update_status(self):
        if sum(self.own.values()) == 0:
            self.status = 'out'
        elif all( [ sum(p.own.values()) == 0 for p in self.game.players if p.name != self.name] ):
            self.status = 'won'

    def start_round(self):
        s = self.game.state
        # for each player (if they haven't lost)
        ## are you ready? screen
        raw_input("\n"*100 + "Ready {}? ".format(s.players_names[s.player]))
            
        
        ## check for a new exploit
        if random.random() <= 1. / 6:
        
            ne = random.choice(self.game.state.OSs)[0] + str(hackattack_util.pick_exp_int())
            #self.players_expl.append(ne)
                
            while ne in self.players_expl:
                ne = random.choice(self.game.state.OSs)[0] + str(hackattack_util.pick_exp_int())
                
            self.players_expl.append(ne)#[s.player]
            self.say({'text':'You found a new exploit! ' + ne, 'type':'new exploit',
                      'exploit':ne})
    
    def update_output(self):
        # to do:
        # X 1. do not let this function update whose turn it is; do that in main loop
        #   2. do not add exploit here; do that in main loop
        #   3. don't use s.player to know who the player is, store it locally
        #   4. do not determine if the game is over in this function, but in main loop
        s = self.game.state
        ### output stuff to update the player
        if self.status == 'out':
            print "{} is out".format(s.players_names[s.player])
            return
        if self.status == 'won':
            print "You won!"
            return

        #print s.news            
        if len(s.news[s.player]) == 0:
            print "No news to report on round {}".format(s.game_round)
        else:
            print "\n   ".join(["ROUND {} NEWS!".format(s.game_round)] + s.news[s.player])
            s.news[s.player] = []

        ## show them what they have
        print "Your access:"
        for k,v in self.own.iteritems(): #self.own = {start:1} at start
            if v > 0:
                print "{} account{} on machine {}, which runs the {} OS".format(
                    v, 's' if v > 1 else '', k, s.board_os[k])
            
        print "Your exploits:", ", ".join(sorted(self.players_expl))
        # for e in self.players_expl:
        #     print "{}{} - {} exploit # {}".format(e[0][0], e[1], e[0], e[1])

        print "Traced players: {}".format( "None" if len(s.players_traced[s.player]) == 0
                                             else " ".join(map(str, s.players_traced[s.player])) )

        # new knowledge system...
        print "Known accounts:", "None" if len(self.min_accounts) == 0 else ""
        for m in self.min_accounts:
            print 'Machine {}:'.format(m)
            for p in self.min_accounts[m]:
                print '   Player {} has {} accounts'.format(p,
                    self.min_accounts[m][p] if self.min_accounts[m][p] == self.max_accounts[m][p]
                    else 'maybe some')
                
        print "Known OSes:", "None" if len(self.oss) == 0 else ""
        for m,os in self.oss.iteritems():
            print '   Machine {} runs {}'.format(m, os)

        if len(self.patches) == 0:
            print "Known Patches: None"
        for m in self.patches:
            print "Machine {} Patches:".format(m)
            patched = [ str(p) for p in self.patches[m] if self.patches[m][p] ]
            vuln    = [ str(p) for p in self.patches[m] if not self.patches[m][p] ]
            if len(patched) > 0:
                print "   Patched: " + ', '.join(patched)
            if len(vuln) > 0:
                print "   Vulnerabilities: " + ', '.join(vuln)

    def get_moves(self):
        s = self.game.state
        ## have them assign a move to each owned machine (or do DDoS)
        print "<acting-machine> (R)econ <machine>"
        print "<acting-machine> (C)lean"
        print "<acting-machine> (H)ack <machine> <exploit>"
        print "<acting-machine> (B)ackdoor"
        print "<acting-machine> (P)atch <exploit>"
        print "<acting-machine> (S)can"
        print "(L)ogreview"
        print "(D)DoS <user>"
        print "(Q)uitAfterSave <filename>"
        
        moves = []  # a list of moves, each is a dictionaries
        # std move format: acting-maching player action parameters (machine/exploit/user)
        while len(moves) < len(self.own.keys()):
            move = None
            while move == None:
                move_str = raw_input("\nSelect a move: ")
                if len(move_str) > 0 and move_str[0].upper() == 'L':
                    print "LOG".center(30,'=')
                    print "\n".join(map(str, self.log))
                    continue
                move = self.parse_move(move_str)
                if move != None and move['action'] not in 'dq' and move['from'] in [ m['from'] for m in moves]:
                    print "Each machine can only have one move"
                    killed = [ m for m in moves if m['from'] == move['from'] ][0]
                    print "Replacing {} with {}".format(killed, move)
                    moves.remove(killed)
            if move['action'] == 'd':
                moves = [move]
                print "DDoS is your only move this turn"
                break
            elif move['action'] == 'q':
                moves = [move]
                print "Saving and quitting"
                break
            else:
                moves.append(move)
        return moves

    def turn_done(self):
        raw_input("\nPress enter to clear screen ")
        print "\n"*100

    def say(self, said):
        '''How the player class receives messages from the game.'''
        print said['text']

        if 'type' not in said:
            said['type'] = 'not_given'
        elif said['type'] == 'accounts':
            self.min_accounts[said['machine']][said['player']] = said['has accounts']
            self.max_accounts[said['machine']][said['player']] = said['has accounts']
        elif said['type'] == 'os':
            self.oss[said['machine']] = said['OS']
        elif said['type'] == 'exploits':
            for e in self.players_expl:
                if e[0] == self.oss[said['machine']][0]:
                    self.patches[said['machine']][int(e[1:])] = \
                        (e not in said['exploitable with'])
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
