def nathaniscool(know, pid):
	nummachines = 0
	for i in xrange(10):
		nummachines += (1.0 - know['owns'][pid, i, 0])
	return nummachines