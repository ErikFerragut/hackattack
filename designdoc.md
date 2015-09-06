Design doc
----------
This document describes some of the details of how the program works.

Classes
-------
*Game* - manages the rounds and discovers who wins; also save and reload games
*Player* - handles requesting moves from strategy and executing the moves, also returns future statuses with their probabilities
*Strategy* - given a player's knowledge at a given time, decide on what moves to make.  This can be a UI that requests moves or it can be an AI that determines its own moves

Structure of a move
-------------------
The moves a player makes are a list of dictionaries. Each dictionary describes a move. Keys and values are described below; not all are necessary for each move.

*action* - the type of move being carried out, length 1 string chosen from 'dbscrhp'
*from* - int indicating the machine whose turn is used to make the move
*to* - int indicating the machine acted upon
*exploit* - the exploit used in a hack or in a patch, string of OS letter + exploit number
*user* - in a DDOS attack, the int number of the player being attacked

If one machine is doing a ddos, then no other action should be carried out.
The moves are executed in the order in which they are listed, which may be tactically important.
An empty list of moves is also valid and effects a "pass".


Knowledge system
----------------
There are different possible ways to do this, which we consider and then adopt one.

*version 1* - keep track of all possible combinations of what other players may own in terms of assets and exploits and what they know and update probabilities

*version 2* - assume independence in pretty much all unknowns, so each player has a probability of having an account on machine i + chance of having each exploit + number of accounts assuming they have at least one, but prob account on i and j is just the product of those individually

*version 3* - expected # of accounts on machine i, expected total number of accts, prob of knowing os on machine i, os of machine i, prob of having exploit 0-19 on each os, prob machine is patched against exploits 0-19

*version 4* - track what player believes other players know

It seems 1 is intractable, 4 is harder than strictly necessary. The question is whether to go with 2 or 3. V2 has the problem that if you need to know how many accounts a player has on a machine, then you will be at a loss. But what really happens when you do need to know that? Hopefully you never need to loop over all account number possibilities. Instead maybe you just need to know if you have more accounts or not. Version 2 seems a bit more complete.

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

The problem is when you learn that someone has exploit i (if you can) then the number of exploits that player has just went up by one.  This is different from knowing they have 3 and then finding out which they are.

