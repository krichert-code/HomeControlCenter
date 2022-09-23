#!/usr/bin/python
# -*- coding: utf-8 -*-
import AlarmClass
import DBClass


class EnergyClass(object):

    __db = None

    def __init__(self):
        EnergyClass.__db = DBClass.DBClass()

    def getCurrentProduceEnergy(self):
        energy = {}
        try:
            alarm = AlarmClass.AlarmClass()
            energy = alarm.getEnergy()
        except:
            print("___________energy exception")

        return energy

    def getTotalEnergy(self):
        try:
            value = str(EnergyClass.__db.getTotalEnergy())
        except:
            value = 0
        return value

    def getTotalPerMonth(self):
        energy = []
        for month in range(1, 13):
            energy.append(EnergyClass.__db.getEnergyPerMonth(month)['energy'
                          ])
        return energy

    def getTotalPerMonthPrevValue(self):
        energy = []
        for month in range(1, 13):
            energy.append(EnergyClass.__db.getEnergyPerMonth(month)['prev_energy'
                          ])
        return energy


