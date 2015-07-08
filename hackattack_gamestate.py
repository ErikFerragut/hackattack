import random
import hackattack_util

class GameState(object):
    def __init__(self):
        self.game = game
        self.exploits_per_os = 5
        self.start_with_exploits = 4
        self.vuln_prob = 0.8

        self.detection_prob = { 'r':0.05, 'h':0.10, 'b':0.15, 'p':0.25, 's' : 0.30 }

        self.OSs = ['Linux', 'Windows', 'Mac', 'Solaris']

        '''self.all_exploits = []
        for o in self.OSs:
            for i in xrange(self.exploits_per_os):
                self.all_exploits.append( (o,i) )'''
        self.all_exploits = [ (o,i) for o in self.OSs for i in xrange(self.exploits_per_os) ]
        
        self.num_hosts = 5*self.game.num_players


        # (os, [vulnerabilities])
        self.board_os = [ random.choice(self.OSs) for i in xrange(self.num_hosts) ]
        self.board_vuln = [ [ i for i in range(self.exploits_per_os)
                              if random.random() < self.vuln_prob ]
                       for h in xrange(self.num_hosts) ]
        
        self.players_expl = []
        for i in xrange(self.num_players):
            E = set([])
            while len(E)<4:
                E.add(random.choice(self.OSs)[0]+str(hackattack_util.pick_exp_int()))
            self.players_expl.append(list(E))
            
        self.players_traced = [ set([]) for i in xrange(self.num_players) ]  # original
        self.news = { p:[] for p in xrange(self.num_players) }

        self.game_round = 0
