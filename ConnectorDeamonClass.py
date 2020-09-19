import threading
import requests
import ConfigClass
import APIClass
import CryptClass
import json





#------------------------------------------------------------------------------------------------------------------------
class ConnectorDeamonClass(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
	#TODO: get ID and url(remote) from configuration
	self.__url = "http://192.168.1.3/register"
	self.__id="00000567"
        self.__stopEvent = False

    def stop(self):
        self.__stopEvent = True

    def run(self):
	apiObj = APIClass.APIClass()
	crypt = CryptClass.CryptClass()
	reg_data = {'action': 'registration'}
	req = json.dumps(reg_data)
	headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

	while (not self.__stopEvent):
	    try:
		response = requests.post(self.__url, data=crypt.EncodeWithId(self.__id,req), headers=headers)
		postData = crypt.DecodeWithId(response.text)
		postData = postData[:postData.rfind("}")+1]
		req = apiObj.invoke(json.loads(postData))
	    except:
		req = json.dumps(reg_data)
