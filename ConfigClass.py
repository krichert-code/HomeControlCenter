from xml.dom import minidom
import EventClass


class ConfigClass(object):
    __xmldoc = None
    
    
    def __init__(self):
        if ConfigClass.__xmldoc == None:
            ConfigClass.__xmldoc = minidom.parse('data/config.xml')
            
    def initializeConfigData(self):
            # clear statuses
            itemsList = ConfigClass.__xmldoc.getElementsByTagName('status')[0].getElementsByTagName('element')
            for item in itemsList:
                    item.setAttribute("state","0")
            ConfigClass.__xmldoc.writexml( open('data/config.xml', 'w'))
            
    def getSwitchURL(self,name):
        ip = ConfigClass.__xmldoc.getElementsByTagName('switch')[0].getAttribute('ip')
        url = ConfigClass.__xmldoc.getElementsByTagName('switch')[0].getElementsByTagName(name)[0].getAttribute('url')
        url = "http://"+ ip + url
        return url

    def getSwitchItemDesc(self, name):
        return ConfigClass.__xmldoc.getElementsByTagName('switch')[0].getElementsByTagName(name)[0].getAttribute('desc')
        
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

    def getCalendarKey(self):
        return ConfigClass.__xmldoc.getElementsByTagName('calendar')[0].getElementsByTagName('key')[0].getAttribute('value')

    def getCalendarsList(self):
        names = []
        for item in ConfigClass.__xmldoc.getElementsByTagName('calendar')[0].getElementsByTagName('calendars_list')[0].getElementsByTagName('element'):
            names.append(item.getAttribute('name'))
        return names

    def getCalendarRange(self):
        return int(ConfigClass.__xmldoc.getElementsByTagName('calendar')[0].getElementsByTagName('range')[0].getAttribute('value'))

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

    def getEvent(self, name):
        xmldoc = minidom.parse('data/config.xml')
        eventData = None
        itemsList = xmldoc.getElementsByTagName('status')[0].getElementsByTagName('element')        
        for item in itemsList:
	    if item.getAttribute('name') == name:
		break
	return EventClass.EventClass(item.getAttribute('desc'),"",item.getAttribute('name'), item.getAttribute('state'))

    def getEvents(self, id, onlyActiveEvents = True):
        xmldoc = minidom.parse('data/config.xml')
        eventsData = []
        itemsList = xmldoc.getElementsByTagName('status')[0].getElementsByTagName('element')        
        for item in itemsList:
            if (item.getAttribute('state') == "1" and onlyActiveEvents == True) or (onlyActiveEvents == False):
                eventsData.append(EventClass.EventClass(item.getAttribute('desc'),"",id, item.getAttribute('state')))                
        return eventsData


    def changeStatus(self, name, value, desc = ""):
	ret_val = "Conf_Change_ok"

	xmldoc = minidom.parse('data/config.xml')
	itemsList = xmldoc.getElementsByTagName('status')[0].getElementsByTagName('element')
        for item in itemsList:
            if item.getAttribute('name') == name:
                break

	if item.getAttribute("state") <> value:
	    item.setAttribute("state", value)
	    if len(desc) > 0:
		item.setAttribute("desc", desc)
	    xmldoc.writexml( open('data/config.xml', 'w'))
	else:
	    ret_val = "Conf_Change_already_in_progress"

	return ret_val

