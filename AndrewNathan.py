from hackattack_player import *
from hackattack_ai import AI
import random

class AndrewNathan(AI):
    def get_moves(self):
        moves = []
        for p in self.own:
            
            if self.own[p] > self.game.num_hosts - 1:
                moves.append({'player' : self.id, 'from' : p , 'action' : 'c'})
                return moves
            
            for exploits in self.expl:
                if self.patches[p][int(exploits[1:])] == False and exploits[0] == self.oss[p][0]:
                    moves.append({'player' : self.id , 'action' : 'p' ,
                                  'from' : p , 'exploit' : exploits})
                    return moves
            moves.append({'player' : self.id , 'action' : 'b' , 'from' : p})
            return moves   
                
                
    
    
    
    
    
