import ConfigClass
import EventClass
import requests
import json

class StationClass:
    def __init__(self, id, name, url):
        self.id = id
        self.name = name
        self.url = url
        
        
class RadioClass(object):
    __stations = []
    __settings = ""    
    __play_req = "/jsonrpc?request={%22jsonrpc%22:%222.0%22,%22id%22:%221%22,%22method%22:%22Player.Open%22,%22params%22:{%22item%22:{%22file%22:%22PLAY_REQUEST%22}}}"
    __stop_req = "/jsonrpc?request={%22jsonrpc%22:%222.0%22,%22method%22:%22Player.Stop%22,%22params%22:{%20%22playerid%22:1},%22id%22:%221%22}"
    __get_volume_req = "/jsonrpc?request={%22jsonrpc%22:%222.0%22,%22method%22:%22Application.GetProperties%22,%22params%22:{%22properties%22:[%22volume%22]},%22id%22:1}"
    __set_volume_req = "/jsonrpc?request={%22jsonrpc%22: %222.0%22, %22method%22: %22Application.SetVolume%22, %22params%22: {%22volume%22: VOLUME_VALUE}, %22id%22: 1}"
    __get_event_req = "/jsonrpc?request={%22jsonrpc%22:%20%222.0%22,%20%22method%22:%20%22Player.GetItem%22,%20%22params%22:%20{%20%22properties%22:%20[%22title%22,%22artist%22],%20%22playerid%22:%201%20},%20%22id%22:%221%22}"
    __get_player_state_req = "/jsonrpc?request={%22jsonrpc%22:%222.0%22,%22method%22:%22Player.GetActivePlayers%22,%22id%22:1}"
                    
    def __init__(self):
        config = ConfigClass.ConfigClass()
        id = 0
        
        if len(RadioClass.__stations) == 0:
            RadioClass.__settings = config.getRadioSettings()
	    
            for name in config.getRadioStationsName():
                req = config.getRadioURL(name)
		url = RadioClass.__play_req
		url = url.replace("PLAY_REQUEST", req)
                station = StationClass(id, name, url)
                RadioClass.__stations.append( station )
                id = id + 1
            
    def getRadioStations(self):        
        return RadioClass.__stations
        
    def getRadioDevice(self):
        return "http://" + RadioClass.__settings 
    
    def getRadioPlayRequest(self, name):
        station = self.getRadioStation(name)
        return self.getRadioDevice() + station.url

    def getRadioStopRequest(self):
        return self.getRadioDevice() + RadioClass.__stop_req
                            
    def getRadioStation(self,name):
        for station in RadioClass.__stations:
            if station.name == name:
                break        
        return station
    
    def setRadioVolume(self, volume):
        try:
            req = self.getRadioDevice() + RadioClass.__set_volume_req
            req = req.replace("VOLUME_VALUE", str(volume))
            requests.get(req, verify = False, timeout = 3)                
        except requests.exceptions.RequestException as e:
            req = None                

    def getRadioVolumeUpRequest(self):        
        req = self.getRadioDevice() + RadioClass.__get_volume_req
        try:
            volume = requests.get(req, verify = False, timeout = 3)            
            data = json.loads(volume.text)
            new_value = data['result']['volume'] + 5
            if new_value <= 95:
                req = self.getRadioDevice() + RadioClass.__set_volume_req
                req = req.replace("VOLUME_VALUE", str(new_value))
                requests.get(req, verify = False, timeout = 3)                
        except requests.exceptions.RequestException as e:
            req = None                
        
    def getRadioVolumeDownRequest(self):
        req = self.getRadioDevice() + RadioClass.__get_volume_req
        try:
            volume = requests.get(req, verify = False, timeout = 3)            
            data = json.loads(volume.text)
            new_value = data['result']['volume'] - 5
            if new_value >= 0:
                req = self.getRadioDevice() + RadioClass.__set_volume_req
                req = req.replace("VOLUME_VALUE", str(new_value))
                requests.get(req, verify = False, timeout = 3)                
        except requests.exceptions.RequestException as e:
            req = None                

    def isPlayerEnabled(self):
	isEnabled = False

        try:
            req = self.getRadioDevice() + RadioClass.__get_player_state_req
            event = requests.get(req, verify = False, timeout = 3)            
            data = json.loads(event.text)
            if len(data['result']) > 0:
		isEnabled = True
        except:
            isEnabled = False
        finally:                    
            return isEnabled


    def getEventsData(self, id):
        events = []
	event_text = ""
        try:
            req = self.getRadioDevice() + RadioClass.__get_event_req
            event = requests.get(req, verify = False, timeout = 3)            
            data = json.loads(event.text)

            if len(data['result']['item']['title']) > 0:
		event_text = data['result']['item']['title']
            elif len(data['result']['item']['label']) > 0:
		event_text = data['result']['item']['label']
	    
	    if len(event_text) > 0:
		req = self.getRadioDevice() + RadioClass.__get_volume_req
    		volume = requests.get(req, verify = False, timeout = 3)            
        	data = json.loads(volume.text)
        	event_text = event_text + "[" + str(data['result']['volume']) + " %]"
		state = EventClass.EventClass(event_text, "", id)
		state.setEventIcon('radio')                
		events.append(state)
        except requests.exceptions.RequestException as e:
            events = []                
        finally:                    
            return events

        