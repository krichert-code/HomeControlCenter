﻿#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests
import threading
import time
import ConfigClass
import RadioClass
import CalendarClass
import HeaterClass
import ActionClass
import SprinklerClass
import EnergyClass
import ConfigurationInterface
import MediaInterface
import DBClass
import RPi.GPIO as GPIO
import json
import AlarmClass
import traceback
import logging
import SwitchClass
import RadioClass
import base64
import os
from datetime import date
from datetime import datetime
from datetime import timedelta
from astral.sun import sun
from astral import LocationInfo
from subprocess import Popen, PIPE

class Alarm:

    def __init__(self):
        self.__config = ConfigClass.ConfigClass()
        self.__calendar = CalendarClass.CalendarClass()
        self.__playing = False

    def __compareTime(self, date):
        hour = datetime.now().time().hour
        minute = datetime.now().time().minute
        hour_param = int(date[:date.find(':')])
        minute_param = int(date[date.find(':') + 1:])
        if hour == hour_param and minute == minute_param:
            return True
        else:
            return False

    def timeEvent(self):
        radio = RadioClass.RadioClass()

        start_time = self.__config.getAlarmSetting('start_time')
        duration = int(self.__config.getAlarmSetting('stop_time'))
        stop_time_obj = datetime.strptime(start_time, '%H:%M')
        stop_time_obj = stop_time_obj \
            + timedelta(minutes=duration)
        stop_time = stop_time_obj.strftime('%H:%M')

        radioChannel = self.__config.getAlarmSetting('channel')
        volume = self.__config.getAlarmSetting('volume')
        policy = self.__config.getAlarmSetting('day_policy')
        alarmOnHoliday = \
            self.__config.getAlarmSetting('alarm_on_holiday')
        curr_day = datetime.now().strftime('%d')
        curr_month = datetime.now().strftime('%m')

        playRadio = True

    # disable alarm if value is = 'disable' or alarm is set on 'week_day' and now is weekend

        if policy == 'disabled' or policy == 'week_day' \
            and datetime.today().weekday() >= 5:
            playRadio = False

    # disable alarm also if alarm_on_holiday = "no" and today is holiday

        for event in self.__calendar.getEventsData():
            if event.date.find(curr_month + '-' + curr_day) != -1 \
                and event.isHoliday == True and alarmOnHoliday == 'no':
                playRadio = False

        if self.__compareTime(start_time) == True and playRadio == True \
            and self.__playing == False:
            try:
                radio.playPVRChannel(int(radioChannel))
                radio.setRadioVolume(int(volume))
                self.__playing = True
            except:
                self.__playing = False
                print("____________radio error1")
                logging.error('RADIO EXCEPT:')
        elif self.__compareTime(stop_time) == True and self.__playing \
            == True:

            try:
                radio.getRadioStopRequest()
                radio.setRadioVolume(50)
                self.__playing = False
            except:
                self.__playing = True
                print ("____________radio error2")


class Speaker:

    __powerPin = 17  # wPi = 0
    __activatePin = 27  # wPi = 2

    __no_activeCounter = 0

    def __init__(self):
        try:
            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.__powerPin, GPIO.OUT)
            GPIO.setup(self.__activatePin, GPIO.OUT)

            GPIO.output(self.__powerPin, GPIO.HIGH)
            GPIO.output(self.__activatePin, GPIO.LOW)
        except:
            print("__________speaker excetion")

    def timeEvent(self):
        try:

        # power is activated by LOW

            player = RadioClass.RadioClass()
            isPlayerEnabled = player.isPlayerEnabled()
            isSpeakerActivated = GPIO.input(self.__powerPin)

            if False == isPlayerEnabled:
                self.__no_activeCounter = self.__no_activeCounter + 1

            if self.__no_activeCounter > 60 and 0 == isSpeakerActivated:
                GPIO.output(self.__powerPin, GPIO.HIGH)

            if True == isPlayerEnabled and 1 == isSpeakerActivated:
                GPIO.output(self.__powerPin, GPIO.LOW)
                time.sleep(1)
                GPIO.output(self.__activatePin, GPIO.HIGH)
                time.sleep(1)
                GPIO.output(self.__activatePin, GPIO.LOW)
                self.__no_activeCounter = 0
        except:
            logging.error('SPEAKER EXCEPT:')
            print("__________speaker excetion")


class Calendar:

    def __init__(self):
        self.__day = 0

    def timeEvent(self):
        try:
            calendar = CalendarClass.CalendarClass()
            curr_day = datetime.now().strftime('%d')
            if self.__day != curr_day:
                self.__day = curr_day
                calendar.generateFiles()
        except:
            logging.error('CALENDAR EXCEPT:')
            print("__________calendar excetion")


class Heater:

    def __init__(self):
        self.__counter = 0
        self.__heater = HeaterClass.HeaterClass()

    def timeEvent(self, tick):
        try:

        # manage heater state once per 60 sec

            if tick % 60 == 0:
                curr_week_day = datetime.today().weekday()
                curr_hour = int(datetime.now().strftime('%H'))
                curr_min = int(datetime.now().strftime('%M'))
                self.__heater.manageHeaterState(curr_week_day,
                        curr_hour, curr_min)
        except Exception as e:
            logging.error('HEATER EXCEPT: ' + str(e) + " " + traceback.format_exc())


class Sprinkler:

    def __init__(self):
        self.__sprinkler = SprinklerClass.SprinklerClass()
        self.__config = ConfigClass.ConfigClass()

    def timeEvent(self, tick):
        try:
            # manage sprinkler state once per 25 sec
            if tick % 25 == 0:
                curr_week_day = datetime.today().weekday()
                curr_hour = int(datetime.now().strftime('%H'))
                curr_min = int(datetime.now().strftime('%M'))
                val = self.__sprinkler.manageSprinklerState(curr_week_day,
                        curr_hour, curr_min)
                #logging.error('-------------SPRINKLER RUN :' + str(val))
        except Exception as e:
            logging.error('SPRINKLER EXCEPT: ' + str(e))


class Messages:

    __diff_calendar_timestamp = 86400

    def __init__(self):

        # self.events = ActionClass.ActionClass()
        # self.config = ConfigClass.ConfigClass()

        self.lastStates = {}
        self.lastSendEventDate = ''
        self.currSendEventDate = ''

    def __sendSmsBulk(
        self,
        apiKey,
        number,
        message,
        ):

        #apiKey = base64.b64encode("D7A6E0DC86E44ED38B298C7BBAF3A15D-02-7:m0fvQo#QDsajOhx*GoU2QyHJxLoLj")
        apiKey = base64.b64encode(apiKey.encode("utf-8"))
        headers = {'content-type': 'application/json', 'Authorization': 'Basic ' + apiKey.decode("utf-8")}
        sms = {
            'from' : 'Dom',
            'to': number,
            'body': message
        }

        status = 'OK'

        try:
            req = 'https://api.bulksms.com/v1/messages?auto-unicode=true&longMessageMaxParts=3'
            r = requests.post(req, data=json.dumps(sms), headers=headers)

            #resp = json.loads(r.text)
            #resp['responseCode']
        except:
            logging.error('MESSAGE (bulk) EXCEPT:')
            status = 'ERROR'

        return status

    def __sendSmsJustSend(
        self,
        apiKey,
        number,
        message,
        ):
        headers = {'content-type': 'application/json',
                   'App-Key': apiKey}
        sms = {
            'to': number,
            'from': 'DOM',
            'message': message,
            'bulkVariant': 'ECO',
            'doubleEncode': True,
            }
        status = 'ERROR'

        try:
            req = 'https://justsend.pl/api/rest/v2/message/send'
            r = requests.post(req, data=json.dumps(sms),
                              headers=headers)
            resp = json.loads(r.text)
            status = resp['responseCode']
        except:
            logging.error('MESSAGE (justsend) EXCEPT:')
            status = 'ERROR'

        return status

    def sendSms(
        self,
        apiKey,
        number,
        message,
        ):
        return self.__sendSmsBulk(apiKey, number, message)

    def __genericEventMessage(self, tick):

        # check if message should be send once per 1min

        update = False
        events = ActionClass.ActionClass()
        config = ConfigClass.ConfigClass()

        # get all generic event (active and inactive)

        items = events.getEvents(events.ActionEventGeneric, True, False)
        eventId = 0
        try:
            for item in items:
                update = False
                name = item.type + str(eventId)
                eventId = eventId + 1

                # add item if not exist in "last state" list

                if name not in self.lastStates:
                    self.lastStates[name] = "0"

                # if state has changed then send message (if needed) and then update last state

                if item.state != self.lastStates[name] \
                    and item.messageSend == 1:

                    # send message
                    phones = config.getPhoneNumbers()
                    if item.state == '0':
                        text = item.messageInactive
                    else:
                        text = item.messageActive
                    token = config.getSmsToken()

                    for to in phones:
                        result = self.sendSms(token, to, text)
                        #if result == 'OK':
                        #    update = True

                    # update last state if at least one message was send succesfully
                    #if update == True:
                    self.lastStates[name] = item.state
        except Exception as e:
            logging.error('MESSAGE EXCEPT:' + str(e))

    def __calendarEventMessage(self):
        calendar = CalendarClass.CalendarClass()
        config = ConfigClass.ConfigClass()
        curr_time = datetime.now().strftime('%H:%M')
        sendMessage = False

        # logging.error('SMS ' +str(config.getCalendarReminderEnabled()))
        # logging.error("SMS: "+ config.getCalendarReminderTime())

        if config.getCalendarReminderEnabled() == 'checked' and curr_time \
            == config.getCalendarReminderTime():
            events = calendar.getEventsData()
            currTS = time.time()
            text = ''
            #logging.error('SMS currTime: ' + str(currTS))

            for event in events:
                eventTS = \
                    time.mktime(datetime.strptime(event.date,
                                '%Y-%m-%d').timetuple())

                # if event is tomorrow then send it

                #logging.error('SMS eventTime=' + str(eventTS) + ' currentTime=' + str(currTS) + ' diffTime=' + str(self.__diff_calendar_timestamp) + ' ' + event.desc)

                if eventTS - currTS <= self.__diff_calendar_timestamp \
                    and eventTS - currTS > 0:
                    if sendMessage == True:
                        text = text + ' , '
                    else:
                        text = event.date + ': '

                    self.currSendEventDate = event.date
                    text = text + event.desc
                    sendMessage = True
                    #logging.error('SMS text events: ' + text)

            if sendMessage == True and self.currSendEventDate \
                != self.lastSendEventDate:
                self.lastSendEventDate = self.currSendEventDate
                sendMessage = False
                phones = config.getPhoneNumbers()
                token = config.getSmsToken()
                for to in phones:
                    #logging.error('SMS send to: ' + to)
                    result = self.sendSms(token, to, text)

    def timeEvent(self, tick):
        if tick % 20 == 0:
            self.__genericEventMessage(tick)
            self.__calendarEventMessage()


class Energy:

    def __init__(self):
        self.__db = DBClass.DBClass()
        self.__energy = EnergyClass.EnergyClass()
        self.__lastGoodValue = 0
        self.__curr_month = datetime.today().month
        self.__curr_day = datetime.today().day

    def timeEvent(self, tick):
        try:
            curr_day = datetime.today().day
            curr_month = datetime.today().month

            # get energy once per 30min
            if tick % 1800 == 0:
                energyValues = self.__energy.getCurrentProduceEnergy()
                for item in energyValues['energy']:
                    if item['type'] == 'today' and item['status'] \
                        == 'OK':
                        self.__lastGoodValue = int(item['power'])

            if self.__curr_day != curr_day:
                # update total value for current month using today produced energy
                energyForMonth = \
                    self.__db.getEnergyPerMonth(self.__curr_month)[2]

                energyForMonth = energyForMonth \
                    + self.__lastGoodValue

                self.__db.updateEnergy(self.__curr_month,
                        energyForMonth)

                # check if it's new month, then copy current value to previous_energy and clear
                if (curr_day == 1):
                    energyForMonth = \
                        self.__db.getEnergyPerMonth(curr_month)[2]
                    self.__db.updatePrevEnergy(curr_month,
                            energyForMonth)
                    self.__db.updateEnergy(curr_month,
                            0)
                    self.__curr_month = curr_month


                self.__lastGoodValue = 0
                self.__curr_day = curr_day

        except Exception as e:
            logging.error('ENERGY EXCEPT:' + str(e))


class Status:

    def __init__(self):
        self.__config = ConfigClass.ConfigClass()

    def timeEvent(self, tick):
        alarm = AlarmClass.AlarmClass()

        if tick % 5 == 0:
            try:
                statusSensors = self.__config.getDeviceSensors('status')
                inputSensors = alarm.getPresence()

                if inputSensors['error'] != 0:
                    raise Exception('Error Response',
                                    str(inputSensors['error']))

                self.__config.changeStatus('status', '0', '0')
                for statusSensor in statusSensors:
                    for inputSensor in inputSensors['presence']:
                        if statusSensor[1] == inputSensor['name'] \
                            and inputSensor['presence'] == 'on':

                # print "---------------Status on for "+ inputSensor['name']

                            self.__config.changeStatus('status',
                                    statusSensor[0], '1')
                        elif statusSensor[1] == inputSensor['name'] \
                            and inputSensor['presence'] == 'off':

                # print "---------------Status off for "+ inputSensor['name']

                            self.__config.changeStatus('status',
                                    statusSensor[0], '0')
            except:
                self.__config.changeStatus('status', '0', '1')


class ProgramAction:

    def __init__(self):
        config = ConfigClass.ConfigClass()

        self.__alarmActivatedTimestamp = 0
        self.__alarmActivatedFlag = False
        self.__lights = config.getProgramLightAction()
        self.__alarmActivatSettings = config.getAlarmActivate()
        self.__alarmTriggered = False


    def __checkIfNoBodyHome(self):
        result = False
        alarm = AlarmClass.AlarmClass()
        settings = self.__alarmActivatSettings
        currentTimestamp = time.time()

        sensors = alarm.getPresence()['presence']
        #logging.error(str(sensors))
        #print(sensors)
        for sensor in sensors:
            #todo : check if sensor exists in any room, if not then continue without checking (szambo case)
            if (sensor['name'] in settings['sensors']) and (sensor['presence'] == 'on'):
                result = True
                self.__alarmActivatedFlag = True
                self.__alarmActivatedTimestamp = currentTimestamp
            elif (sensor['name'] not in settings['sensors']) and (sensor['presence'] == 'on'):
                result = False
                self.__alarmActivatedFlag = False
                break

        #print(currentTimestamp - self.__alarmActivatedTimestamp)
        #print(int(settings['timeToActivate']) * 60)
        #print(self.__alarmActivatedFlag)
        if (currentTimestamp - self.__alarmActivatedTimestamp >= (int(settings['timeToActivate']) * 60)) and (self.__alarmActivatedFlag == True):
            return True
        else:
            return False

    def __checkIfSensorTriggered(self, sensorName):
        result = False
        alarm = AlarmClass.AlarmClass()
        sensors = alarm.getPresence()['presence']
        for sensor in sensors:
            if (sensor['name'] == sensorName) and (sensor['presence'] == 'on'):
                result = True
        return result

    def __isDuskTime(self):
        city = LocationInfo("Warsaw", "Poland")
        s = sun(city.observer, date=date.today())
        duskTimestamp = datetime.timestamp(s["dusk"])
        duskTimestamp = duskTimestamp - (2*3600)

        dawnTimestamp = datetime.timestamp(s["dawn"])

        currentTimestamp = datetime.timestamp(datetime.now())

        if (currentTimestamp > duskTimestamp or currentTimestamp < dawnTimestamp):
            return True
        else:
            return False

    def timeEvent(self, tick):
        alarmActivated = False
        lightSwitch = SwitchClass.SwitchClass()
        currentTime = datetime.now().strftime("%H:%M")
        curr_month = int(datetime.now().strftime('%m'))

        if tick % 1 == 0:
            checkIfNoBodyHome = self.__checkIfNoBodyHome()
            #logging.error(str(checkIfNoBodyHome))

            if (checkIfNoBodyHome == True) and (self.__alarmTriggered == False):
                self.__alarmTriggered = True
                logging.error("[HCC] Program class : move detected")
            elif (checkIfNoBodyHome == False and self.__alarmTriggered == True):
                alarmActivated = True
                self.__alarmTriggered = False
                logging.error("[HCC] Program class : alarm activated")
                # TODO : enable alarm automaticlly

            for light in self.__lights:
                lightInfo=lightSwitch.getSwitchInfo(light['lightIp'])
                if (lightInfo['error'] != 0):
                    continue

                if (light['state'] == 3) and (self.__isDuskTime() == False):
                    light['state'] = 0

                if ((light['validMonths'] & (1 << (curr_month-1))) == 0):
                    continue

                if (light['onAlarmActivate'] == True) and (light['triggerSensor'] != 'none') and (self.__isDuskTime() == True):
                   isTriggered = self.__checkIfSensorTriggered(light['triggerSensor'])

                   if (isTriggered):
                       if (lightInfo['data']['switch'] == 'off'):
                           lightSwitch.changeSwitchState(light['lightIp'], 'on')
                           if (light['timeMode'] == 'switch'):
                               light['switch_state'] = 1
                               logging.error("Program class light " + light['lightIp'] +" on - caused sensor activated")
                   elif (light['timeMode'] == 'switch') and (light['switch_state'] == 1) and (light['state'] != 1):
                       lightSwitch.changeSwitchState(light['lightIp'], 'off')
                       light['switch_state'] = 0
                   else:
                       light['switch_state'] = 0
                   continue

                if (light['onAlarmActivate'] == True) and (alarmActivated == True) and (self.__isDuskTime() == True):
                    lightSwitch.changeSwitchState(light['lightIp'], 'on')
                    logging.error("Program class light " + light['lightIp'] +" on - caused alarm activated")
                    continue

                if (self.__isDuskTime() == True) and (light['state'] == 0) and (light['onAlarmActivate'] == False):
                    light['state'] = 1
                    lightSwitch.changeSwitchState(light['lightIp'], 'on')
                    logging.error("Program class light " + light['lightIp'] +" on - caused dusk")
                    continue

                if (light['timeMode'] == 'on') and (light['timeOff'] == currentTime) and (light['state'] == 1) and (light['onAlarmActivate'] == False):
                    light['state'] = 3
                    lightSwitch.changeSwitchState(light['lightIp'], 'off')
                    logging.error("Program class light " + light['lightIp'] +" off - caused time off")
                    continue


class Media:

    def __init__(self):
        self.__radio = RadioClass.RadioClass()
        self.__idx = 0
        self.__playlist = []

    def initializePlaylistData(self, playlist):
        self.__idx = 0
        self.__playlist.clear()
        self.__playlist = playlist

    def timeEvent(self, tick):
        try:
            if (tick%5 != 0):
                return
            if (self.__radio.isPlayerEnabled() == False and self.__idx < len(self.__playlist) ):
                self.__radio.playYTAddonVideo(self.__playlist[self.__idx])
                self.__idx=self.__idx+1
        except Exception as e:
            logging.error('MEDIA EXCEPT: ' + str(e) + " " + traceback.format_exc())


# ------------------------------------------------------------------------------------------------------------------------

class HccDeamonClass(threading.Thread, ConfigurationInterface.ConfigurationInterface, MediaInterface.MediaInterface):

    def __init__(self):
        threading.Thread.__init__(self)
        self.__stopEvent = False
        self.__speaker = Speaker()
        self.__alarm = Alarm()
        self.__calendar = Calendar()
        self.__heater = Heater()
        self.__messages = Messages()
        self.__sprinkler = Sprinkler()
        self.__energy = Energy()
        self.__status = Status()
        self.__media = Media()
        self.__programAction = ProgramAction()

    def configurationUpdate(self):
        """Overrides ConfigurationInterface.configurationUpdate()"""
        config = ConfigClass.ConfigClass()
        config.initializeConfigData()
        print("* Configuration update")

    def mediaPlaylistUpdate(self, data = []):
        """Overrides MediaInterface.mediaPlaylistUpdate()"""
        self.__media.initializePlaylistData(data)

    def stop(self):
        self.__stopEvent = True

    def run(self):
        logging.basicConfig(handlers=[logging.FileHandler(filename="/media/usb0/hcc.log",
                                     encoding='utf-8', mode='w+')],
                            format="%(asctime)s %(levelname)s %(message)s",
                            datefmt="%F %A %T",
                            level=logging.INFO)
        log = logging.getLogger('werkzeug')

        command = ['ps -A -T | grep hcc.py']
        proc = Popen(
            command,
            shell=True,
            stdin=None,
            stdout=PIPE,
            stderr=None,
            close_fds=True,
            )

        logging.info('HCC deamon pid')
        logging.info(str(proc.communicate()[0]))
        log.setLevel(logging.ERROR)

        timerTick = 0
        while not self.__stopEvent:
            try:
                self.__alarm.timeEvent()
                self.__speaker.timeEvent()
                self.__calendar.timeEvent()
                self.__heater.timeEvent(timerTick)
                self.__messages.timeEvent(timerTick)
                self.__sprinkler.timeEvent(timerTick)
                self.__energy.timeEvent(timerTick)
                self.__status.timeEvent(timerTick)
                self.__media.timeEvent(timerTick)
                self.__programAction.timeEvent(timerTick)
                time.sleep(1)
                timerTick = timerTick + 1
            except Exception as e:
                logging.error(str(e))
