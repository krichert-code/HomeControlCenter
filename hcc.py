#!/usr/bin/python

from flask import Flask, render_template, request, make_response
import WeatherClass
import CalendarClass

app = Flask(__name__)

@app.route("/")
def start():
	return render_template('page.html')

@app.route("/weather")
def weather():
	obj = WeatherClass.WeatherClass()	
	return render_template('weather.html', weather = obj.getCurrentWeather())

@app.route("/tempInside")
def temperatureInside():
	obj = WeatherClass.WeatherClass()	
	return render_template('heater.html', heater = obj.getCurrentTemperatureInside())


@app.route("/calendar")
def calendarInfo():
	obj = CalendarClass.CalendarClass()			
	return render_template('events.html', events = obj.getEventsData())
	

if (__name__ == "__main__"):
	app.run(host="0.0.0.0", port = 8002)
