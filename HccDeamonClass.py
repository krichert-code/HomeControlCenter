#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests
import threading
import time
import datetime
import ConfigClass
import RadioClass
import CalendarClass
import WeatherClass
import HeaterClass
import ActionClass
import SprinklerClass
import EnergyClass
import DBClass
import RPi.GPIO as GPIO
import json
import AlarmClass
import traceback
import logging


class Alarm:

    def __init__(self):
        self.__config = ConfigClass.ConfigClass()
        self.__calendar = CalendarClass.CalendarClass()
        self.__playing = False

    def __compareTime(self, date):
        hour = datetime.datetime.now().time().hour
        minute = datetime.datetime.now().time().minute
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
        stop_time_obj = datetime.datetime.strptime(start_time, '%H:%M')
        stop_time_obj = stop_time_obj \
            + datetime.timedelta(minutes=duration)
        stop_time = stop_time_obj.strftime('%H:%M')

        radioChannel = self.__config.getAlarmSetting('channel')
        volume = self.__config.getAlarmSetting('volume')
        policy = self.__config.getAlarmSetting('day_policy')
        alarmOnHoliday = \
            self.__config.getAlarmSetting('alarm_on_holiday')
        curr_day = datetime.datetime.now().strftime('%d')
        curr_month = datetime.datetime.now().strftime('%m')

        playRadio = True

    # disable alarm if value is = 'disable' or alarm is set on 'week_day' and now is weekend

        if policy == 'disabled' or policy == 'week_day' \
            and datetime.datetime.today().weekday() >= 5:
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
            curr_day = datetime.datetime.now().strftime('%d')
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
                curr_week_day = datetime.datetime.today().weekday()
                curr_hour = int(datetime.datetime.now().strftime('%H'))
                curr_min = int(datetime.datetime.now().strftime('%M'))
                self.__heater.manageHeaterState(curr_week_day,
                        curr_hour, curr_min)
        except e:
            traceback.print_exc()
            logging.error('HEATER EXCEPT:' + str(e))
            print("Heater exception : " + str(e))


class Weather:

    def __init__(self):
        weather = WeatherClass.WeatherClass()
        self.__day = 0
        self.__hour = 0
        self.__weatherFiles = 0

        # Below counter is needed to generate weather files not exactly when new day/hour,
            # but some time later because data are not available.

        self.__counter = 0
        try:
            weather.generateFiles(weather.WeatherDailyFile
                                  | weather.WeatherHourlyFile
                                  | weather.WeatherCurrentFile)
        except:
            logging.error('WEATHER EXCEPT:')
            print("__________wather excetion")

    def timeEvent(self):
        try:
            weather = WeatherClass.WeatherClass()
            curr_day = datetime.datetime.now().strftime('%d')
            curr_hour = datetime.datetime.now().strftime('%H')

            if self.__day != curr_day:
                self.__day = curr_day
                self.__weatherFiles = self.__weatherFiles \
                    | weather.WeatherDailyFile \
                    | weather.WeatherHourlyFile
                self.__counter = 200
                weather.clearRainIndicator()

            if self.__hour != curr_hour:
                self.__hour = curr_hour
                self.__weatherFiles = self.__weatherFiles \
                    | weather.WeatherCurrentFile
                self.__counter = 200

            if self.__weatherFiles != 0 and self.__counter == 0:
                weather.generateFiles(self.__weatherFiles)
                self.__weatherFiles = 0
                weather.updateRainIndicator()

            if self.__counter > 0:
                self.__counter = self.__counter - 1
        except Exception:

            logging.error('WEATHER1 EXCEPT:')
            #print( e.message)
            self.__day = curr_day
            self.__hour = curr_hour
            self.__weatherFiles = 0
            self.__counter = 200


class Sprinkler:

    def __init__(self):
        self.__sprinkler = SprinklerClass.SprinklerClass()
        self.__config = ConfigClass.ConfigClass()

    def timeEvent(self, tick):
        try:

        # manage sprinkler state once per 45 sec

            if tick % 35 == 0:
                curr_week_day = datetime.datetime.today().weekday()
                curr_hour = int(datetime.datetime.now().strftime('%H'))
                curr_min = int(datetime.datetime.now().strftime('%M'))
                self.__sprinkler.manageSprinklerState(curr_week_day,
                        curr_hour, curr_min)
        except Exception:
            #print e.message
            logging.error('SPRINKLER EXCEPT:')
            print("__________sprinkler excetion")


class Messages:

    __diff_calendar_timestamp = 86400

    def __init__(self):

        # self.events = ActionClass.ActionClass()
        # self.config = ConfigClass.ConfigClass()

        self.lastStates = {}
        self.lastSendEventDate = ''
        self.currSendEventDate = ''

    def sendSms(
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
            logging.error('MESSAGE EXCEPT:')
            status = 'ERROR'

        return status

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
                    and len(item.messageId) > 0:

                # send message

                    phones = config.getPhoneNumbers()
                    text = config.getSmsMessage(item.messageId,
                            item.state)
                    token = config.getSmsToken()

                    for to in phones:
                        result = self.sendSms(token, to, text)
                        if result == 'OK':
                            update = True

            # update last state if at least one message was send succesfully

                    if update == True:
                        print( item.state)
                        self.lastStates[name] = item.state
        except Exception as e:
            print("__________message excetion")
            #print str(e)
            logging.error('MESSAGE EXCEPT:' + str(e))

    def __calendarEventMessage(self):
        calendar = CalendarClass.CalendarClass()
        config = ConfigClass.ConfigClass()
        curr_time = datetime.datetime.now().strftime('%H:%M')
        sendMessage = False

        # logging.error('SMS ' +str(config.getCalendarReminderEnabled()))
        # logging.error("SMS: "+ config.getCalendarReminderTime())

        if config.getCalendarReminderEnabled() == True and curr_time \
            == config.getCalendarReminderTime():
            events = calendar.getEventsData()
            currTS = time.time()
            text = ''
            logging.error('SMS currTime: ' + str(currTS))

            for event in events:
                eventTS = \
                    time.mktime(datetime.datetime.strptime(event.date,
                                '%Y-%m-%d').timetuple())

            # if event is tomorrow then send it

                logging.error('SMS some events: ' + str(eventTS))

                if eventTS - currTS <= self.__diff_calendar_timestamp \
                    and eventTS - currTS > 0:
                    if sendMessage == True:
                        text = text + ' , '
                    else:
                        text = event.date + ': '

                    self.currSendEventDate = event.date
                    text = text + event.desc
                    sendMessage = True
                    logging.error('SMS text events: ' + text)

            if sendMessage == True and self.currSendEventDate \
                != self.lastSendEventDate:
                self.lastSendEventDate = self.currSendEventDate
                sendMessage = False
                phones = config.getPhoneNumbers()
                token = config.getSmsToken()
                for to in phones:
                    logging.error('SMS send to: ' + to)
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
        self.__energyProducedForMonth = 0
        self.__curr_week_day = datetime.datetime.today().weekday()

    def timeEvent(self, tick):
        try:
            curr_week_day = datetime.datetime.today().weekday()

        # get energy once per 30min

            if tick % 1800 == 0:
                energyValues = self.__energy.getCurrentProduceEnergy()
                for item in energyValues['energy']:
                    if item['type'] == 'today' and item['status'] \
                        == 'OK':
                        self.__lastGoodValue = int(item['power'])
                        self.__energyProducedForMonth = \
                            datetime.datetime.today().month

            if self.__curr_week_day != curr_week_day:

            # update total value for current month using today produced energy

                if self.__energyProducedForMonth != 0:
                    energyForMonth = \
                        self.__db.getEnergyPerMonth(self.__energyProducedForMonth)['energy'
                            ]
                    energyForMonth = energyForMonth \
                        + self.__lastGoodValue
                    self.__db.updateEnergy(self.__energyProducedForMonth,
                            energyForMonth)
                self.__energyProducedForMonth = 0
                self.__lastGoodValue = 0
                self.__curr_week_day = curr_week_day
        except Exception:

            logging.error('ENERGY EXCEPT:')
            print("_____________Energy exception (HCC deamon)")
            #print e.message


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


class SelfActivateAlarmSystem:

    def __init__(self):
        self.__config = ConfigClass.ConfigClass()

    def timeEvent(self, tick):
        alarm = AlarmClass.AlarmClass()


        # if last activate sensor was one of the self activiation sensor then activate alarm

# ------------------------------------------------------------------------------------------------------------------------

class HccDeamonClass(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.__stopEvent = False

    def stop(self):
        self.__stopEvent = True

    def run(self):
        logging.basicConfig(filename='/media/usb0/hcc.log')
                            #encoding='utf-8', level=logging.ERROR)
                            #format='%(asctime)s %(message)s')
                            #datefmt='%m/%d/%Y %I:%M:%S %p')
        logging.error('Started')
        timerTick = 0
        config = ConfigClass.ConfigClass()
        speaker = Speaker()
        alarm = Alarm()
        calendar = Calendar()
        weather = Weather()
        heater = Heater()
        messages = Messages()
        sprinkler = Sprinkler()
        energy = Energy()
        status = Status()

        while not self.__stopEvent:
            try:
                alarm.timeEvent()
                speaker.timeEvent()
                calendar.timeEvent()
                weather.timeEvent()
                heater.timeEvent(timerTick)
                messages.timeEvent(timerTick)
                sprinkler.timeEvent(timerTick)
                energy.timeEvent(timerTick)
                status.timeEvent(timerTick)
                time.sleep(1)
                timerTick = timerTick + 1
            except e:
                logging.error('ENERGY EXCEPT:')
                logging.error(e.message)
