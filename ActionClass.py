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
        
    def __findItem(self, name):
	xmldoc = minidom.parse('data/config.xml')
	itemsList = xmldoc.getElementsByTagName('status')[0].getElementsByTagName('element')
        for item in itemsList:
            if item.getAttribute('name') == name:
                break
	return xmldoc, item

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
                xmldoc, node = self.__findItem(task.value)
                if node.getAttribute('state') == "0":        
                    node.setAttribute("state","1")                                    
                    node.setAttribute("desc",task.desc)
                    xmldoc.writexml( open('data/config.xml', 'w'))
                    self.__event.set()
                else:
                    # Task is already in progress (state = 1), so just initialize exit thread
                    exit = True
                    self.__event.set()

            if task.type == "clear":
                xmldoc, node = self.__findItem(task.value)
                node.setAttribute("state","0")                                    
                node.setAttribute("desc",task.desc)
                xmldoc.writexml( open('data/config.xml', 'w') )
            
            ActionThread.__mutex.release()
            
            # Below events don't need to in critical section 
            if task.type == "delay" and forceClean == False:
                time.sleep(task.value)

            if exit == True:
                break
    


class ActionClass(object):
    __eventsData = []        
    
    def __init__(self):
        self.__eventsData = []        
        self.config = ConfigClass.ConfigClass()
        
    def actionOnGate0(self):
        taskList = []
        event = threading.Event()                
        url = self.config.getSwitchURL("garage")
        
        taskList.append(Task("set","garage", "Otwieranie/Zamykanie bramy garazowej"))
        taskList.append(Task("request",url))
        taskList.append(Task("delay",20))
        taskList.append(Task("clear","garage", "No action"))
        event.clear()
        ActionThread(event, taskList).start()
        event.wait()
        self.__eventsData = self.config.getEvents()        

    def actionOnGate1(self):
        taskList = []
        event = threading.Event()        
                
        url = self.config.getSwitchURL("mainGate")

        taskList.append(Task("set","mainGate", "Otwieranie bramy wjazdowej"))
        taskList.append(Task("request",url))
        taskList.append(Task("delay",20))
        taskList.append(Task("clear","mainGate", "No action"))
        event.clear()
        ActionThread(event, taskList).start()
        event.wait()
        self.__eventsData = self.config.getEvents()        
        

    def actionOnGate1Perm(self):
        taskList = []
        event = threading.Event()        
        
        url = self.config.getSwitchURL("mainGate")

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
        self.__eventsData = self.config.getEvents()        

                
    def actionOnGetSprinklersStatus(self):
        internalEventList = []
        self.__eventsData = self.config.getEvents(False)        
        # remove events not related to sprinklers
        for item in self.__eventsData:
            if item.name.find("Sprinkler") <> -1:
                # update icon depands on device state
                if item.state == "0":
                    item.icon="img/off_mobile.png"
                else:
                    item.icon="img/on_mobile.png"
                internalEventList.append(item)
                self.__eventsData = internalEventList


    def __actionOnSprinkler(self, id):
        #on/off sprinkler and update status in xml
        pass

    def actionOnSprinkler1(self):
        self.__actionOnSprinkler(1)

    def actionOnSprinkler2(self):
        self.__actionOnSprinkler(2)

    def actionOnSprinkler3(self):
        self.__actionOnSprinkler(3)

    def actionOnGetActiveEvents(self):
        # get only activate events
        self.__eventsData = self.config.getEvents()            

    def getEventsData(self,actionName):
        method_name = 'actionOn' + actionName
        method = getattr(self, method_name)
        method()
        return self.__eventsData
