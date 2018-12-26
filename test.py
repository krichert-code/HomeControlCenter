import CalendarClass
import WeatherClass
import requests
import json

def getRadio():
    get_volume_req = "/jsonrpc?request={%22jsonrpc%22:%222.0%22,%22method%22:%22Application.GetProperties%22,%22params%22:{%22properties%22:[%22volume%22]},%22id%22:1}"

    set_volume_req = "/jsonrpc?request={%22jsonrpc%22: %222.0%22, %22method%22: %22Application.SetVolume%22, %22params%22: {%22volume%22: VOLUME_VALUE}, %22id%22: 1}"

    volume = {"jsonrpc" : "2.0", "method" : "Application.SetVolume", "params" : {"volume" : 52}, "id" : 1}
    test={"jsonrpc" : "2.0", "method" : "Player.GetActivePlayers", "id" : 1}


    try:
        req = "http://192.168.1.3:8080/jsonrpc"
	payload = volume
	headers = {'content-type': 'application/json'}


        r = requests.post(req, data=json.dumps(payload), headers=headers )

        #r = requests.get(q1 ,  verify = False, timeout = 3 )
	print r.url
	print r.text
    except requests.exceptions.RequestException as e:
        req = None

print "TESTS"
getRadio()
