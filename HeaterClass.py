import ConfigClass
import WeatherClass
import AlarmClass
import EventClass
import ActionThread
from datetime import datetime
import json
import traceback


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
    __data_per_day = []
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
	alarm = AlarmClass.AlarmClass()
	thermDevices = alarm.getTemperature()
	temperature = 22
	isTemepratureInit = False
	thermalElements = 1

	thermData = config.getFirstThermDevices()

	while (thermData['error'] == 0):
	    for item in thermDevices['temperature']:
		if thermData['name'] == item['name']:
	    	    tempValue = round(float(item['value']) + float(thermData['offset']), 2)

		    if (isTemepratureInit == False):
			temperature = tempValue
			isTemepratureInit = True
		    elif (thermData['mode'] == "max" and tempValue > temperature) or (thermData['mode'] == "min" and tempValue < temperature):
			temperature = tempValue
		    elif (thermData['mode'] == "avg") or (isTemepratureInit == False):
			temperature = (temperature + tempValue) / thermalElements

		    thermalElements = thermalElements +1
	    	    break
	    thermData = config.getNextThermDevices()

	return temperature


    def getCurrentTemperatureInside(self):
	heater = {}
	try:
	    temp = self.__getTemperatureFromDevice()
	    heater['status'] = "OK"
    	    heater['temp'] = "%.1f" % temp
    	    heater['time'] = datetime.now().strftime('%H:%M:%S')
    	    heater['icon'] = "img/day.gif"
	    heater['mode'] = "day"
	    if HeaterClass.__dayMode == False:
		heater['icon'] = "img/night.gif"
		heater['mode'] = "night"
	except Exception as e:
	    heater['status'] = "ERROR"
    	    heater['temp'] = "-"
    	    heater['time'] = "00:00:00"
    	    heater['icon'] = "img/day.gif"
	    heater['mode'] = "day"
	    print "___________heater exception 1"
            traceback.print_exc()

        return heater

    def getHeaterStatistic(self):
	try:
    	    heaterStats = str(int(HeaterClass.__heaterOnToday / 60)) + "h " + str(HeaterClass.__heaterOnToday % 60) + "min"
	except:
	    print "___________heater exception 2" 
        return heaterStats

    def manageHeaterState(self, dayOfWeek, hour, minute):
		config = ConfigClass.ConfigClass()
		weather = WeatherClass.WeatherClass()
		alarm = AlarmClass.AlarmClass()
		threadTask = None

		dayTemp = float(config.getDayTemp())
		nightTemp = float(config.getNightTemp())
		threshold = float(config.geTempThreshold())

		isDayMode = config.isDayMode(dayOfWeek, hour)

		temp = self.__getTemperatureFromDevice()

		# new day - reset statistics
		if (hour == 0 and minute == 0):
		    HeaterClass.__heaterOnToday = 0
		    HeaterClass.__data_per_day = []
		if (HeaterClass.__lastState == HeaterClass.__StateOn):
		    HeaterClass.__heaterOnToday = HeaterClass.__heaterOnToday + 1

		if HeaterClass.__dayMode != isDayMode:
			#if mode has changed set heater state as 'unknown'(-1)
			HeaterClass.__lastState = HeaterClass.__StateUnknown

		self.__storeDataCounter = self.__storeDataCounter + 1
		HeaterClass.__dayMode = isDayMode

		sensor = config.getDeviceSensors("heater")[0]

		if (isDayMode == True and temp + threshold <= dayTemp) or (isDayMode == False and temp + threshold <= nightTemp):
			#turn on heater
			url = alarm.getUpdateUrl(sensor[1],1)
			if HeaterClass.__lastState == HeaterClass.__StateOff or HeaterClass.__lastState == HeaterClass.__StateUnknown:
				threadTask = ActionThread.ActionThread()
				threadTask.addTask(ActionThread.Task("set", ActionThread.UpdateParam("heater",sensor[0])))
			HeaterClass.__lastState = HeaterClass.__StateOn
		elif (isDayMode == True and temp >= dayTemp + threshold) or (isDayMode == False and temp >= nightTemp + threshold) or (HeaterClass.__lastState == HeaterClass.__StateUnknown):
			#turn off heater
			url = alarm.getUpdateUrl(sensor[1],0)
			if HeaterClass.__lastState == HeaterClass.__StateOn or HeaterClass.__lastState == HeaterClass.__StateUnknown:
				threadTask = ActionThread.ActionThread()
				threadTask.addTask(ActionThread.Task("clear", ActionThread.UpdateParam("heater",sensor[0])))
			HeaterClass.__lastState = HeaterClass.__StateOff

		if threadTask <> None :
			threadTask.addTask(ActionThread.Task("request", ActionThread.RequestParam(url)))
			threadTask.addTask(ActionThread.Task("notify", ActionThread.NotifyParam()))
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
		    HeaterClass.__data_per_day.append(HeaterParam(temp, tempOutside, HeaterClass.__lastState, isDayMode))
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


    def getCharts(self):
	config = ConfigClass.ConfigClass()
	nightItem = 0
	dayItem = 0
	notWorkItem = 0
	nightItemPerDay = 0
	dayItemPerDay = 0
	notWorkItemPerDay = 0


	counter = 0

	jsonData = {}
	percentage = {}
	percentage_per_day = {}
	config_data = {}

	for item in HeaterClass.__data:
	    if item.mode == 0 or item.mode == -1:
		notWorkItem = notWorkItem + 1

	    if item.isDay == True and item.mode == 1:
		dayItem = dayItem + 1

	    if item.isDay == False and item.mode == 1:
		nightItem = nightItem + 1

	percentage['day'] = dayItem
	percentage['night'] = nightItem
	percentage['off'] = notWorkItem
	jsonData['percentage'] = percentage

	for item in HeaterClass.__data_per_day:
	    if item.mode == 0 or item.mode == -1:
		notWorkItemPerDay = notWorkItemPerDay + 1

	    if item.isDay == True and item.mode == 1:
		dayItemPerDay = dayItemPerDay + 1

	    if item.isDay == False and item.mode == 1:
		nightItemPerDay = nightItemPerDay + 1

	percentage_per_day['day'] = dayItemPerDay
	percentage_per_day['night'] = nightItemPerDay
	percentage_per_day['off'] = notWorkItemPerDay
	jsonData['percentagePerDay'] = percentage_per_day

	temp = []
	for item in HeaterClass.__data:
	    if counter % HeaterClass.__lineChartInterval == 0:
		#jsonData['rows'].append({'c':[ {'v':item.date,'f':item.date}, {'v':item.tempInside,'f':str(item.tempInside)}, {'v':item.tempOutside,'f':str(item.tempOutside)}]  })
		value = {}
		value['inside'] = item.tempInside
		value['outside'] = item.tempOutside
		value['date'] = item.date
		temp.append(value)
	    counter = counter + 1
	jsonData['temp'] = temp

	config_data['dayTemp'] = float(config.getDayTemp())
	config_data['nightTemp'] = float(config.getNightTemp())
	config_data['threshold'] = float(config.geTempThreshold())
	config_data['day1'] = int(config.getDayModeSettings(0))
	config_data['day2'] = int(config.getDayModeSettings(1))
	config_data['day3'] = int(config.getDayModeSettings(2))
	config_data['day4'] = int(config.getDayModeSettings(3))
	config_data['day5'] = int(config.getDayModeSettings(4))
	config_data['day6'] = int(config.getDayModeSettings(5))
	config_data['day7'] = int(config.getDayModeSettings(6))
	jsonData['settings'] = config_data


	return jsonData