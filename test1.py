import SprinklerClass
import CalendarClass
import ConfigClass
import time
import datetime
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


#sms send test for calendar
c = CalendarClass.CalendarClass()
conf = ConfigClass.ConfigClass()

lastSendEventDate = ""
currSendEventDate = ""
curr_time = datetime.datetime.now().strftime('%H:%M')

if conf.getCalendarReminderEnabled() == True and curr_time == conf.getCalendarReminderTime():

    #c.generateFiles()
    events = c.getEventsData(0)
    sendMessage = False
    text = ""
    currTS = time.time()
    for event in events:
	eventTS = time.mktime(datetime.datetime.strptime(event.date, "%Y-%m-%d").timetuple())
	# if event is tomorrow then send it
        if (eventTS - currTS <= 86400):
	    if sendMessage == True:
		text = text + " , "
	    else:
		text = event.date + ": "
		currSendEventDate = event.date
	    text = text + event.desc
	    sendMessage = True

    if sendMessage == True and currSendEventDate <> lastSendEventDate:
	lastSendEventDate = currSendEventDate
	print text

