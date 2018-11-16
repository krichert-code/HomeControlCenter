from xml.dom import minidom
import requests
import threading
import EventClass
import time
import ConfigClass

class Task:
    type = ""
    value = ""
    desc = ""    
    def __init__(self, type, value, desc = ""):
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
		self.__event.set()

            if task.type == "clear":
		config = ConfigClass.ConfigClass()
		ret_val = config.changeStatus(task.value, "0", task.desc)

            ActionThread.__mutex.release()
            
            # Below events don't need to be in critical section 
            if task.type == "delay" and forceClean == False:
                time.sleep(task.value)

            if task.type == "notify":
		self.__event.set()

            if exit == True:
                break
    


class ActionClass(object):
    __config = None
    
    def __init__(self):
        self.__config = ConfigClass.ConfigClass()
        
    def actionOnGate0(self):
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

    def actionOnGate1(self):
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
        

    def actionOnGate1Perm(self):
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

                
    def actionOnGetSprinklersStatus(self):
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

	#taskList.append(Task("request",url_off_all))
	taskList.append(Task("clear","Sprinkler1"))
	taskList.append(Task("clear","Sprinkler2"))
	taskList.append(Task("clear","Sprinkler3"))
	
	if xmlEvent.state == "0":
	    taskList.append(Task("set",name))
	else:
	    taskList.append(Task("notify",url))

	#taskList.append(Task("request",url))
	taskList.append(Task("delay",5))

        event.clear()
        ActionThread(event, taskList).start()
        event.wait()


    def actionOnSprinkler1(self):
        self.__actionOnSprinkler("Sprinkler1")
	return self.actionOnGetSprinklersStatus()

    def actionOnSprinkler2(self):
        self.__actionOnSprinkler("Sprinkler2")
	return self.actionOnGetSprinklersStatus()

    def actionOnSprinkler3(self):
        self.__actionOnSprinkler("Sprinkler3")
	return self.actionOnGetSprinklersStatus()

    def actionOnGetActiveEvents(self):
        # get only activate events
        return self.__config.getEvents()

    def getEventsData(self,actionName):
        method_name = 'actionOn' + actionName
        method = getattr(self, method_name)
        events = method()
        return events
