import json
import glob
import requests
import ConfigClass
from datetime import datetime, timedelta
import EventClass

                
class CalendarClass:
    __get_cal_req = "https://www.googleapis.com/calendar/v3/calendars/CALENDAR_NAME/events?timeMax=STOP_DATET00%3A00%3A00-07%3A00&timeMin=START_DATET00%3A00%3A00-07%3A00&key=USER_KEY"

    # The class "constructor" - It's actually an initializer
    def __init__(self):
        self.__eventsData = []

    def __getDataFromFile(self, eventFile, id):
        with open(eventFile) as file:
            data = json.load(file)            
            
        events = data['items']
               
        for element in events:
	    try:
		event = EventClass.EventClass(element['summary'], element['start']['date'], id)
	    except:
		event = EventClass.EventClass(element['summary'], element['start']['dateTime'], id)

	    event.setEventIcon('calendar')
            self.__eventsData.append(event)
                
    def generateFiles(self):
	config = ConfigClass.ConfigClass()

	req = CalendarClass.__get_cal_req
	req = req.replace("USER_KEY", config.getCalendarKey())

	try:
	    start_date = datetime.now().strftime('%Y-%m-%d')
	    delta = timedelta(days=config.getCalendarRange())
	    stop_date = (datetime.now() + delta).strftime('%Y-%m-%d')
	    req = req.replace("START_DATE", start_date)
	    req = req.replace("STOP_DATE", stop_date)

	    calNames = config.getCalendarsList()

	    for name in calNames:
        	req_to_send = req
		req_to_send = req_to_send.replace("CALENDAR_NAME", name)
		resp = requests.get(req_to_send, verify = False, timeout = 10)
		data = json.loads(resp.text)
		with open("data/" + name + "_calendar.json", 'w') as outfile:
		    json.dump(data, outfile)

	except requests.exceptions.RequestException as e:
            pass


    def getEventsData(self,id = 0):
	fileList = glob.glob("data/*_calendar.json")
	for name in fileList:
	    self.__getDataFromFile(name, id)
        return self.__eventsData
