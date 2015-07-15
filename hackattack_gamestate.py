import random
import hackattack_util
from collections import defaultdict as ddict
import json

class GameState(object):
    def __init__(self, game):
        self.game = game
        self.exploits_per_os = 5
        self.start_with_exploits = 4
        self.vuln_prob = 0.2
        self.player = 0

        self.detection_prob = { 'r':0.05, 'h':0.20, 'b':0.15, 'p':0.25, 's' : 0.30 }

        self.OSs = ['Linux', 'Windows', 'Mac', 'Solaris']

        '''self.all_exploits = []
        for o in self.OSs:
            for i in xrange(self.exploits_per_os):
                self.all_exploits.append( (o,i) )'''
        self.all_exploits = [ (o,i) for o in self.OSs for i in xrange(self.exploits_per_os) ]

        self.num_hosts = 5*self.game.num_players


        # (os, [vulnerabilities])
        self.board_os = [ random.choice(self.OSs) for i in xrange(self.num_hosts) ]
        self.board_patches = [ [ i for i in range(self.exploits_per_os)
                              if random.random() < self.vuln_prob ]
                       for h in xrange(self.num_hosts) ]
                       

        self.players_expl = []
        

            
        self.players_traced = [ [] for i in xrange(self.game.num_players) ]
        self.news = { p:[] for p in xrange(self.game.num_players) }

        self.game_round = 0

    def to_json(self):
        special = ['move_funcs', 'players', 'state', 'game']
        savethis = {'state':{k:v for k,v in self.__dict__.iteritems()
                             if k not in special},
                    'game':{k:v for k,v in self.game.__dict__.iteritems()
                            if k not in special},
                    'players':{i: {k:v for k,v in self.game.players[i].__dict__.iteritems()
                                   if k not in special}
                                for i in xrange(self.game.num_players)} }
        return json.dumps(savethis)

    def from_json(self, s):
        # reload variable, convert any dict keys from str to nonstring as fnec.
        j = json.loads(s)
        self.__dict__.update(j['state'])
        self.board_os = map(str, self.board_os)
        #self.news = { int(k):v for k,v in self.news.iteritems() }
        self.game.__dict__.update(j['game'])
        for i in j['players']:
            P = self.game.players[int(i)]
            P.__dict__.update(j['players'][i])
            P.min_accounts = ddict(lambda :ddict(str),
                                   {int(k):ddict(str, {int(kk):vv for kk,vv in v.iteritems()})
                                    for k,v in P.min_accounts.iteritems()})
            P.max_accounts = ddict(lambda :ddict(str),
                                   {int(k):ddict(str, {int(kk):vv for kk,vv in v.iteritems()})
                                    for k,v in P.max_accounts.iteritems()})
            P.patches = ddict(lambda :ddict(str),
                                   {int(k):ddict(str, {int(kk):vv for kk,vv in v.iteritems()})
                                    for k,v in P.max_accounts.iteritems()})
            P.oss = ddict(str, {int(k):v for k,v in P.oss.iteritems()})
            P.own = { int(k): v for k,v in P.own.iteritems() }
    
if __name__ == '__main__':
    import hackattack
    g = hackattack.Game()
    s = g.state.to_json()
    # save this, reload it...
    g.state.from_json(s)
