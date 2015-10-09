from header import *

def jacobAttack(know,pid):
    num_computers = know['owns'].shape[1]
    howmanycomputersyouhave = 0
    for computer in xrange(num_computers):
        howmanycomputersyouhave += know['owns'][pid, computer, 1:].sum()
    return howmanycomputersyouhave


def nathaniscool(know, pid):
	nummachines = 0
	for i in xrange(10):
		nummachines += (1.0 - know['owns'][pid, i, 0])
	return nummachines

def maxeval(know, pid):
	x= np.arrange(Max_Accounts)
	your_accounts = know['owns'][pid].dot(x).sum()
	all_accounts = know['owns'].dot(x).sum()
	return your_accounts * 2 - all_accounts

# your_machines = jacobAttack = nathaniscool
# maxeval = net_accounts

### Accounts

def your_accounts(know, pid):
    return know['owns'][pid].dot( np.arange(Max_Accounts) ).sum()

def all_accounts(know, pid):
    return know['owns'].dot( np.arange(Max_Accounts) ).sum()

def net_accounts(know, pid):
    return your_accounts(know,pid) * 2 - all_accounts(know, pid)


### Machines
def your_machines(know, pid):
    '''Return number of machines with accounts, given as expected value'''
    return know['owns'].shape[1] - know['owns'][pid, :, 0].sum()

def all_machines(know, pid):
    return know['owns'].shape[0] * know['owns'].shape[1] - know['owns'][:,:,0].sum()

def net_machines(know, pid):
    return your_machines(know, pid) * 2 - all_machines(know, pid)




### Clean bonus
def clean_machines(know, pid):
    # prob(you have an account) * prob(other players do not)
    have_machines = know['owns'][:,:,0]
    have_machines[pid,:] = know['owns'].shape[1] - have_machines[pid]
    have_machines = np.prod(have_machines, 0)
    # it should now be an array of len #hosts of clean probs
    return have_machines.sum()

def exploitable_by(know, machine, pid):
    # an exploit works if
    #   os matches and you have exploit and exploit is not patched
    # (breaks if #OS == #patches?)
    A = know['OS'][machine,:] * know['exploits'][pid, :, :].T
    B = A.T *      (1.-know['patches'][machine])
    return np.sum( (know['OS'][machine,:] * know['exploits'][pid, :, :].T).T *
                  (1.-know['patches'][machine]))

### Invulnerability bonus
def security(know, pid):
    # what is the probability that player p can exploit machine m
    machines = [a for a in xrange(know['owns'].shape[1])
                if know['owns'][pid, a, 0] < 1.0]
    return np.sum([ exploitable_by(know, m, p) for p in xrange(know['owns'].shape[0])
             if p != pid for m in machines ])

def get_mixture_eval(a, b, c, d):
    def mixture(know, pid):
        return a * net_accounts(know, pid) + \
          b * net_machines(know, pid) + \
          c * clean_machines(know, pid) + \
          d * security(know, pid)
    return mixture

