#!/usr/bin/python

import requests
import CryptClass
import json
import HeaterClass

id = "00000567"

crypt = CryptClass.CryptClass()
data = {'action': 'toggleCec'}
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}




#---------------------------------------------------------------------------------
#80 - PROXY
#8090 - local network

url = "http://192.168.1.3/restApi"
r = requests.post(url, data=crypt.EncodeWithId(id,json.dumps(data)), headers=headers)
print r.text
postData = crypt.DecodeWithId(r.text)
postData = postData[:postData.rfind("}")+1]
req = json.loads(postData)
print req
