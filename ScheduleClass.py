from xml.dom import minidom
import ConfigClass
import EventClass
import datetime
from datetime import datetime
import requests
import HTMLParser


class MyHTMLParser(HTMLParser.HTMLParser):
    events = []
    __hourHandled = False
    __minuteHandled = False
    __trigger = False
    __tag = ""
    __hour = 0
    __minute = 0
    def handle_starttag(self, tag, attrs):
        if (tag == "span"):
            for name,value in attrs:
                if name == "class" and value == "schedule__details__departure":
                    self.__trigger = True

                if name == "class" and value == "schedule__hour" and self.__trigger == True :
                    self.__tag = "hour"

                if name == "class" and value == "schedule__minutes" and self.__trigger == True :
                    self.__tag = "minute"

    def handle_endtag(self, tag):
        self.__tag = ""
        if tag == "span" and self.__hourHandled == True and self.__minuteHandled == True and self.__trigger == True:
            self.__trigger = False
            self.__minuteHandled = False
            self.__hourHandled = False
            current_day_ts = datetime.now().hour * 60 + datetime.now().minute
            event_day_ts = self.__hour * 60 + self.__minute
            # Add only 5 next trains
            if len(self.events) < 5 and event_day_ts > current_day_ts:
                print "___________" + str(self.__hour) + " : " + str(self.__minute)



    def handle_data(self, data):
        if self.__tag == "hour":
            self.__hour = int(data)
            self.__hourHandled = True

        if self.__tag == "minute":
            self.__minute = int(data)
            self.__minuteHandled = True


class ScheduleClass(HTMLParser.HTMLParser):

    __directionA = "http://www.skm.pkp.pl/pelny-rozklad-jazdy/?tx_fnxpassengercenter_fulltimetable%5Bdata%5D%5Baction%5D=show&tx_fnxpassengercenter_fulltimetable%5Bdata%5D%5Bcontroller%5D=Connection&tx_fnxpassengercenter_fulltimetable%5Bdata%5D%5B__referrer%5D%5B%40request%5D=a:3:{s:13:%22extensionName%22;s:18:%22Fnxpassengercenter%22;s:14:%22controllerName%22;s:10:%22Connection%22;s:10:%22actionName%22;s:4:%22show%22;}0cdbbd1d0008b3856c5d1c43992c887f21c318e7&tx_fnxpassengercenter_fulltimetable%5Bdata%5D%5B__referrer%5D%5BextensionName%5D=Fnxpassengercenter&tx_fnxpassengercenter_fulltimetable%5Bdata%5D%5B__referrer%5D%5BcontrollerName%5D=Connection&tx_fnxpassengercenter_fulltimetable%5Bdata%5D%5B__referrer%5D%5BactionName%5D=show&tx_fnxpassengercenter_fulltimetable%5Bdata%5D%5B__hmac%5D=a:11:{s:13:%22min-swap-time%22;i:1;s:13:%22max-swap-time%22;i:1;s:12:%22station-from%22;i:1;s:16:%22station-through1%22;i:1;s:16:%22station-through2%22;i:1;s:10:%22station-to%22;i:1;s:4:%22date%22;i:1;s:4:%22time%22;i:1;s:13:%22depart-arrive%22;i:1;s:6:%22action%22;i:1;s:10:%22controller%22;i:1;}716d6ba4a79379f7acce1caeabfbe55c73fbce7f&tx_fnxpassengercenter_fulltimetable%5Bdata%5D%5Bmin-swap-time%5D=0&tx_fnxpassengercenter_fulltimetable%5Bdata%5D%5Bmax-swap-time%5D=0&tx_fnxpassengercenter_fulltimetable%5Bdata%5D%5Bstation-from%5D=257521&tx_fnxpassengercenter_fulltimetable%5Bdata%5D%5Bstation-through1%5D=&tx_fnxpassengercenter_fulltimetable%5Bdata%5D%5Bstation-through2%5D=&tx_fnxpassengercenter_fulltimetable%5Bdata%5D%5Bstation-to%5D=257533&tx_fnxpassengercenter_fulltimetable%5Bdata%5D%5Bdate%5D=05%20%20Grudzie%C5%84,%202018&tx_fnxpassengercenter_fulltimetable%5Bdata%5D%5Btime%5D=11:38&tx_fnxpassengercenter_fulltimetable%5Bdata%5D%5Bdepart-arrive%5D=1&tx_fnxpassengercenter_fulltimetable%5Bdata%5D%5Bdepart-date%5D=2018-12-05%2011:38:00&tx_fnxpassengercenter_fulltimetable%5Bdata%5D%5Barrive-date%5D=&tx_fnxpassengercenter_fulltimetable%5Baction%5D=showFullTimetable&tx_fnxpassengercenter_fulltimetable%5Bcontroller%5D=Connection"

    def __init__(self):
        pass


    def getTimetoDirectionA(self):
        events = []
        resp = requests.get(self.__directionA, verify=False, timeout=10)
        parser = MyHTMLParser()
        parser.feed(resp.text)
        #self.feed(resp.text)
        return events

    def getTimetoDirectionB(self):
        events = []
        return events
