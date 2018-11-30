import json
import EventClass

                
class CalendarClass:
    __eventsData = []
    
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
                
    def getEventsData(self,id ):
        self.__getDataFromFile("data/holidays.json", id)
        self.__getDataFromFile("data/mycal.json", id)

        return self.__eventsData
        