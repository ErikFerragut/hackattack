Design doc
----------
This document describes some of the details of how the program works.

Classes
-------
*Game* - manages the rounds and discovers who wins; also save and reload games
*Player* - handles requesting moves from strategy and executing the moves, also
returns future statuses with their probabilities
*Strategy* - given a player's knowledge at a given time, decide on what moves to
make.  This can be a UI that requests moves or it can be an AI that determines its
own moves

Structure of a move
-------------------
The moves a player makes are a list of dictionaries. Each dictionary describes a move. Keys and values are described below; not all are necessary for each move.

*action* - the type of move being carried out, length 1 string chosen from 'dbscrhp'
*from* - int indicating the machine whose turn is used to make the move
*to* - int indicating the machine acted upon
*exploit* - the exploit used in a hack or in a patch, string of OS letter + exploit number
*user* - in a DDOS attack, the int number of the player being attacked

If one machine is doing a ddos, then no other action should be carried out.
The moves are executed in the order in which they are listed, which may be tactically
important.  An empty list of moves is also valid and effects a "pass".


Knowledge system planning
-------------------------
There are different possible ways to do this, which we consider and then adopt one.

*version 1* - keep track of all possible combinations of what other players may own in terms of assets and exploits and what they know and update probabilities

*version 2* - assume independence in pretty much all unknowns, so each player has a probability of having an account on machine i + chance of having each exploit + number of accounts assuming they have at least one, but prob account on i and j is just the product of those individually

*version 3* - expected # of accounts on machine i, expected total number of accts, prob of knowing os on machine i, os of machine i, prob of having exploit 0-19 on each os, prob machine is patched against exploits 0-19

*version 4* - track what player believes other players know

It seems 1 is intractable, 4 is harder than strictly necessary. The question is whether to go with 2 or 3. V2 has the problem that if you need to know how many accounts a player has on a machine, then you will be at a loss. But what really happens when you do need to know that? Hopefully you never need to loop over all account number possibilities. Instead maybe you just need to know if you have more accounts or not. Version 2 seems a bit more complete.

Also, should they keep both own and knowledge of own? Does that fulfill a role?


Knowledge system
----------------
In detail, this means the first implementation of the knowledge system will include the following fields in a dictionary:
    1. for each machine
        1. OS is each possibility (pdf)
        2. Patched against explit i
    2. for each player p
        1. player p has i accounts on machine j (0,1,2,3,4,..., up to?)
        2. player p has exploits (os, number)

For M machines, O OSs, N max patches, P players, A max accounts need:
MO + MP + PMA + PO(N+1)
For a standard 4 player game, we have M=20, O=4, N=20ish, P=4, A=19
20x4 + 20x4 + 4x20x19 + 4x4x20 = 2000 numbers for each state!
If you limit the number of accounts on a machine to 4 (A=4), you get
20x4 + 20x4 + 4x20x4 + 4x4x20 = 800 numbers for each state
which is better, but still high by a factor of about 2 to 10.
Reduce maximum number ofpatches to consider down to 10 (N=10)
20x4 + 20x4 + 4x20x4 + 4x4x10 = 640
If number of machines is reduced from 5P to 3P, we get 12 machines:
12x4 + 12x4 + 4x12x4 + 4x4x10 = 448

The fields are:
{
 'OS':array(#machines, #OSs),   # each row is a pdf of which OS is used
 'patches':array(#machines, max-patch-number)  # is machine i patched against j
 'owns':array(#players, #machines, #accounts)  # pdf on last axis
 'exploits':array(#players, #OSs, max-patch-number)
}

The problem is when you learn that someone has exploit i (if you can)
then the number of exploits that player has just went up by one.  This
is different from knowing they have 3 and then finding out which they
are.

In summary, we have:
'''
1. know['OS'][host, OS] = prob it's that os
2. know['patches'][host, patch_num] = prob machine is patched against
that
3. know['owns'][player, host, k] = prob player has k accounts on host
4. know['exploits'][player, OS, patch_num] = prob player has exploit
OS-patch_num
'''

Where Stuff Is Stored
---------------------

*Game*
1. players - list of player objects
2. players_in - indices of which players are still playing
3. board_os - list of length num_hosts of OS letters for machines
4. board_patches - list of lists of patches, but only the numbers (ints)
5. whose_turn - index of players whose turn it is
6. round - counts number of times each player has had a turn (~#turns/#players)
7. num_players
8. num_hosts

*Player*
1. name - a given name for the player
2. strategy - the Strategy object that makes decisions on moves to make
3. own - dictionary with own[machine] = # accounts (0 accounts => no key)
4. exploits - set of exploits, such as L3, W1, etc.
5. know - the knowledge structure described elsewhere

*Strategy*
1. player - the player the strategy belongs to


The moves do* (* = recon, patch, etc.) have corresponding consider*
methods that produce a list of knowledge dictionaries and a
corresponding list of probabilities.


Detection Events 
----------------
The detect method in the player object receives events, such as:
 ('r', self.id, move['from'], move['to'])
 ('b', self.id, move['from'])                # say num accounts?
 ('s', self.id, move['from']) 


Open Issues in (My Understanding of) Game Theory
------------------------------------------------
To use an evaluation function, the strategy must look ahead and
anticipate what the board will look like after they go and their
opponent goes and so on. If handling each possible scenario as a
separate case, then there is one case for each single
possibility. This means that after, say, a recon of an unknown
machine, there are four scenarios for each possible OS, and then if
you have k exploits for that OS, there are 2^k cases for each of those
being vulnerable or not. So a basic action can easily fan out to 10 or
20 or more scenarios.

1. You have some knowledge
2. You consider a wide range (R1) of possible actions
3. For each action, you get a list of (N1) new knowledges
4. Each opponent then considers a wide range (R2) of possible actions
5. In each case, it further spans out the knowledges (N2)

A simple 2-ply search, you get R1 N1 R2 N2 things to track. If each
R1N1 is about 2, you could go O(20-30) ply. If each is ~1000, then you
can go O(2-3) ply.


Known Bugs
----------

Exploits and patches are created without a limit, but the knowledge
system imposes a limit on them. Perhaps this can be avoided if the
knowledge system ends up with just two states: original uncertainty
and total certainty. To know, we need to step through each action and
see. Otherwise, change the random exploit function to be capped at the
same limit used by knowledge.


Should probably start out by knowing the OS of your first machine and,
in general, you should learn the OS of any machine you get access to.
