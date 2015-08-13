# HACK ATTACK - a cyber hacking game
#
# plans:
# V 3.0 - Refactored to enable evaluation functions

import random
import time
from AndrewAI import *
from hackattack_player import *
from hackattack_NetPlayer import *
from hackattack_ai import *
from hackattack_util import *
from AndrewNathan import *
import sys
from collections import Counter

# new design
#   game    contains board information
#           has      players
#   players have     exploits, access, etc.
#           have     knowledge about the game
#           have     interface
#   ai      is a     player
#   game_setup function allows user(s) to decide on player ai's, player names, etc.

# process:
#   1. create an uninitialized player, which has a name and exploits
#   2. create the game, which updates players with pointer to it and their starting position
def choose_without_replacement(fromthis, thismany):
    '''Return in random order thismany samples from fromthis so that no two are the same.'''
    assert thismany < len(fromthis)
    choices = set([])
    while len(choices) <= thismany:
        choices.add(random.choice(fromthis))
    choices = list(choices)
    random.shuffle(choices)
    return choices


class Game(object):
    def __init__(self, players):
        '''Create an empty board for the game with uninitialized player objects'''
        self.players = players
        self.num_players = len(players)
        self.num_hosts = Hosts_Per_Player * self.num_players

        self.move_funcs = {'r':self.do_recon,    'c':self.do_clean, 'h':self.do_hack,
                           'b':self.do_backdoor, 'p':self.do_patch, 'd':self.do_ddos,
                           's':self.do_scan}

        self.board_os = [ random.choice(OS_List_Letters) for i in xrange(self.num_hosts) ]
        self.board_patches = [ [ i for i in range(Exploits_Per_OS)
                              if random.random() < Vuln_Prob ]
                                for h in xrange(self.num_hosts) ]
        
        self.round = 0   # number of rounds of the game played so far
        self.whose_turn = 0  # player whose turn it is
        
        starting_hosts = choose_without_replacement(xrange(self.num_hosts), self.num_players)
        for i in xrange(len(self.players)):
            self.players[i].start_player(self, starting_hosts[i], i)
        
    def detected(self, user, message):
        self.players[user].news.append(message) 

    def working_attacks(self, player, host):
        '''return a list of the short codes for attacks player has that work on machine'''
        return [ e for e in self.players[player].expl
                 if self.board_os[host][0] == e[0] and int(e[1:]) not in
                  self.board_patches[host] ]

    def do_scan(self, move):
        player = self.players[move['player']]
        for s in xrange(self.num_players):            
            if s != self.whose_turn:
                if move['from'] in self.players[s].own and self.players[s].own[move['from']] > 0:
                    player.say({'text':"Player {} accounts {}".format(s,
                                self.players[s].own[move['from']]),
                                'player':s, 'machine':move['from'], 'type':'accounts',
                                'has accounts':self.players[s].own[move['from']]})
                    
        for playerB in xrange(self.num_players):
            if random.random() < Detection_Prob['s']:
                    if move['from'] in self.players[playerB].own:
                        self.detected( playerB,
                        "Player {} scanned machine {} from machine {}".format(
                            player.name, move['player'], move['from']))
                        
    def do_recon(self,move):
        player = self.players[move['player']]
        player.say({'text':"Machine {} is running the {} OS".format(move['to'],
                    self.board_os[move['to']]), 'type':'os',
                    'action':'r', 'machine':move['to'], 'OS':self.board_os[move['to']]})
        openings = self.working_attacks(move['player'], move['to'])
        if len(openings) == 0:
            player.say({'text':"You have no exploits for that machine.", 'machine':move['to'],
                        'exploitable with':[], 'type':'exploits'}) 
        else:
            player.say({'text':"You can hack it with {}".format(openings), 'machine':move['to'],
                        'exploitable with':[o for o in openings], 'type':'exploits'})

        # check for detection
        for playerB in xrange(self.num_players):
            if random.random() < Detection_Prob['r']:
                if move['from'] in self.players[playerB].own:
                    self.detected(playerB, "Player {} probed machine {} from machine {}".format(
                        player.name, move['to'], move['from']))

    def do_clean(self,move):
        player = self.players[move['player']]
        for p in xrange(self.num_players):
            if p != self.whose_turn:
                if move['from'] in self.players[p].own and self.players[p].own[move['from']] > 0:
                    num_removed = min(player.own[move['from']], self.players[p].own[move['from']])
                    self.players[p].own[move['from']] -= num_removed
                    if self.players[p].own[move['from']] == 0:
                        self.players[p].own.pop(move['from'])
                    player.say({'text':"You removed {} of {}'s accounts".format(
                        num_removed, self.players[p].name),
                                'machine':move['from'], 'accounts removed':num_removed,
                                'player':p, 'type':'clean'})
                    self.players[p].news.append("{} removed {} of your accounts from machine {}".\
                        format(self.players[move['player']].name, num_removed, move['from']))

                    # check for trace
                    if not p in self.players[move['player']].traced:
                        if min([random.random() for i in xrange(num_removed)]) < 1./6:
                            self.players[move['player']].traced.append(p)
                            player.say({'text':"You traced {}!".format(self.players[p].name),
                                        'player':p, 'type':'trace'})

        player.say({'text':"Clean completed on machine {}".format(move['from'])})

    def do_hack(self,move):
        theplayer = self.players[move['player']]
        player = move['player']
        worked = move['exploit'] in self.working_attacks(player, move['to'])

        if worked:
            theplayer.say({'text':"Hack succeeded", 'hacked':move['to'], 'with':move['exploit'],
                            'from':move['from']})
            for playerB in xrange(self.num_players):
                if playerB == move['player']:
                    continue   # don't tell someone what they themselves did
                if random.random() < Detection_Prob['h']:
                    if move['from'] in self.players[playerB].own:
                        self.detected( playerB,
                            "{} successfully hacked machine {} from machine {}".format(
                                theplayer.name, move['to'], move['from']))
                    elif move['to'] in self.players[playerB].own:
                        self.detected( playerB,
                            "Player {} successfully hacked machine {} from machine {}".\
                        format(theplayer.name, move['to'], move['from']))
                        
            # add access
            if move['to'] not in theplayer.own:
                theplayer.own[move['to']] = 1  #tookout [player]
            else:
                theplayer.own[move['to']] += 1
        else:
            theplayer.say({'text':"Hack failed", 'machine':move['to'],
                           'with':move['exploit'], 'from':move['from'],
                           'type':'failed hack'})
            
            for playerB in xrange(self.num_players):
                if move['from'] in self.players[playerB].own:
                    self.detected( playerB,
                        "Player {} failed to hack machine {} from machine {}".format(
                            theplayer.name, move['to'], move['from']))
                elif move['to'] in self.players[playerB].own:
                    self.detected( playerB,
                        "Player {} failed to hack machine {} from machine {}".format(
                            theplayer.name, move['to'], move['from']))

    def do_backdoor(self,move):
        player = move['player']
        theplayer = self.players[move['player']]
        
        self.players[player].own[move['from']] += 1
        
        for playerB in xrange(self.num_players):
            if random.random() < Detection_Prob['b']:
                if move['from'] in self.players[playerB].own:
                    self.detected( playerB,  "Player {} backdoored machine {}".format(
                    theplayer.name, move['from']))

        theplayer.say({'text':"One backdoor added to machine {}; you now have {}".format(
            move['from'], theplayer.own[move['from']]),
            'machine':move['from'], 'type':'backdoor',
            'have accounts':theplayer.own[move['from']]})
        
    def do_patch(self,move):
        theplayer = self.players[move['player']]
        if move['exploit'][0].upper() == self.board_os[move['from']][0]:
            patch_id = int(move['exploit'][1:])
            if patch_id in self.board_patches[move['from']]:
                self.board_patches[move['from']].append(patch_id)
                theplayer.say({'text':"Vulnerability patched", 'machine':move['from'],
                               'patched':patch_id, 'fullname':move['exploit'],
                               'type':'patch'})
            else:
                theplayer.say({'text':"Vulnerability was already patched",
                               'machine':move['from'], 'patched':patch_id,
                               'fullname':move['exploit'], 'type':'patch'})
        else:
            theplayer.say({'text':"Failed patch due to OS mismatch of {} on {}".format(
                move['exploit'], self.board_os[move['from']])})

        for playerB in xrange(self.num_players):
            if random.random() < Detection_Prob['p']:
                if move['from'] in self.players[playerB].own:
                    self.detected( playerB,  "Player {} patched machine {} from machine {}".format(theplayer.name, move['player'], move['from']))

    def do_ddos(self,move):
        # do you have the trace you need
        player = move['player']
        theplayer = self.players[move['player']]
        otherplayer = self.players[move['user']]
        if move['user'] in self.players[player].traced:
            you_str = len(theplayer.own)
            them_str = len(otherplayer.own)
            if you_str > them_str:
                theplayer.say({'text': "YOU WON THE DDOS -- {} IS ELIMINATED".format(self.players[move['user']].name.upper()),
                               'ddoser':move['player'], 'ddosee':move['user'], 'result':'win'})
                otherplayer.own = {}
                self.players[move['user']].news.append(
                    "YOU WERE DDOSED BY {}".format(self.players[player].name.upper()))
                #ddos results into news
                for p in xrange(self.num_players):
                    self.players[p].news.append(
                        "{} HAS SUCCESSFULLY DDOSED {}".format(self.players[player].name.upper(),
                        self.players[move['user']].name.upper() ))
            elif you_str < them_str:
                theplayer.say({'text':"YOU LOST THE DDOS -- YOU ARE ELIMINATED",
                               'ddoser':move['player'], 'ddosee':move['user'], 'result':'lost'})
                theplayer.own = {}
                self.players[move['user']].news.append(
                    "{} tried to DDoS you but lost and was eliminated".format(
                        self.players[player].name))
                #announces in the news about the ddos activity
                for p in xrange(self.num_players):
                    self.players[p].news.append(
                        "{} UNSUCCESSFULLY DDOSED {}".format(
                            self.players[player].name.upper(),
                            self.players[move['user']].name.upper() ))
            else:
                theplayer.say({'text':"DDOS was a tie", 'ddoser':move['player'], 'ddosee':move['user'], 'result':'tie'})
                self.players[move['user']].news.append(
                    "{} tried to DDoS you but it was tie".format(self.players[player].name))
                for p in xrange(self.num_players):
                    self.players[move['user']].news.append(
                        "{} DDOSED {} BUT IT WAS A TIE".format(self.players[player].name.upper(),
                            self.players[move['user']].name.upper() ))
        else:
            theplayer.say({'text':"You need a trace before you can ddos (this output signifies a logic error!)"})
            
    def new_patches(self):
        if random.random()<= 0.15:
            x = random.choice(OS_List)
            y = random.randint(0, 4)
            for i in xrange(self.num_hosts):
                if self.board_os[i] == x and y not in self.board_patches[i]:
                    self.board_patches[i].append(y)

    def mainloop(self, max_rounds=100):
        while True:
            if self.whose_turn == 0:
                self.round += 1
                if self.round == max_rounds:
                    return 'tie'
            self.new_patches()
            player = self.players[self.whose_turn]
            player.update_status()  # did they win, lose?

            player.start_round()   # did they get a new exploit?f
            
            player.update_output()  # show screen
            if player.status == 'won':
                return self.whose_turn
            elif player.status == 'out':
                self.whose_turn = (self.whose_turn + 1) % self.num_players
                continue
            
            moves = player.get_moves()

            # check that the moves are legit
            hosts_used = Counter([ m['from'] for m in moves if 'from' in m ])
            if len(hosts_used) > 0:
                assert set(hosts_used.keys()).issubset( set(player.own.keys()) ), "{} Used non-owned machine:{}\nowned:{}".format(player.name, moves, player.own)
                assert max(hosts_used.values()) <= 1, "{} used machine more than once: {}\nowned:{}".format(player.name, moves, player.own)
                assert len(hosts_used) == len(player.own), "{} did not use some machine(s):{}\nowned:{}".format(player.name, moves, player.own)
            else:
                assert moves[0]['action'] in 'dq', "what?... player {}\nmoves{}\nowns:{}".format(player.name, moves, player.own)
            # handle save and load moves
            if moves[0]['action'] == 'q':
                raise NotImplementedError, "Save and load no longer functioning for now"
                return 'q'

            ### do all the actions and provide results

            player.say({'text':"\nMove results:"})

            for move in moves:
                # player.say({'text':"You did move {}".format(move), 'move':move})
                if move['action'] in self.move_funcs:
                    self.move_funcs[move['action']](move)
                else:
                    print "not yet implemented"

            player.turn_done()
            
            # next player
            self.whose_turn = (self.whose_turn + 1) % self.num_players



if __name__ == '__main__':
    players = [ Andrews('Andrew'), EthanAI('Ethan'), JacobAI('Jacob'), AndrewNathan('AN') ]
    g=Game(players)
    r = g.mainloop()
    print r

