from xml.dom import minidom
import ConfigClass
import requests
import csv
from datetime import datetime
import json


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

    __currWeatherFile = "data/weatherCurrent.json"
    __hourlyWeatherFile = "data/weatherHourly.json"
    __dailyWeatherFile = "data/weatherDaily.json"
    
    # The class "constructor" - It's actually an initializer
    def __init__(self):
        self.__heater = {}
        
    def getCurrentWeather(self):
        weatherData = {}
	try:
    	    with open(WeatherClass.__currWeatherFile) as f:
        	data = json.load(f)

    	    weatherData['icon'] = "https://openweathermap.org/img/w/"+data['weather'][0]['icon']+".png"
    	    weatherData['temp'] = "%.1f" % data['main']['temp']
    	    weatherData['date'] = datetime.fromtimestamp(data['dt']).strftime('%Y-%m-%d')
    	    weatherData['time'] = datetime.fromtimestamp(data['dt']).strftime('%H:%M:%S')
    	    weatherData['pressure'] = "%.1f" % data['main']['pressure']
    	    weatherData['wind']= "%.1f" % data['wind']['speed']
    	    weatherData['wind_dir']=""
	except:
	    print "_____________weather exception1"

    	return weatherData
    
    def getWeatherHourlyForecast(self):
        id = 0
        weatherForecast = []
	try:
    	    with open(WeatherClass.__hourlyWeatherFile) as f:
        	data = json.load(f)
        
    	    for item in data['list']:
        	id = id + 1
        	# skip weather forecast between 1am to 5am, and display only temperature on every 3 hours
        	if id > 2:
            	    icon = "https://openweathermap.org/img/w/"+item['weather'][0]['icon']+".png"
            	    time = datetime.fromtimestamp(item['dt']).strftime('%H:%M')
            	    temp = "%.1f" % item['main']['temp']
            	    wind = "%.1f" % item['wind']['speed']
            	    presure = "%.1f" % item['main']['pressure']
            	    weatherForecast.append(WeatherForecaset(id,time,temp,wind,presure,icon))
            	    if id > 7:
                	break
	except:
	    print "_____________weather exception"
        return weatherForecast


    def getWeatherDailyForecast(self):
        id = 0
        weatherForecast = []
	try:
    	    with open(WeatherClass.__hourlyWeatherFile) as f:
        	data = json.load(f)
        
    	    for item in data['list']:
		if (item['dt_txt'].find('12:00') != -1):
        	    id = id + 1
            	    icon = "https://openweathermap.org/img/w/"+item['weather'][0]['icon']+".png"
            	    time = datetime.fromtimestamp(item['dt']).strftime('%Y-%m-%d')
            	    temp = "%.1f" % item['main']['temp']
            	    wind = "%.1f" % item['wind']['speed']
            	    presure = "%.1f" % item['main']['pressure']
            	    weatherForecast.append(WeatherForecaset(id,time,temp,wind,presure,icon))
            	    if id > 2:
                	break
	except:
	    print "_____________weather exception"
        return weatherForecast


    def __saveWeatherFile(self, url, name):
        try:
            resp = requests.get(url, verify=False, timeout=10)
            with open(name, 'w') as f:
                f.write(resp.text.encode('utf-8'))
	except Exception as e:
            print "_____________weather exception3"


    def generateFiles(self, files):
        config = ConfigClass.ConfigClass()

        if (files & WeatherClass.WeatherCurrentFile) <> 0:
            self.__saveWeatherFile( config.getCurrentWeatherReq(), self.__currWeatherFile)

        if (files & WeatherClass.WeatherHourlyFile) <> 0:
            self.__saveWeatherFile( config.getHourlyWeatherForecastReq(), self.__hourlyWeatherFile)

#        if (files & WeatherClass.WeatherDailyFile) <> 0:
#            self.__saveWeatherFile( config.getDailyWeatherForecastReq(), self.__dailyWeatherFile)

