#testing new_patches
import random
OSs = ['Linux', 'Windows', 'Mac', 'Solaris']
num_hosts = 10
exploits_per_OS = 5
board_OSs = [ random.choice(OSs) for i in xrange(num_hosts) ]
board_vuln = [ [ i for i in range(exploits_per_OS)
                          if random.random() < .8 ]
                       for h in xrange(num_hosts)]
print board_vuln
x = random.choice(OSs)
y = random.randint(0,4)
print x,y
        #if random.random()<=.15:

    for i in xrange(num_hosts):
        if board_OSs[i] == x:
            board_vuln[i].remove(y)
print board_vuln