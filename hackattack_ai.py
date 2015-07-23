from hackattack_player import *
import random

class AI(Player):
    def get_moves(self):
        moves = []
        for p in self.own:
            # decide whether to fortify or expand
            if random.random() < 0.3: # fortify
                moves.append({'player':self.game.state.player,
                              'action':'b', 'from':p})
            else:                     # expand
                moves.append({'player':self.game.state.player,
                              'action':'h', 'from':p,
                              'to':random.randint(0,self.game.state.num_hosts),
                              'exploit':random.choice(self.players_expl)})
        return moves

    def start_round(self):
        s = self.game.state
        
        ## check for a new exploit
        if random.random() <= 1. / 6:
        
            ne = random.choice(self.game.state.OSs)[0] + str(hackattack_util.pick_exp_int())
            #self.players_expl.append(ne)
                
            while ne in self.players_expl:
                ne = random.choice(self.game.state.OSs)[0] + str(hackattack_util.pick_exp_int())
                
            self.players_expl.append(ne)#[s.player]
            self.say({'text':'You found a new exploit! ' + ne, 'type':'new exploit',
                      'exploit':ne})
    

    # def update_output(self):
        # pass
    

    # def turn_done(self):
        # pass

        
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
        # add it to a list for guy2 that are involved
        # store inferred information
        
class BackDoor(AI):

    def get_moves(self):
        moves = []
        for p in self.own:
            moves.append({'player':self.game.state.player,
                            'action':'b', 'from':p})
        return moves
class CleanClass(AI):

    def get_moves(self):
        moves = []
        for p in self.own:
            moves.append({'player':self.game.state.player,
                            'action':'c', 'from':p})
        return moves        
class JacobAI(AI):
    def __init__(self, game, name, start):
        super(JacobAI, self).__init__(game, name, start)
        self.machines = {i:0 for i in xrange(self.game.state.num_hosts)}
        self.machines[start] = 2
        self.counter = 0
        self.getReconTarget()
        
    def getReconTarget(self):
            if not 0 in self.machines.values():
                self.machines = {i:0 for i in xrange(self.game.state.num_hosts)}
            
            while True:
                tempRandomHost = random.randint(0,self.game.state.num_hosts-1)
                if self.machines[tempRandomHost]==0:
                    self.random_host = tempRandomHost
                    break
                    
    def get_moves(self):
        
        moves = []
        
        for p in self.own:
            if self.counter == 0 and self.machines[self.random_host] == 0:
                moves.append({'player':self.game.state.player,
                            'action':'r', 'from':p, 'to':self.random_host})
                self.machines[self.random_host] = 1
                
                #create random target for recon
                
            elif self.counter == 1:
                
                exploits = [ j for j in self.players_expl if self.oss[self.random_host][0]==j[0] and self.patches[self.random_host][int(j[1:])]==False]
                #print exploits
                if len(exploits) > 0:
                    moves.append({'player':self.game.state.player, 'action':'h', 
                    'from':p, 'to':self.random_host, 'exploit':exploits[0]}) 
                    self.machines[self.random_host] = 2
                else:
                    self.getReconTarget()
                    
                    moves.append({'player':self.game.state.player,
                            'action':'r', 'from':p, 'to':self.random_host})
                    self.machines[self.random_host] = 1
                #print moves
            elif self.counter == 2 or self.counter == 4:
                self.getReconTarget()
                
                moves.append({'player':self.game.state.player,
                    'action':'r', 'from':p, 'to':self.random_host})
                self.machines[self.random_host] = 1
            elif self.counter == 3 or self.counter == 5:
                exploits = [(m,e) for m in self.patches for e in self.players_expl if self.patches[m][int(e[1:])]==False ]
                exploits = [ me for me in exploits if me[0] not in self.own]
                print self.counter, exploits
                if len(exploits) > 0:
                    the_exploit = random.choice(exploits)
                    moves.append({'player':self.game.state.player, 'action':'h', 
                    'from':p, 'to':the_exploit[0], 'exploit':the_exploit[1]}) 
                    self.machines[the_exploit[0]] = 2
                else:
                    self.getReconTarget()
                    moves.append({'player':self.game.state.player,
                        'action':'r', 'from':p, 'to':self.random_host})
                    self.machines[self.random_host] = 1
            elif self.counter == 6 or self.counter == 8:
                moves.append({'player':self.game.state.player,
                            'action':'c', 'from':p})
            elif self.counter == 7:
                moves.append({'player':self.game.state.player,
                            'action':'b', 'from':p})
            elif self.counter == 9:
                for s in xrange(self.game.num_players):
                    if s in self.game.state.players_traced[self.game.state.player]:
                        moves.append({'action' : 'd' , 'user' : s , 'player' :self.game.state.player})
                        return moves
                
                exploits = [(m,e) for m in self.patches for e in self.players_expl if self.patches[m][int(e[1:])]==False ]
                exploits = [ me for me in exploits if me[0] not in self.own]
                print self.counter, exploits
                if len(exploits) > 0:
                    the_exploit = random.choice(exploits)
                    moves.append({'player':self.game.state.player, 'action':'h', 
                    'from':p, 'to':the_exploit[0], 'exploit':the_exploit[1]}) 
                    self.machines[the_exploit[0]] = 2
                else:
                    self.getReconTarget()
                    
                    moves.append({'player':self.game.state.player,
                            'action':'r', 'from':p, 'to':self.random_host})
                    self.machines[self.random_host] = 1
            elif self.counter == 10:
                self.counter = 6
                exploits = [(m,e) for m in self.patches for e in self.players_expl if self.patches[m][int(e[1:])]==False ]
                exploits = [ me for me in exploits if me[0] not in self.own]
                print self.counter, exploits
                if len(exploits) > 0:
                    the_exploit = random.choice(exploits)
                    moves.append({'player':self.game.state.player, 'action':'h', 
                    'from':p, 'to':the_exploit[0], 'exploit':the_exploit[1]}) 
                    self.machines[the_exploit[0]] = 2
                else:
                    self.getReconTarget()
                    moves.append({'player':self.game.state.player,
                        'action':'r', 'from':p, 'to':self.random_host})
                    self.machines[self.random_host] = 1
        self.counter +=1  
        return moves