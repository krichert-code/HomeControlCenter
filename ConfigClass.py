from xml.dom import minidom
from collections import OrderedDict
import EventClass
import hashlib
import datetime
import ActionThread
import AlarmClass
import threading

class SettingElementClass(object):
    def __init__(self,name, title, type, param, value):
	xml = ""
	self.name = name
	self.title = title
	self.type = type
	self.value = value
	self.param = param

	if type=="text":
	    doc = minidom.Document()
	    element = doc.createElement('input')
	    element.setAttribute("name", name)
	    element.setAttribute("type", "text")
	    if param <> "md5":
		element.setAttribute("value", value)
	    element.setAttribute("class", "form")
	    doc.appendChild(element)

	if type=="bitfield":
	    doc = minidom.Document()
	    element = doc.createElement('root')
	    doc.appendChild(element)
	    bits = int(value)
	    bit_number = 0
	    while bit_number < int(param):
		element = doc.createElement('input')
		element.setAttribute("name", name)
		element.setAttribute("type", "checkbox")
		if bits & (1 << bit_number) != 0:
		    element.setAttribute("checked", "1")
		element.setAttribute("class", "form")
		doc.firstChild.appendChild(element)
		bit_number=bit_number+1

	    
	if type=="select":
	    doc = minidom.Document()
	    select = doc.createElement('select')
	    select.setAttribute("class", "form")
	    select.setAttribute("name", name)
	    while len(param) > 0:
		idx = param.find(";")
		idx_desc = param.find(",")
		if idx_desc == -1:
		    idx_desc=len(param)
		choice_element = param[:idx]
		choice_desc = param[idx+1:idx_desc]
		param = param[idx_desc+1:]
		option = doc.createElement('option')
		option.setAttribute("value", choice_element)
		if (value == choice_element):
		    option.setAttribute("selected", "selected")
		option.appendChild(doc.createTextNode(choice_desc))
		select.appendChild(option)
	    doc.appendChild(select)
	    
	xml = doc.toxml()
	self.xml = xml[xml.find("?>")+2:]






class ConfigClass(object):
    __xmldoc = None
    __mutex = None

    def __init__(self):
        self.iterator = 0
	if ConfigClass.__mutex == None:
            ConfigClass.__mutex = threading.Lock()

        if ConfigClass.__xmldoc == None:
            ConfigClass.__xmldoc = minidom.parse('data/config.xml')
            
    def initializeConfigData(self):
            # clear statuses
            pass
            
    def getHccId(self):
	id = ConfigClass.__xmldoc.getElementsByTagName('HomeControlCenter')[0].getAttribute('id')
	return id

    def getHccPassword(self):
	passwd = ConfigClass.__xmldoc.getElementsByTagName('HomeControlCenter')[0].getAttribute('password')
	return passwd

    def getHccServer(self):
	server = ConfigClass.__xmldoc.getElementsByTagName('HomeControlCenter')[0].getAttribute('server')
	return server
        
    def getRadioURL(self,name):
        for item in ConfigClass.__xmldoc.getElementsByTagName('radio')[0].getElementsByTagName('element'):
            if item.getAttribute('name') == name:
                break
        return item.getAttribute('url');
                                
    def getRadioSettings(self):
        ip = ConfigClass.__xmldoc.getElementsByTagName('radio')[0].getAttribute('ip')
        port = ConfigClass.__xmldoc.getElementsByTagName('radio')[0].getAttribute('port')
        device = ip + ":" + port 
        return device

    def getRadioStationsName(self):
        names = []                
        for item in ConfigClass.__xmldoc.getElementsByTagName('radio')[0].getElementsByTagName('element'):
            names.append(item.getAttribute('name'))            
        return names

    def getAlarmSetting(self, name):
        return ConfigClass.__xmldoc.getElementsByTagName('alarm')[0].getElementsByTagName(name)[0].getAttribute('value')

    def getRooms(self):
	rooms = []
        for item in ConfigClass.__xmldoc.getElementsByTagName('rooms')[0].getElementsByTagName('room'):
	    room = {}
	    room['id'] = item.getAttribute('id')
	    room['name'] = item.getAttribute('name')
	    room['light_ip'] = item.getAttribute('light')
	    room['tempId'] = item.getAttribute('temperature')

	    room['alarmSensors'] = []
	    for alarmItem in item.getElementsByTagName('alarmSensor'):
		room['alarmSensors'].append( alarmItem.getAttribute("sensorName") )

            rooms.append(room)
        return rooms

    def getAlarmSystem(self):
	alarm = {}
	data = ConfigClass.__xmldoc.getElementsByTagName('AlarmSystem')[0]
	alarm['ip'] = data.getAttribute('ip')
	alarm['port'] = data.getAttribute('port')
	return alarm

#-------------------------- Calendar settings --------------------------
    def getCalendarKey(self):
        return ConfigClass.__xmldoc.getElementsByTagName('calendar')[0].getElementsByTagName('key')[0].getAttribute('value')

    def getCalendarsList(self):
        names = []
        for item in ConfigClass.__xmldoc.getElementsByTagName('calendar')[0].getElementsByTagName('calendars_list')[0].getElementsByTagName('element'):
            names.append(item.getAttribute('name'))
        return names

    def getCalendarRange(self):
        return int(ConfigClass.__xmldoc.getElementsByTagName('calendar')[0].getElementsByTagName('range')[0].getAttribute('value'))

    def getCalendarReminderTime(self):
        return ConfigClass.__xmldoc.getElementsByTagName('calendar')[0].getElementsByTagName('sms')[0].getAttribute('sendTime')

    def getCalendarReminderEnabled(self):
        if ConfigClass.__xmldoc.getElementsByTagName('calendar')[0].getElementsByTagName('sms')[0].getAttribute('value') == "True":
	    return True
	else:
	    return False
#-------------------------- Calendar settings --------------------------

    def getCurrentWeatherReq(self):
        return ConfigClass.__xmldoc.getElementsByTagName('weather')[0].getElementsByTagName('current')[0].getAttribute('url')

    def getHourlyWeatherForecastReq(self):
        return ConfigClass.__xmldoc.getElementsByTagName('weather')[0].getElementsByTagName('hourly')[0].getAttribute('url')

    def getDailyWeatherForecastReq(self):
        return ConfigClass.__xmldoc.getElementsByTagName('weather')[0].getElementsByTagName('daily')[0].getAttribute('url')

    def getDS18B20file(self):
	return ConfigClass.__xmldoc.getElementsByTagName('ds18b20')[0].getElementsByTagName('device')[0].getAttribute('file')

    def getDS18B20offset(self):
	return ConfigClass.__xmldoc.getElementsByTagName('ds18b20')[0].getElementsByTagName('offset')[0].getAttribute('value')


    def getlocalIPmask(self):
	return ConfigClass.__xmldoc.getElementsByTagName('passwd')[0].getAttribute('localIPmask')

    def getmd5passwd(self):
	return ConfigClass.__xmldoc.getElementsByTagName('passwd')[0].getElementsByTagName('md5')[0].getAttribute('value')


#-------------------------- Sprinkler settings --------------------------
    def getDurationTime(self):
	return ConfigClass.__xmldoc.getElementsByTagName('autowater')[0].getElementsByTagName('duration')[0].getAttribute('value')

    def checkRainOccured(self):
        if ConfigClass.__xmldoc.getElementsByTagName('autowater')[0].getElementsByTagName('rain')[0].getAttribute('value') == "True":
	    return True
	else:
	    return False

    def getStartTime(self):
	return ConfigClass.__xmldoc.getElementsByTagName('autowater')[0].getElementsByTagName('start_time')[0].getAttribute('value')

    def getGlobalEnable(self):
	globalEnableState = ConfigClass.__xmldoc.getElementsByTagName('autowater')[0].getElementsByTagName('state')[0].getAttribute('value')
	if (globalEnableState == "disable"):
	    return 0
	else:
	    return 1

    def getLocalEnable(self, dayNumber):
	tag = "day"+ str(dayNumber+1)
	activeDay = ConfigClass.__xmldoc.getElementsByTagName('autowater')[0].getElementsByTagName(tag)[0].getAttribute('value')
	if (activeDay == "False"):
	    return 0
	else:
	    return 1

    def isStartTime(self, dayNumber, hour, minute):
	globalEnableState = ConfigClass.__xmldoc.getElementsByTagName('autowater')[0].getElementsByTagName('state')[0].getAttribute('value')
	tag = "day"+ str(dayNumber+1)
	activeDay = ConfigClass.__xmldoc.getElementsByTagName('autowater')[0].getElementsByTagName(tag)[0].getAttribute('value')
	start_time = ConfigClass.__xmldoc.getElementsByTagName('autowater')[0].getElementsByTagName('start_time')[0].getAttribute('value')

	try:
	    if (globalEnableState == "disable" or (globalEnableState == "enable" and activeDay == "False")):
		result = False
	    else:
		if hour == int(start_time[:start_time.find(':')]) and minute == int(start_time[start_time.find(':')+1:]):
	    	    result = True
		else:
		    result = False
	except:
	    result = False
	
	return result
#-------------------------- Sprinkler settings --------------------------

#-------------------------- Heater settings -----------------------------
    def getThermMode(self):
        return ConfigClass.__xmldoc.getElementsByTagName('heater')[0].getElementsByTagName('thermometer')[0].getAttribute('mode')

    def getFirstThermDevices(self):
        self.iterator = 0
	data = {}
	try:
	    data['error']  = 0
	    data['mode']   = ConfigClass.__xmldoc.getElementsByTagName('heater')[0].getElementsByTagName('thermometer')[0].getAttribute('mode')
	    data['name']   = ConfigClass.__xmldoc.getElementsByTagName('heater')[0].getElementsByTagName('thermometer')[0].getElementsByTagName('device')[0].getAttribute('name')
	    data['offset'] = ConfigClass.__xmldoc.getElementsByTagName('heater')[0].getElementsByTagName('thermometer')[0].getElementsByTagName('device')[0].getAttribute('offset')
	except:
	    data['error']  = 255
	    data['name']   = ""
	    data['offset'] = ""
	    data['mode']   = ""
        return data

    def getNextThermDevices(self):
        self.iterator = self.iterator + 1
	data = {}
	try:
	    data['error'] = 0
	    data['mode']   = ConfigClass.__xmldoc.getElementsByTagName('heater')[0].getElementsByTagName('thermometer')[0].getAttribute('mode')
	    data['name'] = ConfigClass.__xmldoc.getElementsByTagName('heater')[0].getElementsByTagName('thermometer')[0].getElementsByTagName('device')[self.iterator].getAttribute('name')
	    data['offset'] = ConfigClass.__xmldoc.getElementsByTagName('heater')[0].getElementsByTagName('thermometer')[0].getElementsByTagName('device')[self.iterator].getAttribute('offset')
	except:
	    data['error']  = 255
	    data['name']   = ""
	    data['offset'] = ""
	    data['mode']   = ""
	return data

    def getDayTemp(self):
	return ConfigClass.__xmldoc.getElementsByTagName('HomeControlCenter')[0].getElementsByTagName('heater')[0].getElementsByTagName('day_temperature')[0].getAttribute('value')

    def geTempThreshold(self):
        return ConfigClass.__xmldoc.getElementsByTagName('heater')[0].getElementsByTagName('threshold')[
            0].getAttribute('value')

    def getNightTemp(self):
	return ConfigClass.__xmldoc.getElementsByTagName('heater')[0].getElementsByTagName('night_temperature')[0].getAttribute('value')

    def getDayModeSettings(self, dayNumber):
	tag = "day"+ str(dayNumber+1)
	hours = int(ConfigClass.__xmldoc.getElementsByTagName('heater')[0].getElementsByTagName(tag)[0].getAttribute('value'))
	return hours

    def isDayMode(self,dayNumber, hour):
	tag = "day"+ str(dayNumber+1)
	hours = int(ConfigClass.__xmldoc.getElementsByTagName('heater')[0].getElementsByTagName(tag)[0].getAttribute('value'))
	if (hours & (1 << hour) != 0):
	    return True
	else:
	    return False
#-------------------------- Heater settings -----------------------------

#---------------------------Settings method -----------------------------
    def __getSettings(self, pageId = -1):
	settingsData = OrderedDict()
	settingsData['alarm']     = { "id":"0", "icon":"alarm.png", "icon_size":"30", "nodes":['start_time', 'stop_time', 'radio', 'channel', 'day_policy' ,'volume'] }
	settingsData['heater']    = { "id":"1", "icon":"piec.png", "icon_size":"30", "nodes":['day_temperature', 'night_temperature', 'threshold', 'day1', 'day2', 'day3', 'day4', 'day5', 'day6', 'day7'] }
	settingsData['autowater'] = { "id":"2", "icon":"garden.png", "icon_size":"30", "nodes":['state','start_time', 'duration', 'rain', 'day1', 'day2', 'day3', 'day4', 'day5', 'day6', 'day7'] }
	settingsData['calendar'] = { "id":"3", "icon":"calendar.png", "icon_size":"30", "nodes":['range','sms'] }
	settingsData['passwd'] = { "id":"4", "icon":"gate.png", "icon_size":"30", "nodes":['md5'] }

	#change icon size for active page setting
	for element_name in settingsData:
	    settingElement = settingsData[element_name]
	    if int(settingElement['id']) == pageId:
		settingElement['icon_size'] = "60"
		break

	return settingsData

    def __getSettingPage(self,pageId):
	#find element by pageId
	settingsData = self.__getSettings()
	settingElement = None

	for element_name in settingsData:
	    settingElement = settingsData[element_name]
	    if int(settingElement['id']) == pageId:
		break;
	return element_name, settingElement

    def __getSettingElements(self,pageId):
	elements = []
	element_name,settingElement = self.__getSettingPage(pageId)
	if settingElement <> None:
	    for node_name in settingElement['nodes']:
		node = ConfigClass.__xmldoc.getElementsByTagName(element_name)[0].getElementsByTagName(node_name)[0]
		elements.append(SettingElementClass(node_name, node.getAttribute('title'), node.getAttribute('type'), node.getAttribute('param'), node.getAttribute('value') ))
	return elements



    def saveSettingsData(self, pageId, data):
	element_name,settingElement = self.__getSettingPage(pageId)
	for key, value in data.iteritems():
	    try:
		item = ConfigClass.__xmldoc.getElementsByTagName(element_name)[0].getElementsByTagName(key)[0]

		if item.getAttribute('param') == "md5":
		    value = hashlib.md5(value).hexdigest()

		item.setAttribute("value", value)
	    except:
		pass
	ConfigClass.__xmldoc.writexml( open('data/config.xml', 'w'))

    def getSettingsData(self, pageId):
	data = {}

	settingsData = self.__getSettings(pageId)
	elements   = self.__getSettingElements(pageId)

	data['settings'] = settingsData
	data['html_elements']  = elements

	return data
#---------------------------Settings method -----------------------------

#---------------------------MP3 method ----------------------------------
    def getMp3Directory(self):
	return ConfigClass.__xmldoc.getElementsByTagName('radio')[0].getAttribute('mp3_directory')
#---------------------------MP3 method ----------------------------------


#---------------------------text message method --------------------------
    def getPhoneNumbers(self):
	phones = []
	for item in ConfigClass.__xmldoc.getElementsByTagName('text_messages')[0].getElementsByTagName('phones')[0].getElementsByTagName('element'):
	    phones.append(item.getAttribute('number'))
	return phones

    def getSmsToken(self):
	return ConfigClass.__xmldoc.getElementsByTagName('text_messages')[0].getElementsByTagName('token')[0].getAttribute('value')

    def getSmsMessage(self, id, state):
	message = ""
	tag = "active"
	if state == "0":
	    tag = "inactive"
	for item in ConfigClass.__xmldoc.getElementsByTagName('text_messages')[0].getElementsByTagName('text')[0].getElementsByTagName('element'):
	    if item.getAttribute('id') == id:
		message = item.getElementsByTagName(tag)[0].getAttribute('message')
		break
	return message
#---------------------------text message method --------------------------



#---------------------------Generic config methods ----------------------
    def __createEventsRecord(self, itemsList, id, type, onlyActiveEvents = True):
	eventsData = []
	ConfigClass.__mutex.acquire()
	for item in itemsList:
            if (item.getAttribute('state') == "1" and onlyActiveEvents == True) or (onlyActiveEvents == False):
		event = EventClass.EventClass(item.getAttribute('desc'),"",id, item.getAttribute('state'))		
		event.type = type
		try:
		    event.messageId = item.getAttribute('messageId')
		except:
		    event.messageId = -1
		
		eventsData.append(event)
	ConfigClass.__mutex.release()
	return eventsData
    
    
    def getEvents(self, id, onlyActiveEvents = True):
        eventsData = []

        itemsList = ConfigClass.__xmldoc.getElementsByTagName('devices')[0].getElementsByTagName('status')[0].getElementsByTagName('element')                    
        eventsData = eventsData +  self.__createEventsRecord(itemsList, id, "status", onlyActiveEvents)

        itemsList = ConfigClass.__xmldoc.getElementsByTagName('devices')[0].getElementsByTagName('gate')[0].getElementsByTagName('element')                    
        eventsData = eventsData +  self.__createEventsRecord(itemsList, id, "gate", onlyActiveEvents)

        itemsList = ConfigClass.__xmldoc.getElementsByTagName('devices')[0].getElementsByTagName('heater')[0].getElementsByTagName('element')                    
        eventsData = eventsData +  self.__createEventsRecord(itemsList, id, "heater", onlyActiveEvents)

        itemsList = ConfigClass.__xmldoc.getElementsByTagName('devices')[0].getElementsByTagName('sprinkler')[0].getElementsByTagName('element')                    
        eventsData = eventsData +  self.__createEventsRecord(itemsList, id, "sprinkler", onlyActiveEvents)
        
        return eventsData


    def changeStatus(self, type, id, value):
        ret_val = 0
	ConfigClass.__mutex.acquire()
        itemsList = ConfigClass.__xmldoc.getElementsByTagName('devices')[0].getElementsByTagName(type)[0].getElementsByTagName('element')
        for item in itemsList:
            if item.getAttribute('id') == id:
		item.setAttribute("state", value)
                break
	ConfigClass.__mutex.release()

    def getDeviceSensor(self, type, id):
        ret_val = ""
	ConfigClass.__mutex.acquire()
        itemsList = ConfigClass.__xmldoc.getElementsByTagName('devices')[0].getElementsByTagName(type)[0].getElementsByTagName('element')
        for item in itemsList:
            if item.getAttribute('id') == id:
		ret_val = item.getAttribute("sensor")
		break
	ConfigClass.__mutex.release()
	return ret_val

    def getDeviceSensors(self, type):
        ret_val = []
	ConfigClass.__mutex.acquire()
        itemsList = ConfigClass.__xmldoc.getElementsByTagName('devices')[0].getElementsByTagName(type)[0].getElementsByTagName('element')
        for item in itemsList:            
		ret_val.append( (item.getAttribute("id"),item.getAttribute("sensor")))
	ConfigClass.__mutex.release()
	return ret_val

    def getStatus(self, type, id):
        ret_val = "-1"
	ConfigClass.__mutex.acquire()
        itemsList = ConfigClass.__xmldoc.getElementsByTagName('devices')[0].getElementsByTagName(type)[0].getElementsByTagName('element')
        for item in itemsList:
            if item.getAttribute('id') == id:
		ret_val = item.getAttribute("state")
		break
	ConfigClass.__mutex.release()
	return ret_val

    def getDeviceSensorActionDuration(self, type, id):
        ret_val = 0
	ConfigClass.__mutex.acquire()
        itemsList = ConfigClass.__xmldoc.getElementsByTagName('devices')[0].getElementsByTagName(type)[0].getElementsByTagName('element')
        for item in itemsList:
            if item.getAttribute('id') == id:
		ret_val = int(item.getAttribute("time"))
		break
	ConfigClass.__mutex.release()
	return ret_val


#---------------------------Generic config methods ----------------------