import ConfigClass
import WeatherClass
import HeaterClass
import RadioClass

class InfoClass:
    def __init__(self):
        pass
    def getInfoData(self):
            config = ConfigClass.ConfigClass()
            weather = WeatherClass.WeatherClass()
            heater = HeaterClass.HeaterClass()
	    radio = RadioClass.RadioClass()

            infoObj = {}
            if config.getAlarmSetting('day_policy') == 'disable':
                infoObj['alarm_state'] = "Alarm wylaczony"
		infoObj['alarm_state_value'] = 1
            elif config.getAlarmSetting('day_policy') == 'week_day':
                infoObj['alarm_state'] = "Alarm wlaczony na dni tygodnia"
		infoObj['alarm_state_value'] = 2
            else:
                infoObj['alarm_state'] = "Alarm wlaczony"
		infoObj['alarm_state_value'] = 3

            infoObj['alarm_start'] = config.getAlarmSetting('start_time')
	    infoObj['alarm_stop'] = config.getAlarmSetting('stop_time')
	    infoObj['alarm_channel'] = config.getAlarmSetting('channel')

            if weather.rainOccured() == False:
                infoObj['rain'] = "Dzisiaj nie zanotowano opadu"
                infoObj['rain_value'] = 0
            else:
                infoObj['rain'] = "Dzisiaj zanotowano opady"
                infoObj['rain_value'] = 1



	    infoObj['alarm_channels'] = radio.getPVRRadioStations()
	    infoObj['alarm_volume']   = config.getAlarmSetting('volume')

            infoObj['heater_time'] = heater.getHeaterStatistic()

	    return infoObj