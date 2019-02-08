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
    __StateOn      =  1
    __StateOff     =  0
    __StateUnknown = -1

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
        heater['time'] = datetime.now().strftime('%H:%M:%S')
        heater['icon'] = "img/day.gif"
	if HeaterClass.__dayMode == False:
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

		if HeaterClass.__dayMode != isDayMode:
			#if mode has changed set heater state as 'unknown'(-1)
			HeaterClass.__lastState = HeaterClass.__StateUnknown

		HeaterClass.__dayMode = isDayMode

		print "________State = " + str(HeaterClass.__lastState)
		print "Temp curr = " + str(temp) + "  Threshold " + str(threshold)
		print "DatMode = " + str(isDayMode)
		print "TEMP = " + str(dayTemp) + "  ;  " + str(nightTemp)
		if (isDayMode == True and temp + threshold <= dayTemp) or (isDayMode == False and temp + threshold <= nightTemp):
			#turn on heater
			url = config.getSwitchURL("HeaterOn")
			if isDayMode == True:
				val = dayTemp + threshold
				desc = "Piec w trybie dziennym ["+ str(val) +"]"
			else:
				val = nightTemp + threshold
				desc = "Piec w trybie nocnym ["+ str(val) +"]"
			status = "set"
			if HeaterClass.__lastState == HeaterClass.__StateOff or HeaterClass.__StateUnknown:
				threadTask = ActionThread.ActionThread()
			HeaterClass.__lastState = HeaterClass.__StateOn
		elif (isDayMode == True and temp >= dayTemp + threshold) or (isDayMode == False and temp >= nightTemp + threshold) or (HeaterClass.__lastState == HeaterClass.__StateUnknown):
			#turn off heater
			url = config.getSwitchURL("HeaterOff")
			desc = "No action"
			status = "clear"
			if HeaterClass.__lastState == HeaterClass.__StateOn or HeaterClass.__lastState == HeaterClass.__StateUnknown:
				threadTask = ActionThread.ActionThread()
			HeaterClass.__lastState = HeaterClass.__StateOff

		if threadTask <> None :
			threadTask.addTask("request", url)
			threadTask.addTask(status, "heater", desc)
			threadTask.addTask("notify")
			threadTask.start()
			threadTask.suspend()

		weatherData = weather.getCurrentWeather()
		HeaterClass.__data.append(HeaterParam(temp, weatherData['temp'], HeaterClass.__lastState))
		if (len(HeaterClass.__data) > 10000):
		    HeaterClass.__data.pop(0)
