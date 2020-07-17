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

app = Flask(__name__)

SESSION_TYPE = 'filesystem'
PERMANENT_SESSION_LIFETIME = 120
app.config.from_object(__name__)
Session(app)


def isAuthNeed():
	config = ConfigClass.ConfigClass()
	result = True

	idx = request.remote_addr.find(config.getlocalIPmask())
	if (idx == 0):
	    result = False
	else:    	    
    	    if (session.get('passwd','0') == '1'):
	        result = False

	return result

@app.route("/")
def start():
	if (isAuthNeed() == True):
	    return render_template('auth.html')
	return render_template('page.html')


@app.route("/auth", methods=['POST'])
def auth():
    config = ConfigClass.ConfigClass()
    passwd = request.form['passwd']
    passwd = hashlib.md5(passwd).hexdigest()
    if (passwd == config.getmd5passwd()):
	session['passwd'] = '1'
	return render_template('page.html')
    else:
	return render_template('auth.html')
	#return redirect(url_for('/'))

@app.route("/weather")
def weather():
	if (isAuthNeed() == False):	
	    obj = WeatherClass.WeatherClass()	
	    return render_template('weather.html', weather = obj.getCurrentWeather())

@app.route("/weatherForecast")
def weatherForecast():
	if (isAuthNeed() == False):
	    obj = WeatherClass.WeatherClass()
    	    return render_template('weatherForecast.html', weather = obj.getWeatherHourlyForecast(), dailyweather = obj.getWeatherDailyForecast())

@app.route("/tempInside")
def temperatureInside():
	if (isAuthNeed() == False):
	    obj = HeaterClass.HeaterClass()	
	    return render_template('heater.html', heater = obj.getCurrentTemperatureInside())

@app.route("/action/<actionName>")
def action(actionName):
	if (isAuthNeed() == False):
	    action = ActionClass.ActionClass()
	    action.performAction(actionName)
	    return render_template('events.html', events = action.getEvents())

@app.route("/heater", methods=['GET', 'POST'])	
@app.route("/heater/<actionName>", methods=['GET', 'POST'])	
def heater(actionName=""):
	if (isAuthNeed() == False):
	    heater = HeaterClass.HeaterClass()
	    if len(actionName) == 0:
		return render_template('heater_stat.html')
	    elif actionName=="pieChart":
		return heater.getPercentHeatWorkChart()
	    elif actionName=="lineChart":
		return heater.getStateHeatWorkChart()


@app.route("/sprinkler", methods=['GET', 'POST'])	
@app.route("/sprinkler/<actionName>", methods=['GET', 'POST'])
def sprinkler(actionName=""):
	if (isAuthNeed() == False):
	    sprinkler = SprinklerClass.SprinklerClass()
	    if len(actionName) == 0:
		return render_template('sprinkler.html', sprinklerElements = sprinkler.getSprinklerItems())
	    else:
		action = ActionClass.ActionClass()
		sprinklerName = request.args.get('param')
		action.performAction(actionName, sprinklerName)
		return render_template('events.html', events = action.getEvents(action.ActionEventGeneric))

@app.route("/radio", methods=['GET', 'POST'])
@app.route("/radio/<actionName>", methods=['GET', 'POST'])
def radio(actionName=""):
	if (isAuthNeed() == False):
	    radio = RadioClass.RadioClass()
	    if len(actionName) == 0:
		return render_template('radio.html', radioMenu = radio.getRadioStations())
	    else:
		stationName = request.args.get('param')		
		action = ActionClass.ActionClass()
		action.performAction(actionName, stationName)
		return render_template('events.html', events = action.getEvents(action.ActionEventRadio))

@app.route("/mp3", methods=['GET', 'POST'])
@app.route("/mp3/<actionName>", methods=['GET', 'POST'])
def mp3(actionName=""):
	if (isAuthNeed() == False):
	    radio = RadioClass.RadioClass()
	    if len(actionName) == 0:
		return render_template('mp3.html', files = radio.getFiles())
	    elif actionName == "ChdirUp":
		return render_template('mp3.html', files = radio.getFiles(radio.getParentDirectory()))
	    elif actionName == "Chdir":
		path = request.args.get('param')
		return render_template('mp3.html', files = radio.getFiles(path))
	    else:
		mp3File = request.args.get('param')		
		if (mp3File == None):
		    # this is directory intead of single mp3 file
		    mp3File = radio.getCurrentDirectory()
		action = ActionClass.ActionClass()
		action.performAction(actionName, mp3File)
		return render_template('events.html', events = action.getEventsData(action.ActionEventRadio))

@app.route("/settings", methods=['GET', 'POST'])
@app.route("/settings/<pageId>", methods=['GET', 'POST'])
def settings(pageId=0):
	if (isAuthNeed() == False):
	    config = ConfigClass.ConfigClass()
	    if request.content_length > 0:
		config.saveSettingsData(int(pageId), request.form)
	    return render_template('settings.html', page = pageId,  elements = config.getSettingsData(int(pageId)))

@app.route("/train_schedule")
@app.route("/train_schedule/<direction>")
@app.route("/train_schedule/<direction>/<offset>")
def train_schedule(direction="A", offset=0):
	if (isAuthNeed() == False):
	    obj = ScheduleClass.ScheduleClass()
	    switch_url = "train_schedule/"

	    if direction=="A":
		switch_url = switch_url + "B"
	    else:
		switch_url = switch_url + "A"

	    return render_template('train_schedule.html', eventsDirA = obj.getTimetoDirection(direction, offset), url = switch_url, next_url = "train_schedule/" + direction)

@app.route("/info")
def info():
	if (isAuthNeed() == False):
	    infoObj = InfoClass.InfoClass()
	    return render_template('info.html', info = infoObj.getInfoData())

@app.route("/menu")
def menu():	
	if (isAuthNeed() == False):
	    return render_template('menu.html')


@app.route("/restApi/<cmd>")
@app.route("/restApi/<cmd>/<param>")
def restApi(cmd="version", param=""):
	if (cmd=="version"):
	    response = {}
	    response['name'] = "Home Control Center"
	    response['version'] = "1.0"
	elif (cmd=="temperature"):
	    obj = HeaterClass.HeaterClass()
	    response = obj.getCurrentTemperatureInside()
	elif (cmd=="info"):
	    infoObj = InfoClass.InfoClass()
	    response = infoObj.getInfoData()
	elif (cmd=="weather"):
	    obj = WeatherClass.WeatherClass()
	    response = obj.getCurrentWeather()
	else:
	    duration = 0
	    if (cmd <> "events"):
		action = ActionClass.ActionClass()
		duration = action.performAction(cmd,param)

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

	return json.dumps(response)



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