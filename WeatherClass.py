#!/usr/bin/python
# -*- coding: utf-8 -*-
from xml.dom import minidom
import ConfigClass
import requests
import csv
from datetime import datetime
import json



class WeatherClass(object):

    __currWeatherFile = '/HomeControlCenter/data/weatherCurrent.json'
    __rainStringIndicator = 'eszcz'
    __rainIndicator = False

    # The class "constructor" - It's actually an initializer

    def __init__(self):
        pass

    def clearRainIndicator(self):
        WeatherClass.__rainIndicator = False

    def rainOccured(self):
        return WeatherClass.__rainIndicator

    def updateRainIndicator(self):
        try:
            with open(WeatherClass.__currWeatherFile) as f:
                data = json.load(f)

            if data['data'][0]['weather']['description'
                    ].find(self.__rainStringIndicator) != -1:
                WeatherClass.__rainIndicator = True
        except:
            WeatherClass.__rainIndicator = False
            print("_____________update rain indicator exception!!!")

    def getCurrentWeather(self):
        weatherData = {}
        try:
            with open(WeatherClass.__currWeatherFile) as f:
                data = json.load(f)

            weatherData['temp'] = '%.1f' % data['data'][0]['temp']
            datetime = data['data'][0]['ob_time']
            weatherData['date'] = datetime[:datetime.find(' ')]
            weatherData['time'] = datetime[datetime.find(' '):]

            weatherData['pressure'] = '%.1f' % data['data'][0]['pres']
            weatherData['wind'] = '%.1f' % data['data'][0]['wind_spd']
            weatherData['sunrise'] = data['data'][0]['sunrise']
            weatherData['sunset'] = data['data'][0]['sunset']
        except:
            weatherData['temp'] = '0.0'
            weatherData['date'] = '0000-00-00'
            weatherData['time'] = '0:00'
            weatherData['pressure'] = '0.0'
            weatherData['wind'] = '0.0'

        return weatherData


    def __saveWeatherFile(self, url, name):
        resp = requests.get(url, verify=False, timeout=10)
        data = json.loads(resp.text)
        with open(name, 'w+') as f:
            json.dump(data, f)


    def generateFiles(self):
        config = ConfigClass.ConfigClass()
        result = True
        try:
            self.__saveWeatherFile(config.getCurrentWeatherReq(),
                                   self.__currWeatherFile)

        except Exception as e:
            #logging.error(str(e))
            print("_____________weather class exception : " +str(e))
            result = False

        return result
