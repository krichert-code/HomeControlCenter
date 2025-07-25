﻿#!/usr/bin/python
# -*- coding: utf-8 -*-
import ConfigClass
import HeaterClass
import RadioClass
import EnergyClass


class InfoClass:

    def __init__(self):
        pass

    def getInfoData(self):
        config = ConfigClass.ConfigClass()
        heater = HeaterClass.HeaterClass()
        radio = RadioClass.RadioClass()
        energy = EnergyClass.EnergyClass()

        infoObj = {}
        if config.getAlarmSetting('day_policy') == 'disable':
            infoObj['alarm_state'] = 'Alarm wylaczony'
            infoObj['alarm_state_value'] = 1
        elif config.getAlarmSetting('day_policy') == 'week_day':
            infoObj['alarm_state'] = 'Alarm wlaczony na dni tygodnia'
            infoObj['alarm_state_value'] = 2
        else:
            infoObj['alarm_state'] = 'Alarm wlaczony'
            infoObj['alarm_state_value'] = 3

        infoObj['alarm_start'] = config.getAlarmSetting('start_time')
        infoObj['alarm_stop'] = config.getAlarmSetting('stop_time')
        infoObj['alarm_channel'] = config.getAlarmSetting('channel')

        infoObj['alarm_channels'] = radio.getPVRRadioStations()
        infoObj['alarm_volume'] = config.getAlarmSetting('volume')

        infoObj['heater_time'] = heater.getHeaterStatistic()

        infoObj['total_energy'] = energy.getTotalEnergy()

        infoObj['total_per_month'] = energy.getTotalPerMonth()

        infoObj['total_per_month_prev_value'] = energy.getTotalPerMonthPrevValue()

        return infoObj
