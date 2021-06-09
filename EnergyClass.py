import AlarmClass

class EnergyClass(object):

    def __init__(self):
	pass


    def getCurrentProduceEnergy(self):
	energy = {}
	try:
	    alarm = AlarmClass.AlarmClass()
	    energy = alarm.getEnergy()
	except:
	    print "___________energy exception"

        return energy

