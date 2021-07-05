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

