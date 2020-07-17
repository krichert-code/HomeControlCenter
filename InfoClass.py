import ConfigClass
import WeatherClass
import HeaterClass


class InfoClass:
    def __init__(self):
        pass
    def getInfoData(self):
            config = ConfigClass.ConfigClass()
            weather = WeatherClass.WeatherClass()
            heater = HeaterClass.HeaterClass()

            infoObj = {}
            if config.getAlarmSetting('day_policy') == 'disabled':
                infoObj['alarm_state'] = "Alarm wylaczony"
            elif config.getAlarmSetting('day_policy') == 'week_day':
                infoObj['alarm_state'] = "Alarm wlaczony na dni tygodnia"
            else:
                infoObj['alarm_state'] = "Alarm wlaczony"
            infoObj['alarm_start'] = config.getAlarmSetting('start_time')

            if weather.rainOccured() == False:
                infoObj['rain'] = "Dzisiaj nie zanotowano opadu"
            else:
                infoObj['rain'] = "Dzisiaj zanotowano opady"

            infoObj['heater_time'] = heater.getHeaterStatistic()

	    return infoObj