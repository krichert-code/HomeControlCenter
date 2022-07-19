#!/usr/bin/python
# -*- coding: utf-8 -*-
from xml.dom import minidom
import ConfigClass
import requests
import csv
from datetime import datetime
import json

class WeatherForecaset(object):

    time = ''
    wind = ''
    presure = ''
    temp = ''
    icon = ''
    id = 0

    def __init__(
        self,
        id,
        time,
        temp,
        wind,
        presure,
        icon,
        ):
        self.temp = temp
        self.time = time
        self.icon = icon
        self.presure = presure
        self.wind = wind
        self.id = id


class WeatherClass(object):

    WeatherCurrentFile = 1 << 0
    WeatherHourlyFile = 1 << 1
    WeatherDailyFile = 1 << 2

    __currWeatherFile = '/HomeControlCenter/data/weatherCurrent.json'
    __hourlyWeatherFile = '/HomeControlCenter/data/weatherHourly.json'
    __dailyWeatherFile = '/HomeControlCenter/data/weatherDaily.json'
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

            weatherData['icon'] = \
                'https://www.weatherbit.io/static/img/icons/' \
                + data['data'][0]['weather']['icon'] + '.png'
            weatherData['temp'] = '%.1f' % data['data'][0]['temp']
            datetime = data['data'][0]['ob_time']
            weatherData['date'] = datetime[:datetime.find(' ')]
            weatherData['time'] = datetime[datetime.find(' '):]
            weatherData['pressure'] = '%.1f' % data['data'][0]['pres']
            weatherData['wind'] = '%.1f' % data['data'][0]['wind_spd']
            weatherData['wind_dir'] = ''
        except:
            weatherData['icon'] = \
                'https://www.weatherbit.io/static/img/icons/' \
                + data['data'][0]['weather']['icon'] + '.png'
            weatherData['temp'] = '0.0'
            weatherData['date'] = ''
            weatherData['time'] = ''
            weatherData['pressure'] = '0.0'
            weatherData['wind'] = '0.0'
            weatherData['wind_dir'] = ''

        return weatherData


    def __saveWeatherFile(self, url, name):
        resp = requests.get(url, verify=False, timeout=10)
        data = json.loads(resp.text)
        with open(name, 'w+') as f:
            json.dump(data, f)


    def generateFiles(self, files):
        config = ConfigClass.ConfigClass()
        result = True
        try:
            if files & WeatherClass.WeatherCurrentFile != 0:
                self.__saveWeatherFile(config.getCurrentWeatherReq(),
                                       self.__currWeatherFile)

            #if files & WeatherClass.WeatherHourlyFile != 0:
            #    self.__saveWeatherFile(config.getHourlyWeatherForecastReq(),
            #                           self.__hourlyWeatherFile)

            #if files & WeatherClass.WeatherDailyFile != 0:
            #    self.__saveWeatherFile(config.getDailyWeatherForecastReq(),
            #                           self.__dailyWeatherFile)

        except Exception as e:
            #logging.error(str(e))
            print("_____________weather class exception : " +str(e))
            result = False

        return result
