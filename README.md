# hackattack
hackattack is a game developed for the purpose of cyber conflict modeling

## to do items

### Finish modularizing the code
1. ~~move variables having to do with players to the player class (see GameState init)~~
2. ~~change do_ functions to use player.say() instead of print~~
3. ~~move non-output parts from updateoutput to mainloop~~
4. Develop test code: maybe start with a random seed and feed in fixed commands and check output?
5. Make it so it works more uniformly for one screen and many
6. Allow for player types (AI?) or other parameters (IP?) to be specified up front

### Game mechanics
1. ~~Announce DDoS as news~~
2. ~~Don't learn OS on failed hack attempts~~
3. ~~Create a deep recon move to detect accounts on your machine~~
4. ~~From time to time, most common exploit gets patched~~
5. ~~Make it so there are arbitrarily many exploits with different probabilities~~
6. ~~Tinker with probabilities, such as more likely to be detected on
failed hack attempts~~
7. ~~Each player checks for detection separately~~

### Knowledge system
1. ~~Store events by machine~~
2. ~~Store all moves and move results~~
3. ~~Formalize the say method and store what was said~~
4. ~~Store known info (e.g., OS, patches, accounts) from events~~
5. Make "detected" and "news" use say function

### New user interface
1. Design the information display to show all knowledge (update_output)
2. Create a new way to grab moves (parse_moves)
3. Have a way to show move results (say)
4. Test UI separately

### Load and save game
1. ~~Develop serialize and deserialize functions for GameState and
Player to store knowledge in knowledge system~~
2. Automatically save game after each player
3. ~~Allow some way to load a saved game~~

### Artificial intelligence
1. Create a simple/random AI by making a variation of Player
2. Create an evaluation function for a player's knowledge
3. Implement an probabilistic alpha-beta pruning k-ply search

### Networking
1. Create a Player type that sends info and gets moves from a client
2. Create the player client
3. Incorporate new UI into player client
4. Players can choose custom names




## known bugs

hackattack.player line 123 errors the program before it can give the error message
## doesn't clarify hack success in detection / news

1. ~~hackattack.player line 123 errors the program before it can give the error message~~

2. ~~Given enough time, one could have multiples or duplicates of any exploit. the while block on line 168 doesn't work 
because ne isn't appended yet
tl;dr : you can get 2 of the same exploit~~

3. ~~hackattack.py line 68 in do_scan uses old form of players own~~
4. ~~skips turn if OS of patch is wrong but you own it~~ 
5. ~~if x in hackattack_util is greater than .75, the program crashes~~
6. Knowledge system doesnt show home pc in known operating systems
7. things displayed in news are not incorporated into the knowledge system
8. ~~ on line 203, may bug out.... unknown debug item printed every turn: this should be removed e.g. {0,[],[]}~~

## Recently fixed bugs

### ~~when enter is repeatedly pressed, it causes this error~~


