#!/usr/bin/python

from flask import Flask, render_template, request, make_response
import WeatherClass
import CalendarClass
import ActionClass
import ConfigClass

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
	obj = WeatherClass.WeatherClass()	#	
	return render_template('weatherForecast.html', weather = obj.getWeatherForecast())

@app.route("/tempInside")
def temperatureInside():
	obj = WeatherClass.WeatherClass()	
	return render_template('heater.html', heater = obj.getCurrentTemperatureInside())

@app.route("/action/<actionName>")
def action(actionName):	
	action = ActionClass.ActionClass()
	calendar = CalendarClass.CalendarClass()
	allEvents = action.getEventsData(actionName) + calendar.getEventsData()		
	return render_template('events.html', events = allEvents)
	
@app.route("/sprinkler/<actionName>")
def sprinkler(actionName):
	action = ActionClass.ActionClass()
	return render_template('sprinkler.html', sprinklerStatus = action.getEventsData(actionName))
	
@app.route("/menu")
def menu():	
	return render_template('menu.html')


if (__name__ == "__main__"):
	config = ConfigClass.ConfigClass()
	config.initializeConfigData()
	app.run(host="0.0.0.0", port = 8002)
