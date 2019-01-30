#!/usr/bin/python

from flask import Flask, render_template, request, make_response, session
import WeatherClass
import CalendarClass
import ActionClass
import ConfigClass
import RadioClass
import SprinklerClass
import ScheduleClass
import HccDeamonClass
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') or 'e5ac358c-f0bf-11e5-9e39-d3b532c10a28'

def isAuthNeed():
	result = True
	idx = request.remote_addr.find("192.168.1.")
	if (idx == 0):
	    print "______________________idx -ok"
	    result = False
	else:
    	    try:
    		if (session['passwd'] == 1):
		    print "______________________passwd -ok"
		    result = False
	    except:
		result = True

	return result

@app.route("/")
def start():
	if (isAuthNeed() == True):
	    return render_template('auth.html')
	return render_template('page.html')


@app.route("/auth", methods=['POST'])
def auth():
    passwd = request.form['passwd']
    if (passwd == "Test1"):
	session['passwd'] = 1
	return render_template('page.html')
    else:
	return "Authentication ERROR"

@app.route("/weather")
def weather():
	if (isAuthNeed() == True):
	    return "Authentication ERROR"

	obj = WeatherClass.WeatherClass()	
	return render_template('weather.html', weather = obj.getCurrentWeather())

@app.route("/weatherForecast")
def weatherForecast():
	if (isAuthNeed() == True):
	    return "Authentication ERROR"

	obj = WeatherClass.WeatherClass()
	return render_template('weatherForecast.html', weather = obj.getWeatherHourlyForecast(), dailyweather = obj.getWeatherDailyForecast())

@app.route("/tempInside")
def temperatureInside():
	if (isAuthNeed() == True):
	    return "Authentication ERROR"

	obj = WeatherClass.WeatherClass()	
	return render_template('heater.html', heater = obj.getCurrentTemperatureInside())

@app.route("/action/<actionName>")
def action(actionName):
	if (isAuthNeed() == True):
	    return "Authentication ERROR"

	action = ActionClass.ActionClass()
	return render_template('events.html', events = action.getEventsData(actionName))

@app.route("/sprinkler", methods=['GET', 'POST'])	
@app.route("/sprinkler/<actionName>", methods=['GET', 'POST'])
def sprinkler(actionName=""):
	if (isAuthNeed() == True):
	    return "Authentication ERROR"

	sprinkler = SprinklerClass.SprinklerClass()
	if len(actionName) == 0:
	    return render_template('sprinkler.html', sprinklerElements = sprinkler.getSprinklerEvents())
	else:
	    sprinklerName = request.args.get('param')		
	    action = ActionClass.ActionClass()
	    return render_template('events.html', events = action.getEventsData(actionName, sprinklerName, action.ActionEventSprinkler))

@app.route("/radio", methods=['GET', 'POST'])
@app.route("/radio/<actionName>", methods=['GET', 'POST'])
def radio(actionName=""):
	if (isAuthNeed() == True):
	    return "Authentication ERROR"

	radio = RadioClass.RadioClass()
	if len(actionName) == 0:
		return render_template('radio.html', radioMenu = radio.getRadioStations())
	else:
		stationName = request.args.get('param')		
		action = ActionClass.ActionClass()
		return render_template('events.html', events = action.getEventsData(actionName, stationName, action.ActionEventRadio))

@app.route("/mp3", methods=['GET', 'POST'])
@app.route("/mp3/<actionName>", methods=['GET', 'POST'])
def mp3(actionName=""):
	if (isAuthNeed() == True):
	    return "Authentication ERROR"

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
		return render_template('events.html', events = action.getEventsData(actionName, mp3File, action.ActionEventRadio))

@app.route("/train_schedule")
@app.route("/train_schedule/<direction>")
def train_schedule(direction="A"):
	if (isAuthNeed() == True):
	    return "Authentication ERROR"

	obj = ScheduleClass.ScheduleClass()
	switch_url = "train_schedule/"
	if direction=="A":
		switch_url = switch_url + "B"
	else:
		switch_url = switch_url + "A"
	return render_template('train_schedule.html', eventsDirA = obj.getTimetoDirection(direction), url = switch_url)

@app.route("/info")
def info():
	if (isAuthNeed() == True):
	    return "Authentication ERROR"

	config = ConfigClass.ConfigClass()
	infoObj = {}
	if config.getAlarmSetting('day_policy') == 'disabled':
		infoObj['alarm_state'] = "Alarm wylaczony"
	elif config.getAlarmSetting('day_policy') == 'week_day':
		infoObj['alarm_state'] = "Alarm wlaczony na dni tygodnia"
	else:
		infoObj['alarm_state'] = "Alarm wlaczony"
	infoObj['alarm_start'] = config.getAlarmSetting('start_time')

	if config.getEvent('rain').state == "0":
		infoObj['rain'] = "Dzisiaj nie zanotowano opadow"
	else:
		infoObj['rain'] = "Dzisiaj zanotowano opady"
	return render_template('info.html', info = infoObj)

@app.route("/menu")
def menu():	
	if (isAuthNeed() == True):
	    return "Authentication ERROR"

	return render_template('menu.html')




if (__name__ == "__main__"):
	config = ConfigClass.ConfigClass()
	config.initializeConfigData()

	hccDeamon = HccDeamonClass.HccDeamonClass()
	hccDeamon.start()

	app.run(host="0.0.0.0", port = 8000)

	hccDeamon.stop()
	hccDeamon.join()