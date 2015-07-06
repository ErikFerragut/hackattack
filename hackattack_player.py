class Player(object):
    '''Handle all server-side interactions with the user'''
    def __init__(self, game, name):
        self.game = game
        self.name = name
        
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
            return {'action':'d', 'user':user}
        
        if len(words) < 2:
            print "Follow format: <acting-machine> <action> ... --or-- (D)DoS <user>"
            return

        try:
            move = { 'from': int(words[0]), 'action': words[1][0], 'player':s.player }
        except:
            print "Must indicate source of move first (as int) and then action (by letter)"
            return

        if move['from'] not in s.players_own[s.player]:
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
        elif move['action'] == 'c':
            return move
        elif move['action'] == 'h':
            if len(words) != 4:
                print "Follow format: <acting-machine> (H)ack <machine> <exploit>"
                return
            try:
                mac2 = int(words[2])
            except:
                print "Target machine must be an integer"
                return
            if mac2 not in xrange(s.num_hosts):
                print "Invalid target"
                return
            try:
                # print "debug:", words[2], words[2][0], words[2][1:]
                # print int(words[2][1:])
                if not any([ e[0][0] == words[3][0:1].upper() and e[1] == int(words[3][1:])
                        for e in s.players_expl[s.player] ]):
                    print "Not a valid exploit"
                    return
            except:
                print "Third word must be letter followed by number (no space)"
                return
            move['to'] = mac2
            move['exploit'] = words[3].upper()
            return move
        elif move['action'] == 'b':
            return move
        elif move['action'] == 'p':
            if len(words) != 3:
                print "Follow format: <acting-machine> (P)atch <exploit>"
                return
            try:
                if not any([ e[0][0] == words[2][0].upper() and e[1] == int(words[2][1:])
                        for e in s.players_expl[s.player] ]):
                    print "Must apply a patch for an exploit you have"
                    return
            except:
                print "Third word must be a letter followed by a number (no space)"
                return
            move['exploit'] = words[2].upper()
            return move
        else:
            print "Invalid action"
            return

    def update_output(self):
        # to do:
        #   1. do not let this function update whose turn it is; do that in main loop
        #   2. do not add exploit here; do that in main loop
        #   3. don't use s.player to know who the player is, store it locally
        #   4. do not determine if the game is over in this function, but in main loop
        s = self.game.state
        ### output stuff to update the player
        if sum(s.players_own[s.player].values()) == 0:
            print "{} is out".format(s.players_names[s.player])
            s.player = (s.player + 1) % s.num_players
            return True
        elif all( [ sum(s.players_own[p].values()) == 0
                    for p in xrange(s.num_players)
                    if p != s.player ] ):
            print "You won!"
            return False
            
        # for each player (if they haven't lost)
        ## are you ready? screen
        raw_input("\n"*100 + "Ready {}? ".format(s.players_names[s.player]))
            
        if len(s.news[s.player]) == 0:
            print "No news to report on round {}".format(s.game_round)
        else:
            print "\n   ".join(["ROUND {} NEWS!".format(s.game_round)] + s.news[s.player])
            s.news[s.player] = []

        ## show them what they have
        print "Your access:"
        for k,v in s.players_own[s.player].iteritems():
            if v > 0:
                print "{} account{} on machine {}, which runs the {} OS".format(
                    v, 's' if v > 1 else '', k, s.board_os[k])
        ## check for a new exploit
        if random.random() <= 1./6:
            ne = random.choice(list(set(s.all_exploits).difference(s.players_expl[s.player])))
            s.players_expl[s.player].append( ne )
            print "\nYou found a new exploit! ", ne
            
        print "\nYour exploits:"
        for e in s.players_expl[s.player]:
            print "{}{} - {} exploit # {}".format(e[0][0], e[1], e[0], e[1])

        print "\nTraced players: {}".format( "None" if len(s.players_traced[s.player]) == 0
                                             else " ".join(map(str, s.players_traced[s.player])) )

        return True
    
    def get_moves(self):
        s = self.game.state
        ## have them assign a move to each owned machine (or do DDoS)
        print "<acting-machine> (R)econ <machine>"
        print "<acting-machine> (C)lean"
        print "<acting-machine> (H)ack <machine> <exploit>"
        print "<acting-machine> (B)ackdoor"
        print "<acting-machine> (P)atch <exploit>"
        print "(D)DoS <user>"
        moves = []  # a list of moves, each is a dictionaries
        # std move format: acting-maching player action parameters (machine/exploit/user)
        while len(moves) < len(s.players_own[s.player].keys()):
            move = None
            while move == None:
                move_str = raw_input("\nSelect a move: ")
                move = self.parse_move(move_str)
                if move != None and move['from'] in [ m['from'] for m in moves]:
                    print "Each machine can only have one move"
                    killed = [ m for m in moves if m['from'] == move['from'] ][0]
                    print "Replacing {} with {}".format(killed, move)
                    moves.remove(killed)
            if move['action'] == 'd':
                moves = [move]
                print "DDoS is your only move this turn"
                break
            else:
                moves.append(move)
        return moves

    def turn_done(self):
        raw_input("\nPress enter to clear screen ")
        print "\n"*100

    def say(self, thing_to_say):
        print thing_to_say
