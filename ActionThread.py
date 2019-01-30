import requests
import threading
import time
import ConfigClass

class Task:
    def __init__(self, type, value="", desc = ""):
        self.type = type
        self.value = value
        self.desc = desc        
        
class ActionThread(threading.Thread):
    __mutex = None

    def __init__(self):
        threading.Thread.__init__(self)
        self.__response = ""
        self.__taskList = []
        self.__event = threading.Event()

        self.__event.clear()

        if ActionThread.__mutex == None:	    
            ActionThread.__mutex = threading.Lock()
        

    def suspend(self):
	self.__event.wait()

    def addTask(self, type, value="", desc=""):
	self.__taskList.append(Task(type,value,desc))

    def getResponse(self):
	return self.__response

    def run(self):
        exit = False
        forceClean = False
        
        for task in self.__taskList:
            
            ActionThread.__mutex.acquire()

            if task.type == "request":
                try:
                    # Wait up to 3 second for response
                    # If no response then initialize 'cleaning' - set forceClean
                    req = requests.get(task.value, verify = False, timeout = 10)
		    self.__response = req.text
                except requests.exceptions.RequestException as e:
                    req = None                
		    self.__response = ""
                finally:
                    if req == None:                    
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
    


