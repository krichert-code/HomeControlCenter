import ConfigClass
import WeatherClass
import EventClass
import ActionThread
from datetime import datetime
import json


class HeaterParam(object):

    def __init__(self, tempInside, tempOutside, mode, isDay):
	self.tempInside = tempInside
	self.tempOutside = tempOutside
	self.mode = mode
	self.isDay = isDay
	self.date = datetime.now().strftime('%H:%M %d/%m/%y')

class HeaterClass(object):
    # static data
    __data = []
    __dayMode = False
    __lastState = -1
    # statistic - how long heater is on today
    __heaterOnToday = 0
    # State defines
    __StateOn      =  1
    __StateOff     =  0
    __StateUnknown = -1
    # Stored data buffer size - data to generate charts
    __maxDataBuffer = 50000
    # How offent data should be stored in buffer (more offten means shorter period displayed on chart)
    __storeDataInterval = 10
    # How many data should be used to generate 'WorkHeatChart' (every __lineChartInterval sample will be used) - more data means that chart will be generated slower
    __lineChartInterval = 24

    def __init__(self):
	self.__storeDataCounter = 0

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
	try:
	    temp = self.__getTemperatureFromDevice()

    	    heater['temp'] = "%.1f" % temp
    	    heater['time'] = datetime.now().strftime('%H:%M:%S')
    	    heater['icon'] = "img/day.gif"
	    if HeaterClass.__dayMode == False:
		heater['icon'] = "img/night.gif"
	except:
	    print "___________heater exception" 
        return heater

    def getHeaterStatistic(self):
	try:
    	    heaterStats = str(int(self.__heaterOnToday / 60)) + "h " + str(self.__heaterOnToday % 60) + "min"
	except:
	    print "___________heater exception" 
        return heaterStats

    def manageHeaterState(self, dayOfWeek, hour, minute):
		config = ConfigClass.ConfigClass()
		weather = WeatherClass.WeatherClass()
		threadTask = None

		dayTemp = float(config.getDayTemp())
		nightTemp = float(config.getNightTemp())
		threshold = float(config.geTempThreshold())

		isDayMode = config.isDayMode(dayOfWeek, hour)

		temp = self.__getTemperatureFromDevice()

		# new day - reset statistics
		if (hour == 0 and minute == 0):
		    self.__heaterOnToday = 0
		if (HeaterClass.__lastState == HeaterClass.__StateOn):
		    self.__heaterOnToday = self.__heaterOnToday + 1

		if HeaterClass.__dayMode != isDayMode:
			#if mode has changed set heater state as 'unknown'(-1)
			HeaterClass.__lastState = HeaterClass.__StateUnknown

		self.__storeDataCounter = self.__storeDataCounter + 1
		HeaterClass.__dayMode = isDayMode

		print "________State = " + str(HeaterClass.__lastState)
		print "Temp curr = " + str(temp) + "  Threshold " + str(threshold)
		print "DatMode = " + str(isDayMode)
		print "TEMP (day;night) = " + str(dayTemp) + "  ;  " + str(nightTemp)
		if (isDayMode == True and temp + threshold <= dayTemp) or (isDayMode == False and temp + threshold <= nightTemp):
			#turn on heater
			url = config.getSwitchURL("HeaterOn")
			if HeaterClass.__lastState == HeaterClass.__StateOff or HeaterClass.__lastState == HeaterClass.__StateUnknown:
				threadTask = ActionThread.ActionThread()
			HeaterClass.__lastState = HeaterClass.__StateOn
		elif (isDayMode == True and temp >= dayTemp + threshold) or (isDayMode == False and temp >= nightTemp + threshold) or (HeaterClass.__lastState == HeaterClass.__StateUnknown):
			#turn off heater
			url = config.getSwitchURL("HeaterOff")
			if HeaterClass.__lastState == HeaterClass.__StateOn or HeaterClass.__lastState == HeaterClass.__StateUnknown:
				threadTask = ActionThread.ActionThread()
			HeaterClass.__lastState = HeaterClass.__StateOff

		if threadTask <> None :
			threadTask.addTask("request", url)
			threadTask.addTask("delay", 2)
			threadTask.addTask("notify")
			threadTask.start()
			threadTask.suspend()

		# store data once per defined invokes (currently it means once per 10min) - not need so many data
		if self.__storeDataCounter % HeaterClass.__storeDataInterval == 0:
		    weatherData = weather.getCurrentWeather()
		    if not weatherData:
			tempOutside = 0
		    else:
			tempOutside = weatherData['temp']

		    HeaterClass.__data.append(HeaterParam(temp, tempOutside, HeaterClass.__lastState, isDayMode))
		    if (len(HeaterClass.__data) > HeaterClass.__maxDataBuffer):
			HeaterClass.__data.pop(0)

    def getPercentHeatWorkChart(self):
	nightItem = 0
	dayItem = 0
	notWorkItem = 0

	jsonData = {}
	jsonData['cols'] = []  
	jsonData['rows'] = []  

	jsonData['cols'].append({
	    'id':'',
	    'label':'Action',
	    'pattern':'',
	    'type':'string'
	})

	jsonData['cols'].append({
	    'id':'',
	    'label':'Percent',
	    'pattern':'',
	    'type':'number'
	})

	for item in HeaterClass.__data:
	    if item.mode == 0 or item.mode == -1:
		notWorkItem = notWorkItem + 1

	    if item.isDay == True and item.mode == 1:
		dayItem = dayItem + 1

	    if item.isDay == False and item.mode == 1:
		nightItem = nightItem + 1

	jsonData['rows'].append({'c':[ {'v':'Tyb dzienny','f':'Tyb dzienny'}, {'v': dayItem,'f':''}]  })
	jsonData['rows'].append({'c':[ {'v':'Tyb nocny','f':'Tyb nocny'}, {'v': nightItem,'f':''}]  })
	jsonData['rows'].append({'c':[ {'v':'Brak pracy','f':'Brak pracy'}, {'v': notWorkItem,'f':''}]  })


	return json.dumps(jsonData, indent=4)


    def getStateHeatWorkChart(self):
	counter = 0
	jsonData = {}
	jsonData['cols'] = []  
	jsonData['rows'] = []  

	jsonData['cols'].append({
	    'id':'',
	    'label':'Date',
	    'pattern':'',
	    'type':'string'
	})

	jsonData['cols'].append({
	    'id':'',
	    'label':'Temp.wew',
	    'pattern':'',
	    'type':'number'
	})

	jsonData['cols'].append({
	    'id':'',
	    'label':'Temp.zew',
	    'pattern':'',
	    'type':'number'
	})

	for item in HeaterClass.__data:
	    if counter % HeaterClass.__lineChartInterval == 0:
		jsonData['rows'].append({'c':[ {'v':item.date,'f':item.date}, {'v':item.tempInside,'f':str(item.tempInside)}, {'v':item.tempOutside,'f':str(item.tempOutside)}]  })
	    counter = counter + 1

#	jsonData['rows'].append({'c':[ {'v':'01.01.2019','f':'01.01.2019'}, {'v':20,'f':'20'}, {'v':5,'f':'5'}]  })
#	jsonData['rows'].append({'c':[ {'v':'01.01.2019','f':'01.01.2019'}, {'v':21,'f':'21'}, {'v':3,'f':'3'}]  })
#	jsonData['rows'].append({'c':[ {'v':'01.01.2019','f':'01.01.2019'}, {'v':21,'f':'21'}, {'v':3,'f':'3'}]  })
#	jsonData['rows'].append({'c':[ {'v':'01.01.2019','f':'01.01.2019'}, {'v':21,'f':'21'}, {'v':3,'f':'3'}]  })

	return json.dumps(jsonData, indent=4)

