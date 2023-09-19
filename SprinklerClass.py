#!/usr/bin/python
# -*- coding: utf-8 -*-
import ConfigClass
import EventClass
import ActionThread
import AlarmClass
import time


class SprinklerClass(object):

    __Max_num_of_sprinklers = 3

    # must be global static because auto-sprinklers may be triggered
    # manually from different object
    __force_auto_water = False
    __autowater = False

    def __init__(self):
        self.__state = 0
        self.__timestamp = 0

    def setSprinklerForceAuto(self):
        SprinklerClass.__force_auto_water = True

    def __controlSprinkler(self, ctrlType=0, ctrlParam='-1'):
        alarm = AlarmClass.AlarmClass()
        threadTask = ActionThread.ActionThread()
        config = ConfigClass.ConfigClass()

        # make sure all sprinklers are disabled - only one sprinkler can be enable in the same time

        sensors = config.getDeviceSensors('sprinkler')
        for item in sensors:
            sensor = item[1]
            id = item[0]
            url_off = alarm.getUpdateUrl(sensor, 0)
            threadTask.addTask(ActionThread.Task('request',
                               ActionThread.RequestParam(url_off)))
            threadTask.addTask(ActionThread.Task('clear',
                               ActionThread.UpdateParam('sprinkler',
                               id)))

    # enable one sprinkler device

        if ctrlType != 0:
            sensor = config.getDeviceSensor('sprinkler', ctrlParam)
            url_on = alarm.getUpdateUrl(sensor, 1)
            threadTask.addTask(ActionThread.Task('request',
                               ActionThread.RequestParam(url_on)))
            threadTask.addTask(ActionThread.Task('set',
                               ActionThread.UpdateParam('sprinkler',
                               ctrlParam)))

        threadTask.addTask(ActionThread.Task('notify',
                           ActionThread.NotifyParam()))
        threadTask.start()
        threadTask.suspend()

    def setSprinklerOn(self, param='-1'):
        self.__controlSprinkler(1, param)

    def setSprinklerOff(self):
        self.__controlSprinkler(0)
        SprinklerClass.__autowater = False
        SprinklerClass.__force_auto_water = False

    def manageSprinklerState(
        self,
        curr_week_day,
        curr_hour,
        curr_min,
        ):
        returnState = False
        config = ConfigClass.ConfigClass()
        duration = int(config.getDurationTime()) * 60
        currentTS = time.time()
        print ("---------------AutoWater Begin")
        if SprinklerClass.__autowater == False:
            self.__state = 0
            self.__timestamp = currentTS
            print ("---------------AutoWaterOff")
            if config.isStartTime(curr_week_day, curr_hour, curr_min) \
                or SprinklerClass.__force_auto_water == True:
                print ("---------------Time or force = " + str(SprinklerClass.__force_auto_water))
                SprinklerClass.__autowater = True

        if SprinklerClass.__autowater == True and currentTS >= self.__timestamp \
            + self.__state * duration:
            self.__state = self.__state + 1
            if self.__state <= SprinklerClass.__Max_num_of_sprinklers:
                print ("---------------ON :" + str(self.__state))
                self.setSprinklerOn(str(self.__state))
                returnState = True
            else:
                returnState = False
                self.setSprinklerOff()

        return returnState

    def getSettings(self):
        config = ConfigClass.ConfigClass()
        jsonData = {}
        jsonData['duration'] = config.getDurationTime()
        jsonData['startTime'] = config.getStartTime()
        jsonData['globalEnable'] = config.getGlobalEnable()
        jsonData['day1'] = config.getLocalEnable(0)
        jsonData['day2'] = config.getLocalEnable(1)
        jsonData['day3'] = config.getLocalEnable(2)
        jsonData['day4'] = config.getLocalEnable(3)
        jsonData['day5'] = config.getLocalEnable(4)
        jsonData['day6'] = config.getLocalEnable(5)
        jsonData['day7'] = config.getLocalEnable(6)
        return jsonData
