from header import *
from Strategy import *

# next: k-ply evaluation strategies
class EvaluationStrategy(Strategy):
    def __init__(self, player, strategy_args):
        '''Create a strategy that uses a k-ply search on an evaluation function
        where both k and the function are given.  The function takes both
        the knowledge object and the player id as inputs.'''
        Strategy.__init__(self, player, strategy_args)
        self.evaluation_function = strategy_args['f']
        self.num_ply = strategy_args['k']
        
    def set_evaluation_function(self, evaluation_function):
        '''Set the evaluation function to be something that scores 'know'
        structures with larger values being more desirable.'''
        self.evaluation_function = evaluation_function

    def set_num_ply(self, k):
        self.num_ply = k

    def tree_your_move(self, know, k, mover):
        '''
        the tree_functions do the various steps of the k-ply search:
           start with tree_your_move with a given knowledge, probability, level to go
           it constructs a tree (dictionary) of knowledges
           if k = 1, it scores each one
           otherwise, it calls tree_fuzz (with k-1) to get scores and moves
           compute the average score for each set of outcomes
           returns the max choice (move) and its score

           in tree_fuzz, it computes what happens after opponent makes a random move
           if k = 1, it then scores that result
           otherwise, it calls tree_your_move (with k-1) on it to get score
           returns the score

           if k is negative then that's how many moves ahead it looks, but without
           in-between fuzzes
        '''
        pid = self.player.id
        candidates = self.candidate_moves(self.player.know, self.player.id)[mover]

        # from IPython import embed
        # embed()
        
        # candidate move --> pair (list of knows, list of probs)
        knows_and_probs = { i:self.player.consider_moves([candidates[i]], deepcopy(know))
                            for i in xrange(len(candidates)) }
        # compute score for each outcome directly or via recursion
        if k == 1 or k == -1:
            scores = { i: np.array([self.evaluation_function(kk,pid)
                                    for kk in kp[0]])
                       for i,kp in knows_and_probs.iteritems() }
        elif k < -1:
            scores = { i: np.array([self.tree_your_move(kk, k+1, mover)['maxscore']
                                    for kk in kp[0]])
                       for i,kp in knows_and_probs.iteritems() }
        else:            
            scores = { i: np.array([self.tree_fuzz(kk, k-1, mover)
                                    for kk in kp[0]])
                       for i,kp in knows_and_probs.iteritems() }
        # average sores according to their probabilities
        scores = { i: np.sum(sc * np.array(knows_and_probs[i][1]))
                   for i,sc in scores.iteritems() }
        # find the best move and return that and its score
        m = max(scores.values())
        best = [ c for c in scores if scores[c] == m ]
        best_move = candidates[random.choice(best)]
        return {'bestmove':best_move, 'maxscore':m,
                'allmoves':candidates, 'allscores':scores}
    
    def tree_fuzz(self, know, k, mover):
        '''Using this implies a model where the opponent moves randomly.
        To keep things moving, use only 1% of the possible moves to check, and
        then add the existing 'know' to get it to add to full probability.'''
        # breaks on > 2 players -- and only considers small pct. of moves
        new_know = deepcopy(self.know_fuzz(1 - self.player.id, know, sample=0.01))
        if k == 1:
            score = self.evaluation_function(new_know, self.player.id)
        else:
            result = self.tree_your_move(new_know, k-1, mover)
            score = result['maxscore']

        return score
    

    def get_moves(self):
        '''
        -- to avoid combinatorial explosion, pick moves one at a time:        
        choose movers in a random order
        create a k-deep tree for first mover from current know
        roll it up according to min,max,avg and select best move
          state0 --your-move-->  1ply  --outcomes-->  2ply  --fuzz-->   3ply  --your-next-move-->  4ply  --outcomes-> 5ply
          score5 <----max------ score4 <--average--- score3 <--equal-- score2 <------max------- score1 <--average-- score0
                                
        assume that move (i.e., consider it)
        from there, create k-deep tree for second mover
        continue to make trees and roll them up until all moves are picked
        '''

        # choose movers in random order
        movers = [m for m in self.player.own.keys()]
        np.random.shuffle(movers)
    
        # recursively construct and score tree to get best move
        moves = []
        knows = [deepcopy(self.player.know)]
        probs = [ 1.0 ]
        for mover in movers:
            # best_move, score = self.tree_your_move(know, self.num_ply, mover)
            # for each knowledge, get scores for all moves
            results = [ self.tree_your_move(kn, self.num_ply, mover)
                        for kn in knows ]
            
            # compute best expected score and choose that
            candidates = results[0]['allmoves']
            scores = [ sum([ pr * r['allscores'][r['allmoves'].index(c)]
                         for r, pr in zip(results, probs) ])
                       for c in candidates ]
            m = max(scores)
            best = [ candidates[i] for i in xrange(len(candidates))
                     if scores[i] == m ]
            best_move = random.choice(best)
            print "best move is {} with score {} and {} ties".format(
                best_move, m, len(best))
            moves.append(best_move)

            # now consider the best move and branch on it
            new_knows = []
            new_probs = []
            for kn, pr in zip(knows, probs):
                branch_knows, branch_probs = self.player.consider_moves([best_move], kn)
                new_knows.extend(branch_knows)
                new_probs.extend( [ bp * pr for bp in branch_probs ] )

            knows, probs = new_knows, new_probs
            print "Explored {} knowledge states after {} moves".format(len(knows),
                                                                       len(moves))
                        
        print "moves =", moves
        return moves

