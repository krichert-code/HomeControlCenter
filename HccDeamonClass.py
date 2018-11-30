import requests
import threading
import time
import datetime
import ConfigClass
import RadioClass

        
class Alarm:
    def __init__(self):
	config = ConfigClass.ConfigClass()
	self.__start_time = config.getAlarmSetting("start_time")
	self.__stop_time = config.getAlarmSetting("stop_time")
	self.__radio = config.getAlarmSetting("radio")
	self.__volume = config.getAlarmSetting("volume")
	self.__playing = False

    def __compareTime(self, date):
	hour = datetime.datetime.now().time().hour;
	minute = datetime.datetime.now().time().minute;
	hour_param = int(date[:date.find(":")])
	minute_param = int(date[date.find(":")+1:])
	if (hour == hour_param) and (minute == minute_param):
	    return True
	else:
	    return False

    def timeEvent(self):
	radio = RadioClass.RadioClass()

	if  self.__compareTime(self.__start_time) == True and self.__playing == False:
	    try:
		req = radio.getRadioPlayRequest(self.__radio)
		requests.get(req , verify = False)
		req = radio.setRadioVolume(int(self.__volume))
		self.__playing = True
            except requests.exceptions.RequestException as e:
		self.__playing = False

	if self.__compareTime(self.__stop_time) == True and self.__playing == True:
	    try:
		req = radio.getRadioStopRequest()
		requests.get(req , verify = False)
                self.__playing = False
            except requests.exceptions.RequestException as e:
		self.__playing = True



#------------------------------------------------------------------------------------------------------------------------
class HccDeamonClass(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
	self.__stopEvent = False
	pass        

    def stop(self):
	self.__stopEvent = True

    def run(self):
	config = ConfigClass.ConfigClass()
	alarm = Alarm()

	while (not self.__stopEvent):
	    alarm.timeEvent()
	    
	    time.sleep(1)


