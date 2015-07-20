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
    
    """def update_output(self):
        pass
    

    def turn_done(self):
        pass"""
        
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
class Andrew(AI):
    def get_moves(self):
        alreadyreconed = []
        import random
        moves = []
        
        
        for s in xrange(self.game.num_players):
            if s in self.game.state.players_traced[self.game.state.player]:
                moves.append({'action' : 'd' , 'user' : self.game.state.player , 'player' : s})
                print moves
                return moves
        
        
        
        
        
        
        amount2 = self.game.state.num_hosts / 2
        if len(self.own) > amount2:
            for p in self.own:
                moves.append({'player' : self.game.state.player, 'action' : 'c', 'from' : p})
        
        
            return moves 
        
        # guy = random.randint(0, 9)
        amount = 1
        # print guy
        
        
        for p in self.own:
            
            
            for machines in xrange(self.game.state.num_hosts):
                
                for exploits in self.players_expl:
                    
                    guy2 = random.randint(0, self.game.state.num_hosts)
                        
                        
                    if self.patches[machines][int(exploits[1:])] == False and machines not in self.own:
                        # print 'False'
                        if amount > len(self.own):
                            break
                        amount += 1
                        print exploits
                        
                            
                        moves.append({'player':self.game.state.player,
                              'action':'h', 'from':p,
                              'to': machines,
                              'exploit': exploits})
                    elif self.patches[machines][int(exploits[1:])] == True and machines not in self.own:
                        # print 'True'
                        if amount > len(self.own):
                            break
                        guy3 = random.randint(0, self.game.state.num_hosts - 1)
                        
                        while guy3 in self.own or guy3 in alreadyreconed or self.patches[guy3][int(exploits[1:])] == True:  
                            
                            guy3 = random.randint(0, self.game.state.num_hosts - 1)
                        
                        
                        
                        moves.append({'player' : self.game.state.player, 'action' : 'r', 'from' : p, 'to' : guy3})
                        alreadyreconed.append(guy3)
               
        
        if len(moves) < len(self.own):
            for p in xrange(len(self.own)):
                
                guy3 = random.randint(0, self.game.state.num_hosts - 1)
                
                    
                while guy3 in self.own or alreadyreconed or self.patches[guy3][int(exploits[1:])] == True:
                    
                    guy3 = random.randint(0, self.game.state.num_hosts - 1)
                
                
                moves.append({'player' : self.game.state.player, 'action' : 'r', 'from' : p, 'to' : guy3})
                alreadyreconed.append(guy3)
        print moves
        
        return moves    
        #Need to fix list:
        """
            1. Doesn't recon same machine twice over period of game 
            2. Knowns what OS it is hacking with 
            3. Hacks when it needs to
            
            
            
            
            
            
            """
            
            
        