from xml.dom import minidom
import ConfigClass
import requests
import csv
from datetime import datetime

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
    WeatherCurrentFile  =  1 << 0
    WeatherHourlyFile   =  1 << 1
    WeatherDailyFile    =  1 << 2

    __currWeatherFile = "data/weather.xml"
    __hourlyWeatherFile = "data/weatherHourly.xml"
    __dailyWeatherFile = "data/weatherDaily.xml"
    
    # The class "constructor" - It's actually an initializer
    def __init__(self):
        self.__heater = {}
        
    def getCurrentWeather(self):
        weatherData = {}
        xmldoc = minidom.parse(WeatherClass.__currWeatherFile)
        
        item = xmldoc.getElementsByTagName('current_observation')[0].getElementsByTagName('icon_url')        
        weatherData['icon']=item[0].childNodes[0].nodeValue
        
        item = xmldoc.getElementsByTagName('current_observation')[0].getElementsByTagName('temp_c')        
        weatherData['temp']=item[0].childNodes[0].nodeValue

        item = xmldoc.getElementsByTagName('current_observation')[0].getElementsByTagName('local_time_rfc822')        
        weatherData['date']=item[0].childNodes[0].nodeValue
        time = weatherData['date']
        time = time[:time.rfind(" ")]
        time = time[time.rfind(" "):]
        weatherData['time'] = time
        
        item = xmldoc.getElementsByTagName('current_observation')[0].getElementsByTagName('pressure_mb')        
        weatherData['pressure']=item[0].childNodes[0].nodeValue
        
        item = xmldoc.getElementsByTagName('current_observation')[0].getElementsByTagName('wind_kph')        
        weatherData['wind']=item[0].childNodes[0].nodeValue
        
        item = xmldoc.getElementsByTagName('current_observation')[0].getElementsByTagName('wind_dir')        
        weatherData['wind_dir']=item[0].childNodes[0].nodeValue
        return weatherData
    
    def getWeatherHourlyForecast(self):
        id = 0
        skip = -1
        weatherForecast = []
        xmldoc = minidom.parse(WeatherClass.__hourlyWeatherFile)
        
        itemlist = xmldoc.getElementsByTagName('forecast')
        
        for item in itemlist:
            skip = skip + 1
            # skip weather forecast between 1am to 5am, and display only temperature on every 3 hours
            if skip % 3 == 0 and skip > 5:
                icon = item.getElementsByTagName('icon_url')[0].childNodes[0].nodeValue
                time = item.getElementsByTagName('FCTTIME')[0].getElementsByTagName('hour')[0].childNodes[0].nodeValue + " : 00"
                temp = item.getElementsByTagName('temp')[0].getElementsByTagName('metric')[0].childNodes[0].nodeValue
                wind = item.getElementsByTagName('wspd')[0].getElementsByTagName('metric')[0].childNodes[0].nodeValue
                presure = item.getElementsByTagName('mslp')[0].getElementsByTagName('metric')[0].childNodes[0].nodeValue
                weatherForecast.append(WeatherForecaset(id,time,temp,wind,presure,icon))
                id = id + 1
                if id > 5:
                    break

        return weatherForecast

    def getWeatherDailyForecast(self):
        id = 0
        weatherForecast = []
        xmldoc = minidom.parse(WeatherClass.__dailyWeatherFile)
        itemlist = xmldoc.getElementsByTagName('simpleforecast')[0].getElementsByTagName('forecastdays')[0].getElementsByTagName('forecastday')
        for item in itemlist:
            icon = item.getElementsByTagName('icon_url')[0].childNodes[0].nodeValue
            time = item.getElementsByTagName('date')[0].getElementsByTagName('day')[0].childNodes[0].nodeValue + " " + \
                   item.getElementsByTagName('date')[0].getElementsByTagName('monthname_short')[0].childNodes[0].nodeValue
            temp = temp = item.getElementsByTagName('low')[0].getElementsByTagName('celsius')[0].childNodes[0].nodeValue + \
                          "/" + item.getElementsByTagName('high')[0].getElementsByTagName('celsius')[0].childNodes[0].nodeValue
            wind = item.getElementsByTagName('avewind')[0].getElementsByTagName('kph')[0].childNodes[0].nodeValue
            weatherForecast.append(WeatherForecaset(id,time,temp,wind,"",icon))
            id = id + 1
            if id > 2:
                break
        return weatherForecast

    def __saveWeatherFile(self, url, name):
        try:
            resp = requests.get(url, verify=False, timeout=10)
            with open(name, 'w') as f:
                f.write(resp.text)
        except requests.exceptions.RequestException as e:
            pass


    def generateFiles(self, files):
        config = ConfigClass.ConfigClass()

        if (files & WeatherClass.WeatherCurrentFile) <> 0:
            self.__saveWeatherFile( config.getCurrentWeatherReq(), self.__currWeatherFile)

        if (files & WeatherClass.WeatherHourlyFile) <> 0:
            self.__saveWeatherFile( config.getHourlyWeatherForecastReq(), self.__hourlyWeatherFile)

        if (files & WeatherClass.WeatherDailyFile) <> 0:
            self.__saveWeatherFile( config.getDailyWeatherForecastReq(), self.__dailyWeatherFile)



    def getCurrentTemperatureInside(self):
        config = ConfigClass.ConfigClass()

	offset = config.getDS18B20offset()
        file = open(config.getDS18B20file(), "rb")
        for line in file:
	    pass

	temp = int(line[line.find("=")+1:])/1000.0
	temp = temp + int(offset)

        self.__heater['temp'] = "%.1f" % temp
        self.__heater['state'] = "0"
        self.__heater['mode'] = "1"
        self.__heater['time'] = datetime.now().strftime('%H:%M:%S')
        self.__heater['heat_state_icon'] = "img/piec_on1.gif"
        self.__heater['icon'] = "img/day.gif"
        return self.__heater

                

            


        
