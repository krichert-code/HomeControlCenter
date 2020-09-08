import CryptClass
import json

st = '{"action":"temperature"}'



d = json.loads(st)

print d['action']

#obj = CryptClass.CryptClass();
#test = obj.Encode("ABBA")
#obj.Decode(test)



