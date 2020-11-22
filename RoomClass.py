import ConfigClass
import SwitchClass
import AlarmClass

class RoomClass:
    def __init__(self):
        pass

    def getRoomsData(self):
            config = ConfigClass.ConfigClass()
	    switch = SwitchClass.SwitchClass()
	    alarm = AlarmClass.AlarmClass()

            roomsObj = {}
	    rooms = []

	    temperature = alarm.getTemperature()
	    alerts = alarm.getAlerts()
	    presence = alarm.getPresence()

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

		roomAlarm['state'] = "0"
		roomAlarm['presence'] = "0"
		roomAlarm['alert'] = "0"
		roomAlarm['present'] = 0
		for alarmSensor in item['alarmSensors']:
		    for alarmItem in alerts['alerts']:	    
			if alarmItem['name'] == alarmSensor and roomAlarm['alert'] == "0":
			    roomAlarm['state'] = alarmItem['alert']
			    roomAlarm['alert'] = alarmItem['alert']

		    for presenceItem in presence['presence']:	    
		        if presenceItem['name'] == alarmSensor and roomAlarm['presence'] == "0":
			    roomAlarm['presence'] = presenceItem['presence']

		    if alarmItem['name'] == alarmSensor:
			roomAlarm['present'] = 1


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

		roomParams['light'] = roomlight
		roomParams['alarm'] = roomAlarm
		roomParams['temperature'] = roomTemp
		rooms.append(roomParams)

	    roomsObj['rooms'] = rooms
	    return roomsObj