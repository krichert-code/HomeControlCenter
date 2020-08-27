import ConfigClass
import EventClass
import requests
import json
import os
import time
import copy

class StationClass:
    def __init__(self, id, name, post_data):
        self.id = id
        self.name = name
        self.post_data = post_data

class Mp3Class:
    def __init__(self, file, label, type):
	self.file = file
	self.label = label
	if (type == "file"):
	    self.icon = "img/play.png"
	    self.action = "PlayMp3"
	    self.box = "infoBox"
	else:
	    self.icon = "img/folder.png"
	    self.action = "Chdir"
	    self.box = "content"

        
        
class RadioClass(object):
    __stations = []
    __settings = ""
    __current_directory = ""
    __headers        = {'content-type': 'application/json'}
    __play_req       = {"jsonrpc":"2.0","id":"1","method":"Player.Open","params":{"item":{"file":"PLAY_REQUEST"}}}
    __play_req_dir   = {"jsonrpc":"2.0","id":"1","method":"Player.Open","params":{"item":{"directory":"PLAY_REQUEST"}}}
    __stop_req       = {"jsonrpc":"2.0","method":"Player.Stop","params":{"playerid":1},"id":"1"}
    __get_volume_req = {"jsonrpc":"2.0", "method":"Application.GetProperties","params":{"properties":["volume"]},"id":1}
    __get_event_req  = {"jsonrpc" : "2.0", "method" :"Player.GetItem", "params" : { "properties" : ["title","artist"], "playerid" : 1 }, "id" : 1}
    __set_volume_req = {"jsonrpc" : "2.0", "method" : "Application.SetVolume", "params" : {"volume" : 0}, "id" : 1}
    __get_player_state_req = {"jsonrpc" : "2.0", "method" : "Player.GetActivePlayers", "id" : 1}
    __get_files_req = {"jsonrpc" : "2.0", "method" : "Files.GetDirectory", "params" : { "directory" : "PATH", "media" : "files" }, "id" : 1}

    __get_pvr_channels = {"jsonrpc" : "2.0", "method" : "PVR.GetChannels", "params" : {"channelgroupid" : 2},  "id" : 1}
#    __play_req_pvr   = {"jsonrpc":"2.0","id":"1","method":"Player.Open","params":{"item":{"channelid":"PLAY_REQUEST"}}}

    # Depricatated get method : 
    #__set_volume_req = "/jsonrpc?request={%22jsonrpc%22: %222.0%22, %22method%22: %22Application.SetVolume%22, %22params%22: {%22volume%22: VOLUME_VALUE}, %22id%22: 1}"
    #__get_event_req = "params%22:%20{%20%22properties%22:%20[%22title%22,%22artist%22],%20%22playerid%22:%201%20},%20%22id%22:%221%22}"
    #__get_volume_req = "/jsonrpc?request={%22jsonrpc%22:%222.0%22,%22method%22:%22Application.GetProperties%22,%22params%22:{%22properties%22:[%22volume%22]},%22id%22:1}"
    #__stop_req = "/jsonrpc?request={%22jsonrpc%22:%222.0%22,%22method%22:%22Player.Stop%22,%22params%22:{%20%22playerid%22:1},%22id%22:%221%22}"                    
    #__play_req = "/jsonrpc?request={%22jsonrpc%22:%222.0%22,%22id%22:%221%22,%22method%22:%22Player.Open%22,%22params%22:{%22item%22:{%22file%22:%22PLAY_REQUEST%22}}}

    def __init__(self):
        config = ConfigClass.ConfigClass()
        id = 0
        
        if len(RadioClass.__stations) == 0:
            RadioClass.__settings = config.getRadioSettings()
	    
            for name in config.getRadioStationsName():
                req = config.getRadioURL(name)

		post_data = copy.deepcopy(RadioClass.__play_req)
		post_data['params']['item']['file'] = req
                station = StationClass(id, name, post_data)
                RadioClass.__stations.append( station )
                id = id + 1

    def __getPlayerVolume(self):
        req = self.__getRadioDevice() + "/jsonrpc"

        payload = RadioClass.__get_volume_req
        volume = requests.post(req, data=json.dumps(payload), headers=RadioClass.__headers, verify = False, timeout = 3)            

        data = json.loads(volume.text)
        value = data['result']['volume']
	return value

    def __getRadioDevice(self):
        return "http://" + RadioClass.__settings 

    def __getRadioStation(self,name):
        for station in RadioClass.__stations:
            if station.name == name:
		break
        return station
            
    def getPVRRadioStations(self):
	post_data = copy.deepcopy(RadioClass.__get_pvr_channels)

        req = self.__getRadioDevice() + "/jsonrpc"
        resp = requests.post(req, data=json.dumps(post_data), headers=RadioClass.__headers, verify = False, timeout = 10)
        data = json.loads(resp.text)
	return data['result']['channels']

    def getRadioStations(self):        
        return RadioClass.__stations
        
    def getParentDirectory(self):
	directory = RadioClass.__current_directory
	if (directory[len(directory)-1] == '/'):
	    directory = directory[:directory.rfind("/")]
	directory = directory[:directory.rfind("/")]
	return directory

    def getCurrentDirectory(self):
	return RadioClass.__current_directory

    def getFiles(self, path = ""):
	files = []
        config = ConfigClass.ConfigClass()

	post_data = copy.deepcopy(RadioClass.__get_files_req)
	if (len(path) == 0):
	    path = config.getMp3Directory()

	RadioClass.__current_directory = path
        post_data['params']['directory'] = path

        req = self.__getRadioDevice() + "/jsonrpc"
        resp = requests.post(req, data=json.dumps(post_data), headers=RadioClass.__headers, verify = False, timeout = 10)
        data = json.loads(resp.text)
        items = data['result']['files']
        for item in items:
	    element = Mp3Class(item['file'], item['label'], item['filetype'])
	    files.append( element )
	files.sort(key=lambda x: x.label, reverse=False)
	return files

    def playMp3File(self, file):
	isDirectory = os.path.isdir(file)
	if (isDirectory == False):
	    post_data = copy.deepcopy(RadioClass.__play_req)
    	    post_data['params']['item']['file'] = file
	else:
	    post_data = copy.deepcopy(RadioClass.__play_req_dir)
    	    post_data['params']['item']['directory'] = file

        try:
            req = self.__getRadioDevice() + "/jsonrpc"
            requests.post(req, data=json.dumps(post_data), headers=RadioClass.__headers, verify = False, timeout = 5)            
	    time.sleep(1)	    
        except:
            req = None                

    def getRadioPlayRequest(self, name):
        station = self.__getRadioStation(name)
        try:
            req = self.__getRadioDevice() + "/jsonrpc"
            requests.post(req, data=json.dumps(station.post_data), headers=RadioClass.__headers, verify = False, timeout = 10)            
	    time.sleep(1)	    
        except:
            req = None                

    def getRadioStopRequest(self):
        try:
            req = self.__getRadioDevice() + "/jsonrpc"
	    payload = RadioClass.__stop_req
	    for idx in range(0, 2):
		payload['params']['playerid'] = idx
        	requests.post(req, data=json.dumps(payload), headers=RadioClass.__headers, verify = False, timeout = 3)            
		time.sleep(1)
        except:
            req = None                
    
    def setRadioVolume(self, volume):
        try:
            req = self.__getRadioDevice() + "/jsonrpc"
    	    payload = RadioClass.__set_volume_req
	    payload['params']['volume'] = volume
            volume = requests.post(req, data=json.dumps(payload), headers=RadioClass.__headers, verify = False, timeout = 3)            
        except requests.exceptions.RequestException as e:
            req = None                


    def getRadioVolumeUpRequest(self):        
        try:
	    new_value = self.__getPlayerVolume() + 5

            if new_value > 100:
		new_value = 100
	    self.setRadioVolume(new_value)
        except requests.exceptions.RequestException as e:
            req = None                
        
    def getRadioVolumeDownRequest(self):
        try:
	    new_value = self.__getPlayerVolume() - 5
            if new_value < 0:
		new_value = 0
	    self.setRadioVolume(new_value)
        except requests.exceptions.RequestException as e:
            req = None                

    def isPlayerEnabled(self):
	isEnabled = False

        try:
            req = self.__getRadioDevice() + "/jsonrpc"
	    payload = RadioClass.__get_player_state_req
            event = requests.post(req, data=json.dumps(payload), headers=RadioClass.__headers, verify = False, timeout = 3)            
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
    
        req = self.__getRadioDevice() + "/jsonrpc"
        payload = RadioClass.__get_event_req	

        for idx in range(0, 2):
	    try:
		payload['params']['playerid']=idx
		event = requests.post(req, data=json.dumps(payload), headers=RadioClass.__headers, verify = False, timeout = 3)            
    		data = json.loads(event.text)

    		if len(data['result']['item']['title']) > 0:
	    	    event_text = data['result']['item']['title']
    		elif len(data['result']['item']['label']) > 0:
	    	    event_text = data['result']['item']['label']

		if len(event_text) > 0:
		    break
	    except:
		pass
	    
        if len(event_text) > 0:
	    # get volume to present next to title
	    volume = self.__getPlayerVolume()
    	    event_text = event_text + "[" + str(volume) + " %]"
	    state = EventClass.EventClass(event_text, "", id)
	    state.setEventIcon('radio')                
	    events.append(state)

        return events

        