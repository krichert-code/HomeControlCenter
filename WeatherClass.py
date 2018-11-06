from xml.dom import minidom
#import subprocess as sub
import csv

class WeatherForecaset(object):
    time = ""
    wind = ""
    presure = ""
    temp = ""
    icon = ""
    id = 0;
    
    def __init__(self, id, time, temp, wind, presure,icon):
        self.temp = temp
        self.time = time
        self.icon = icon
        self.presure = presure
        self.wind = wind
        self.id = id
    
class WeatherClass(object):
    __weatherData = {}
    __weatherForecast = []
    __heater = {}
    
    # The class "constructor" - It's actually an initializer
    def __init__(self):
        self.__weatherData = {}
        self.__heater = {}
        self.__weatherForecast = []
        
    def getCurrentWeather(self):
        xmldoc = minidom.parse('data/weather.xml')
        
        item = xmldoc.getElementsByTagName('current_observation')[0].getElementsByTagName('icon_url')        
        self.__weatherData['icon']=item[0].childNodes[0].nodeValue
        
        item = xmldoc.getElementsByTagName('current_observation')[0].getElementsByTagName('temp_c')        
        self.__weatherData['temp']=item[0].childNodes[0].nodeValue

        item = xmldoc.getElementsByTagName('current_observation')[0].getElementsByTagName('observation_time_rfc822')        
        self.__weatherData['date']=item[0].childNodes[0].nodeValue
        time = self.__weatherData['date']
        time = time[:time.rfind(" ")]
        time = time[time.rfind(" "):]
        self.__weatherData['time'] = time
        
        item = xmldoc.getElementsByTagName('current_observation')[0].getElementsByTagName('pressure_mb')        
        self.__weatherData['pressure']=item[0].childNodes[0].nodeValue
        
        item = xmldoc.getElementsByTagName('current_observation')[0].getElementsByTagName('wind_kph')        
        self.__weatherData['wind']=item[0].childNodes[0].nodeValue
        
        item = xmldoc.getElementsByTagName('current_observation')[0].getElementsByTagName('wind_dir')        
        self.__weatherData['wind_dir']=item[0].childNodes[0].nodeValue
        
        return self.__weatherData
    
    def getWeatherForecast(self):
        id = 0
        xmldoc = minidom.parse('data/weatherDaily.xml')        
        
        itemlist = xmldoc.getElementsByTagName('forecast')
        
        for item in itemlist:
            icon = item.getElementsByTagName('icon_url')[0].childNodes[0].nodeValue
            time = item.getElementsByTagName('FCTTIME')[0].getElementsByTagName('hour')[0].childNodes[0].nodeValue + " : 00" 
            temp = item.getElementsByTagName('temp')[0].getElementsByTagName('metric')[0].childNodes[0].nodeValue            
            wind = item.getElementsByTagName('wspd')[0].getElementsByTagName('metric')[0].childNodes[0].nodeValue            
            presure = item.getElementsByTagName('mslp')[0].getElementsByTagName('metric')[0].childNodes[0].nodeValue
            self.__weatherForecast.append(WeatherForecaset(id,time,temp,wind,presure,icon))
            id = id + 1
        
        return self.__weatherForecast
    
    def getCurrentTemperatureInside(self):
        print "test"
        with open("data/heater.csv", "rb") as csvfile:
            reader = csv.DictReader(csvfile,['temp','state','mode','time','icon'])
            #reader = csv.reader(csvfile, delimiter=",", quotechar="|")
            for row in reader:
                pass
                
            
            self.__heater['temp'] = row['temp']
            self.__heater['state'] = row['state']
            self.__heater['mode'] = row['mode']
            self.__heater['time'] = row['time']            
  
            if self.__heater['state'] == "1":
                self.__heater['heat_state_icon'] = "img/piec_on1.gif";
            else:
                self.__heater['heat_state_icon'] = "";
                
            if self.__heater['mode'] == "1":
                self.__heater['icon'] = "img/day.gif"
            else:
                self.__heater['icon'] = "img/night.gif"
                
            return self.__heater
            


        
