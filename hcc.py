#!/usr/bin/python

from flask import Flask, render_template, request, make_response, session, redirect, url_for
from flask_sessionstore import Session
import WeatherClass
import CalendarClass
import ActionClass
import ConfigClass
import RadioClass
import SprinklerClass
import HeaterClass
import ScheduleClass
import HccDeamonClass
import InfoClass
import os
import hashlib
import json
import re
import CryptClass

app = Flask(__name__)



@app.route("/restApi", methods=['POST'])
def restApi():

    req = {}
    crypt = CryptClass.CryptClass()
    postData = crypt.Decode(request.data)
    postData = postData[:postData.rfind("}")+1]
    req = json.loads(postData)


    if (req['action'] == "temperature"):
	obj = HeaterClass.HeaterClass()
	response = obj.getCurrentTemperatureInside()
	r = json.dumps(response)
	w = crypt.Encode(r)
	return w
    elif (req['action']=="version"):
	response = {}
	response['name'] = "Home Control Center"
	response['version'] = "1.0"
	r = json.dumps(response)
	w = crypt.Encode(r)
	return w
    elif (req['action'] == "getMediaChannels"):
        obj = RadioClass.RadioClass()
        response = {}
        response = obj.getPVRStations()
	r = json.dumps(response)
	w = crypt.Encode(r)
	return w
    elif (req['action']=="info"):
	infoObj = InfoClass.InfoClass()
	response = infoObj.getInfoData()
	r = json.dumps(response)
	w = crypt.Encode(r)
	return w
    elif (req['action']=="weather"):
        obj = WeatherClass.WeatherClass()
        response = obj.getCurrentWeather()
	r = json.dumps(response)
	w = crypt.Encode(r)
	return w
    elif (req['action']=="schedule"):
	obj = ScheduleClass.ScheduleClass()
	response = {}
	response['DirectionA'] = obj.getJsonFromKoleo('A', 0)
	response['DirectionB'] = obj.getJsonFromKoleo('B', 0)
	r = json.dumps(response)
	w = crypt.Encode(r)
	return w
    elif (req['action']=="heaterCharts"):
	obj = HeaterClass.HeaterClass()
	response = {}
	response = obj.getCharts()
	r = json.dumps(response)
	w = crypt.Encode(r)
	return w
    elif (req['action'] == "getGardenSettings"):
	obj = SprinklerClass.SprinklerClass()
	response = {}
	response = obj.getSettings()
	r = json.dumps(response)
	w = crypt.Encode(r)
	return w
    elif (req['action'] == "playMediaChannel"):
	obj = RadioClass.RadioClass()
	response = {}
	response = obj.playPVRChannel(param)
	r = json.dumps(response)
	w = crypt.Encode(r)
	return w
    elif (req['action'] == "toggleCec"):
	obj = RadioClass.RadioClass()
	response = {}
	response = obj.toggleCEC()
	r = json.dumps(response)
	w = crypt.Encode(r)
	return w
    elif (req['action']=="setGardenSettings"):
	response = {}	
	config = ConfigClass.ConfigClass()
	config.saveSettingsData(2, req)
	response['state'] = "OK"
	r = json.dumps(response)
	w = crypt.Encode(r)
	return w
    elif (req['action']=="setHeaterSettings"):
	response = {}
	config = ConfigClass.ConfigClass()
	config.saveSettingsData(1, req)
	response['state'] = "OK"
	r = json.dumps(response)
	w = crypt.Encode(r)
	return w
    elif (req['action']=="setAlarmSettings"):
	response = {}
	config = ConfigClass.ConfigClass()
	config.saveSettingsData(0, req)
	response['state'] = "OK"
	r = json.dumps(response)
	w = crypt.Encode(r)
	return w
    else:
	duration = 0
	param = ""
	if (req['action'] <> "events"):
	    if (req['action'] == "VolumeSet"):
		param=req['volume']
	    if (req['action'] == "PlayPVR"):
		param=req['channel']
	    if (req['action'] == "SprinklerOn"):
		param=str(req['id'])

	    action = ActionClass.ActionClass()
	    duration = action.performAction(req['action'],param)


	obj = ActionClass.ActionClass()
	events = obj.getEvents()
	response = {}
	resEvents = []
	for event in events:
	    row = {}
	    row['eventType'] = event.id
	    row['eventDesc'] = event.desc
	    row['eventIcon'] = event.icon
	    row['eventDate'] = event.date
	    resEvents.append(row)
	response['events'] = resEvents
	response['eventDuration'] = duration
	r = json.dumps(response)
	w = crypt.Encode(r)
	return w




if (__name__ == "__main__"):
	config = ConfigClass.ConfigClass()
	config.initializeConfigData()

	try:
	    hccDeamon = HccDeamonClass.HccDeamonClass()
	    hccDeamon.start()

	    app.run(host="0.0.0.0", port = 80)
	except Exception as e:
	    print "Cannot run application ! Critical error"

	hccDeamon.stop()
	hccDeamon.join()