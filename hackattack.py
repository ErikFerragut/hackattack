# HACK ATTACK - a cyber hacking game
#
# plans:
# V 2.0 - added knowledge system
# Future verseion in unknown order:
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

class Game(object):
    def __init__(self):
        self.state = GameState()
        self.move_funcs = {'r':self.do_recon, 'c':self.do_clean, 'h':self.do_hack,
                           'b':self.do_backdoor, 'p':self.do_patch, 'd':self.do_ddos}
        
        self.state.players_names = [ "Player {}".format(i)
                                     for i in xrange(self.state.num_players) ]
        
        self.players = [ Player(self, name) for name in self.state.players_names ]
        


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

        while True:
            if self.state.player == 0:
                self.state.game_round += 1

            player = self.players[self.state.player]
            if not player.update_output():
                break
            
            moves = player.get_moves()

            ### do all the actions and provide results

            player.say("\nMove results:")
            for move in moves:
                player.say("You did move {}".format(move))
                if move['action'] in self.move_funcs:
                    self.move_funcs[move['action']](move)
                else:
                    print "not yet implemented"

            player.turn_done()
            
            # next player
            self.state.player = (self.state.player + 1) % self.state.num_players


if __name__ == '__main__':
    g=Game()
    g.mainloop()
