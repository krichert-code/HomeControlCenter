import ConfigClass
import requests
import json

class StationClass:
    name = ""
    url = ""
    id = 0
    def __init__(self, id, name, url):
        self.id = id
        self.name = name
        self.url = "/jsonrpc?request={%22jsonrpc%22:%222.0%22,%22id%22:%221%22,%22method%22:%22Player.Open%22,%22params%22:{%22item%22:{%22file%22:%22"+url+"%22}}}" 
        
        
class RadioClass(object):
    __stations = []
    __settings = ""    
    __stop_req = "/jsonrpc?request={%22jsonrpc%22:%222.0%22,%22method%22:%22Player.Stop%22,%22params%22:{%20%22playerid%22:1},%22id%22:%221%22}"
    __get_volume_req = "/jsonrpc?request={%22jsonrpc%22:%222.0%22,%22method%22:%22Application.GetProperties%22,%22params%22:{%22properties%22:[%22volume%22]},%22id%22:1}"
    __set_volume_req = "/jsonrpc?request={%22jsonrpc%22: %222.0%22, %22method%22: %22Application.SetVolume%22, %22params%22: {%22volume%22: VOLUME_VALUE}, %22id%22: 1}"
                    
    def __init__(self):
        config = ConfigClass.ConfigClass()        
        id = 0
        
        if len(RadioClass.__stations) == 0:
            RadioClass.__settings = config.getRadioSettings()
	    
            for name in config.getRadioStationsName():
                url = config.getRadioURL(name)
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

        