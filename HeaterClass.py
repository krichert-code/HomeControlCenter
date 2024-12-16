#!/usr/bin/python
# -*- coding: utf-8 -*-
import ConfigClass
import AlarmClass
import EventClass
import SwitchClass
import ActionThread
from datetime import datetime
import json
import traceback
import DBClass
import threading


class HeaterParam(object):

    def __init__(self):
        self.timeOffSampleCount = 0
        self.timeOnDaySampleCount = 0
        self.timeOnNightSampleCount = 0
    
    def initializeSamples(self, timeOnDay, timeOnNight, timeOff):
        self.timeOffSampleCount = timeOff
        self.timeOnDaySampleCount = timeOnDay
        self.timeOnNightSampleCount = timeOnNight

    def updateTimeOff(self):
        self.timeOffSampleCount = self.timeOffSampleCount + 1
    def updateTimeOnDay(self):
        self.timeOnDaySampleCount = self.timeOnDaySampleCount + 1
    def updateTimeOnNight(self):
        self.timeOnNightSampleCount = self.timeOnNightSampleCount + 1
    def getData(self):
        return (self.timeOffSampleCount,self.timeOnDaySampleCount,self.timeOnNightSampleCount)
    def clearData(self):
        self.timeOffSampleCount = 0
        self.timeOnDaySampleCount = 0
        self.timeOnNightSampleCount = 0
    def getPercentStatistics(self):
        total = self.timeOffSampleCount + self.timeOnDaySampleCount + self.timeOnNightSampleCount
        return (self.timeOffSampleCount / total, self.timeOnDaySampleCount / total, 
                self.timeOnNightSampleCount /total)


class HeaterClass(object):
    # static data - states and statistics

    __singletonInit = False
    __mutex = None
    __dayMode = False
    __lastState = -1
    __lastSupportState = -1

    __data = []
    __data_per_day = HeaterParam()
    __data_per_total = HeaterParam()
    __heaterOnToday = 0

    # Defines (state and statistics)

    __StateOn = 1
    __StateOff = 0
    __StateUnknown = -1

    # Stored data buffer size - data to generate charts

    __maxDataBuffer = 10000

    # How offent data should be stored in buffer [min]

    __storeDataInterval = 60

    def __init__(self):
        if (HeaterClass.__singletonInit == False):            
            HeaterClass.__singletonInit = True                        
            HeaterClass.__mutex = threading.Lock()

            self.__storeDataCounter = 0
            db = DBClass.DBClass()
            stats = db.getHeaterStats()
            HeaterClass.__data_per_total.initializeSamples(stats[0][0], stats[0][1], stats[0][2])
            
            tempEntries = db.getTemeperatureEntries()
            for item in tempEntries:
                HeaterClass.__data.append((item[0], item[1], str(item[2])))
            
            
    def __getTemperatureFromDevice(self, thermType):
        config = ConfigClass.ConfigClass()
        alarm = AlarmClass.AlarmClass()
        thermDevices = alarm.getTemperature()
        temperature = 0
        isTemepratureInit = False
        thermalElements = 1
        status = 0
        mode = ""

        if thermDevices['error'] != 0:
            status = 1
        else:
            thermData = config.getFirstThermDevices(thermType)
            mode = thermData['mode']
            while thermData['error'] == 0:
                for item in thermDevices['temperature']:
                    if thermData['name'] == item['name']:
                        try:
                            tempValue = round(float(item['value'])
                                    + float(thermData['offset']), 2)
                        except:
                            status = 1
                            tempValue = 0

                        if isTemepratureInit == False:
                            temperature = tempValue
                            isTemepratureInit = True
                        elif thermData['mode'] == 'max' and tempValue \
                            > temperature or thermData['mode'] == 'min' \
                            and tempValue < temperature:
                            temperature = tempValue
                        elif thermData['mode'] == 'avg' \
                            or isTemepratureInit == False:
                            temperature = (temperature + tempValue)                                

                        thermalElements = thermalElements + 1
                        break
                thermData = config.getNextThermDevices(thermType)
            
            if (mode == 'avg'):
                temperature = temperature / thermalElements

        return (status, temperature)

    def getCurrentTemperatureInside(self):
        heater = {}
        (status, temp) = self.__getTemperatureFromDevice('thermometerInside')
        if status == 0:
            heater['status'] = 'OK'
        else:
            heater['status'] = 'ERROR'

        heater['temp'] = '%.1f' % temp
        heater['time'] = datetime.now().strftime('%H:%M:%S')
        heater['mode'] = 'day'
        if HeaterClass.__dayMode == False:
            heater['mode'] = 'night'

        return heater

    def getCurrentTemperature(self):
        heater = {}
        (status, temp) = self.__getTemperatureFromDevice('thermometerInside')
        if status == 0:
            heater['statusInside'] = 'OK'
        else:
            heater['statusInside'] = 'ERROR'

        heater['tempInside'] = '%.1f' % temp

        (status, temp) = self.__getTemperatureFromDevice('thermometerOutside')
        if status == 0:
            heater['statusOutside'] = 'OK'
        else:
            heater['statusOutside'] = 'ERROR'

        heater['tempOutside'] = '%.1f' % temp

        heater['time'] = datetime.now().strftime('%H:%M:%S')
        heater['mode'] = 'day'
        if HeaterClass.__dayMode == False:
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
        alarm = AlarmClass.AlarmClass()

        dayTemp = float(config.getDayTemp())
        nightTemp = float(config.getNightTemp())
        threshold = float(config.geTempThreshold())

        isDayMode = config.isDayMode(dayOfWeek, hour)
        isMainDeviceEnable = config.isMainDeviceEnabled()
        sensor = config.getDeviceSensors('heater')[0]

        isSupportedDeviceMode = config.isSupportedDeviceEnabled(dayOfWeek, hour)
        isSupportedDeviceEnable = config.isSupportDeviceEnabled()

        # New day - reset statistics per day
        if hour == 0 and minute < 2:
            HeaterClass.__heaterOnToday = 0
            HeaterClass.__data_per_day.clearData()

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
        (status, temp) = self.__getTemperatureFromDevice('thermometerInside')
        if status != 0:
            return

        # Update current mode (day or night mode)
        if HeaterClass.__dayMode != isDayMode:
            # if mode has changed set heater state as 'unknown'(-1)
            HeaterClass.__lastState = HeaterClass.__StateUnknown
        HeaterClass.__dayMode = isDayMode

        # Main heat source control
        if (isMainDeviceEnable == False):
            # turn off heater
            url = alarm.getUpdateUrl(sensor[1], 0)
            self.__mainHeatSourceControl(url, 'clear', sensor[0])
            HeaterClass.__lastState = HeaterClass.__StateOff
        elif (isDayMode == True and temp + threshold <= dayTemp) \
            or (isDayMode == False and temp + threshold <= nightTemp):

            # turn on heater
            url = alarm.getUpdateUrl(sensor[1], 1)
            #if HeaterClass.__lastState == HeaterClass.__StateOff \
            #    or HeaterClass.__lastState \
            #    == HeaterClass.__StateUnknown:
            #    self.__mainHeatSourceControl(url, 'set', sensor[0])
            self.__mainHeatSourceControl(url, 'set', sensor[0])
            HeaterClass.__lastState = HeaterClass.__StateOn
        elif (isDayMode == True and temp >= dayTemp + threshold) \
            or (isDayMode == False and temp >= nightTemp + threshold) \
            or (HeaterClass.__lastState == HeaterClass.__StateUnknown):

            # turn off heater
            url = alarm.getUpdateUrl(sensor[1], 0)
            #if HeaterClass.__lastState == HeaterClass.__StateOn \
            #    or HeaterClass.__lastState \
            #    == HeaterClass.__StateUnknown:
            #    self.__mainHeatSourceControl(url, 'clear', sensor[0])
            self.__mainHeatSourceControl(url, 'clear', sensor[0])
            HeaterClass.__lastState = HeaterClass.__StateOff


        # Update statistics
        self.__storeDataCounter = self.__storeDataCounter + 1

        if HeaterClass.__lastState == HeaterClass.__StateOn:
            HeaterClass.__heaterOnToday = HeaterClass.__heaterOnToday \
                + 1
            if (HeaterClass.__dayMode == True):
                HeaterClass.__data_per_total.updateTimeOnDay()
                HeaterClass.__data_per_day.updateTimeOnDay()
            else:
                HeaterClass.__data_per_total.updateTimeOnNight()
                HeaterClass.__data_per_day.updateTimeOnNight()
        else:
            HeaterClass.__data_per_total.updateTimeOff()
            HeaterClass.__data_per_day.updateTimeOff()

        # Store data statistics to local database - once per defined interval (currently it means once per 1h)
        if self.__storeDataCounter % HeaterClass.__storeDataInterval \
            == 0:
            # read from external temperature sensor
            (status, tempOutside) = self.__getTemperatureFromDevice('thermometerOutside')
            if status != 0:
                return
            db = DBClass.DBClass()

            HeaterClass.__data.append((temp, tempOutside, datetime.now().strftime('%H:%M %d/%m/%y')))

            # store to database once per 1 hour
            db.addTemperatureEntry(temp, tempOutside)
            db.addHeaterEntry(HeaterClass.__data_per_total.getData()[0], HeaterClass.__data_per_total.getData()[1], 
                HeaterClass.__data_per_total.getData()[2])

            if len(HeaterClass.__data) > HeaterClass.__maxDataBuffer:
                HeaterClass.__data.pop(0)
            db.deleteTemepratureOldEntries()


    def getHeaterInfo(self):
        config = ConfigClass.ConfigClass()
        nightItem = 0
        dayItem = 0
        notWorkItem = 0
        nightItemPerDay = 0
        dayItemPerDay = 0
        notWorkItemPerDay = 0

        counter = 0
        limiter = int(len(HeaterClass.__data) / 150)
        limiter = limiter + 1
        begin = len(HeaterClass.__data) - 100

        jsonData = {}
        percentage = {}
        percentage_per_day = {}
        config_data = {}

        percentage['off'] = HeaterClass.__data_per_total.getData()[0]
        percentage['day'] = HeaterClass.__data_per_total.getData()[1]
        percentage['night'] = HeaterClass.__data_per_total.getData()[2]        
        jsonData['percentage'] = percentage

        percentage_per_day['off'] = HeaterClass.__data_per_day.getData()[0]
        percentage_per_day['day'] = HeaterClass.__data_per_day.getData()[1]
        percentage_per_day['night'] = HeaterClass.__data_per_day.getData()[2]        
        jsonData['percentagePerDay'] = percentage_per_day

        temp = []
        for item in HeaterClass.__data:
            if (counter % limiter == 0):
            #if (begin < 0 or (begin > 0 and counter > begin)):
                value = {}
                value['inside'] = item[0]
                value['outside'] = item[1]
                value['date'] = item[2]
                temp.append(value)
            counter = counter + 1
            #if (counter == 200):
            #    break

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
