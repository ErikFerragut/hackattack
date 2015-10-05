# summary
hackattack is a game developed for the purpose of cyber conflict modeling

V 3.0 - evaluation functions and k-ply searching
V 2.0 - included knowledge system, ddos, etc.
V 1.0 - simple starting version


## to do items

### Tweak knowledge handling
1. ~~Correctly compute what is learned when a hack fails (lines
759--762)~~
2. ~~After each move is selected, branch on the results before selecting
the next move rather than averaging, which will prevent, for example,
all owned machines doing the same hack (lines 1241--1248)~~

### Update git repo
1. Split file into multiple files
2. Merge refactor branch back into master branch
3. Tag master branch with v 3.0

### Game playability (PlayerStrategy)
1. Make the PlayerStrategy summarize the know clearly and succinctly
2. Recreate the news system
3. Create better UIs (graphical and not)
4. Reinstate the load and save game ability
5. Create networking capability
6. Reinstate ddos to make non-simulation games more fun

### Artificial intelligence
1. Revisit the game theory book for easy ways to speed-up algorithms
2. Create more evaluation functions in some reasonable way
3. Make starting situations comparable (same number of exploits of
   each level?)
4. Test evals against each other and document winners

### Write paper
1. Introduction (problem, purpose, thesis, main contributions) [0.5p]
2. Background (related papers, how we're different) [0.5p]
3. Method (summary of creating a game, eval functions, testing) [0.5p]
4. Description of the game [1.5p]
5. Description of eval functions [1.5p]
6. Results (how many times each one won and other observations) [1p]
7. Discussion (how results support thesis) [1p]
8. Conclusion (restate main points) [0.5p]
9. References [0.5p]

### Develop test code
1. Allow a seed to be fixed so that the game is deterministic
2. Write unit tests

## known bugs

# Plan going forward (email of 25 July)
Target: my group's annual conference

Paper plan:
* Cyber conflicts can be viewed as games (in the math sense),
* Strategies for cyber conflict can be reduced to optimizing evaluation functions,
* The best evaluation functions we can find depend on probabilities (explain...)
* The best strategies would be hard to do "manually" (with human intervention)
* The results indicate parameters we need to estimate to make this a realistic tool.

Immediate next steps:
1. ~~Refactor the hackattack code to allow evaluation-function based
   analysis.~~ (orig. Aug 28, done Oct 3)
2. Create evaluation functions and test them (orig. Sep 13, now Oct 5-8)
3. Simulate the functions in various combinations with different
   levels of look-ahead. Vary detection probabilities and other
   parameters to see how the evaluation functions' outcomes change.
   This is probably the hardest part.  (orig. Oct 3, now Oct 6-8)
4. Write up the results as an 8-page full paper (deadline is October
   16, but is usually extended by a week or two).

Level of Effort: 2 or 3 times per month (2-4 hours each time) to get
this done, starting in September after I've completed item 1.

