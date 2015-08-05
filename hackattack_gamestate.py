import random
from hackattack_util import *
from collections import defaultdict as ddict
import json

class GameState(object):
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
        self.news = { int(k):v for k,v in self.news.iteritems() }
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
