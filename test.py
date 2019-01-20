import CalendarClass
import WeatherClass
import requests
import json
import copy

def getRadio():
    get_volume_req = "/jsonrpc?request={%22jsonrpc%22:%222.0%22,%22method%22:%22Application.GetProperties%22,%22params%22:{%22properties%22:[%22volume%22]},%22id%22:1}"
    play = {"jsonrpc":"2.0","id":"1","method":"Player.Open","params":{"item":{"directory":"PLAY_REQUEST"}}}
    set_volume_req = "/jsonrpc?request={%22jsonrpc%22: %222.0%22, %22method%22: %22Application.SetVolume%22, %22params%22: {%22volume%22: VOLUME_VALUE}, %22id%22: 1}"
    get_files_req = {"jsonrpc" : "2.0", "method" : "Files.GetDirectory", "params" : { "directory" : "PATH", "media" : "files" }, "id" : 1}
    get_state = {"jsonrpc" : "2.0", "method" :"Player.GetItem", "params" : { "properties" : ["title","artist"], "playerid" : 1 }, "id" : 1}

    volume = {"jsonrpc" : "2.0", "method" : "Application.SetVolume", "params" : {"volume" : 52}, "id" : 1}
    test={"jsonrpc" : "2.0", "method" : "Player.GetActivePlayers", "id" : 1}


    try:
        req = "http://192.168.1.3:8080/jsonrpc"
	payload = volume
	post_data = copy.deepcopy(play)
	post_data['params']['item']['directory'] = "/media/usb0/Muzyka/Jennifer Lopez/"
	headers = {'content-type': 'application/json'}


        r = requests.post(req, data=json.dumps(post_data), headers=headers )

        #r = requests.get(q1 ,  verify = False, timeout = 3 )
	print r.url
	print r.text
    except requests.exceptions.RequestException as e:
        req = None


getRadio()



