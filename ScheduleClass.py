import EventClass
from datetime import datetime, timedelta
import requests
import json

class ScheduleClass:

    __offset = 0

    def __init__(self):
        self.events = []


    def getJsonFromKoleo(self, direction = "A", offset = "0"):
        self.events = []

	if offset == 0:
	    ScheduleClass.__offset = 0
	else:
	    ScheduleClass.__offset = self.__offset + int(offset)

        req = "https://koleo.pl/api/v2/main/connections"
	h = {'X-KOLEO-Version': '1', 'X-KOLEO-Client': 'Node-1'}
	delta = timedelta(hours=ScheduleClass.__offset, minutes=0)
	date = (datetime.now() + delta).strftime('%d-%m-%Y+%H:%M:%S')


        if direction == "A" :
            d = {'query[start_station]': 'gdansk-rebiechowo', 'query[end_station]': 'gdansk-wrzeszcz', 'query[date]': date}
            dir = "Kierunek Gdansk"
        else:
            d = {'query[start_station]': 'gdansk-rebiechowo', 'query[end_station]': 'gdynia-glowna', 'query[date]': date}
            dir = "Kierunek Gdynia"


	try:
	    data = requests.get(req, headers = h, data = d, verify=False, timeout=10)
	    resp = json.loads(data.text)
	except:
	    resp = {}

	return resp



    def getTimetoDirection(self, direction = "A", offset = "0"):
	resp = self.getJsonFromKoleo(direction, offset)

        if direction == "A" :
	    dir = "Kierunek Gdansk"
        else:
	    dir = "Kierunek Gdynia"

	delta = timedelta(hours=ScheduleClass.__offset, minutes=0)
        date = (datetime.now() + delta).strftime('%Y-%m-%d')
	current_day_ts = (datetime.now() + delta).hour * 60 + (datetime.now() + delta).minute

	event = EventClass.EventClass(dir, date)
        event.setStyle("title")
	self.events.append(event)

        for connection in resp['connections']:
	    time = connection['departure']
	    time = time[time.find('T')+1:]
	    hour = time[:time.find(':')]
	    time = time[time.find(':')+1:]
	    minute = time[:time.find(':')]
	    event_day_ts = int(hour) * 60 + int(minute)
	    departure_time = event_day_ts - current_day_ts
	    if departure_time > 0:
		self.events.append(EventClass.EventClass("Odjazd za " + str(departure_time + (60*ScheduleClass.__offset)) + "min", hour+":"+minute))

        return self.events
