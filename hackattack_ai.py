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
        # add it to a list for machines that are involved
        # store inferred information
        
class NathanAI(AI):
    def __init__(self, game, name, start):
        super(NathanAI, self).__init__(game, name, start)
        self.counter = 0
        
    def get_moves(self):
        moves = []
        
        for p in self.own:
            
            # decide if patching is possible
            print self.oss, self.players_expl, self.game.state.board_patches[p], "!!!"
            unpatched_exploits = [ e for e in self.players_expl 
                 if e[0] == self.oss[p][0] and self.patches[p][int(e[1:])] != True ]
            if len(unpatched_exploits) > 0: # fortify
                moves.append({'player':self.game.state.player,'from':p,
                              'action':'p', 'exploit':random.choice(unpatched_exploits)})
           elif self.counter == 0:
                self.counter = 1
                moves.append({'player':self.game.state.player,'from':p, 'action':'p', 'recon': self.own)
           else:                     # expand
                moves.append({'player':self.game.state.player,
                              'action':'b', 'from':p})
                
        return moves

'''
class EthanAI(AI):
    import random
    def __init__(self, game, name, start):
        super(EthanAI, self).__init__()
        easy_hacks = []
        turns_since_c = ()
        recon = moves.append({'player':self.game.state.player,'action':r, 'from':p,'to'random.randint(0,self.game.state.num_hosts)})#should not recon computers in known OSes
    def update_lists():
        easy_hacks.append(computer if you have an exploit for known OS and a player is on it)
        turns_since_c
    def func1():
        when len(moves) < len(self.own)#:           
            if #any in self.known accounts = any in self.own:
                if len(easy_hacks) = 0:
                    use other computer to backdoor by hacking then clean on original computer
                else clean
            elif len(easy_hacks) > 0:
                moves.append({'player':self.game.state.player,
                                  'action':'h', 'from':p,
                                  'to':random.choice(easy_hacks),
                                  'exploit':random expl with OS the same as target})
            else moves.append({'player':self.game.state.player,
                               'action':r, 'from':p,
                               'to'rendom.randint(0,self.game.state.num_hosts)})#should not recon computers in known OSes
        return moves
    def war():
        '''recon target if not already done
        hack target with three computers
        if some remain but you were cleaned hack with 1 - number removed
        if some remain and not cleaned clean then scan if nothing detected
        if all cleaned hack with 7 and follow same procedure, but if still cleaned label target Nathan'''
    def func2():
        when len(moves) < len(self.own) 
            if ?.known accounts = self.own:
                    use other computer to backdoor by hacking then clean on original computer
            elif turns_since_c > random.randint(2,3)
                clean
            elif len(easy_hacks) > 0:
                do them
            elif war possible:
                start war
            else return recon

    update_lists    
    if len(self.own) < 3:
        moves = func1
    if len(self.own) >2 and <13
        moves = func2
                    '''if random.random() < 0.3: # fortify
                    moves.append({'player':self.game.state.player,
                                  'action':'b', 'from':p})
                else:                     # expand
                    moves.append({'player':self.game.state.player,
                                  'action':'h', 'from':p,
                                  'to':random.randint(0,self.game.state.num_hosts),
                                  'exploit':random.choice(self.players_expl)})'''
        
class Andrew(AI):
    def get_moves(self):
        import random
        moves = []
        for p in self.own:
            # decide whether to fortify or expand
            if vuln == []:
                moves.append({'player': self.game.state.player, 'action' : 'r', 'from' : p, 'to' : random.randint(0, self.game.state.num_hosts)}) 
            else:
                moves.append({'player':self.game.state.player,
                              'action':'b', 'from':p})
        return moves

'''
