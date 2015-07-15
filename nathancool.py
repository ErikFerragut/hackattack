#just finished your strategy nathan!!!!!
class Nathan(AI):
    def get_moves(self):
        moves = []
        for p in self.own:
            # decide whether to fortify or expand
            
            moves.append({'player':self.game.state.player,
                          'action':'b', 'from':p})
        return moves