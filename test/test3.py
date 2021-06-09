import CryptClass
import json
import ConfigClass
import RoomClass
import APIClass

api = APIClass.APIClass()
c = RoomClass.RoomClass()

req = {}
#req['ip'] = "192.168.1.49"
#req['ip'] = "192.168.1.26"
#req['ip'] = "192.168.1.14"

#api.APItoggleLight(req)
print api.APIGetRooms("")