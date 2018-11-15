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
                req = requests.get(task.value)
		print "____________Request cc = " + req.text
                if req.text <> "OK":
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
		    print "____________Action already in progress:exit"
                    exit = True
		    self.__event.set()

            if task.type == "clear":
		print "____________Clear Action"
                xmldoc, node = self.__findItem(task.value)
                node.setAttribute("state","0")                                    
                node.setAttribute("desc",task.desc)
                xmldoc.writexml( open('data/config.xml', 'w') )
            
            ActionThread.__mutex.release()
            
            if task.type == "delay" and forceClean == False:
                time.sleep(task.value)
		print "____________Delay action"

            if exit == True:
                break
    


class ActionClass(object):
    __eventsData = []
    __xmldoc = None
    
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
        event.clear()
        
        url = self.__xmldoc.getElementsByTagName('switch')[0].getElementsByTagName('garage')[0].getAttribute('url')
	taskList.append(Task("set","garage", "Otwieranie/Zamykanie bramy garazowej"))
	taskList.append(Task("request",url))
	taskList.append(Task("delay",5))
	taskList.append(Task("clear","garage", "No action"))
	ActionThread(event, taskList).start()
	event.wait()

        #itemsList = self.__xmldoc.getElementsByTagName('status')[0].getElementsByTagName('element')
        #for item in itemsList:
        #    if item.getAttribute('name') == "garage":
        #        break

        # allow to open gate only if action is not in progress already
        #if item.getAttribute('state') == "0":                                    
        #    req = requests.get(url)
        #    if req.text=="OK":                
        #        item.setAttribute("state","1")                                    
        #        item.setAttribute("desc","Otwieranie/Zamykanie bramy garazowej")
        #        self.__xmldoc.writexml( open('data/config.xml', 'w'))
        #        ActionThread(event, taskList).start()
        #        event.wait(5)
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
