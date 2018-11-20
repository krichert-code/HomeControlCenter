import ConfigClass
import EventClass
import requests


class SprinklerClass(object):

    def __init__(self):
        pass


    def getSprinklerElements(self):
        desc = []
        config = ConfigClass.ConfigClass()
        
        desc.append(config.getSwitchItemDesc("Sprinkler1"))
        return desc
        
    def getSprinklersOffRequest(self):
        config = ConfigClass.ConfigClass()
        return config.getSwitchURL("SprinklerOff")
	

    def getEventsData(self, id):
        events = []
        config = ConfigClass.ConfigClass()
        url_status = config.getSwitchURL("SprinklerStatus")

        try:
            event = requests.get(url_status, verify = False, timeout = 3)
            print "_______________" + event.text
            #events.append(EventClass.EventClass("System zraszaczy jest wlaczony", "", "Sprinkler"))
        except requests.exceptions.RequestException as e:
            events = []
        finally:
            return events


