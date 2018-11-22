import ConfigClass
import EventClass
import requests


class SprinklerClass(object):

    def __init__(self):
        pass


    def getSprinklerEvents(self):
        events = []
        config = ConfigClass.ConfigClass()
        desc = config.getSwitchItemDesc("Sprinkler1")
	item = EventClass.EventClass(desc)
	item.setEventName("Sprinkler1")
	item.setEventIcon("img/off_mobile.png")
        events.append(item)

        desc = config.getSwitchItemDesc("Sprinkler2")
	item = EventClass.EventClass(desc)
	item.setEventName("Sprinkler2")
	item.setEventIcon("img/off_mobile.png")
        events.append(item)

        desc = config.getSwitchItemDesc("Sprinkler3")
	item = EventClass.EventClass(desc)
	item.setEventName("Sprinkler3")
	item.setEventIcon("img/off_mobile.png")
        events.append(item)

        return events

    def getSprinklersOffRequest(self):
        config = ConfigClass.ConfigClass()
        return config.getSwitchURL("SprinklerOff")
	

    def getEventsData(self, id):
        events = []
	sprinkler1Status1 = (1 << 1)
	sprinkler1Status2 = (1 << 2)
	sprinkler1Status3 = (1 << 3)
	status = 0
        config = ConfigClass.ConfigClass()
        url_status = config.getSwitchURL("SprinklerStatus")

        try:
            event = requests.get(url_status, verify = False, timeout = 3)
	    status = int(event.text)
	    if (status & sprinklerStatus1) <> 0:
        	events.append(EventClass.EventClass("System zraszaczy 1 jest wlaczony", "", id))
	    elif (status & sprinklerStatus2) <> 0:
        	events.append(EventClass.EventClass("System zraszaczy 2 jest wlaczony", "", id))
	    elif (status & sprinklerStatus3) <> 0:
        	events.append(EventClass.EventClass("System zraszaczy 3 jest wlaczony", "", id))
	    
        except requests.exceptions.RequestException as e:
            events = []
        finally:
            return events


