from xml.dom import minidom
import ConfigurationInterface
import threading


class AdminPanelSyncClass(object):

    def __init__(self):        
        self.__mutex = threading.Lock()
        self.__observerList = []
        self.__configurationChanged = False

    def notify(self):
        self.__mutex.acquire()
        for observer in self.__observerList:
            observer.configurationUpdate()            
        self.__configurationChanged = False
        self.__mutex.release()        

    def registerObserver(self,observer):
        self.__mutex.acquire()
        self.__observerList.append(observer)
        self.__mutex.release()



    
