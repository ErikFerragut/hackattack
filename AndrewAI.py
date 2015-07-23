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








class Andrews(AI):
    def __init__(self, game, name, start):
        super(Andrews, self).__init__(game, name, start)
        self.alreadyreconed = []
        self.DDOSED = []
        self.itemlistA = [ "L", "S", "M", "W"]
    def get_moves(self):
        import random
        moves = []
        if self.game.num_players > 1:   
            for s in xrange(self.game.num_players):
                if s in self.game.state.players_traced[self.game.state.player] and s not in self.DDOSED:
                    moves.append({'action' : 'd' , 'user' : s , 'player' : self.game.state.player})
                    self.DDOSED.append(s)
                    return moves
        self.whatmoved = []
        amount2 = self.game.state.num_hosts / 2
        if len(self.own) > amount2: 
            for p in self.own:
                moves.append({'player' : self.game.state.player, 'action' : 'c', 'from' : p})
            return moves 
        amount = 1
        for p in self.own:
            if self.own[0] > self.game.state.num_hosts - 1:
                moves.append({'player' : self.game.state.player, 'action' : 'c', 'from' : p})
                self.whatmoved.append(p)
                
        
        for p in self.own:
            if p not in self.whatmoved:    
                for machines in xrange(self.game.state.num_hosts - 1):
                    for exploits in self.players_expl:  
                        if self.patches[machines][int(exploits[1:])] == False and machines not in self.own and exploits[0] == self.oss[machines][0]:
                            if amount > len(self.own):
                                break
                            amount += 1 
                            moves.append({'player':self.game.state.player,
                                  'action':'h', 'from':p,
                                  'to': machines,
                                  'exploit': exploits})
                            self.whatmoved.append(p)
        if len(moves) < len(self.own):
            for p in xrange(len(self.own) - len(moves)):
                if p not in self.whatmoved:    
                    for i in xrange(self.game.state.num_hosts - 1):
                        if i not in self.own and i not in self.alreadyreconed:
                            moves.append({'player' : self.game.state.player, 'action' : 'r', 'from' : p, 'to' : i})
                            self.whatmoved.append(p)
                            self.alreadyreconed.append(i)
                            if len(moves) >= len(self.own):
                                return moves
            if len(moves) < len(self.own):
                for p in self.own:
                    if p not in self.whatmoved: 
                        moves.append({'player' : self.game.state.player, 'action' : 'b', 'from' : p})
                        self.whatmoved.append(p)
        return moves 