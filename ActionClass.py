from xml.dom import minidom
import requests
import threading
import EventClass
import time

class ActionThread(threading.Thread):
    __xmldoc = None
    __xmlItem = None
    __url = ""
    __pause = 0
    __delay = 0
    
    def __init__(self, xmldoc, item, delay, url="", pause=0):
        threading.Thread.__init__(self)
        self.__delay = delay
        self.__xmldoc = xmldoc
        self.__xmlItem = item
        self.__pause = pause
        self.__url = url 
        
    def run(self):
        time.sleep(self.__delay)
        if len(self.__url) > 0:
            req = requests.get(self.__url)
            time.sleep(self.__pause)
            req = requests.get(self.__url)
        self.__xmlItem.setAttribute("state","0")                                    
        self.__xmlItem.setAttribute("desc","No action")
        self.__xmldoc.writexml( open('data/config.xml', 'w'))

    


class ActionClass:
    __eventsData = []
    __xmldoc = None
    
    def __init__(self):
        self.__eventsData = []
        self.__xmldoc = minidom.parse('data/config.xml')
        
    def __actionOnGate0(self):
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
                ActionThread(self.__xmldoc, item, 20).start()

    def __actionOnGate1(self, permament):
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
                
                if permament == False:
                    ActionThread(self.__xmldoc, item, 18).start()
                else:                                        
                    ActionThread(self.__xmldoc, item, 25, url, 2).start()
                
            
            
    def __updateEvents(self):
        itemsList = self.__xmldoc.getElementsByTagName('status')[0].getElementsByTagName('element')        
        for item in itemsList:
            if item.getAttribute('state') == "1":
                self.__eventsData.append(EventClass.EventClass(item.getAttribute('desc'),"","action"))    
    
    def getEventsData(self,actionName):
        if actionName == "gate0":    
            self.__actionOnGate0()       

        if actionName == "gate1":    
            self.__actionOnGate1(False)       

        if actionName == "gate1_perm":    
            self.__actionOnGate1(True)       
                 
        self.__updateEvents();        
        return self.__eventsData
    