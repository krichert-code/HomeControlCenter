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
        #self.__delay = delay
        #self.__xmldoc = xmldoc
        #self.__xmlItem = item
        #self.__pause = pause
        #self.__url = url
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
                req = requests.get(task.value)
                if req.text <> "OK":
                    forceClean = True
                    
            if task.type == "set":
                item = __findItem(task.value)
                if item.getAttribute('state') == "0":        
                    item.setAttribute("state","1")                                    
                    item.setAttribute("desc",desc)
                    self.__xmldoc.writexml( open('data/config.xml', 'w'))
                else:
                    exit = True
                    
            if task.type == "clear":
                item = __findItem(task.value)
                item.setAttribute("state","0")                                    
                item.setAttribute("desc",desc)
                self.__xmldoc.writexml( open('data/config.xml', 'w'))
            
            ActionThread.__mutex.release()
            
            if task.type == "delay" and forceClean == False:
                time.sleep(task.value)

            if exit == True:
                break
            
        event.set()
            
        time.sleep(self.__delay)
        if len(self.__url) > 0:
            req = requests.get(self.__url)
            time.sleep(self.__pause)
            req = requests.get(self.__url)
        self.__xmlItem.setAttribute("state","0")                                    
        self.__xmlItem.setAttribute("desc","No action")
        self.__xmldoc.writexml( open('data/config.xml', 'w'))

    


class ActionClass(object):
    __eventsData = []
    __xmldoc = None
    
    def __init__(self):
        self.__eventsData = []
        self.__xmldoc = minidom.parse('data/config.xml')

    def __updateEvents(self, onlyActiveEvents = True):
        itemsList = self.__xmldoc.getElementsByTagName('status')[0].getElementsByTagName('element')        
        for item in itemsList:
            if (item.getAttribute('state') == "1" and onlyActiveEvents == True) or (onlyActiveEvents == False):
                self.__eventsData.append(EventClass.EventClass(item.getAttribute('desc'),"",item.getAttribute('name'), item.getAttribute('state')))    
        
    def actionOnGate0(self):
        taskList = []
        event = threading.Event()
        event.clear()
        
        url = self.__xmldoc.getElementsByTagName('switch')[0].getElementsByTagName('garage')[0].getAttribute('url')

        itemsList = self.__xmldoc.getElementsByTagName('status')[0].getElementsByTagName('element')
        for item in itemsList:
            if item.getAttribute('name') == "garage":
                break

        # allow to open gate only if action is not in progress already
        if item.getAttribute('state') == "0":                                    
            req = requests.get(url)
            if req.text=="OK":                
                item.setAttribute("state","1")                                    
                item.setAttribute("desc","Otwieranie/Zamykanie bramy garazowej")
                self.__xmldoc.writexml( open('data/config.xml', 'w'))
                ActionThread(event, taskList).start()
                event.wait(5)
	self.__updateEvents();

    def actionOnGate1(self):
        url = self.__xmldoc.getElementsByTagName('switch')[0].getElementsByTagName('mainGate')[0].getAttribute('url')

        itemsList = self.__xmldoc.getElementsByTagName('status')[0].getElementsByTagName('element')
        for item in itemsList:
            if item.getAttribute('name') == "mainGate":
                break

        # allow to open gate only if action is not in progress already
        if item.getAttribute('state') == "0":                                    
            req = requests.get(url)
            if req.text=="OK":                
                item.setAttribute("state","1")                                    
                item.setAttribute("desc","Otwieranie bramy wjazdowej")
                self.__xmldoc.writexml( open('data/config.xml', 'w'))
                ActionThread(self.__xmldoc, item, 18).start()
	self.__updateEvents();

    def actionOnGate1Perm(self):
        url = self.__xmldoc.getElementsByTagName('switch')[0].getElementsByTagName('mainGate')[0].getAttribute('url')

        itemsList = self.__xmldoc.getElementsByTagName('status')[0].getElementsByTagName('element')
        for item in itemsList:
            if item.getAttribute('name') == "mainGate":
                break

        # allow to open gate only if action is not in progress already
        if item.getAttribute('state') == "0":                                    
            req = requests.get(url)
            if req.text=="OK":                
                item.setAttribute("state","1")                                    
                item.setAttribute("desc","Otwieranie bramy wjazdowej")
                self.__xmldoc.writexml( open('data/config.xml', 'w'))
                ActionThread(self.__xmldoc, item, 25, url, 2).start()
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
