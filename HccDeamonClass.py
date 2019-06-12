import requests
import threading
import time
import datetime
import ConfigClass
import RadioClass
import CalendarClass
import WeatherClass
import HeaterClass
import ActionClass
import SprinklerClass
import RPi.GPIO as GPIO
import json

        
class Alarm:
    def __init__(self):
	self.__config = ConfigClass.ConfigClass()
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

	start_time = self.__config.getAlarmSetting("start_time")
	stop_time = self.__config.getAlarmSetting("stop_time")
	radioName = self.__config.getAlarmSetting("radio")
	volume = self.__config.getAlarmSetting("volume")
	policy = self.__config.getAlarmSetting("day_policy")


	playRadio = True
	#disable alarm if value is = 'disable' or alarm is set on 'week_day' and now is weekend
	if (policy == "disabled") or (policy == "week_day" and datetime.datetime.today().weekday() >= 5):
	    playRadio = False

	if  self.__compareTime(start_time) == True and self.__playing == False and playRadio == True:
	    try:
		radio.getRadioPlayRequest(radioName)
		radio.setRadioVolume(int(volume))
		self.__playing = True
            except:
		self.__playing = False
		print "____________radio error1"
	elif self.__compareTime(stop_time) == True and self.__playing == True:
	    try:
		radio.getRadioStopRequest()
		radio.setRadioVolume(50)
                self.__playing = False
            except:
		self.__playing = True
		print "____________radio error2"


class Speaker:
    __powerPin    = 17    #wPi = 0
    __activatePin = 27    #wPi = 2

    __no_activeCounter = 0

    def __init__(self):
	try:
	    GPIO.setwarnings(False)
	    GPIO.setmode(GPIO.BCM)
	    GPIO.setup(self.__powerPin, GPIO.OUT)
	    GPIO.setup(self.__activatePin, GPIO.OUT)

	    GPIO.output(self.__powerPin, GPIO.HIGH)
	    GPIO.output(self.__activatePin, GPIO.LOW)
	except:
	    print "__________speaker excetion"

    def timeEvent(self):
	try:
	    # power is activated by LOW
	    player = RadioClass.RadioClass()
	    isPlayerEnabled = player.isPlayerEnabled()
	    isSpeakerActivated = GPIO.input(self.__powerPin)

	    if False == isPlayerEnabled:
		self.__no_activeCounter = self.__no_activeCounter + 1
	    
	    if self.__no_activeCounter > 60 and 0 == isSpeakerActivated:
		GPIO.output(self.__powerPin, GPIO.HIGH)

	    if True == isPlayerEnabled and 1 == isSpeakerActivated:
		GPIO.output(self.__powerPin, GPIO.LOW)
		time.sleep(1)
		GPIO.output(self.__activatePin, GPIO.HIGH)
		time.sleep(1)
		GPIO.output(self.__activatePin, GPIO.LOW)
		self.__no_activeCounter = 0
	except:
	    print "__________speaker excetion"


class Calendar:
    def __init__(self):
	self.__day = 0

    def timeEvent(self):
	try:
	    calendar = CalendarClass.CalendarClass()
	    curr_day = datetime.datetime.now().strftime('%d')
	    if self.__day <> curr_day:
		self.__day = curr_day
		calendar.generateFiles()
	except:
	    print "__________calendar excetion"

class Heater:
	def __init__(self):
	    self.__counter = 0
	    self.__heater = HeaterClass.HeaterClass()

	def timeEvent(self, tick):
	    try:
		# manage heater state once per 60 sec
		if (tick % 60  == 0):
		    curr_week_day = datetime.datetime.today().weekday()
		    curr_hour = int(datetime.datetime.now().strftime('%H'))
		    self.__heater.manageHeaterState(curr_week_day, curr_hour)
	    except:
		print "__________heater excetion"
	    
	    
class Weather:
	def __init__(self):    
		weather = WeatherClass.WeatherClass()
		self.__day = 0
		self.__hour = 0
		self.__weatherFiles = 0;
		# Below counter is needed to generate weather files not exactly when new day/hour,
    		# but some time later because data are not available.
		self.__counter = 0
		try:
		    weather.generateFiles(weather.WeatherDailyFile | weather.WeatherHourlyFile | weather.WeatherCurrentFile)
		except:
		    print "__________wather excetion"

	def timeEvent(self):
		try:
		    weather = WeatherClass.WeatherClass()

		    curr_day = datetime.datetime.now().strftime('%d')
		    curr_hour = datetime.datetime.now().strftime('%H')

		    if self.__day <> curr_day:
			    self.__day = curr_day
			    self.__weatherFiles = self.__weatherFiles | weather.WeatherDailyFile | weather.WeatherHourlyFile
			    self.__counter = 200

		    if self.__hour <> curr_hour:
			    self.__hour = curr_hour
			    self.__weatherFiles = self.__weatherFiles | weather.WeatherCurrentFile
			    self.__counter = 200

		    if self.__weatherFiles <> 0 and self.__counter == 0:
			weather.generateFiles(self.__weatherFiles)
			self.__weatherFiles = 0

		    if self.__counter > 0 :
			self.__counter = self.__counter - 1
		except:
		    self.__day = curr_day
		    self.__hour = curr_hour
		    self.__weatherFiles = 0
		    self.__counter = 200
		    print "__________weather excetion"

class Sprinkler:
	def __init__(self):
	    self.__sprinkler = SprinklerClass.SprinklerClass()

	def timeEvent(self, tick):
	    try:
		# manage sprinkler state once per 60 sec
		if (tick % 60  == 0):
		    curr_week_day = datetime.datetime.today().weekday()
		    curr_hour = int(datetime.datetime.now().strftime('%H'))
		    curr_min = int(datetime.datetime.now().strftime('%M'))
		    self.__sprinkler.manageSprinklerState(curr_week_day, curr_hour, curr_min)
	    except:
		print "__________sprinkler excetion"


class Messages:
	__diff_calendar_timestamp = 86400
	def __init__(self):
	    #self.events = ActionClass.ActionClass()
	    #self.config = ConfigClass.ConfigClass()
	    self.lastStates = {}
	    self.lastSendEventDate = ""
	    self.currSendEventDate = ""


	def sendSms(self,apiKey, number, message):
    	    headers = {'content-type': 'application/json', 'App-Key':apiKey}
    	    sms={ "to": number, "from" :"DOM", "message": message, "bulkVariant": "ECO", "doubleEncode": True}
    	    status = "ERROR"

    	    try:
        	req = "https://justsend.pl/api/rest/v2/message/send"
        	r = requests.post(req, data =json.dumps(sms), headers=headers )
        	resp = json.loads(r.text)
        	status = resp['responseCode']
    	    except:
        	status = "ERROR"

    	    return status

	def __genericEventMessage(self, tick):
	    # check if message should be send once per 1min
	    update = False
	    events = ActionClass.ActionClass()
	    config = ConfigClass.ConfigClass()

	    # get all generic event (active and inactive)
	    items = events.getEvents( events.ActionEventGeneric, True, False )
	    try:
		for item in items:
		    update = False
		    # add item if not exist in "last state" list
		    if item.name not in self.lastStates:
		        self.lastStates[item.name] = "0"

		    # if state has changed then send message (if needed) and then update last state
		    if item.state != self.lastStates[item.name] and len(item.messageId) > 0:
		        #send message
		        phones = config.getPhoneNumbers()
		        text = config.getSmsMessage(item.messageId, item.state)
		        token = config.getSmsToken()

			for to in phones:
			    result = self.sendSms(token, to, text)
			    if result == "OK":
			        update = True

			# update last state if at least one message was send succesfully 
			if update == True:
		    	    self.lastStates[item.name] = item.state
	    except:
		print "__________message excetion"


	def __calendarEventmessage(self):
	    calendar = CalendarClass.CalendarClass()
	    config = ConfigClass.ConfigClass()
	    curr_time = datetime.datetime.now().strftime('%H:%M')
	    sendMessage = False

	    if config.getCalendarReminderEnabled() == True and curr_time == config.getCalendarReminderTime():
	        events = calendar.getEventsData(ActionClass.ActionEventCalendar)
		currTS = time.time()
		text = ""

	        for event in events:
		    eventTS = time.mktime(datetime.datetime.strptime(event.date, "%Y-%m-%d").timetuple())
		    # if event is tomorrow then send it
		    if (eventTS - currTS <= self.__diff_calendar_timestamp):
		        if sendMessage == True:
			    text = text + " , "
		    else:
			text = event.date + ": "

		    self.currSendEventDate = event.date
		    text = text + event.desc
		    sendMessage = True

		if sendMessage == True and self.currSendEventDate <> self.lastSendEventDate:
		    self.lastSendEventDate = self.currSendEventDate
		    phones = config.getPhoneNumbers()
		    token = config.getSmsToken()
		    for to in phones:
		        result = self.sendSms(token, to, text)

	def timeEvent(self,tick):
	    if (tick % 30) == 0:
		self.__genericEventMessage(tick)
		self.__calendarEventMessage()



#------------------------------------------------------------------------------------------------------------------------
class HccDeamonClass(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
	self.__stopEvent = False

    def stop(self):
	self.__stopEvent = True

    def run(self):
	timerTick = 0;
	config = ConfigClass.ConfigClass()
	speaker = Speaker()
	alarm = Alarm()
	calendar = Calendar()
	weather = Weather()
	heater = Heater()
	messages = Messages()
	sprinkler = Sprinkler()

	while (not self.__stopEvent):
		alarm.timeEvent()
		speaker.timeEvent()
		calendar.timeEvent()
		weather.timeEvent()
		heater.timeEvent(timerTick)
		messages.timeEvent(timerTick)
		sprinkler.timeEvent(timerTick)
		time.sleep(1)
		timerTick = timerTick + 1
