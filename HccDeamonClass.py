import requests
import threading
import time
import datetime
import ConfigClass
import RadioClass
import CalendarClass
import RPi.GPIO as GPIO

        
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


class Speaker:
    __powerPin    = 17    #wPi = 0
    __activatePin = 27    #wPi = 2

    __no_activeCounter = 0

    def __init__(self):
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(self.__powerPin, GPIO.OUT)
	GPIO.setup(self.__activatePin, GPIO.OUT)

	GPIO.output(self.__powerPin, GPIO.LOW)
	GPIO.output(self.__activatePin, GPIO.LOW)


    def timeEvent(self):
	player = RadioClass.RadioClass()
	isPlayerEnabled = player.isPlayerEnabled()
	isSpeakerActivated = GPIO.input(self.__powerPin)
    
	if False == isPlayerEnabled:
	    self.__no_activeCounter = self.__no_activeCounter + 1
	    if self.__no_activeCounter > 60 and 1 == isSpeakerActivated:
		GPIO.output(self.__powerPin, GPIO.LOW)

	if True == isPlayerEnabled and 0 == isSpeakerActivated:
	    GPIO.output(self.__powerPin, GPIO.HIGH)
	    time.sleep(1)
	    GPIO.output(self.__activatePin, GPIO.HIGH)
	    time.sleep(1)
	    GPIO.output(self.__activatePin, GPIO.LOW)
	    self.__no_activeCounter = 0

class Calendar:
    def __init__(self):
	pass

    def timeEvent(self):
	calendar = CalendarClass.CalendarClass()
	calendar.generateFiles()

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
	speaker = Speaker()
	alarm = Alarm()
	calendar = Calendar()

	while (not self.__stopEvent):
	    alarm.timeEvent()
	    speaker.timeEvent()
	    calendar.timeEvent()
	    
	    time.sleep(1)


