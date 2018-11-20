from xml.dom import minidom
import requests
import threading
import EventClass
import time
import ConfigClass
import CalendarClass
import RadioClass
import SprinklerClass

class Task:
    type = ""
    value = ""
    desc = ""    
    def __init__(self, type, value="", desc = ""):
        self.type = type
        self.value = value
        self.desc = desc        
        
class ActionThread(threading.Thread):
    __event = None
    __taskList = None
    __mutex = None    
    
    def __init__(self, event, tasks):
        threading.Thread.__init__(self)
        self.__event = event
        self.__taskList = tasks        
        if ActionThread.__mutex == None:	    
            ActionThread.__mutex = threading.Lock()
        

    def run(self):
        exit = False
        forceClean = False
        
        for task in self.__taskList:
            
            ActionThread.__mutex.acquire()

            if task.type == "request":
                try:
                    # Wait up to 3 second for response
                    # If no response then initialize 'cleaning' - set forceClean
                    req = requests.get(task.value, verify = False, timeout = 3)
                except requests.exceptions.RequestException as e:
                    req = None                
                finally:
                    if req == None or req.text <> "OK":                    
                        forceClean = True
                    
            if task.type == "set":
                # After set state event to waiting thread have to be send
                # Waiting thread may collect and disaply active events 
                config = ConfigClass.ConfigClass()
                ret_val = config.changeStatus(task.value, "1", task.desc)
                if ret_val <> "Conf_Change_ok":
                    # Task is already in progress (state = 1), so just initialize exit thread
                    exit = True
		if self.__event <> None:
		    self.__event.set()

            if task.type == "clear":
                config = ConfigClass.ConfigClass()
                ret_val = config.changeStatus(task.value, "0", task.desc)

            ActionThread.__mutex.release()
            
            # Below events don't need to be in critical section 
            if task.type == "delay" and forceClean == False:
                time.sleep(task.value)

            if task.type == "notify" and self.__event <> None:
                self.__event.set()

            if exit == True:
                break
    


class ActionClass(object):
    __config = None
    __actionEvents = []
    ActionEventAll       = 1 << 0
    ActionEventGeneric   = 1 << 1
    ActionEventCalendar  = 1 << 2
    ActionEventRadio     = 1 << 3
    ActionEventSprinkler = 1 << 4

    def __init__(self):
        self.__config = ConfigClass.ConfigClass()
	
        
    def __isEventEnable(self, events, eventID):
	if (events & eventID <> 0) or (events & ActionClass.ActionEventAll <> 0):
	    return True
	else:
	    return False

    def __updateEvents(self, events, filters):
	if (filters & ActionClass.ActionEventAll <> 0):
	    ActionClass.__actionEvents = events
	else:
	    # find events in global event list and update them, if not exist then add
	    for item in events:
		exist = False
		for global_event_item in ActionClass.__actionEvents:
		    if global_event_item.name == item.name:
			exist = True
			global_event_item = item
			break
		if exist == False:
		    ActionClass.__actionEvents.append(item)


    def actionOnGate0(self, param = ""):
        taskList = []
        event = threading.Event()                
        url = self.__config.getSwitchURL("garage")
        
        taskList.append(Task("set","garage", "Otwieranie/Zamykanie bramy garazowej"))
        taskList.append(Task("request",url))
        taskList.append(Task("delay",20))
        taskList.append(Task("clear","garage", "No action"))
        event.clear()
        ActionThread(event, taskList).start()
        event.wait()
        return self.__config.getEvents()        

    def actionOnGate1(self, param = ""):
        taskList = []
        event = threading.Event()        
                
        url = self.__config.getSwitchURL("mainGate")

        taskList.append(Task("set","mainGate", "Otwieranie bramy wjazdowej"))
        taskList.append(Task("request",url))
        taskList.append(Task("delay",20))
        taskList.append(Task("clear","mainGate", "No action"))
        event.clear()
        ActionThread(event, taskList).start()
        event.wait()
        return self.__config.getEvents()        
        

    def actionOnGate1Perm(self, param = ""):
        taskList = []
        event = threading.Event()        
        
        url = self.__config.getSwitchURL("mainGate")

        taskList.append(Task("set","mainGate", "Otwieranie bramy wjazdowej"))
        taskList.append(Task("request",url))
        taskList.append(Task("delay",25))
        taskList.append(Task("request",url))
        taskList.append(Task("delay",2))
        taskList.append(Task("request",url))
        taskList.append(Task("clear","mainGate", "No action"))
        event.clear()
        ActionThread(event, taskList).start()
        event.wait()
        return self.__config.getEvents()        

                
    def actionOnGetSprinklersStatus(self, param = ""):
        internalEventList = []

        internalEventList.append(self.__config.getEvent("Sprinkler1"))
        internalEventList.append(self.__config.getEvent("Sprinkler2"))
        internalEventList.append(self.__config.getEvent("Sprinkler3"))

        # remove events not related to sprinklers
        for item in internalEventList:
            # update icon depands on device state
            if item.state == "0":
                item.icon="img/off_mobile.png"
            else:
                item.icon="img/on_mobile.png"

        return internalEventList


    def __actionOnSprinkler(self, name):
        #on/off sprinkler and update status in xml
        taskList = []
        event = threading.Event()
        url = self.__config.getSwitchURL(name)
        url_off_all = self.__config.getSwitchURL("SprinklerOff")

        xmlEvent = self.__config.getEvent(name)

        taskList.append(Task("request",url_off_all))
        taskList.append(Task("clear","Sprinkler1"))
        taskList.append(Task("clear","Sprinkler2"))
        taskList.append(Task("clear","Sprinkler3"))
	
        if xmlEvent.state == "0":
            taskList.append(Task("set",name))
	    taskList.append(Task("delay",5))
	    taskList.append(Task("request",url))
        else:
            taskList.append(Task("notify"))

        event.clear()
        ActionThread(event, taskList).start()
        event.wait()


    def actionOnSprinkler1(self, param = ""):
        self.__actionOnSprinkler("Sprinkler1")

    def actionOnSprinkler2(self, param = ""):
        self.__actionOnSprinkler("Sprinkler2")

    def actionOnSprinkler3(self, param = ""):
        self.__actionOnSprinkler("Sprinkler3")

    def actionOnPlay(self, param = ""):
        taskList = []
        event = threading.Event()
        radio = RadioClass.RadioClass()
        radio_station = radio.getRadioStation(param)
        radio_req = radio.getRadioPlayRequest(param) 
        taskList.append(Task("request",radio_req))
        taskList.append(Task("notify"))        
        taskList.append(Task("delay",2))
        event.clear()
        ActionThread(event, taskList).start()
        event.wait()

    def actionOnStop(self, param = ""):
        taskList = []
        event = threading.Event()
        radio = RadioClass.RadioClass()
        radio_req = radio.getRadioStopRequest()
        taskList.append(Task("request",radio_req))
        taskList.append(Task("notify"))        
        taskList.append(Task("delay",2))
        event.clear()
        ActionThread(event, taskList).start()
        event.wait()

    def actionOnVolumeUp(self, param = ""):
        taskList = []
        radio = RadioClass.RadioClass()
        radio_req = radio.getRadioVolumeUpRequest() 
        taskList.append(Task("request",radio_req))
        taskList.append(Task("delay",3))
        ActionThread(None, taskList).start()

    def actionOnVolumeDown(self, param = ""):
        taskList = []
        radio = RadioClass.RadioClass()
        radio_req = radio.getRadioVolumeDownRequest() 
        taskList.append(Task("request",radio_req))
        taskList.append(Task("delay",3))
        ActionThread(None, taskList).start()

    def actionOnGetActiveEvents(self, param = ""):
        # get only activate events
	pass

#---------------------------------------------------------------------------------------------------------------
    def getEventsData(self,actionName, param = "", filters = ActionEventAll, returnOnlyRequestedEvents = False):
	events = []

	calendarEvents = CalendarClass.CalendarClass()
	radioEvents = RadioClass.RadioClass()
	sprinklerEvent = SprinklerClass.SprinklerClass()

	if actionName <> None:
    	    method_name = 'actionOn' + actionName
    	    method = getattr(self, method_name)
    	    method(param)

	if self.__isEventEnable(filters, ActionClass.ActionEventRadio) == True:
	    events = events + radioEvents.getEventsData()

	if self.__isEventEnable(filters, ActionClass.ActionEventSprinkler) == True:
	    events = events + sprinklerEvent.getEventsData()

	if self.__isEventEnable(filters, ActionClass.ActionEventGeneric) == True:
	    events = events + self.__config.getEvents()

	if self.__isEventEnable(filters, ActionClass.ActionEventCalendar) == True:
	    events = events + calendarEvents.getEventsData()

	self.__updateEvents(events, filters)


	if returnOnlyRequestedEvents == True:
	    return events
	else:
	    return ActionClass.__actionEvents


