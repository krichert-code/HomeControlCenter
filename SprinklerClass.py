import ConfigClass
import EventClass
import ActionThread
import WeatherClass
import time


class SprinklerClass(object):
    __Max_num_of_sprinklers = 3
    __break_auto_water = False
    __force_auto_water = False

    def __init__(self):
	self.__autowater = False
	self.__state = 0
	self.__timestamp = 0



    def getSprinklerItems(self):
        events = []
        desc = "Zraszacze w polu 1"
	item = EventClass.EventClass(desc)
	item.setEventName("1")
        events.append(item)

        desc = "Zraszacze w polu 2"
	item = EventClass.EventClass(desc)
	item.setEventName("2")
        events.append(item)

        desc = "Zraszacze w polu 3"
	item = EventClass.EventClass(desc)
	item.setEventName("3")
        events.append(item)

        return events

    def setSprinklerForceAuto(self):
	SprinklerClass.__force_auto_water = True

    def setSprinklerOn(self, param = ""):
	threadTask = ActionThread.ActionThread()
	config = ConfigClass.ConfigClass()
	url_on = config.getSwitchURL("Sprinkler"+param)
        threadTask.addTask("request",url_on)
        threadTask.addTask("delay",2)
	threadTask.addTask("notify")
        threadTask.start()
	threadTask.suspend()

    def setSprinklerOff(self):
	threadTask = ActionThread.ActionThread()
	config = ConfigClass.ConfigClass()
	SprinklerClass.__break_auto_water = True
	url_off = config.getSwitchURL("SprinklerOff")
        threadTask.addTask("request", url_off)
	threadTask.addTask("delay", 2)
	threadTask.addTask("notify")
        threadTask.start()
	threadTask.suspend()

    def manageSprinklerState(self, curr_week_day, curr_hour, curr_min):
	config = ConfigClass.ConfigClass()
	weather = WeatherClass.WeatherClass()

	rainOccured = False
	duration = int(config.getDurationTime()) * 60
	currentTS = time.time()

	if (weather.rainOccured() == True and config.checkRainOccured() == True):
	    rainOccured = True

	if self.__autowater == False:
	    self.__state = 0
	    if (config.isStartTime(curr_week_day, curr_hour, curr_min) or SprinklerClass.__force_auto_water == True):
		self.__autowater = True
	    self.__timestamp = currentTS
	    SprinklerClass.__break_auto_water = False
	
	print "---------DEBUG autowater = " + str(self.__autowater)
	print "---------DEBUG brake = " + str(SprinklerClass.__break_auto_water)
	print "---------DEBUG force = " + str(SprinklerClass.__force_auto_water)

	if self.__autowater == True and ( currentTS >= self.__timestamp + (self.__state * duration) ):
	    self.__state = self.__state + 1
	    if self.__state <= SprinklerClass.__Max_num_of_sprinklers and rainOccured == False:
		#print "---------------ON :" + str(self.__state)
		if SprinklerClass.__break_auto_water == False:
		    self.setSprinklerOn(str(self.__state))
		else:
		    self.__autowater = False
		    SprinklerClass.__force_auto_water = False
	    else:
		self.setSprinklerOff()
		self.__autowater = False
		SprinklerClass.__force_auto_water = False

    def getSettings(self):
	config = ConfigClass.ConfigClass()
	jsonData = {}
	jsonData['duration'] = config.getDurationTime()
	jsonData['startTime'] = config.getStartTime()
	jsonData['globalEnable'] = config.getGlobalEnable()
	jsonData['day1'] = config.getLocalEnable(0)
	jsonData['day2'] = config.getLocalEnable(1)
	jsonData['day3'] = config.getLocalEnable(2)
	jsonData['day4'] = config.getLocalEnable(3)
	jsonData['day5'] = config.getLocalEnable(4)
	jsonData['day6'] = config.getLocalEnable(5)
	jsonData['day7'] = config.getLocalEnable(6)
	return jsonData
