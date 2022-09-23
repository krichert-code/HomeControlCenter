#!/usr/bin/python
# -*- coding: utf-8 -*-
import sqlalchemy as db
import os.path

class DBClass(object):

    def __init__(self):
        if os.path.isfile('hcc.db') == False:
            engine = db.create_engine('sqlite:///hcc.db')
            connection = engine.connect()

            metadata = db.MetaData()

            energy = db.Table('EnergyData', metadata, db.Column('Id',
                              db.Integer()), db.Column('month_name',
                              db.String(255), nullable=False),
                              db.Column('energy', db.Integer(),
                              default=0),
                              db.Column('prev_energy', db.Integer()))

            metadata.create_all(engine)  # Creates the table

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
        else:
            engine = db.create_engine('sqlite:///hcc.db')
            connection = engine.connect()

    def updateEnergy(self, monthId, value):
        engine = db.create_engine('sqlite:///hcc.db')
        connection = engine.connect()

        metadata = db.MetaData()
        energy = db.Table('EnergyData', metadata, autoload=True,
                          autoload_with=engine)
        query = db.update(energy).values(energy=value)
        query = query.where(energy.columns.Id == monthId)
        results = connection.execute(query)

    def updatePrevEnergy(self, monthId, value):
        engine = db.create_engine('sqlite:///hcc.db')
        connection = engine.connect()

        metadata = db.MetaData()
        energy = db.Table('EnergyData', metadata, autoload=True,
                          autoload_with=engine)
        query = db.update(energy).values(prev_energy=value)
        query = query.where(energy.columns.Id == monthId)
        results = connection.execute(query)

    def getEnergyPerMonth(self, monthId):
        engine = db.create_engine('sqlite:///hcc.db')
        connection = engine.connect()

        metadata = db.MetaData()
        energy = db.Table('EnergyData', metadata, autoload=True,
                          autoload_with=engine)
        results = \
            connection.execute(db.select([energy]).where(energy.columns.Id
                               == monthId)).fetchall()
        return results[0]

    def getTotalEnergy(self):
        engine = db.create_engine('sqlite:///hcc.db')
        connection = engine.connect()

        val = 0
        metadata = db.MetaData()
        energy = db.Table('EnergyData', metadata, autoload=True,
                          autoload_with=engine)
        results = connection.execute(db.select([energy])).fetchall()
        for item in results:
            val = val + item['energy']
        return val
