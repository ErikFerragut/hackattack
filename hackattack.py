# HACK ATTACK - a cyber hacking game
#
# V 1.0 - first working version - 6/11/2015
# V 1.1 - various bug fixes 
#         - recon now says what was probed
#         - added some ascii art on title page
#         - now keeps track of rounds
#         - put names in, but using "Player <i>" since still specify them by number
#         - drops out players who have lost (but without first notifying them!)
#         - made it so you specify machines and thereby the order of the actions
#         - breaks out of loop when you specify ddos

# known bugs:
#  - when you lose, you never get another turn, so you don't really learn why

# plans:
# V 2.0 - added knowledge system
# Future verseion in unknown order:
#  - network game
#  - private/public messaging capability
#  - optional gui, maybe curses (maybe as a plug-in?)
#  - computer AI players
#  - expanded rules

# possible future rules:
#  - bricking move that resets a machine
#  - be able to abandon a machine (maybe a free move or in conjunction with a backdoor?)
#  - everyone hears about the ddos even if they are not involved
#  - have more machine #s than machines
#  - modify recon to apply to a collection of machines numbers (addresses)
#  - or add a scanning move that does just an OS scan on machine numbers
#  - allow a random chance that the machine's real user will pactch something
#  - make a zero-day exploit mechanism
#    + e.g., there are an infinite number of exploits with lower numbers being better known
#  - allow exchanges of exploits, accounts, and information
#  - fine-tune probabilities of detection and make detection higher when attack fails
#  - differentiated exploit types (e.g., trojans, worms)
#  - allow ways to make traps, such as honeypots
#  - modify what you learn from failed attacks
#  - change the tracing process
#    + more proxies between you and the others so there's multiple levels of traces?
#    + put your home machine as one in play?
#    + allow special moves that increase the probability of tracing (e.g., a wireshark move)


import random
import time

class GameState(object):
	def __init__(self):
		self.num_players = 5
		self.exploits_per_os = 5
		self.start_with_exploits = 4
		self.vuln_prob = 0.8

		self.detection_prob = { 'r':0.05, 'h':0.15, 'b':0.10, 'p':0.25 }

		self.OSs = ['Linux', 'Windows', 'Mac', 'Solaris']
		self.all_exploits = [ (o,i) for o in self.OSs for i in xrange(self.exploits_per_os) ]
		self.num_hosts = 5*self.num_players

		a = range(self.num_hosts)
		random.shuffle(a)

		# (os, [vulnerabilities])
		self.board_os = [ random.choice(self.OSs) for i in xrange(self.num_hosts) ]
		self.board_vuln = [ [ i for i in range(self.exploits_per_os) if random.random() < self.vuln_prob ]
					   for h in xrange(self.num_hosts) ]

		self.players_start = [ aa for aa in a[:self.num_players] ]
		self.players_own = [ {s:1} for s in self.players_start ]
		self.players_expl = []
		for i in xrange(self.num_players):
			random.shuffle(self.all_exploits)
			self.players_expl.append( self.all_exploits[:self.start_with_exploits] )
		self.players_traced = [ set([]) for i in xrange(self.num_players) ]
		self.news = { p:[] for p in xrange(self.num_players) }

class Game(object):
	def __init__(self):
		self.state = GameState()
		self.move_funcs = {'r':self.do_recon, 'c':self.do_clean, 'h':self.do_hack, 'b':self.do_backdoor,
					  'p':self.do_patch, 'd':self.do_ddos}

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

		# or
		self.state.players_names = [ "Player {}".format(i) for i in xrange(self.state.num_players) ]

	def parse_move(self,move_str):
		
		"""Return move {'from':from_machine, 'to':to_machine, 'player':player,
		'exploit':exploit, 'user':target_user, 'action':action} based on an input
		of the form 'machine action parameters' and for player (global variable)"""
		s=self.state
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
			if len(words) != 2:
				print "Follow format: <acting-machine> (P)atch <exploit>"
				return
			try:
				if not any([ e[0][0] == words[1][0].upper() and e[1] == int(words[1][1:])
						for e in s.players_expl[s.player] ]):
					print "Must apply a patch for an exploit you have"
					return
			except:
				print "Third word must be a letter followed by a number (no space)"
				return
			move['exploit'] = words[1].upper()
			return move
		else:
			print "Invalid action"
			return

	def detected(self,host, message):
		s=self.state
		for p in xrange(s.num_players): 
			if host in s.players_own[p]:
				s.news[p].append(message) 
            
	def working_attacks(self,player, host):
		'''return a list of the short codes for attacks player has that work on machine'''
		return [ e[0][0] + str(e[1]) for e in self.state.players_expl[player]
				 if self.state.board_os[host] == e[0] and e[1] in self.state.board_vuln[host] ]

	def do_recon(self,move):
		player = move['player']
		print "Machine {} is running the {} OS".format(move['to'], self.state.board_os[move['to']])
		openings = self.working_attacks(player, move['to'])
		if len(openings) == 0:
			print "You have no exploits for that machine."
		else:
			print "You can hack it with", ", ".join(openings)
		# check for detection
		if random.random() < self.state.detection_prob['r']:
			self.detected(move['to'], "{} probed machine {} from machine {}".format(self.state.players_names[move['player']], move['to'], move['from']))

	def do_clean(self,move):
		for p in xrange(self.state.num_players):
			if p != self.state.player:
				if move['from'] in self.state.players_own[p] and self.state.players_own[p][move['from']] > 0:
					num_removed = min(self.state.players_own[p][move['from']], self.state.players_own[move['player']][move['from']])
					self.state.players_own[p][move['from']] -= num_removed
					if self.state.players_own[p][move['from']] == 0:
						self.state.players_own[p].pop(move['from'])
					print "You removed {} of {}'s accounts".format(num_removed, self.state.players_names[p])
					self.state.news[p].append("{} removed {} of your accounts from machine {}".format(
						self.state.players_names[move['player']], num_removed, move['from']))
					# check for trace
					if not p in self.state.players_traced[move['player']]:
						if min([random.random() for i in xrange(num_removed)]) < 1./6:
							self.state.players_traced[move['player']].add(p)
							print "You traced {}!".format(self.state.players_names[p])
							
		print "Clean completed on machine {}".format(move['from'])

	def do_hack(self,move):
		player = move['player']
		worked = move['exploit'] in self.working_attacks(player, move['to'])
		# detected? -- do it first so you don't learn if you were detected
		if random.random() < self.state.detection_prob['h']:
			self.detected(move['to'], "{} {}successfully hacked machine {} from {}".format(
			  self.state.players_names[player], "" if worked else "un", move['to'], move['from']))

		if worked:
			print "Hack succeeded"
			# add access
			if move['to'] not in self.state.players_own[player]:
				self.state.players_own[player][move['to']] = 1
			else:
				self.state.players_own[player][move['to']] += 1
		else:
			print "Hack failed"
			print "OS was {}".format(self.state.board_os[move['to']])

	def do_backdoor(self,move):
		player = move['player']
		self.state.players_own[player][move['from']] += 1
		if random.random() < self.state.detection_prob['b']:
			self.detected(move['from'], "{} added a backdoor to machine {}".format(self.state.players_names[player],
																			  move['from']))
		print "One backdoor added to machine {}; you now have {}".format(move['from'],
																	  self.state.players_own[player][move['from']])
		
	def do_patch(self,move):
		if move['exploit'][0].upper() == self.state.board_os[move['from']][0]:
			patch_id = int(move['exploit'][1:])
			if patch_id in self.state.board_vuln[move['from']]:
				self.state.board_vuln[move['from']].remove(patch_id)
				print "Vulnerability patched"
			else:
				print "Vulnerability was already patched"
		else:
			print "Failed patch due to OS mismatch of {} on {}".format(move['exploit'],
																	   self.state.board_os[move['from']])

		if random.random() < self.state.detection_prob['p']:
			self.detected(move['from'], "{} patched machine {}".format(self.state.players_names[move['player']],
																  move['from']))

	def do_ddos(self,move):
		# do you have the trace you need
		player = move['player']
		if move['user'] in self.state.players_traced[player]:
			you_str = len(self.state.players_own[player])
			them_str = len(self.state.players_own[move['user']])
			if you_str > them_str:
				print "YOU WON THE DDOS -- {} IS ELIMINATED".format(self.state.players_names[move['user']].upper())
				self.state.players_own[move['user']] = {}
				self.state.news[move['user']].append("YOU WERE DDOSED BY {}".format(self.state.players_names[player].upper()))
			elif you_str < them_str:
				print "YOU LOST THE DDOS -- YOU ARE ELIMINATED"
				self.state.players_own[player] = {}
				self.state.news[move['user']].append("{} tried to DDoS you but lost and was eliminated".format(self.state.players_names[player]))
			else:
				print "DDOS was a tie"
				self.state.news[move['user']].append("{} tried to DDoS you but it was tie".format(self.state.players_names[player]))
		else:
			print "You need a trace before you can ddos (this output signifies a logic error!)"
			
									 


	def mainloop(self):
		
		self.state.player = 0
		# while True:

		game_round = 0

		while True:
			if self.state.player == 0:
				game_round += 1
				
			if sum(self.state.players_own[self.state.player].values()) == 0:
				print "{} is out".format(self.state.players_names[self.state.player])
				self.state.player = (self.state.player + 1) % self.state.num_players
				continue
			elif all( [ sum(self.state.players_own[p].values()) == 0 for p in xrange(self.state.num_players)
						if p != self.state.player ] ):
				print "You won!"
				break
			
			# for each player (if they haven't lost)
			## are you ready? screen
			raw_input("\n"*100 + "Ready {}? ".format(self.state.players_names[self.state.player]))
			
			if len(self.state.news[self.state.player]) == 0:
				print "No news to report on round {}".format(game_round)
			else:
				print "\n   ".join(["ROUND {} NEWS!".format(game_round)] + self.state.news[self.state.player])
				self.state.news[self.state.player] = []

			## show them what they have
			print "Your access:"
			for k,v in self.state.players_own[self.state.player].iteritems():
				if v > 0:
					print "{} account{} on machine {}, which runs the {} OS".format(
						v, 's' if v > 1 else '', k, self.state.board_os[k])
			## check for a new exploit
			if random.random() <= 1./6:
				ne = random.choice(list(set(self.state.all_exploits).difference(self.state.players_expl[self.state.player])))
				self.state.players_expl[self.state.player].append( ne )
				print "\nYou found a new exploit! ", ne
			
			print "\nYour exploits:"
			for e in self.state.players_expl[self.state.player]:
				print "{}{} - {} exploit # {}".format(e[0][0], e[1], e[0], e[1])

			print "\nTraced players: {}".format( "None" if len(self.state.players_traced[self.state.player]) == 0
												 else " ".join(map(str, self.state.players_traced[self.state.player])) )


			## have them assign a move to each owned machine (or do DDoS)
			print "<acting-machine> (R)econ <machine>"
			print "<acting-machine> (C)lean"
			print "<acting-machine> (H)ack <machine> <exploit>"
			print "<acting-machine> (B)ackdoor"
			print "<acting-machine> (P)atch <exploit>"
			print "(D)DoS <user>"
			moves = []  # a list of moves, each is a dictionaries
			# std move format: acting-maching player action parameters (machine/exploit/user)
			while len(moves) < len(self.state.players_own[self.state.player].keys()):
		#    for machine in sorted(players_own[player].keys()):
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
				
			## do all the actions
			print "\nMove results:"
			for move in moves:
				print "You did move {}".format(move)
				if move['action'] in self.move_funcs:
					self.move_funcs[move['action']](move)
				else:
					print "not yet implemented"
				# print board_os
				# print board_vuln
				
			raw_input("\nPress enter to clear screen ")
			print "\n"*100
			
			# next player
			self.state.player = (self.state.player + 1) % self.state.num_players


g=Game()
g.mainloop()
