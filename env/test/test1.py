import SprinklerClass
import CalendarClass
import ConfigClass
import AlarmClass
import time
import datetime
import RadioClass
import InfoClass
import SwitchClass
import RoomClass
import socket
import fcntl
import struct
import sys
from datetime import date



# sprinkler test
#s = SprinklerClass.SprinklerClass()
#while(1):
#    curr_week_day = datetime.datetime.today().weekday()
#    curr_hour = int(datetime.datetime.now().strftime('%H'))
#    curr_min = int(datetime.datetime.now().strftime('%M'))
#    print "------check : " + str(curr_hour)+" : "+str(curr_min)
#    s.manageSprinklerState(curr_week_day, curr_hour, curr_min)

#    time.sleep(60)


#r = InfoClass.InfoClass()
#radio = RadioClass.RadioClass()
#radio.playPVRChannel(46)

#result = r.getInfoData()
#print result
#result = radio.playPVRChannel(46)

#result = radio.getEventsData(0)
#print result
#print radio.toggleCEC()



r = SwitchClass.SwitchClass()
print r.changeSwitchState("192.168.1.180","off")
#print r.toggleSwitchState("192.168.1.26")
#print r.getSwitchInfo("192.168.1.26")
#print r.discoveryDevices()


#r =  RoomClass.RoomClass()
#print r.getRoomsData()

