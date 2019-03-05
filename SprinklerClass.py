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

    def setSprinklerOn(self, param = ""):
	threadTask = ActionThread.ActionThread()
	config = ConfigClass.ConfigClass()
	url_on = config.getSwitchURL("Sprinkler"+param)
        threadTask.addTask("request",url_on)
        threadTask.addTask("delay",2)
	threadTask.addTask("notify")
        threadTask.start()
	threadTask.suspend()


    def setSprinklerOff(self):
	threadTask = ActionThread.ActionThread()
	config = ConfigClass.ConfigClass()

	url_off = config.getSwitchURL("SprinklerOff")
        threadTask.addTask("request", url_off)
	threadTask.addTask("delay", 2)
	threadTask.addTask("notify")
        threadTask.start()
	threadTask.suspend()

