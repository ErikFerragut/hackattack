# HACK ATTACK - a cyber hacking game
#
# plans:
# V 2.0 - added knowledge system
# Future version in unknown order:
#  - network game
#  - private/public messaging capability
#  - optional gui, maybe curses (maybe as a plug-in?)
#  - computer AI players
#  - expanded rules
#
# V 1.1 - various bug fixes 
#         - recon now says what was probed
#         - added some ascii art on title page
#         - now keeps track of rounds
#         - put names in, but using "Player <i>" since still specify them by number
#         - drops out players who have lost (but without first notifying them!)
#         - made it so you specify machines and thereby the order of the actions
#         - breaks out of loop when you specify ddos
# V 1.0 - first working version - 6/11/2015

# known bugs:
#  - when you lose, you never get another turn, so you don't really learn why

import random
import time
from hackattack_gamestate import *
from hackattack_player import *
import sys


class Game(object):
    def __init__(self):
        self.num_players = 2
        self.state = GameState(self)
        self.move_funcs = {'r':self.do_recon, 'c':self.do_clean, 'h':self.do_hack,
                           'b':self.do_backdoor, 'p':self.do_patch, 'd':self.do_ddos, 's' : self.do_scan}
        
        self.state.players_names = [ "Player {}".format(i)
        
                                     for i in xrange(self.num_players) ]
        
        start = set([])
        while len(start)<self.num_players:
            start.add(random.randrange(self.state.num_hosts))
        start = list(start)
        random.shuffle(start)
        self.players = [ Player(self, name,s) for name,s in zip(self.state.players_names, start) ]
        


    def detected(self, user, message):
        #s=self.state
        self.state.news[user].append(message) 
        
    def working_attacks(self,player, host):
        '''return a list of the short codes for attacks player has that work on machine'''
        # print "player {}'s exploits are {} (vuln = {})".format(player, self.state.players_expl[player], self.state.board_vuln[host])
        return [ e for e in self.players[player].players_expl
                 if self.state.board_os[host][0] == e[0] and int(e[1:]) not in self.state.board_patches[host] ]
                 
    def do_scan(self, move):
        
        #player = move['player']
        #player2 = self.state.player[move['to']]
        player = self.players[move['player']]
        for s in xrange(self.num_players):
            
            if s != self.state.player:
                if move['from'] in self.players[s].own and self.players[s].own[move['from']] > 0:
                    player.say({'text':"Player {} accounts {}".format(s,
                                self.players[s].own[move['from']]),
                                'player':s, 'machine':move['from'], 'type':'accounts',
                                'has accounts':self.players[s].own[move['from']]})
                    
        for playerB in xrange(self.num_players):
            
            if random.random() < self.state.detection_prob['s']:
                #for s in xrange(self.num_players):
                #for b in xrange(self.players[s].own[playerB]):
                    if move['from'] in self.players[playerB].own:
                        self.detected( playerB,  "Player {} scanned machine {} from machine {}".format(player.name, move['player'], move['from']))    
                
                #if self.players[s].own[player][move['from']] is self.players[s].own[playerB]:
                    #self.detected( playerB,  "Player {} probed machine {} from machine {}".format(player.name, move['player'], move['from']))    
                    #if self.game.players_own[s][move['from']] == 0:
                    #self.game.players_own[s].pop(move['from'])
                    #print "Player {} has accounts".format(self.state.players_names[s])
                    #print self.game.players_own
                    
    def do_recon(self,move):
        player = self.players[move['player']]
        player.say({'text':"Machine {} is running the {} OS".format(move['to'],
                    self.state.board_os[move['to']]), 'type':'os',
                    'action':'r', 'machine':move['to'], 'OS':self.state.board_os[move['to']]})
        openings = self.working_attacks(move['player'], move['to'])
        if len(openings) == 0:
            player.say({'text':"You have no exploits for that machine.", 'machine':move['to'], 'exploitable with':[], 'type':'exploits'}) 
        else:
            player.say({'text':"You can hack it with {}".format(openings), 'machine':move['to'],
                        'exploitable with':[o for o in openings], 'type':'exploits'})

        # check for detection
        for playerB in xrange(self.num_players):
            if random.random() < self.state.detection_prob['r']:
                if move['from'] in self.players[playerB].own:
                
                    self.detected( playerB,  "Player {} probed machine {} from machine {}".format(player.name, move['to'], move['from']))

    def do_clean(self,move):
        player = self.players[move['player']]
        for p in xrange(self.num_players):
            if p != self.state.player:
                if move['from'] in self.players[p].own and self.players[p].own[move['from']] > 0:
                    num_removed = min(player.own[move['from']], self.players[p].own[move['from']])
                    self.players[p].own[move['from']] -= num_removed
                    if self.players[p].own[move['from']] == 0:
                        self.players[p].own.pop(move['from'])
                    player.say({'text':"You removed {} of {}'s accounts".format(num_removed, self.state.players_names[p]),
                                'machine':move['from'], 'accounts removed':num_removed, 'player':p, 'type':'clean'})
                    self.state.news[p].append("{} removed {} of your accounts from machine {}".format(
                        self.state.players_names[move['player']], num_removed, move['from']))
                    # check for trace
                    if not p in self.state.players_traced[move['player']]:
                        if min([random.random() for i in xrange(num_removed)]) < 1./6:
                            self.state.players_traced[move['player']].append(p)
                            player.say({'text':"You traced {}!".format(self.state.players_names[p]), 'player':p, 'type':'trace'})
                            
        player.say({'text':"Clean completed on machine {}".format(move['from'])})

    def do_hack(self,move):
        theplayer = self.players[move['player']]
        self.state.detection_prob['h'] = 0.15
        player = move['player']
        worked = move['exploit'] in self.working_attacks(player, move['to'])
        # detected? -- do it first so you don't learn if you were detected
        #if random.random() < self.state.detection_prob['h']:
           # self.detected(move['to'], "{} {}successfully hacked machine {} from {}".format(
             # self.state.players_names[player], "" if worked else "un", move['to'], move['from']))
        
        if worked:
            theplayer.say({'text':"Hack succeeded", 'hacked':move['to'], 'with':move['exploit'], 'from':move['from']})
            for playerB in xrange(self.num_players):
                if playerB == move['player']:
                    continue   # don't tell someone what they themselves did
                if random.random() < self.state.detection_prob['h']:
                    if move['from'] in self.players[playerB].own:
                        self.detected( playerB,  "{} successfully hacked machine {} from machine {}".format(theplayer.name, move['to'], move['from']))
                    elif move['to'] in self.players[playerB].own:
                        self.detected( playerB,  "Player {} successfully hacked machine {} from machine {}".format(theplayer.name, move['to'], move['from']))
            # add access
            if move['to'] not in theplayer.own:
                theplayer.own[move['to']] = 1  #tookout [player]
            else:
                theplayer.own[move['to']] += 1
        else:
            theplayer.say({'text':"Hack failed", 'machine':move['to'],
                           'with':move['exploit'], 'from':move['from'],
                           'type':'failed hack'})
            self.state.detection_prob['h'] = self.state.detection_prob['h'] * 3
            
            for playerB in xrange(self.num_players):
                #if random.random() < self.state.detection_prob['h']:
                    #self.detected( playerB,  "Player {} failed a hack on machine {} from machine {}".format(theplayer.name, move['to'], move['from']))
                if move['from'] in self.players[playerB].own:
                    self.detected( playerB,  "Player {} successfully hacked machine {} from machine {}".format(theplayer.name, move['to'], move['from']))
                elif move['to'] in self.players[playerB].own:
                    self.detected( playerB,  "Player {} failed to hack machine {} from machine {}".format(theplayer.name, move['to'], move['from']))
                

    def do_backdoor(self,move):
        player = move['player']
        theplayer = self.players[move['player']]
        
        self.players[player].own[move['from']] += 1
        #if random.random() < self.state.detection_prob['b']:
            #self.detected(move['from'], "{} added a backdoor to machine {}".format(self.state.players_names[player],
                                  #                                            move['from']))
        for playerB in xrange(self.num_players):
            if random.random() < self.state.detection_prob['b']:
                if move['from'] in self.players[playerB].own:
                    self.detected( playerB,  "Player {} backdoored machine {} from machine {}".format(theplayer.name, move['player'], move['from']))

        theplayer.say({'text':"One backdoor added to machine {}; you now have {}".format(
            move['from'], theplayer.own[move['from']]),
            'machine':move['from'], 'type':'backdoor',
            'have accounts':theplayer.own[move['from']]})
        
    def do_patch(self,move):
        theplayer = self.players[move['player']]
        if move['exploit'][0].upper() == self.state.board_os[move['from']][0]:
            patch_id = int(move['exploit'][1:])
            if patch_id in self.state.board_patches[move['from']]:
                self.state.board_patches[move['from']].append(patch_id)
                theplayer.say({'text':"Vulnerability patched", 'machine':move['from'],
                               'patched':patch_id, 'fullname':move['exploit'],
                               'type':'patch'})
            else:
                theplayer.say({'text':"Vulnerability was already patched",
                               'machine':move['from'], 'patched':patch_id,
                               'fullname':move['exploit'], 'type':'patch'})
        else:
            theplayer.say({'text':"Failed patch due to OS mismatch of {} on {}".format(move['exploit'], self.state.board_os[move['from']])})

        #if random.random() < self.state.detection_prob['p']:
           # self.detected(move['from'], "{} patched machine {}".format(self.state.players_names[move['player']],
                         #                                         move['from']))
        for playerB in xrange(self.num_players):
            if random.random() < self.state.detection_prob['p']:
                if move['from'] in self.players[playerB].own:
                    self.detected( playerB,  "Player {} patched machine {} from machine {}".format(theplayer.name, move['player'], move['from']))

    def do_ddos(self,move):
        # do you have the trace you need
        player = move['player']
        theplayer = self.players[move['player']]
        otherplayer = self.players[move['user']]
        if move['user'] in self.state.players_traced[player]:
            you_str = len(theplayer.own)
            them_str = len(otherplayer.own)
            if you_str > them_str:
                theplayer.say({'text': "YOU WON THE DDOS -- {} IS ELIMINATED".format(self.state.players_names[move['user']].upper()),
                               'ddoser':move['player'], 'ddosee':move['user'], 'result':'win'})
                player.own[move['user']] = {}
                self.state.news[move['user']].append("YOU WERE DDOSED BY {}".format(self.state.players_names[player].upper()))
                #ddos results into news
                for p in xrange(self.num_players):
                    self.state.news[p].append("{} HAS SUCCESSFULLY DDOSED {}".format(self.state.players_names[player].upper(), self.state.players_names[move['user']].upper() ))
            elif you_str < them_str:
                theplayer.say({'text':"YOU LOST THE DDOS -- YOU ARE ELIMINATED",
                               'ddoser':move['player'], 'ddosee':move['user'], 'result':'lost'})
                theplayer.own = {}#need?[player]
                self.state.news[move['user']].append("{} tried to DDoS you but lost and was eliminated".format(self.state.players_names[player]))
                #announces in the news about the ddos activity
                for p in xrange(self.num_players):
				    self.state.news[p].append("{} UNSUCCESSFULLY DDOSED {}".format(self.state.players_names[player].upper(), self.state.players_names[move['user']].upper() ))
            else:
                theplayer.say({'text':"DDOS was a tie", 'ddoser':move['player'], 'ddosee':move['user'], 'result':'tie'})
                self.state.news[move['user']].append("{} tried to DDoS you but it was tie".format(self.state.players_names[player]))
                for p in xrange(self.num_players):
                    self.state.news[move['user']].append("{} DDOSED {} BUT IT WAS A TIRE".format(self.state.players_names[player].upper(), self.state.players_names[move['user']].upper() ))
        else:
            theplayer.say({'text':"You need a trace before you can ddos (this output signifies a logic error!)"})
            
    def new_patches(self):
        x = random.choice(self.state.OSs)
        y = random.randint(0, 4)
        if random.random()<= 0.15:
            for i in xrange(self.state.num_hosts):
                if self.state.board_os[i] == x:
                    try:
                        self.state.board_vuln[i].append(y)
                    except:
                        pass

    def mainloop(self):
        while True:
            if self.state.player == 0:
                self.state.game_round += 1
            self.new_patches()
            player = self.players[self.state.player]
            player.update_status()  # did they win, lose?

            player.start_round()   # did they get a new exploit?f
            
            player.update_output()  # show screen
            if player.status == 'won':
                break
            elif player.status == 'out':
                self.state.player = (self.state.player + 1) % self.num_players
                continue
            
            moves = player.get_moves()

            # handle save and load moves
            if moves[0]['action'] == 'q':
                open(moves[0]['filename'], 'w').write( self.state.to_json() )
                print "Game saved as file {}".format(moves[0]['filename'])
                print "Reload using  'python hackattack.py {}'".format(moves[0]['filename'])
                break

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
            self.state.player = (self.state.player + 1) % self.num_players



if __name__ == '__main__':
    g=Game()
    if len(sys.argv) > 1:
        S = '\n'.join(open(sys.argv[1], 'r').readlines())
        g.state.from_json(S)
    else:
        self.state.player = 0

    g.mainloop()
