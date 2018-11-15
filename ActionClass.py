from xml.dom import minidom
import requests
import threading
import EventClass
import time

class Task:
    type = ""
    value = ""
    desc = ""    
    def __init__(self, type, value, desc = ""):
        self.type = type
        self.value = value
        self.desc = desc
        
class ActionThread(threading.Thread):
    __xmldoc = None
    __xmlItem = None
    __url = ""
    __pause = 0
    __delay = 0

    __event = None
    __taskList = None
    __mutex = None
    
    def __init__(self, event, tasks):
        threading.Thread.__init__(self)
        self.__event = event
        self.__taskList = tasks
        if ActionThread.__mutex == None:
	    print "____________MUTEX was created"
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
            print "_____________" + task.type
            if task.type == "request":
                try:
                    req = requests.get(task.value, verify = False, timeout = 3)
                except requests.exceptions.RequestException as e:
                    req = None                
                
                if req == None or req.text <> "OK":
                    print "____________FORCEClean is needed"
                    forceClean = True
                    
            if task.type == "set":
                xmldoc, node = self.__findItem(task.value)
                if node.getAttribute('state') == "0":        
                    node.setAttribute("state","1")                                    
                    node.setAttribute("desc",task.desc)
                    xmldoc.writexml( open('data/config.xml', 'w'))
                    self.__event.set()
                else:
                    exit = True
                    self.__event.set()

            if task.type == "clear":
                xmldoc, node = self.__findItem(task.value)
                node.setAttribute("state","0")                                    
                node.setAttribute("desc",task.desc)
                xmldoc.writexml( open('data/config.xml', 'w') )
            
            ActionThread.__mutex.release()
            
            if task.type == "delay" and forceClean == False:
                time.sleep(task.value)

            if exit == True:
                break
    


class ActionClass(object):
    __eventsData = []    
    
    def __init__(self):
        self.__eventsData = []
        self.__xmldoc = minidom.parse('data/config.xml')

    def __updateEvents(self, onlyActiveEvents = True):
        xmldoc = minidom.parse('data/config.xml')
        itemsList = xmldoc.getElementsByTagName('status')[0].getElementsByTagName('element')        
        for item in itemsList:
            if (item.getAttribute('state') == "1" and onlyActiveEvents == True) or (onlyActiveEvents == False):
                self.__eventsData.append(EventClass.EventClass(item.getAttribute('desc'),"",item.getAttribute('name'), item.getAttribute('state')))    
        
    def actionOnGate0(self):
        taskList = []
        event = threading.Event()        
        xmldoc = minidom.parse('data/config.xml')
        
        url = xmldoc.getElementsByTagName('switch')[0].getElementsByTagName('garage')[0].getAttribute('url')
        taskList.append(Task("set","garage", "Otwieranie/Zamykanie bramy garazowej"))
        taskList.append(Task("request",url))
        taskList.append(Task("delay",20))
        taskList.append(Task("clear","garage", "No action"))
        event.clear()
        ActionThread(event, taskList).start()
        event.wait()
        self.__updateEvents();

    def actionOnGate1(self):
        taskList = []
        event = threading.Event()        
        xmldoc = minidom.parse('data/config.xml')
        
        url = xmldoc.getElementsByTagName('switch')[0].getElementsByTagName('mainGate')[0].getAttribute('url')
        taskList.append(Task("set","mainGate", "Otwieranie bramy wjazdowej"))
        taskList.append(Task("request",url))
        taskList.append(Task("delay",20))
        taskList.append(Task("clear","mainGate", "No action"))
        event.clear()
        ActionThread(event, taskList).start()
        event.wait()
        self.__updateEvents();
        

    def actionOnGate1Perm(self):
        taskList = []
        event = threading.Event()        
        xmldoc = minidom.parse('data/config.xml')
        
        url = xmldoc.getElementsByTagName('switch')[0].getElementsByTagName('mainGate')[0].getAttribute('url')
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
        self.__updateEvents();

                
    def actionOnGetSprinklersStatus(self):
        internalEventList = []
        self.__updateEvents(False);
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
        self.__updateEvents();

    def getEventsData(self,actionName):
        method_name = 'actionOn' + actionName
        method = getattr(self, method_name)
        method()
        return self.__eventsData
