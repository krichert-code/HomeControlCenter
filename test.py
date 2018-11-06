import CalendarClass
import WeatherClass

print "TESTS"
x = CalendarClass.CalendarClass()
y = WeatherClass.WeatherClass()

y.getWeatherForecast()

obj = x.getEventsData()

for event in obj:
    print event.name
