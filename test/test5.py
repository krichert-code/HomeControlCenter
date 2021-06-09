import requests
import EnergyClass
from HccDeamonClass import Messages
import json

import ActionClass

#req = "https://mysecurity.eufylife.com/api/v1/passport/login"
#headers = {}
#post_data = {"email": "krzysiek.richert@gmail.com", "password": "Krizo80!"}
#r = requests.post(req, data=json.dumps(post_data), headers=headers )
#print r

#mess= Messages()
#mess.sendSms("JDJhJDEyJEtyREhBYWttOE1XVmYwSVRDUERrOS51WUxrRVhFUEM2a09XaUVXUmlTZ0x6YVNuc1puZHU2", "505200871", "test")
#print "dsdas"


ev = EnergyClass.EnergyClass()
print ev.getCurrentProduceEnergy()
