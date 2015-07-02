# hackattack
cyber conflict modeling


## bugs

### backdoor a machine you don't own
Move results:
You did move {'action': 'b', 'player': 3, 'from': 13}
Traceback (most recent call last):
  File "hackattack.py", line 402, in <module>
    g.mainloop()
  File "hackattack.py", line 388, in mainloop
    self.move_funcs[move['action']](move)
  File "hackattack.py", line 260, in do_backdoor
    self.state.players_own[player][move['from']] += 1
KeyError: 13
