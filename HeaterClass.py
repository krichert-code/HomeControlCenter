import ConfigClass
import WeatherClass
import EventClass
import ActionThread
from datetime import datetime


class HeaterParam(object):

    def __init__(self, tempInside, tempOutside, mode):
	self.tempInside = tempInside
	self.tempOutside = tempOutside
	self.mode = mode

class HeaterClass(object):
    __lastState = -1
    __dayMode = False
    __data = []

    def __init__(self):
        pass


    def __getTemperatureFromDevice(self):
	config = ConfigClass.ConfigClass()

	#todo: get temperature depands on mode (min,max)
	devFile, offset = config.getFirstThermDevices()

        file = open(devFile, "rb")
        for line in file:
	    pass
        
	temp = int(line[line.find("=")+1:])/1000.0
	temp = temp + int(offset)
	return temp


    def getCurrentTemperatureInside(self):
	heater = {}
	temp = self.__getTemperatureFromDevice()

        heater['temp'] = "%.1f" % temp
#        heater['state'] = "0"
#        heater['mode'] = "1"
        heater['time'] = datetime.now().strftime('%H:%M:%S')
#        heater['heat_state_icon'] = "img/piec_on1.gif"
        heater['icon'] = "img/day.gif"
	if HeaterClass.dayMode == False:
	    heater['icon'] = "img/night.gif"
        return heater


    def manageHeaterState(self, dayOfWeek, hour):
		config = ConfigClass.ConfigClass()
		weather = WeatherClass.WeatherClass()
		threadTask = None

		dayTemp = float(config.getDayTemp())
		nightTemp = float(config.getNightTemp())
		threshold = float(config.geTempThreshold())

		isDayMode = config.isDayMode(dayOfWeek, hour)

		temp = self.__getTemperatureFromDevice()

		HeaterClass.dayMode = isDayMode

		if (isDayMode == True and temp + threshold <= dayTemp) or (isDayMode == False and temp + threshold <= nightTemp):
			#turn on heater
			url = config.getSwitchURL("HeaterOn")
			if isDayMode:
				desc = "Piec w trybie dziennym"
			else:
				desc = "Piec w trybie nocnym"
			status = "set"
			if HeaterClass.__lastState == 0 or HeaterClass.__lastState == -1:
				threadTask = ActionThread.ActionThread()
			HeaterClass.__lastState = 1
		elif (isDayMode == True and temp >= dayTemp + threshold) or (isDayMode == False and temp >= nightTemp + threshold):
			#turn off heater
			url = config.getSwitchURL("HeaterOff")
			desc = "No action"
			status = "clear"
			if HeaterClass.__lastState == 1 or HeaterClass.__lastState == -1:
				threadTask = ActionThread.ActionThread()
			HeaterClass.__lastState = 0

		if threadTask <> None :
			threadTask.addTask("request", url)
			threadTask.addTask(status, "heater", desc)
			threadTask.addTask("notify")
			threadTask.start()
			threadTask.suspend()
			print "_____PIEC zmiana stanu"

		weatherData = weather.getCurrentWeather()
		HeaterClass.__data.append(HeaterParam(temp, weatherData['temp'], HeaterClass.__lastState))
		if (len(HeaterClass.__data) > 10000):
		    HeaterClass.__data.pop(0)

		print "_____________TEMP = " + str(temp)
		print "_____________DEY_TEMP " + str(dayTemp)
		print "_____________" + str(dayOfWeek) + " " + str(hour)
		print "________IS DAY MODE " + str(isDayMode)



