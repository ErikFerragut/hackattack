from hackattack_player import *
from hackattack_util import *
import random

class AI(Player):
    def get_moves(self):
        moves = []
        for p in self.own:
            # decide whether to fortify or expand
            if random.random() < 0.3: # fortify
                moves.append({'player':self.id,
                              'action':'b', 'from':p})
            else:                     # expand
                moves.append({'player':self.id,
                              'action':'h', 'from':p,
                              'to':random.randint(0,self.game.num_hosts),
                              'exploit':random.choice(self.players_expl)})
        return moves

    def start_round(self):
        ## check for a new exploit
        if random.random() <= 1. / 6:
        
            ne = random.choice(OS_List_Letters) + str(pick_exp_int())
            #self.players_expl.append(ne)
                
            while ne in self.players_expl:
                ne = random.choice(OS_List_Letters) + str(pick_exp_int())
                
            self.players_expl.append(ne)
            self.say({'text':'You found a new exploit! ' + ne, 'type':'new exploit',
                      'exploit':ne})
        
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
            moves.append({'player':self.id,
                            'action':'b', 'from':p})
        return moves
    
class CleanClass(AI):
    def get_moves(self):
        moves = []
        for p in self.own:
            moves.append({'player':self.id,
                            'action':'c', 'from':p})
        return moves
           
class JacobAI(AI):
    def init_ai(self):
        self.machines = {i:0 for i in xrange(self.game.num_hosts)}
        self.machines[start] = 2
        self.counter = 0
        self.getReconTarget()
        
    def getReconTarget(self):
            if not 0 in self.machines.values():
                self.machines = {i:0 for i in xrange(self.game.num_hosts)}
            
            while True:
                tempRandomHost = random.randint(0,self.game.num_hosts-1)
                if self.machines[tempRandomHost]==0:
                    self.random_host = tempRandomHost
                    break
                    
    def get_moves(self):
        moves = []
        for p in self.own:
            if self.counter == 0 and self.machines[self.random_host] == 0:
                moves.append({'player':self.id,
                            'action':'r', 'from':p, 'to':self.random_host})
                self.machines[self.random_host] = 1
                
                #create random target for recon
                
            elif self.counter == 1:
                
                exploits = [ j for j in self.players_expl if self.oss[self.random_host][0]==j[0] and self.patches[self.random_host][int(j[1:])]==False]
                #print exploits
                if len(exploits) > 0:
                    moves.append({'player':self.id, 'action':'h', 
                    'from':p, 'to':self.random_host, 'exploit':exploits[0]}) 
                    self.machines[self.random_host] = 2
                else:
                    self.getReconTarget()
                    
                    moves.append({'player':self.id,
                            'action':'r', 'from':p, 'to':self.random_host})
                    self.machines[self.random_host] = 1
                #print moves
            elif self.counter == 2 or self.counter == 4:
                self.getReconTarget()
                
                moves.append({'player':self.id,
                    'action':'r', 'from':p, 'to':self.random_host})
                self.machines[self.random_host] = 1
            elif self.counter == 3 or self.counter == 5:
                exploits = [(m,e) for m in self.patches for e in self.players_expl if self.patches[m][int(e[1:])]==False ]
                exploits = [ me for me in exploits if me[0] not in self.own]
                print self.counter, exploits
                if len(exploits) > 0:
                    the_exploit = random.choice(exploits)
                    moves.append({'player':self.id, 'action':'h', 
                    'from':p, 'to':the_exploit[0], 'exploit':the_exploit[1]}) 
                    self.machines[the_exploit[0]] = 2
                else:
                    self.getReconTarget()
                    moves.append({'player':self.id,
                        'action':'r', 'from':p, 'to':self.random_host})
                    self.machines[self.random_host] = 1
            elif self.counter == 6 or self.counter == 8:
                moves.append({'player':self.id,
                            'action':'c', 'from':p})
            elif self.counter == 7:
                moves.append({'player':self.id,
                            'action':'b', 'from':p})
            elif self.counter == 9:
                for s in xrange(self.game.num_players):
                    if s in self.ids_traced[self.id]:
                        moves.append({'action' : 'd' , 'user' : s , 'player' :self.id})
                        return moves
                
                exploits = [(m,e) for m in self.patches for e in self.players_expl if self.patches[m][int(e[1:])]==False ]
                exploits = [ me for me in exploits if me[0] not in self.own]
                print self.counter, exploits
                if len(exploits) > 0:
                    the_exploit = random.choice(exploits)
                    moves.append({'player':self.id, 'action':'h', 
                    'from':p, 'to':the_exploit[0], 'exploit':the_exploit[1]}) 
                    self.machines[the_exploit[0]] = 2
                else:
                    self.getReconTarget()
                    
                    moves.append({'player':self.id,
                            'action':'r', 'from':p, 'to':self.random_host})
                    self.machines[self.random_host] = 1
            elif self.counter == 10:
                self.counter = 6
                exploits = [(m,e) for m in self.patches for e in self.players_expl if self.patches[m][int(e[1:])]==False ]
                exploits = [ me for me in exploits if me[0] not in self.own]
                print self.counter, exploits
                if len(exploits) > 0:
                    the_exploit = random.choice(exploits)
                    moves.append({'player':self.id, 'action':'h', 
                    'from':p, 'to':the_exploit[0], 'exploit':the_exploit[1]}) 
                    self.machines[the_exploit[0]] = 2
                else:
                    self.getReconTarget()
                    moves.append({'player':self.id,
                        'action':'r', 'from':p, 'to':self.random_host})
                    self.machines[self.random_host] = 1
        self.counter +=1  
            
        return moves
    
class EthanAI(AI):
    def init_ai(self):
        self.easy_hacks = []
        self.turns_since_c = {n:0 for n in self.own} 
        
    def update_lists(self):
        self.easy_hacks = [m for m in self.patches
                           if any([self.patches[m][l] == False for l in self.patches[m]])]
        self.easy_hacks = [m for m in self.easy_hacks if m not in self.own]
        for i in self.own:
            if i not in self.turns_since_c:#.keys()
                self.turns_since_c.update({i:3})
        for h in self.own:
            self.turns_since_c[h] += 1
        return
        
    def func1(self):
        self.own2 = [m for m in self.own.keys()]
        while 0 < len(self.own2):  
            for i in self.own2:
                if len(self.min_accounts[i]) > 0 and \
                  any([self.min_accounts[i][u] != '' and self.min_accounts[i][u] > 0 for u in self.min_accounts[i]]):
                    self.moves.append({'player':self.id,'action':'c', 'from':i})
                    self.own2.remove(i)
            if len(self.own2) == 0:
                break                         
            if len(self.easy_hacks) > 0:
                for l in self.easy_hacks:
                    q = random.choice(self.own2)
                    self.moves.append({'player':self.id,'action':'h','from':q,'to':l,
                    'exploit':random.choice([e for e in self.players_expl 
                    if e[0] == self.oss[l][0] and self.patches[l][int(e[1:])] == False])})                 
                    self.own2.remove(q)
                    self.easy_hacks.remove(l)
                    if len(self.own2) == 0:
                        break                        
            if len(self.own2) > 0:
                v = random.choice(self.own2)
                self.moves.append({'player':self.id,'action':'r', 'from':v,
                'to':random.choice(list(set(xrange(self.game.num_hosts)).difference(list(self.own))))})
                self.own2.remove(v)
        return self.moves
    def func2(self):
        self.own2 = [m for m in self.own.keys()]
        while 0 < len(self.own2): 
            for i in self.own2:
                if len(self.min_accounts[i]) > 0 and \
                  any([self.min_accounts[i][u] != '' and self.min_accounts[i][u] > 0 for u in self.min_accounts[i]]):
                    self.moves.append({'player':self.id,'action':'c', 'from':i})
                    self.own2.remove(i)            
                    if len(self.own2) == 0:
                        break  
            if len(self.easy_hacks) > 0:
                for l in self.easy_hacks:
                    q = random.choice(self.own2)
                    self.moves.append({'player':self.id,'action':'h','from':q,'to':l,
                    'exploit':random.choice([e for e in self.players_expl 
                    if e[0] == self.oss[l][0] and self.patches[l][int(e[1:])] == False])})                 
                    self.own2.remove(q)
                    self.easy_hacks.remove(l)
                    if len(self.own2) == 0:
                        break
            for y in self.own2:
                if self.turns_since_c[y] > 2:
                    self.moves.append({'player':self.id,'action':'c', 'from':y})
                    self.turns_since_c[y] = 0
                    self.own2.remove(y)
            if len(self.own2) > 0:
                v = random.choice(self.own2)
                self.moves.append({'player':self.id,'action':'r', 'from':v,
                        'to':random.choice(
                        list(set(xrange(self.game.num_hosts)).difference(list(self.own))))})
                self.own2.remove(v)
        return self.moves

    def get_moves(self):
        self.update_lists()
        self.moves = []
        if len(self.own) < 3:
            self.moves = self.func1()
        if len(self.own) > 2 and len(self.own) < 20:
            self.moves = self.func2()
        if len(self.own) > 20:
            for j in self.own:
                self.moves.append({'player':self.id,'action':'c', 'from':j})
        if self.moves == []:
            for i in self.own:
                self.moves.append({'player':self.id,'action':'b', 'from':i})            
        return self.moves       
    '''def war():
        hack target with three computers
        if some remain but you were cleaned hack with 1 - number removed
        if some remain and not cleaned clean then scan if nothing detected
        if all cleaned hack with 7 and follow same procedure, but if still 
        cleaned label target Nathan'''
