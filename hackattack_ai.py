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

        
class BackDoor(AI):

    def get_moves(self):
        moves = []
        for p in self.own:
            moves.append({'player':self.game.state.player,
                            'action':'b', 'from':p})
        return moves
        
class JacobAI(AI):
    def __init__(self, game, name, start):
        super(JacobAI, self).__init__(game, name, start)
        self.random_host = random.randint(0,self.game.state.num_hosts-1)
        self.machines = []
        self.counter = 0
        
    def get_moves(self):
        moves = []
        for p in self.own:
            if self.counter == 0 and self.random_host not in self.machines:
                moves.append({'player':self.game.state.player,
                            'action':'r', 'from':p, 'to':self.random_host})
                self.machines.append(self.random_host)
            elif self.counter == 1:
                #if not patched hack
                '''for i in self.players_expl:
                    if self.patches[self.random_host][i] == False:
                        moves.append({'player':self.game.state.player, 
                            'action':'h', 'from':p, 'to':self.random_host})'''
                #if self.patches[self.random_host][j for j in self.players_expl]==True:
                exploits = [ j for j in self.players_expl if self.patches[self.random_host][int(j[1:])]==False]
                print exploits
                if len(exploits) > 0:
                    moves.append({'player':self.game.state.player, 'action':'h', 
                    'from':p, 'to':self.random_host, 'exploit':exploits[0]}) 
                elif self.random_host not in self.machines:
                    moves.append({'player':self.game.state.player,
                            'action':'r', 'from':p, 'to':self.random_host})
                    self.machines.append(self.random_host)
                else:
                    moves.append({'player':self.game.state.player,
                            'action':'r', 'from':p, 'to':self.random_host})
                    self.machines.append(self.random_host)
                self.random_host = random.randint(0,self.game.state.num_hosts-1)
                print moves
            elif self.counter == 2 or self.counter == 4:
                if self.random_host not in self.machines:
                    moves.append({'player':self.game.state.player,
                        'action':'r', 'from':p, 'to':self.random_host})
                elif self.random_host not in self.machines:
                    moves.append({'player':self.game.state.player,
                        'action':'r', 'from':p, 'to':self.random_host})
                else:
                    moves.append({'player':self.game.state.player,
                        'action':'r', 'from':p, 'to':self.random_host})
                self.machines.append(self.random_host)       
                self.random_host = random.randint(0,self.game.state.num_hosts-1)
            elif self.counter == 3 or self.counter == 5:
                #if self.patches[self.machines[j for j in xrange(len(self.machines))][i for i in self.players_expl]==True:
                #[[moves.append({'player':self.game.state.player, 'action':'h', 'from':p, 'to':self.machine[j]}), del self.machines[j] for j in xrange(len(self.machines))] for (i in self.players_expl) if self.patches[self.machines[j]][i]==False]
                foundmove = False
                tempHackMachine = []
                for j in xrange(len(self.machines)):
                    for i in self.players_expl:
                        if self.patches[self.machines[j]][int(i[1:])]==False and foundmove == False and j not in tempHackMachine:
                            moves.append({'player':self.game.state.player, 'action':'h', 'from':p, 'to':self.machines[j], 'exploit':i})
                            #del self.machines[j] this messes up the for loop
                            tempHackMachine.append(j)
                            foundmove = True
                if not foundmove:
                    self.random_host = random.randint(0,self.game.state.num_hosts-1)
                    moves.append({'player':self.game.state.player,
                        'action':'r', 'from':p, 'to':self.random_host})
                    self.machines.append(self.random_host)  
                    self.random_host = random.randint(0,self.game.state.num_hosts-1)

                #del self.machines[j]
            elif self.counter == 6 or self.counter == 8:
                moves.append({'player':self.game.state.player,
                            'action':'c', 'from':p})
            elif self.counter == 7:
                moves.append({'player':self.game.state.player,
                            'action':'b', 'from':p})
            elif self.counter == 9:
                if len(self.game.state.players_traced) > 0:#there is a trace:
                    moves.append({'player':self.game.state.player,
                                'action':'d', 'from':p, 'to':random.choice(self.game.state.players_traced)})
                else:
                    #[moves.append({'player':self.game.state.player, 'action':'h', 'from':p, 'to':self.machine[j]}), del self.machines[j] for j in xrange(len(self.machines)) for i in self.players_expl if self.patches[self.machines[j]][i]==False]
                    foundmove = False
                    tempHackMachine = []
                    for j in xrange(len(self.machines)):
                        for i in self.players_expl:
                            if self.patches[self.machines[j]][int(i[1:])]==False and foundmove == False and j not in tempHackMachine:
                                moves.append({'player':self.game.state.player, 'action':'h', 'from':p, 'to':self.machines[j], 'exploit':i})
                                #del self.machines[j] this messes up the for loop
                                tempHackMachine.append(j)
                                foundmove = True
            elif self.counter == 10:
                self.counter = 6
                foundmove = False
                tempHackMachine = []
                for j in xrange(len(self.machines)):
                    for i in self.players_expl:
                        if self.patches[self.machines[j]][int(i[1:])]==False and foundmove == False and j not in tempHackMachine:
                            moves.append({'player':self.game.state.player, 'action':'h', 'from':p, 'to':self.machines[j], 'exploit':i})
                            #del self.machines[j] this messes up the for loop
                            tempHackMachine.append(j)
                            foundmove = True
                

        self.counter +=1  
        #self.game.state.news[0].append(moves)

            # decide whether to fortify or expand
            
        return moves
        '''if random.random() < 0.3: # fortify
                moves.append({'player':self.game.state.player,
                              'action':'b', 'from':p})
            else:                     # expand
                moves.append({'player':self.game.state.player,
                              'action':'h', 'from':p,
                              'to':random.randint(0,self.game.state.num_hosts-1),
                              'exploit':random.choice(self.players_expl)})'''

class NathanAI(AI):
    def __init__(self, game, name, start):
        super(NathanAI, self).__init__(game, name, start)

"""class NathanAI(AI):
    def __init__(self, game, name, start):
        super(NathanAI, self).__init__()

        self.counter = 0
        
    def get_moves(self):
        moves = []
        
        for p in self.own:
            
            # decide whether to fortify or expand
            unpatched_exploits = [ e for e in self.players_expl 
                 if e[0] == self.'''oss'''[p] and int(e[1:]) not in self.patches[p] ]
            if len(unpatched_exploits) !> 0: # fortify
                moves.append({'player':self.game.state.player,
                              'action':'b', 'from':p})
            else:                     # expand
                moves.append({'player':self.game.state.player,
                              'action':'p', 'from':p,
                              'to':random.randint(0,self.game.state.num_hosts),
                              'exploit':random.choice(self.players_expl)})
        return moves"""
class EthanAI(AI):
    import random
    def __init__(self, game, name, start):
        super(EthanAI, self).__init__(game, name, start)
        self.easy_hacks = []
        self.turns_since_c = {n:0 for n in self.own} 
    def update_lists():
        self.easy_hacks = [m for m in self.patches if any([l == False for l in self.patches[m]])]
        for i in xrange(self.own):
            if i not in self.turns_since_c:
                self.turns_since_c.append({i:0})
        for h in self.turns_since_c:
            self.turns_since_c[h] += 1
        return
    def func1():
        update_lists()  
        new_num_hosts = num_hosts
        while len(moves) < len(self.own):           
            for i in xrange(self.own):
                if i in self.known_accounts:
                    moves.append({'player':self.game.state.player,'action':'c', 'from':i})
                #if len(easy_hacks) = 0:
                    #use other computer to backdoor by hacking then clean on original computer
                # else clean
            if len(self.easy_hacks) > 0:
                for l in self.easy_hacks:
                    moves.append({'player':self.game.state.player,'action':'h',
                    'from':p,'to':l,'exploit':random.choice(self.players_expl)})
                    #h in players_expl if h[0] = known_OSes[l: ]}) players_expl is a list of tueples 
            else:                
                for h in xrange(known_OSes):
                    new_num_hosts.remove(h)
                moves.append({'player':self.game.state.player,'action':'r', 'from':p,'to':random.choice(new_num_hosts)})
        return moves 

    update_lists()    
    if len(self.own) < 3:
        moves = func1

    if len(self.own) >2 and len(self.own)<13:
        moves = func2
    
    return moves
        
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
            3. Hacks when it needs to """

