#!/usr/bin/python
# -*- coding: utf-8 -*-
import ConfigClass
import WeatherClass
import AlarmClass
import EventClass
import SwitchClass
import ActionThread
from datetime import datetime
import json
import traceback


class HeaterParam(object):

    def __init__(
        self,
        tempInside,
        tempOutside,
        mode,
        isDay,
        ):
        self.tempInside = tempInside
        self.tempOutside = tempOutside
        self.mode = mode
        self.isDay = isDay
        self.date = datetime.now().strftime('%H:%M %d/%m/%y')


class HeaterClass(object):

    # static data

    __data = []
    __data_per_day = []
    __dayMode = False
    __lastState = -1
    __lastSupportState = -1

    # statistic - how long heater is on today

    __heaterOnToday = 0

    # State defines

    __StateOn = 1
    __StateOff = 0
    __StateUnknown = -1

    # Stored data buffer size - data to generate charts

    __maxDataBuffer = 50000

    # How offent data should be stored in buffer (more offten means shorter period displayed on chart)

    __storeDataInterval = 10

    # How many data should be used to generate 'WorkHeatChart' (every __lineChartInterval sample will be used) - more data means that chart will be generated slower

    __lineChartInterval = 24

    def __init__(self):
        self.__storeDataCounter = 0

    def __getTemperatureFromDevice(self):
        config = ConfigClass.ConfigClass()
        alarm = AlarmClass.AlarmClass()
        thermDevices = alarm.getTemperature()
        temperature = 0
        isTemepratureInit = False
        thermalElements = 1
        status = 0

        if thermDevices['error'] != 0:
            status = 1
        else:
            thermData = config.getFirstThermDevices()
            while thermData['error'] == 0:
                for item in thermDevices['temperature']:
                    if thermData['name'] == item['name']:
                        tempValue = round(float(item['value'])
                                + float(thermData['offset']), 2)

                        if isTemepratureInit == False:
                            temperature = tempValue
                            isTemepratureInit = True
                        elif thermData['mode'] == 'max' and tempValue \
                            > temperature or thermData['mode'] == 'min' \
                            and tempValue < temperature:
                            temperature = tempValue
                        elif thermData['mode'] == 'avg' \
                            or isTemepratureInit == False:
                            temperature = (temperature + tempValue) \
                                / thermalElements

                        thermalElements = thermalElements + 1
                        break
                thermData = config.getNextThermDevices()

        return (status, temperature)

    def getCurrentTemperatureInside(self):
        heater = {}
        (status, temp) = self.__getTemperatureFromDevice()
        if status == 0:
            heater['status'] = 'OK'
        else:
            heater['status'] = 'ERROR'

        heater['temp'] = '%.1f' % temp
        heater['time'] = datetime.now().strftime('%H:%M:%S')
        heater['icon'] = 'img/day.gif'
        heater['mode'] = 'day'
        if HeaterClass.__dayMode == False:
            heater['icon'] = 'img/night.gif'
            heater['mode'] = 'night'

        return heater

    def getHeaterStatistic(self):
        try:
            heaterStats = str(int(HeaterClass.__heaterOnToday / 60)) \
                + 'h ' + str(HeaterClass.__heaterOnToday % 60) + 'min'
        except:
            print ("___________heater exception 2")
        return heaterStats

    def __mainHeatSourceControl(self, url, action, sensorId):
        threadTask = ActionThread.ActionThread()
        threadTask.addTask(ActionThread.Task(action,
                           ActionThread.UpdateParam('heater',
                           sensorId)))

        threadTask.addTask(ActionThread.Task('request',
                           ActionThread.RequestParam(url)))
        threadTask.addTask(ActionThread.Task('notify',
                           ActionThread.NotifyParam()))
        threadTask.start()
        threadTask.suspend()

    def __supportHeatSourceControl(self, action, sensorId):
        state = 'off'
        config = ConfigClass.ConfigClass()
        currentState = HeaterClass.__lastSupportState
        threadTask = ActionThread.ActionThread()
        exceptOccured = False

        errorHeaterSensor = config.getDeviceSensors('status')[3]
        supportedDevices = config.getSupportDevices()

        if (action == 'set'):
            state = 'on'
            HeaterClass.__lastSupportState = HeaterClass.__StateOn
        else:
            state = 'off'
            HeaterClass.__lastSupportState = HeaterClass.__StateOff

        controlInterface = SwitchClass.SwitchClass()
        try:
            if ( HeaterClass.__lastSupportState != currentState):
                for dev in supportedDevices:
                    controlInterface.changeSwitchState(dev, state)

                threadTask.addTask(ActionThread.Task(action,
                                   ActionThread.UpdateParam('heater',
                                   sensorId)))


                threadTask.addTask(ActionThread.Task('clear',
                                   ActionThread.UpdateParam('status',
                                   errorHeaterSensor[0])))


        except:
            exceptOccured = True
            HeaterClass.__lastSupportState = currentState
            threadTask.addTask(ActionThread.Task('set',
                               ActionThread.UpdateParam('status',
                               errorHeaterSensor[0])))

        if ( HeaterClass.__lastSupportState != currentState or exceptOccured == True):
            threadTask.addTask(ActionThread.Task('notify',
                               ActionThread.NotifyParam()))
            threadTask.start()
            threadTask.suspend()


    def manageHeaterState(
        self,
        dayOfWeek,
        hour,
        minute,
        ):
        config = ConfigClass.ConfigClass()
        weather = WeatherClass.WeatherClass()
        alarm = AlarmClass.AlarmClass()

        dayTemp = float(config.getDayTemp())
        nightTemp = float(config.getNightTemp())
        threshold = float(config.geTempThreshold())

        isDayMode = config.isDayMode(dayOfWeek, hour)
        isMainDeviceEnable = config.isMainDeviceEnabled()
        sensor = config.getDeviceSensors('heater')[0]

        isSupportedDeviceMode = config.isSupportedDeviceEnabled(dayOfWeek, hour)
        isSupportedDeviceEnable = config.isSupportDeviceEnabled()

        # New day - reset statistics
        if hour == 0 and minute < 2:
            HeaterClass.__heaterOnToday = 0
            HeaterClass.__data_per_day = []
        if HeaterClass.__lastState == HeaterClass.__StateOn:
            HeaterClass.__heaterOnToday = HeaterClass.__heaterOnToday \
                + 1

        # Check support source - if enable then turn off main source and
        # operate only on support source.
        # Supported divice is consider as enabled if for particular time is enabled
        # and main switch (support_device_enable) is enabled.
        # print("----Check support state = " + str(isSupportedDeviceEnable) + " " + str(isSupportedDeviceMode))
        if (isSupportedDeviceEnable == True and isSupportedDeviceMode == True):
            # print("----Support device start. Current main source = " + str(HeaterClass.__lastState))
            # turn off main heat source
            url = alarm.getUpdateUrl(sensor[1], 0)
            if HeaterClass.__lastState == HeaterClass.__StateOn \
                or HeaterClass.__lastState \
                == HeaterClass.__StateUnknown:
                self.__mainHeatSourceControl(url, 'clear', sensor[0])
            HeaterClass.__lastState = HeaterClass.__StateOff

            # Turn on supported devices
            self.__supportHeatSourceControl('set', sensor[0])
            return
        else:
            # Turn off supported devices and go with main heat source
            self.__supportHeatSourceControl('clear', sensor[0])


        # Read current temperature
        (status, temp) = self.__getTemperatureFromDevice()
        if status != 0:
            return

        # Update current mode (day or night mode)
        if HeaterClass.__dayMode != isDayMode:
            # if mode has changed set heater state as 'unknown'(-1)
            HeaterClass.__lastState = HeaterClass.__StateUnknown
        HeaterClass.__dayMode = isDayMode

        # Main heat source control
        if (isMainDeviceEnable == False):
            self.__mainHeatSourceControl(url, 'clear', sensor[0])
            HeaterClass.__lastState = HeaterClass.__StateOff
        elif (isDayMode == True and temp + threshold <= dayTemp) \
            or (isDayMode == False and temp + threshold <= nightTemp):

            # turn on heater
            url = alarm.getUpdateUrl(sensor[1], 1)
            if HeaterClass.__lastState == HeaterClass.__StateOff \
                or HeaterClass.__lastState \
                == HeaterClass.__StateUnknown:
                self.__mainHeatSourceControl(url, 'set', sensor[0])
            HeaterClass.__lastState = HeaterClass.__StateOn
        elif (isDayMode == True and temp >= dayTemp + threshold) \
            or (isDayMode == False and temp >= nightTemp + threshold) \
            or (HeaterClass.__lastState == HeaterClass.__StateUnknown):

            # turn off heater
            url = alarm.getUpdateUrl(sensor[1], 0)
            if HeaterClass.__lastState == HeaterClass.__StateOn \
                or HeaterClass.__lastState \
                == HeaterClass.__StateUnknown:
                self.__mainHeatSourceControl(url, 'clear', sensor[0])
            HeaterClass.__lastState = HeaterClass.__StateOff


        # Store data once per defined invokes (currently it means once per 10min) - not need so many data
        self.__storeDataCounter = self.__storeDataCounter + 1
        if self.__storeDataCounter % HeaterClass.__storeDataInterval \
            == 0:
            weatherData = weather.getCurrentWeather()
            if not weatherData:
                tempOutside = 0
            else:
                tempOutside = weatherData['temp']

            HeaterClass.__data.append(HeaterParam(temp, tempOutside,
                    HeaterClass.__lastState, isDayMode))
            HeaterClass.__data_per_day.append(HeaterParam(temp,
                    tempOutside, HeaterClass.__lastState, isDayMode))
            if len(HeaterClass.__data) > HeaterClass.__maxDataBuffer:
                HeaterClass.__data.pop(0)

    def getPercentHeatWorkChart(self):
        nightItem = 0
        dayItem = 0
        notWorkItem = 0

        jsonData = {}
        jsonData['cols'] = []
        jsonData['rows'] = []

        jsonData['cols'].append({
            'id': '',
            'label': 'Action',
            'pattern': '',
            'type': 'string',
            })

        jsonData['cols'].append({
            'id': '',
            'label': 'Percent',
            'pattern': '',
            'type': 'number',
            })

        for item in HeaterClass.__data:
            if item.mode == 0 or item.mode == -1:
                notWorkItem = notWorkItem + 1

            if item.isDay == True and item.mode == 1:
                dayItem = dayItem + 1

            if item.isDay == False and item.mode == 1:
                nightItem = nightItem + 1

        jsonData['rows'].append({'c': [{'v': 'Tyb dzienny',
                                'f': 'Tyb dzienny'}, {'v': dayItem,
                                'f': ''}]})
        jsonData['rows'].append({'c': [{'v': 'Tyb nocny',
                                'f': 'Tyb nocny'}, {'v': nightItem,
                                'f': ''}]})
        jsonData['rows'].append({'c': [{'v': 'Brak pracy',
                                'f': 'Brak pracy'}, {'v': notWorkItem,
                                'f': ''}]})

        return json.dumps(jsonData, indent=4)

    def getStateHeatWorkChart(self):
        counter = 0
        jsonData = {}
        jsonData['cols'] = []
        jsonData['rows'] = []

        jsonData['cols'].append({
            'id': '',
            'label': 'Date',
            'pattern': '',
            'type': 'string',
            })

        jsonData['cols'].append({
            'id': '',
            'label': 'Temp.wew',
            'pattern': '',
            'type': 'number',
            })

        jsonData['cols'].append({
            'id': '',
            'label': 'Temp.zew',
            'pattern': '',
            'type': 'number',
            })

        for item in HeaterClass.__data:
            if counter % HeaterClass.__lineChartInterval == 0:
                jsonData['rows'].append({'c': [{'v': item.date,
                        'f': item.date}, {'v': item.tempInside,
                        'f': str(item.tempInside)},
                        {'v': item.tempOutside,
                        'f': str(item.tempOutside)}]})
            counter = counter + 1

        return json.dumps(jsonData, indent=4)

    def getCharts(self):
        config = ConfigClass.ConfigClass()
        nightItem = 0
        dayItem = 0
        notWorkItem = 0
        nightItemPerDay = 0
        dayItemPerDay = 0
        notWorkItemPerDay = 0

        counter = 0

        jsonData = {}
        percentage = {}
        percentage_per_day = {}
        config_data = {}

        for item in HeaterClass.__data:
            if item.mode == 0 or item.mode == -1:
                notWorkItem = notWorkItem + 1

            if item.isDay == True and item.mode == 1:
                dayItem = dayItem + 1

            if item.isDay == False and item.mode == 1:
                nightItem = nightItem + 1

        percentage['day'] = dayItem
        percentage['night'] = nightItem
        percentage['off'] = notWorkItem
        jsonData['percentage'] = percentage

        for item in HeaterClass.__data_per_day:
            if item.mode == 0 or item.mode == -1:
                notWorkItemPerDay = notWorkItemPerDay + 1

            if item.isDay == True and item.mode == 1:
                dayItemPerDay = dayItemPerDay + 1

            if item.isDay == False and item.mode == 1:
                nightItemPerDay = nightItemPerDay + 1

        percentage_per_day['day'] = dayItemPerDay
        percentage_per_day['night'] = nightItemPerDay
        percentage_per_day['off'] = notWorkItemPerDay
        jsonData['percentagePerDay'] = percentage_per_day

        temp = []
        for item in HeaterClass.__data:
            if counter % HeaterClass.__lineChartInterval == 0:

        # jsonData['rows'].append({'c':[ {'v':item.date,'f':item.date}, {'v':item.tempInside,'f':str(item.tempInside)}, {'v':item.tempOutside,'f':str(item.tempOutside)}]  })

                value = {}
                value['inside'] = item.tempInside
                value['outside'] = item.tempOutside
                value['date'] = item.date
                temp.append(value)
            counter = counter + 1
        jsonData['temp'] = temp


        config_data['mainDevice'] = int(config.isMainDeviceEnabled())
        config_data['supportDevice'] = int(config.isSupportDeviceEnabled())
        config_data['dayTemp'] = float(config.getDayTemp())
        config_data['nightTemp'] = float(config.getNightTemp())
        config_data['threshold'] = float(config.geTempThreshold())
        config_data['day1'] = int(config.getDayModeSettings(0))
        config_data['day2'] = int(config.getDayModeSettings(1))
        config_data['day3'] = int(config.getDayModeSettings(2))
        config_data['day4'] = int(config.getDayModeSettings(3))
        config_data['day5'] = int(config.getDayModeSettings(4))
        config_data['day6'] = int(config.getDayModeSettings(5))
        config_data['day7'] = int(config.getDayModeSettings(6))

        config_data['day_support1'] = int(config.getEnabledSupportDeviceSettings(0))
        config_data['day_support2'] = int(config.getEnabledSupportDeviceSettings(1))
        config_data['day_support3'] = int(config.getEnabledSupportDeviceSettings(2))
        config_data['day_support4'] = int(config.getEnabledSupportDeviceSettings(3))
        config_data['day_support5'] = int(config.getEnabledSupportDeviceSettings(4))
        config_data['day_support6'] = int(config.getEnabledSupportDeviceSettings(5))
        config_data['day_support7'] = int(config.getEnabledSupportDeviceSettings(6))

        jsonData['settings'] = config_data

        return jsonData
