
import random
import time
num_players = 5

exploits_per_os = 5
start_with_exploits = 4
vuln_prob = 0.8

detection_prob = { 'r':0.05, 'h':0.15, 'b':0.10, 'p':0.25 }

OSs = ['Linux', 'Windows', 'Mac', 'Solaris']
all_exploits = [ (o,i) for o in OSs for i in xrange(exploits_per_os) ]
num_hosts = 5*num_players

a = range(num_hosts)
random.shuffle(a)

# (os, [vulnerabilities])
board_os = [ random.choice(OSs) for i in xrange(num_hosts) ]
board_vuln = [ [ i for i in range(exploits_per_os) if random.random() < vuln_prob ]
               for h in xrange(num_hosts) ]

players_start = [ aa for aa in a[:num_players] ]
players_own = [ {s:1} for s in players_start ]
players_expl = []
for i in xrange(num_players):
    random.shuffle(all_exploits)
    players_expl.append( all_exploits[:start_with_exploits] )
players_traced = [ set([]) for i in xrange(num_players) ]
news = { p:[] for p in xrange(num_players) }

# what exploits you have  (others have?) (players_expl)
# which players you've traced (players_traced)
# for each machine you can know:
#   patches and vulnerabilities it has  (P, V, ?)
#   accounts you have on it (players_own)
#   accounts other have on it (or have they never been seen there)
#   OS

players_know = [ {'patched':{}, 'os':{}} for i in xrange(num_players) ]



			  
player = 0

def parse_move(move_str):
    """Return move {'from':from_machine, 'to':to_machine, 'player':player,
    'exploit':exploit, 'user':target_user, 'action':action} based on an input
    of the form 'machine action parameters' and for player (global variable)"""
    words = move_str.lower().split()

    if words[0].lower() == 'd':        
        if len(words) != 2:
            print "Follow format: (D)DoS <user>"
            return
        try:
            user = int(words[1])
        except:
            print "Must specify a user by number"
            return
        if user not in players_traced[player]:
            print "You can only DDoS a player after you have traced them"
            return
        return {'action':'d', 'user':user}
    
    if len(words) < 2:
        print "Follow format: <acting-machine> <action> ... --or-- (D)DoS <user>"
        return

    try:
        move = { 'from': int(words[0]), 'action': words[1][0], 'player':player }
    except:
        print "Must indicate source of move first (as int) and then action (by letter)"
        return
    
    if move['action'] == 'r':
        if len(words) != 3:
            print "Follow format: <acting-machine> (R)econ <machine>"
            return
        try:
            mac2 = int(words[2])
        except:
            print "Target machine must be an integer"
            return
        if mac2 not in xrange(num_hosts):
            print "Invalid target"
            return
        move['to'] = mac2
        return move
    elif move['action'] == 'c':
        return move
    elif move['action'] == 'h':
        if len(words) != 4:
            print "Follow format: <acting-machine> (H)ack <machine> <exploit>"
            return
        try:
            mac2 = int(words[2])
        except:
            print "Target machine must be an integer"
            return
        if mac2 not in xrange(num_hosts):
            print "Invalid target"
            return
        try:
            # print "debug:", words[2], words[2][0], words[2][1:]
            # print int(words[2][1:])
            if not any([ e[0][0] == words[3][0:1].upper() and e[1] == int(words[3][1:])
                    for e in players_expl[player] ]):
                print "Not a valid exploit"
                return
        except:
            print "Third word must be letter followed by number (no space)"
            return
        move['to'] = mac2
        move['exploit'] = words[3].upper()
        return move
    elif move['action'] == 'b':
        return move
    elif move['action'] == 'p':
        if len(words) != 2:
            print "Follow format: <acting-machine> (P)atch <exploit>"
            return
        try:
            if not any([ e[0][0] == words[1][0].upper() and e[1] == int(words[1][1:])
                    for e in players_expl[player] ]):
                print "Must apply a patch for an exploit you have"
                return
        except:
            print "Third word must be a letter followed by a number (no space)"
            return
        move['exploit'] = words[1].upper()
        return move
    else:
        print "Invalid action"
        return

def detected(host, message):
    for p in xrange(num_players): 
        if host in players_own[p]:
            news[p].append(message) 
            
def working_attacks(player, host):
    '''return a list of the short codes for attacks player has that work on machine'''
    return [ e[0][0] + str(e[1]) for e in players_expl[player]
             if board_os[host] == e[0] and e[1] in board_vuln[host] ]

def do_recon(move):
    player = move['player']
    print "Machine {} is running the {} OS".format(move['to'], board_os[move['to']])
    openings = working_attacks(player, move['to'])
    if len(openings) == 0:
        print "You have no exploits for that machine."
    else:
        print "You can hack it with", ", ".join(openings)
    # check for detection
    if random.random() < detection_prob['r']:
        detected(move['to'], "{} probed machine {} from machine {}".format(players_names[move['player']], move['to'], move['from']))

def do_clean(move):
    for p in xrange(num_players):
        if p != player:
            if move['from'] in players_own[p] and players_own[p][move['from']] > 0:
                num_removed = min(players_own[p][move['from']], players_own[move['player']][move['from']])
                players_own[p][move['from']] -= num_removed
                if players_own[p][move['from']] == 0:
                    players_own[p].pop(move['from'])
                print "You removed {} of {}'s accounts".format(num_removed, players_names[p])
                news[p].append("{} removed {} of your accounts from machine {}".format(
                    players_names[move['player']], num_removed, move['from']))
                # check for trace
                if not p in players_traced[move['player']]:
                    if min([random.random() for i in xrange(num_removed)]) < 1./6:
                        players_traced[move['player']].add(p)
                        print "You traced {}!".format(players_names[p])
                        
    print "Clean completed on machine {}".format(move['from'])

def do_hack(move):
    player = move['player']
    worked = move['exploit'] in working_attacks(player, move['to'])
    # detected? -- do it first so you don't learn if you were detected
    if random.random() < detection_prob['h']:
        detected(move['to'], "{} {}successfully hacked machine {} from {}".format(
          players_names[player], "" if worked else "un", move['to'], move['from']))

    if worked:
        print "Hack succeeded"
        # add access
        if move['to'] not in players_own[player]:
            players_own[player][move['to']] = 1
        else:
            players_own[player][move['to']] += 1
    else:
        print "Hack failed"
        print "OS was {}".format(board_os[move['to']])

def do_backdoor(move):
    player = move['player']
    players_own[player][move['from']] += 1
    if random.random() < detection_prob['b']:
        detected(move['from'], "{} added a backdoor to machine {}".format(players_names[player],
                                                                          move['from']))
    print "One backdoor added to machine {}; you now have {}".format(move['from'],
                                                                  players_own[player][move['from']])
    
def do_patch(move):
    if move['exploit'][0].upper() == board_os[move['from']][0]:
        patch_id = int(move['exploit'][1:])
        if patch_id in board_vuln[move['from']]:
            board_vuln[move['from']].remove(patch_id)
            print "Vulnerability patched"
        else:
            print "Vulnerability was already patched"
    else:
        print "Failed patch due to OS mismatch of {} on {}".format(move['exploit'],
                                                                   board_os[move['from']])

    if random.random() < detection_prob['p']:
        detected(move['from'], "{} patched machine {}".format(players_names[move['player']],
                                                              move['from']))

def do_ddos(move):
    # do you have the trace you need
    player = move['player']
    if move['user'] in players_traced[player]:
        you_str = len(players_own[player])
        them_str = len(players_own[move['user']])
        if you_str > them_str:
            print "YOU WON THE DDOS -- {} IS ELIMINATED".format(players_names[move['user']].upper())
            players_own[move['user']] = {}
            news[move['user']].append("YOU WERE DDOSED BY {}".format(players_names[player].upper()))
        elif you_str < them_str:
            print "YOU LOST THE DDOS -- YOU ARE ELIMINATED"
            players_own[player] = {}
            news[move['user']].append("{} tried to DDoS you but lost and was eliminated".format(players_names[player]))
        else:
            print "DDOS was a tie"
            news[move['user']].append("{} tried to DDoS you but it was tie".format(players_names[player]))
    else:
        print "You need a trace before you can ddos (this output signifies a logic error!)"
        
                                 