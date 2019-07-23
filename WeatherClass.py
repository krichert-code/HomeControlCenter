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
    __rainStringIndicator = "eszcz"
    __rainIndicator = False
    
    # The class "constructor" - It's actually an initializer
    def __init__(self):
        self.__heater = {}
        
    def clearRainIndicator(self):
	WeatherClass.__rainIndicator = False
	pass

    def rainOccured(self):
	return WeatherClass.__rainIndicator

    def updateRainIndicator(self):
	try:
    	    with open(WeatherClass.__currWeatherFile) as f:
		data = json.load(f)

    	    if data['data'][0]['weather']['description'].find(self.__rainStringIndicator) <> -1:
		WeatherClass.__rainIndicator = True

	except:
	    print "_____________weather exception!!!"


    def getCurrentWeather(self):
        weatherData = {}
	try:
    	    with open(WeatherClass.__currWeatherFile) as f:
    		data = json.load(f)

    	    weatherData['icon'] = "https://www.weatherbit.io/static/img/icons/"+data['data'][0]['weather']['icon']+".png"
    	    weatherData['temp'] = "%.1f" % data['data'][0]['temp']
	    datetime = data['data'][0]['ob_time']
    	    weatherData['date'] = datetime[:datetime.find(" ")]
    	    weatherData['time'] = datetime[datetime.find(" "):]
    	    weatherData['pressure'] = "%.1f" % data['data'][0]['pres']
    	    weatherData['wind']= "%.1f" % data['data'][0]['wind_spd']
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
        
    	    for item in data['data']:
        	# skip weather forecast between 1am to 5am, and display only temperature on every 3 hours
        	if (id % 3) == 0:
            	    icon = "https://www.weatherbit.io/static/img/icons/"+item['weather']['icon']+".png"
		    time = item['timestamp_local']
            	    time = time[time.find("T")+1:]
            	    temp = "%.1f" % item['temp']
            	    wind = "%.1f" % item['wind_spd']
            	    presure = "%.1f" % item['pres']
            	    weatherForecast.append(WeatherForecaset(id/3,time,temp,wind,presure,icon))
        	id = id + 1
		if id > 15:
            	    break
	except:
	    print "_____________weather exception"
        return weatherForecast


    def getWeatherDailyForecast(self):
        id = 0
        weatherForecast = []
	try:
    	    with open(WeatherClass.__dailyWeatherFile) as f:
        	data = json.load(f)
        
    	    for item in data['data']:
        	id = id + 1
            	icon = "https://www.weatherbit.io/static/img/icons/"+item['weather']['icon']+".png"
		time = item['datetime']
            	#time = time[time.find("T")+1:]
		temp = "%.1f" % item['temp']
            	wind = "%.1f" % item['wind_gust_spd']
            	presure = "%.1f" % item['pres']
            	weatherForecast.append(WeatherForecaset(id,time,temp,wind,presure,icon))
            	if id > 2:
            	    break
	except:
	    print "_____________weather exception_DAILY"
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

        if (files & WeatherClass.WeatherDailyFile) <> 0:
            self.__saveWeatherFile( config.getDailyWeatherForecastReq(), self.__dailyWeatherFile)



