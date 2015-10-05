from hackattack_player import *
from hackattack_ai import AI
import random


class Andrews(AI):
    def init_ai(self):
        self.alreadyreconed = []
        self.DDOSED = []
        self.itemlistA = [ "L", "S", "M", "W"]
        
    def get_moves(self):
        import random
        moves = []
        self.whatmoved = []
        
        if self.game.num_players > 1:   
            for s in xrange(self.game.num_players):
                if s in self.traced and s not in self.DDOSED:
                    moves.append({'action' : 'd' , 'user' : s ,
                                  'player' : self.id})
                    self.DDOSED.append(s)
                    return moves
        
        amount2 = self.game.num_hosts / 2
        if len(self.own) > amount2: 
            for p in self.own:
                moves.append({'player' : self.id, 'action' : 'c', 'from' : p})
            return moves 
        
        for p in self.own:
            if self.own[p] > self.game.num_hosts - 1:
                moves.append({'player' : self.id, 'action' : 'c', 'from' : p})
                self.whatmoved.append(p)
                
        
        for p in self.own:
            if p not in self.whatmoved:    
                for machines in xrange(self.game.num_hosts - 1):
                    for exploits in self.expl:  
                        if p not in self.whatmoved: 
                            if self.patches[machines][int(exploits[1:])] == False and machines not in self.own and exploits[0] == self.oss[machines][0]:
                                
                                moves.append({'player':self.id,
                                      'action':'h', 'from':p,
                                      'to': machines,
                                      'exploit': exploits})
                                self.whatmoved.append(p)
        if len(self.whatmoved) < len(self.own):
            for p in self.own:
                 
                    for i in xrange(self.game.num_hosts - 1):
                        if p not in self.whatmoved:
                            if i not in self.own and i not in self.alreadyreconed:
                                moves.append({'player' : self.id, 'action' : 'r', 'from' : p, 'to' : i})
                                self.whatmoved.append(p)
                                self.alreadyreconed.append(i)
                                if len(moves) >= len(self.own):
                                    return moves
            if len(moves) < len(self.own):
                for p in self.own:
                    if p not in self.whatmoved: 
                        moves.append({'player' : self.id, 'action' : 'b', 'from' : p})
                        self.whatmoved.append(p)
        print moves
        return moves 
