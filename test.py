import CalendarClass
import WeatherClass
import requests
import json
import copy
#import xbmc

def getRadio():
    get_volume_req = "/jsonrpc?request={%22jsonrpc%22:%222.0%22,%22method%22:%22Application.GetProperties%22,%22params%22:{%22properties%22:[%22volume%22]},%22id%22:1}"
    play = {"jsonrpc":"2.0","id":"1","method":"Player.Open","params":{"item":{"directory":"PLAY_REQUEST"}}}
    set_volume_req = "/jsonrpc?request={%22jsonrpc%22: %222.0%22, %22method%22: %22Application.SetVolume%22, %22params%22: {%22volume%22: VOLUME_VALUE}, %22id%22: 1}"
    get_files_req = {"jsonrpc" : "2.0", "method" : "Files.GetDirectory", "params" : { "directory" : "PATH", "media" : "files" }, "id" : 1}

    get_state = {"jsonrpc" : "2.0", "method" :"Player.GetItem", "params" : { "properties" : ["title","artist"], "playerid" : 0 }, "id" : 1}



    volume = {"jsonrpc" : "2.0", "method" : "Application.SetVolume", "params" : {"volume" : 52}, "id" : 1}
    test={"jsonrpc" : "2.0", "method" : "PVR.GetChannels", "params" : {"channelgroupid" : 2},  "id" : 1}


    try:
        req = "http://192.168.1.3:8080/jsonrpc"

	post_data = copy.deepcopy(get_state)
	#post_data['params']['item']['directory'] = "/media/usb0/Muzyka/Jennifer Lopez/"
	headers = {'content-type': 'application/json'}


        r = requests.post(req, data=json.dumps(post_data), headers=headers )


	print r.url
	print r.text
    except requests.exceptions.RequestException as e:
        req = None


def getSpotifyObject(self, directory="plugin://plugin.audio.spotify/"):
    get_state = {"jsonrpc": "2.0", "method": "Files.GetDirectory", "params": {"directory":"plugin://plugin.audio.spotify/", "media":"files"}, "id": "1"}
    get_state["params"]["directory"] = directory
    try:
        req = "http://192.168.1.3:8080/jsonrpc"

	post_data = copy.deepcopy(get_state)
	headers = {'content-type': 'application/json'}


        r = requests.post(req, data=json.dumps(post_data), headers=headers )

	print r.url
	print r.text
    except requests.exceptions.RequestException as e:
        req = None



def getWeather():

    #get_state = {"jsonrpc" : "2.0", "method" :"Addons.GetAddons", "params": {"type": "xbmc.addon.video", "content": "video","enabled": True,"properties": ["name", "fanart", "thumbnail", "description"]},"id": 1}

#spotify search items
    get_state = {"jsonrpc": "2.0", "method": "Files.GetDirectory", "params": {"directory":"plugin://plugin.audio.spotify/?action=search", "media":"files"}, "id": "1"}
    #get_state = {"jsonrpc": "2.0", "method": "Files.GetDirectory", "params": {"directory":"plugin://plugin.audio.spotify/?action=search_artists&artistid='roxette'", "media":"files"}, "id": "1"}
    #get_state = {"jsonrpc": "2.0", "method": "Files.GetDirectory", "params": {"directory":"plugin://plugin.audio.spotify/?action=search_tracks&trackid='november'", "media":"files"}, "id": "1"}
    #get_state = {"jsonrpc": "2.0", "method": "Files.GetDirectory", "params": {"directory":"plugin://plugin.audio.spotify/?action=search&trackid='november'", "media":"files"}, "id": "1"}

#get items from directory
    #get_state = {"jsonrpc": "2.0", "method": "Files.GetDirectory", "params": {"directory":"plugin://plugin.audio.spotify/", "media":"files"}, "id": "1"}
    #get_state = {"jsonrpc": "2.0", "method": "Files.GetDirectory", "params": {"directory":"plugin://plugin.audio.spotify/?action=browse_playlist&ownerid=spotify&playlistid=37i9dQZF1DX4pq3ejIlJu2", "media":"files"}, "id": "1"}
#play
    #get_state = { "jsonrpc":"2.0", "method":"Player.Open", "params":{ "item":{"directory":"plugin://plugin.audio.spotify/?action=browse_playlist&ownerid=spotify&playlistid=37i9dQZF1DX4pq3ejIlJu2" } }, "id":1 }
    #get_state = { "jsonrpc":"2.0", "method":"Player.Open", "params":{ "item":{"directory":"plugin://plugin.audio.spotify/?action=search_tracks&trackid='november'" } }, "id":1 }

#----------------------youtube------------------------
#    get_state = { "jsonrpc":"2.0", "method":"Player.Open", "params":{ "item":{"file":"plugin://plugin.video.youtube/play/?screensaver=true&video_id=TzU4fntZYnY" } }, "id":1 }
#    get_state = { "jsonrpc":"2.0", "method":"Player.Open", "params":{ "item":{"file":"plugin://plugin.video.youtube/play/?play=1&&order=default&playlist_id=RDEMDs8vWIQKMflBG8QUQQaUrw" } }, "id":1 }


    try:
        req = "http://192.168.1.3:8080/jsonrpc"

	post_data = copy.deepcopy(get_state)
	headers = {'content-type': 'application/json'}


        r = requests.post(req, data=json.dumps(post_data), headers=headers )


	print r.url
	print r.text
    except requests.exceptions.RequestException as e:
        req = None


def stations():
        req = "https://koleo.pl/api/v2/main/stations"
	h = {'X-KOLEO-Version': '1', 'X-KOLEO-Client': 'Node-1'}
	r = requests.get(req, headers = h)
	print r.text.encode(encoding='UTF-8',errors='strict')

def j():
	warszawa = { 'type': 'station', 'id': '33605', 'slug': 'warszawa-centralna' }
	wroclaw = { 'type': 'station', 'id': '60103', 'slug': 'wroclaw-glowny' }

        req = "https://koleo.pl/api/v2/main/connections"
	h = {'X-KOLEO-Version': '1', 'X-KOLEO-Client': 'Node-1'}
#	d = {'query[start_station]': 'gdansk-rebiechowo', 'query[end_station]': 'gdansk-wrzeszcz', 'query[date]': '31-03-2019+10:45:00'}
	d = {'query[start_station]': 'gdansk-rebiechowo', 'query[end_station]': 'gdynia-glowna', 'query[date]': '31-03-2019+10:45:00'}
	r = requests.get(req, headers = h, data = d)
	print r.text.encode(encoding='UTF-8',errors='strict')
	res = json.loads(r.text)
	for con in res['connections']:
	    t = con['departure']
	    t = t[t.find('T')+1:]
	    hour = t[:t.find(':')]
	    t = t[t.find(':')+1:]
	    minute = t[:t.find(':')]
	    print hour + "-" + minute

	

getWeather()
#getRadio()
#stations()
#j()



