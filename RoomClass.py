import ConfigClass
import SwitchClass
import AlarmClass
import WeatherClass

class RoomClass:
    def __init__(self):
        pass

    def getRoomsData(self):
            config = ConfigClass.ConfigClass()
	    switch = SwitchClass.SwitchClass()
	    alarm = AlarmClass.AlarmClass()
	    weather = WeatherClass.WeatherClass()
	    tempOut = weather.getCurrentWeather()['temp']

            roomsObj = {}
	    rooms = []

	    temperature = alarm.getTemperature()
	    alerts = alarm.getAlerts()
	    presence = alarm.getPresence()
	    roomsObj['error']  = 0

	    for item in config.getRooms():
		roomParams = {}
		roomlight = {}
		roomAlarm = {}
		roomTemp = {}
		roomPresence = {}

		roomParams['id'] = item['id']
		roomParams['name']  = item['name']

		roomlight['light_ip'] = item['light_ip']
		data =  switch.getSwitchInfo(item['light_ip'])
		if data['error'] == 0:
		    roomlight['light_state'] = data['data']['switch']
		    roomlight['light_present'] = 1
		else:
		    roomlight['light_state'] = "off"
		    roomlight['light_present'] = 0

		roomAlarm['presence'] = "off"
		roomAlarm['alert'] = "off"
		roomAlarm['present'] = 0
		try:
		    for alarmSensor in item['alarmSensors']:
			for alarmItem in alerts['alerts']:	    
			    if alarmItem['name'] == alarmSensor and roomAlarm['alert'] == "off":
				roomAlarm['alert'] = alarmItem['alert']
				roomAlarm['present'] = 1

			for presenceItem in presence['presence']:	    
		    	    if presenceItem['name'] == alarmSensor and roomAlarm['presence'] == "off":
				roomAlarm['presence'] = presenceItem['presence']
				roomAlarm['present'] = 1

		except:
		    roomsObj['error']  = 255

		roomTemp['id'] = item['tempId']
		roomTemp['temperature'] = ""
		roomTemp['thresholdExceeded'] = "no"
		roomTemp['present'] = 0
		for tempItem in temperature['temperature']:
		    if tempItem['name'] == item['tempId']:
			roomTemp['temperature'] = tempItem['value'][:tempItem['value'].find(".")+2]
			roomTemp['thresholdExceeded'] = tempItem['thresholdExceeded']
			roomTemp['present'] = 1
			break

		if item['tempId'] == "weather":
			roomTemp['temperature'] = tempOut
			roomTemp['thresholdExceeded'] = "no"
			roomTemp['present'] = 1


		roomParams['light'] = roomlight
		roomParams['alarm'] = roomAlarm
		roomParams['temperature'] = roomTemp
		rooms.append(roomParams)

	    roomsObj['rooms'] = rooms
	    return roomsObj