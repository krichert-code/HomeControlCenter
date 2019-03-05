import ConfigClass
import EventClass
import ActionThread
import time

class SprinklerClass(object):

    def __init__(self):
        pass


    def getSprinklerItems(self):
        events = []
        desc = "Zraszacze w polu 1"
	item = EventClass.EventClass(desc)
	item.setEventName("1")
        events.append(item)

        desc = "Zraszacze w polu 2"
	item = EventClass.EventClass(desc)
	item.setEventName("2")
        events.append(item)

        desc = "Zraszacze w polu 3"
	item = EventClass.EventClass(desc)
	item.setEventName("3")
        events.append(item)

        return events


    def getSprinklerStatus(self):
	sprinklerStatus3 = (1 << 1)
	sprinklerStatus2 = (1 << 2)
	sprinklerStatus1 = (1 << 3)
	ret_val = 0
	# getting status have to be perform by ActionThread class because switch may handle only one request in the same time
        config = ConfigClass.ConfigClass()
	status_url = config.getSwitchURL("Status")
	threadStatus = ActionThread.ActionThread()
	threadStatus.addTask("request",status_url)
	threadStatus.addTask("notify")
	threadStatus.start()
	threadStatus.suspend()
	try:
	    status = int(threadStatus.getResponse())
	    if (status & sprinklerStatus1 <> 0):
		ret_val = 1
	    if (status & sprinklerStatus2 <> 0):
		ret_val = 2
	    if (status & sprinklerStatus3 <> 0):
		ret_val = 3
	except:
	    ret_val = -1
	    
	return ret_val


    def getEventsData(self, id):
        events = []
	status = self.getSprinklerStatus()
	event = None

	if status == -1:
	    event = EventClass.EventClass("System zraszaczy - Blad krytyczny", "", id)
	elif status == 1:
	    event = EventClass.EventClass("System zraszaczy 1 jest wlaczony", "", id)
	elif status == 2:
	    event =EventClass.EventClass("System zraszaczy 2 jest wlaczony", "", id)
	elif status == 3:
    	    event = EventClass.EventClass("System zraszaczy 3 jest wlaczony", "", id)
	    
	if event <> None:
	    event.setEventIcon('garden')
	    events.append(event)
        return events


