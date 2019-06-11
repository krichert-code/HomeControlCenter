import SprinklerClass
import time
import datetime


s = SprinklerClass.SprinklerClass()

while(1):
    curr_week_day = datetime.datetime.today().weekday()
    curr_hour = int(datetime.datetime.now().strftime('%H'))
    curr_min = int(datetime.datetime.now().strftime('%M'))
    print "------check : " + str(curr_hour)+" : "+str(curr_min)
    s.manageSprinklerState(curr_week_day, curr_hour, curr_min)

    time.sleep(60)




