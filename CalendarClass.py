import json
import EventClass

                
class CalendarClass:
    __eventsData = []
    
    # The class "constructor" - It's actually an initializer
    def __init__(self):
        self.__eventsData = []

    def __getDataFromFile(self, eventFile):
        with open(eventFile) as file:
            data = json.load(file)            
            
        events = data['items']
               
        for element in events:
            self.__eventsData.append(EventClass.EventClass(element['summary'], element['start']['date']))
                
    def getEventsData(self):
        self.__getDataFromFile("data/holidays.json")
        self.__getDataFromFile("data/mycal.json")

        return self.__eventsData
        