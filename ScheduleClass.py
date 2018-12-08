import EventClass
from datetime import datetime
import requests
import HTMLParser


class ScheduleClass(HTMLParser.HTMLParser, object):

    __directionA = "http://www.skm.pkp.pl/pelny-rozklad-jazdy/?tx_fnxpassengercenter_fulltimetable%5Bdata%5D%5Baction%5D=show&tx_fnxpassengercenter_fulltimetable%5Bdata%5D%5Bcontroller%5D=Connection&tx_fnxpassengercenter_fulltimetable%5Bdata%5D%5B__referrer%5D%5B%40request%5D=a:3:{s:13:%22extensionName%22;s:18:%22Fnxpassengercenter%22;s:14:%22controllerName%22;s:10:%22Connection%22;s:10:%22actionName%22;s:4:%22find%22;}4d4cfc4571ff33e626c3e4cce1354b6601b85178&tx_fnxpassengercenter_fulltimetable%5Bdata%5D%5B__referrer%5D%5BextensionName%5D=Fnxpassengercenter&tx_fnxpassengercenter_fulltimetable%5Bdata%5D%5B__referrer%5D%5BcontrollerName%5D=Connection&tx_fnxpassengercenter_fulltimetable%5Bdata%5D%5B__referrer%5D%5BactionName%5D=find&tx_fnxpassengercenter_fulltimetable%5Bdata%5D%5B__hmac%5D=a:12:{s:12:%22station-from%22;i:1;s:16:%22station-through1%22;i:1;s:16:%22station-through2%22;i:1;s:10:%22station-to%22;i:1;s:4:%22date%22;i:1;s:4:%22time%22;i:1;s:13:%22depart-arrive%22;i:1;s:13:%22min-swap-time%22;i:1;s:13:%22max-swap-time%22;i:1;s:17:%22direct-connection%22;i:1;s:6:%22action%22;i:1;s:10:%22controller%22;i:1;}3c30b2e5e154892f42bdef11e3b9d41745fa3027&tx_fnxpassengercenter_fulltimetable%5Bdata%5D%5Bstation-from%5D=257521&tx_fnxpassengercenter_fulltimetable%5Bdata%5D%5Bstation-through1%5D=&tx_fnxpassengercenter_fulltimetable%5Bdata%5D%5Bstation-through2%5D=&tx_fnxpassengercenter_fulltimetable%5Bdata%5D%5Bstation-to%5D=257533&tx_fnxpassengercenter_fulltimetable%5Bdata%5D%5Bdate%5D=06%20%20Grudzie%C5%84,%202018&tx_fnxpassengercenter_fulltimetable%5Bdata%5D%5Btime%5D=10:08&tx_fnxpassengercenter_fulltimetable%5Bdata%5D%5Bdepart-arrive%5D=1&tx_fnxpassengercenter_fulltimetable%5Bdata%5D%5Bmin-swap-time%5D=0&tx_fnxpassengercenter_fulltimetable%5Bdata%5D%5Bmax-swap-time%5D=0&tx_fnxpassengercenter_fulltimetable%5Bdata%5D%5Bdirect-connection%5D=&tx_fnxpassengercenter_fulltimetable%5Bdata%5D%5Bdepart-date%5D=DEP_DATE%2010:08:00&tx_fnxpassengercenter_fulltimetable%5Bdata%5D%5Barrive-date%5D=&tx_fnxpassengercenter_fulltimetable%5Baction%5D=showFullTimetable&tx_fnxpassengercenter_fulltimetable%5Bcontroller%5D=Connection"
    __directionB = "http://www.skm.pkp.pl/pelny-rozklad-jazdy/?tx_fnxpassengercenter_fulltimetable%5Bdata%5D%5Baction%5D=show&tx_fnxpassengercenter_fulltimetable%5Bdata%5D%5Bcontroller%5D=Connection&tx_fnxpassengercenter_fulltimetable%5Bdata%5D%5B__referrer%5D%5B%40request%5D=a:3:{s:13:%22extensionName%22;s:18:%22Fnxpassengercenter%22;s:14:%22controllerName%22;s:10:%22Connection%22;s:10:%22actionName%22;s:4:%22find%22;}4d4cfc4571ff33e626c3e4cce1354b6601b85178&tx_fnxpassengercenter_fulltimetable%5Bdata%5D%5B__referrer%5D%5BextensionName%5D=Fnxpassengercenter&tx_fnxpassengercenter_fulltimetable%5Bdata%5D%5B__referrer%5D%5BcontrollerName%5D=Connection&tx_fnxpassengercenter_fulltimetable%5Bdata%5D%5B__referrer%5D%5BactionName%5D=find&tx_fnxpassengercenter_fulltimetable%5Bdata%5D%5B__hmac%5D=a:12:{s:12:%22station-from%22;i:1;s:16:%22station-through1%22;i:1;s:16:%22station-through2%22;i:1;s:10:%22station-to%22;i:1;s:4:%22date%22;i:1;s:4:%22time%22;i:1;s:13:%22depart-arrive%22;i:1;s:13:%22min-swap-time%22;i:1;s:13:%22max-swap-time%22;i:1;s:17:%22direct-connection%22;i:1;s:6:%22action%22;i:1;s:10:%22controller%22;i:1;}3c30b2e5e154892f42bdef11e3b9d41745fa3027&tx_fnxpassengercenter_fulltimetable%5Bdata%5D%5Bstation-from%5D=257521&tx_fnxpassengercenter_fulltimetable%5Bdata%5D%5Bstation-through1%5D=&tx_fnxpassengercenter_fulltimetable%5Bdata%5D%5Bstation-through2%5D=&tx_fnxpassengercenter_fulltimetable%5Bdata%5D%5Bstation-to%5D=5900&tx_fnxpassengercenter_fulltimetable%5Bdata%5D%5Bdate%5D=06%20%20Grudzie%C5%84,%202018&tx_fnxpassengercenter_fulltimetable%5Bdata%5D%5Btime%5D=12:30&tx_fnxpassengercenter_fulltimetable%5Bdata%5D%5Bdepart-arrive%5D=1&tx_fnxpassengercenter_fulltimetable%5Bdata%5D%5Bmin-swap-time%5D=0&tx_fnxpassengercenter_fulltimetable%5Bdata%5D%5Bmax-swap-time%5D=0&tx_fnxpassengercenter_fulltimetable%5Bdata%5D%5Bdirect-connection%5D=&tx_fnxpassengercenter_fulltimetable%5Bdata%5D%5Bdepart-date%5D=DEP_DATE%2012:30:00&tx_fnxpassengercenter_fulltimetable%5Bdata%5D%5Barrive-date%5D=&tx_fnxpassengercenter_fulltimetable%5Baction%5D=showFullTimetable&tx_fnxpassengercenter_fulltimetable%5Bcontroller%5D=Connection"

    def __init__(self):
        super(ScheduleClass, self).__init__()
        self.events = []
        self.__hourHandled = False
        self.__minuteHandled = False
        self.__changeHandled = False

        self.__triggerTime = False
        self.__triggerChange = False

        self.__tag = ""

        self.__change = 0
        self.__hour = 0
        self.__minute = 0

    def handle_starttag(self, tag, attrs):
        if (tag == "div"):
            for name, value in attrs:
                if name == "class" and value == "schedule__col schedule__col__1 -large": #"schedule__details__departure":
                    self.__triggerTime = True

                if name == "class" and value == "schedule__col schedule__col__3 -large": #"schedule__details__departure":
                    self.__triggerChange = True

        if (tag == "span"):
            if self.__triggerChange == True:
                self.__tag = "change"

            for name, value in attrs:
                if name == "class" and value == "schedule__hour" and self.__triggerTime == True:
                    self.__tag = "hour"

                if name == "class" and value == "schedule__minutes" and self.__triggerTime == True:
                    self.__tag = "minute"


    def handle_endtag(self, tag):
        self.__tag = ""

        # handler for schedule time
        if tag == "span" and self.__hourHandled == True and self.__minuteHandled == True  and self.__triggerTime == True:
            self.__triggerTime = False
            self.__minuteHandled = False
            self.__hourHandled = False

        # handler for stops
        if tag == "span" and self.__changeHandled == True and self.__triggerChange == True:
            self.__triggerChange = False
            self.__changeHandled = False

            current_day_ts = datetime.now().hour * 60 + datetime.now().minute
            event_day_ts = self.__hour * 60 + self.__minute

            if (self.__hour < 10):
                time = "0" + str(self.__hour)
            else:
                time = str(self.__hour)

            time = time + " : "

            if (self.__minute < 10):
                time = time + "0" + str(self.__minute)
            else:
                time = time + str(self.__minute)

            # Add only 5 next trains, and only direct connections (change = 0)
            if len(self.events) < 5 and event_day_ts > current_day_ts and self.__change == 0:
                self.events.append(EventClass.EventClass("Odjazd za " + str(event_day_ts - current_day_ts) + "min", time))


    def handle_data(self, data):
        if self.__tag == "change":
            self.__change = int(data)
            self.__changeHandled = True

        if self.__tag == "hour":
            self.__hour = int(data)
            self.__hourHandled = True

        if self.__tag == "minute":
            self.__minute = int(data)
            self.__minuteHandled = True

    def getTimetoDirection(self, direction = "A"):
        self.events = []

        if direction == "A" :
            req = self.__directionA
            dir = "Kierunek Gdansk"
        else:
            req = self.__directionB
            dir = "Kierunek Gdynia"

        date = datetime.now().strftime('%Y-%m-%d')
	event = EventClass.EventClass(dir, date)
	event.setStyle("title")
        self.events.append(event)

        req = req.replace("DEP_DATE", date)
        try:
            resp = requests.get(req, verify=False, timeout=10)
            self.feed(resp.text)
        except:
            self.events.append(EventClass.EventClass("Blad sieci/parsera", date))

        return self.events


