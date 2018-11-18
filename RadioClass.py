import ConfigClass
import requests

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
    __volume = 0
    __stop_req = "/jsonrpc?request={%22jsonrpc%22:%222.0%22,%22method%22:%22Player.Stop%22,%22params%22:{%20%22playerid%22:1},%22id%22:%221%22}"
                
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
        