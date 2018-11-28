#!/usr/bin/python

from flask import Flask, render_template, request, make_response
import WeatherClass
import CalendarClass
import ActionClass
import ConfigClass
import RadioClass
import SprinklerClass

app = Flask(__name__)

@app.route("/")
def start():
	return render_template('page.html')

@app.route("/weather")
def weather():
	obj = WeatherClass.WeatherClass()	
	return render_template('weather.html', weather = obj.getCurrentWeather())

@app.route("/weatherForecast")
def weatherForecast():
	obj = WeatherClass.WeatherClass()
	return render_template('weatherForecast.html', weather = obj.getWeatherForecast())

@app.route("/tempInside")
def temperatureInside():
	obj = WeatherClass.WeatherClass()	
	return render_template('heater.html', heater = obj.getCurrentTemperatureInside())


@app.route("/action")
@app.route("/action/<actionName>")
def action(actionName=""):
	action = ActionClass.ActionClass()
	return render_template('events.html', events = action.getEventsData(actionName))

@app.route("/sprinkler", methods=['GET', 'POST'])	
@app.route("/sprinkler/<actionName>", methods=['GET', 'POST'])
def sprinkler(actionName=""):
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
	radio = RadioClass.RadioClass()
	if len(actionName) == 0:
		return render_template('radio.html', radioMenu = radio.getRadioStations())
	else:
		stationName = request.args.get('param')		
		action = ActionClass.ActionClass()
		return render_template('events.html', events = action.getEventsData(actionName, stationName, action.ActionEventRadio))
	
@app.route("/menu")
def menu():	
	return render_template('menu.html')


if (__name__ == "__main__"):
	config = ConfigClass.ConfigClass()
	config.initializeConfigData()
	app.run(host="0.0.0.0", port = 8002)
