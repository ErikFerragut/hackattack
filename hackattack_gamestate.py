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


        # (os, [vulnerabilities])
        self.board_os = [ random.choice(self.OSs) for i in xrange(self.num_hosts) ]
        self.board_vuln = [ [ i for i in range(self.exploits_per_os)
                              if random.random() < self.vuln_prob ]
                       for h in xrange(self.num_hosts) ]

        a = range(self.num_hosts)
        random.shuffle(a)
        players_start = [ aa for aa in a[:self.num_players] ]
        self.players_own = [ {s:1} for s in self.players_start ]
        self.players_expl = []
        for i in xrange(self.num_players):
            random.shuffle(self.all_exploits)
            self.players_expl.append( self.all_exploits[:self.start_with_exploits] )
        self.players_traced = [ set([]) for i in xrange(self.num_players) ]
        self.news = { p:[] for p in xrange(self.num_players) }
        self.game_round = 0
