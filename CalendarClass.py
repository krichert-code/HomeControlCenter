import json
import requests
from datetime import datetime, timedelta
import EventClass

                
class CalendarClass:
    __eventsData = []
    __get_my_cal_req = "https://www.googleapis.com/calendar/v3/calendars/krzysiek.richert@gmail.com/events?timeMax=STOP_DATET00%3A00%3A00-07%3A00&timeMin=START_DATET00%3A00%3A00-07%3A00&key=AIzaSyDepBebtgRz7DIOR60j4Uu0Y-CnOpy22fo"
    __get_holidays_req = "https://www.googleapis.com/calendar/v3/calendars/polish@holiday.calendar.google.com/events?timeMax=STOP_DATET00%3A00%3A00-07%3A00&timeMin=START_DATET00%3A00%3A00-07%3A00&key=AIzaSyDepBebtgRz7DIOR60j4Uu0Y-CnOpy22fo"

    __myCalFile = "data/mycal.json"
    __holidaysCalFile = "data/holidays.json"

    # The class "constructor" - It's actually an initializer
    def __init__(self):
        self.__eventsData = []

    def __getDataFromFile(self, eventFile, id):
        with open(eventFile) as file:
            data = json.load(file)            
            
        events = data['items']
               
        for element in events:
	    event = EventClass.EventClass(element['summary'], element['start']['date'], id)
	    event.setEventIcon('calendar')
            self.__eventsData.append(event)
                
    def generateFiles(self):
	try:
	    start_date = datetime.now().strftime('%Y-%m-%d')
	    delta = timedelta(days=7)
	    stop_date = (datetime.now() + delta).strftime('%Y-%m-%d')

            req = CalendarClass.__get_my_cal_req
            req = req.replace("START_DATE", start_date)
            req = req.replace("STOP_DATE", stop_date)
	    resp = requests.get(req, verify = False, timeout = 5)
	    data = json.loads(resp.text)
	    with open(CalendarClass.__myCalFile, 'w') as outfile:
		json.dump(data, outfile)

            req = CalendarClass.__get_holidays_req
            req = req.replace("START_DATE", start_date)
            req = req.replace("STOP_DATE", stop_date)
	    resp = requests.get(req, verify = False, timeout = 5)
	    data = json.loads(resp.text)
	    with open(CalendarClass.__holidaysCalFile, 'w') as outfile:
		json.dump(data, outfile)

	except requests.exceptions.RequestException as e:
            pass


    def getEventsData(self,id ):
        self.__getDataFromFile(CalendarClass.__holidaysCalFile, id)
        self.__getDataFromFile(CalendarClass.__myCalFile, id)

        return self.__eventsData
        