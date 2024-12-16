#!/usr/bin/python
# -*- coding: utf-8 -*-
import sqlalchemy as db
from datetime import datetime
import os.path

class DBClass(object):

    def __init__(self):
        if os.path.isfile('hcc.db') == False:
            print("Creating databae")
            engine = db.create_engine('sqlite:///hcc.db', echo=True)

            metadata_energy = db.MetaData()
            metadata_temp = db.MetaData()
            metadata_heater = db.MetaData()

            energy = db.Table('EnergyData', metadata_energy, db.Column('Id',
                              db.Integer()), db.Column('month_name',
                              db.String(255), nullable=False),
                              db.Column('energy', db.Integer(),
                              default=0),
                              db.Column('prev_energy', db.Integer()))
            metadata_energy.create_all(engine)  # Creates the table

            heater = db.Table('HeaterData', metadata_heater, db.Column('heaterOnDay', db.Integer(),
                              default=0), db.Column('heaterOnNight', db.Integer(),
                              default=0), db.Column('heaterOff', db.Integer(),
                              default=0) )
            metadata_heater.create_all(engine)  # Creates the table

            temperature = db.Table('TemperatureData', metadata_temp, db.Column('inside',
                              db.String(20), nullable=False),db.Column('outside',
                              db.String(20), nullable=False),db.Column('date',
                              db.String(20), nullable=False) )
            metadata_temp.create_all(engine)  # Creates the table

            connection = engine.connect()
            query = db.insert(energy)
            values_list = [
                {'Id': '1', 'month_name': 'Styczen', 'energy': 0, 'prev_energy' : 0},
                {'Id': '2', 'month_name': 'Luty', 'energy': 0, 'prev_energy' : 0},
                {'Id': '3', 'month_name': 'Marzec', 'energy': 0, 'prev_energy' : 0},
                {'Id': '4', 'month_name': 'Kwiecien', 'energy': 0, 'prev_energy' : 0},
                {'Id': '5', 'month_name': 'Maj', 'energy': 0, 'prev_energy' : 0},
                {'Id': '6', 'month_name': 'Czerwiec', 'energy': 0, 'prev_energy' : 0},
                {'Id': '7', 'month_name': 'Lipiec', 'energy': 0, 'prev_energy' : 0},
                {'Id': '8', 'month_name': 'Sierpien', 'energy': 0, 'prev_energy' : 0},
                {'Id': '9', 'month_name': 'Wrzesien', 'energy': 0, 'prev_energy' : 0},
                {'Id': '10', 'month_name': 'Pazdziernik', 'energy': 0, 'prev_energy' : 0},
                {'Id': '11', 'month_name': 'Listopad', 'energy': 0, 'prev_energy' : 0},
                {'Id': '12', 'month_name': 'Grudzien', 'energy': 0, 'prev_energy' : 0},
                ]
            ResultProxy = connection.execute(query, values_list)


            query = db.insert(heater).values(heaterOnDay = 0, heaterOnNight = 0, heaterOff = 0)
            ResultProxy = connection.execute(query)
            connection.commit()

#        else:
#            engine = db.create_engine('sqlite:///hcc.db')
#            connection = engine.connect()

    def addHeaterEntry(self, offTime, dayOnTime, nightOnTime):
        engine = db.create_engine('sqlite:///hcc.db')
        connection = engine.connect()

        metadata = db.MetaData()
        metadata.reflect(bind=engine)
        heaterData = db.Table('HeaterData', metadata, autoload=True,
                          autoload_with=engine)
        
        query = db.update(heaterData).values(heaterOff=offTime, 
            heaterOnDay=dayOnTime, heaterOnNight=nightOnTime)

        results = connection.execute(query)
        connection.commit()

    def addTemperatureEntry(self, inside, outside):
        engine = db.create_engine('sqlite:///hcc.db')
        connection = engine.connect()

        metadata = db.MetaData()
        metadata.reflect(bind=engine)
        temperature = db.Table('TemperatureData', metadata, autoload=True,
                          autoload_with=engine)
        query = db.insert(temperature).values(outside=str(outside), inside=str(inside), 
                          date=datetime.now().strftime('%H:%M %d/%m/%y'))
        results = connection.execute(query)
        connection.commit()

    def getTemeperatureEntries(self):
        data = []
        engine = db.create_engine('sqlite:///hcc.db')
        connection = engine.connect()

        metadata = db.MetaData()
        metadata.reflect(bind=engine)

        temperature = db.Table('TemperatureData', metadata, autoload=True,
                          autoload_with=engine)
        results = \
            connection.execute(temperature.select()).fetchall()
        return results

    def getHeaterStats(self):
        data = []
        engine = db.create_engine('sqlite:///hcc.db')
        connection = engine.connect()

        metadata = db.MetaData()
        metadata.reflect(bind=engine)
        heaterStats = db.Table('HeaterData', metadata, autoload=True,
                          autoload_with=engine)

        results = \
            connection.execute(heaterStats.select()).fetchall()

        return results

    def deleteTemepratureOldEntries(self):
        pass

    def updateEnergy(self, monthId, value):
        engine = db.create_engine('sqlite:///hcc.db')
        connection = engine.connect()

        metadata = db.MetaData()
        metadata.reflect(bind=engine)
        energy = db.Table('EnergyData', metadata, autoload=True,
                          autoflush=True, autoload_with=engine)

        query = db.update(energy).values(energy=value)
        query = query.where(energy.columns.Id == monthId)
        results = connection.execute(query)
        connection.commit()

    def updatePrevEnergy(self, monthId, value):
        engine = db.create_engine('sqlite:///hcc.db')
        connection = engine.connect()

        metadata = db.MetaData()
        metadata.reflect(bind=engine)
        energy = db.Table('EnergyData', metadata, autoload=True,
                          autoload_with=engine)
        query = db.update(energy).values(prev_energy=value)
        query = query.where(energy.columns.Id == monthId)
        results = connection.execute(query)
        connection.commit()

    def getEnergyPerMonth(self, monthId):
        engine = db.create_engine('sqlite:///hcc.db')
        connection = engine.connect()

        metadata = db.MetaData()
        metadata.reflect(bind=engine)
        energy = db.Table('EnergyData', metadata, autoload=True,
                          autoload_with=engine)
        results = \
            connection.execute(energy.select().where(energy.columns.Id
                               == monthId)).fetchall()

        return results[0]

    def getTotalEnergy(self):
        engine = db.create_engine('sqlite:///hcc.db')
        connection = engine.connect()

        val = 0
        metadata = db.MetaData()
        metadata.reflect(bind=engine)
        energy = db.Table('EnergyData', metadata, autoload=True,
                          autoload_with=engine)
        results = connection.execute(energy.select()).fetchall()
        for item in results:
            val = val + item[2]
        return val
