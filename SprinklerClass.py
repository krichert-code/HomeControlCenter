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

    def setForceAutoWater(self):
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
	SprinklerClass.__force_auto_water = False
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
	    if (config.isStartTime(curr_week_day, curr_hour, curr_min) or SprinklerClass.__force_auto_water):
		self.__autowater = True
	    else:
		self.__autowater = False

	    self.__timestamp = currentTS
	    SprinklerClass.__break_auto_water = False
	
	if self.__autowater == True and ( currentTS >= self.__timestamp + (self.__state * duration) ):
	    self.__state = self.__state + 1
	    if self.__state <= SprinklerClass.__Max_num_of_sprinklers and rainOccured == False:
		#print "---------------ON :" + str(self.__state)
		if SprinklerClass.__break_auto_water == False:
		    self.setSprinklerOn(str(self.__state))
	    else:
		self.setSprinklerOff()
		#print "---------------OFF------------"
		self.__autowater = False
		self.__state = 0
		SprinklerClass.__force_auto_water = False

	    

