import requests
import threading
import time
import ConfigClass

        
class HccDeamonClass(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
	self.__stopEvent = False
	pass        

    def stop(self):
	self.__stopEvent = True

    def run(self):
	while (not self.__stopEvent):
	    print "_____________DEAMON"
	    time.sleep(1)


