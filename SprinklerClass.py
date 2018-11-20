import ConfigClass
import EventClass
import requests


class RadioClass(object):

    def __init__(self):
	pass


    def getSprinklersOffRequest(self):
	config = ConfigClass.ConfigClass()
	return config.getSwitchURL("SprinklerOff")
	

    def getEventsData(self):
	events = []
	config = ConfigClass.ConfigClass()
	url_status = config.getSwitchURL("SprinklerStatus")

	try:
	    event = requests.get(url_status, verify = False, timeout = 3)
	    #events.append(EventClass.EventClass("System zraszaczy jest wlaczony", "", "Sprinkler"))
        except requests.exceptions.RequestException as e:
            events = []
	finally:
	    return events


