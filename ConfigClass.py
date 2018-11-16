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

    def getEvent(self, name):
        xmldoc = minidom.parse('data/config.xml')
        eventData = None
        itemsList = xmldoc.getElementsByTagName('status')[0].getElementsByTagName('element')        
        for item in itemsList:
	    if item.getAttribute('name') == name:
		break
	return EventClass.EventClass(item.getAttribute('desc'),"",item.getAttribute('name'), item.getAttribute('state'))

    def getEvents(self, onlyActiveEvents = True):
        xmldoc = minidom.parse('data/config.xml')
        eventsData = []
        itemsList = xmldoc.getElementsByTagName('status')[0].getElementsByTagName('element')        
        for item in itemsList:
            if (item.getAttribute('state') == "1" and onlyActiveEvents == True) or (onlyActiveEvents == False):
                eventsData.append(EventClass.EventClass(item.getAttribute('desc'),"",item.getAttribute('name'), item.getAttribute('state')))                
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

