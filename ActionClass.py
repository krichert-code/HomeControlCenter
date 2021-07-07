from xml.dom import minidom
import ActionThread
import EventClass
import ConfigClass
import CalendarClass
import RadioClass
import SprinklerClass
import HeaterClass
import EnergyClass
import AlarmClass
import threading
import copy


class ActionClass(object):
    ActionEventAll       = 1 << 0
    ActionEventGeneric   = 1 << 1
    ActionEventCalendar  = 1 << 2
    ActionEventRadio     = 1 << 3
    __actionEvents = []
    __mutex = None

    def __init__(self):
        self.__config = ConfigClass.ConfigClass()
        if ActionClass.__mutex == None:
            ActionClass.__mutex = threading.Lock()

    def __isEventEnable(self, events, eventID):
        if (events & eventID <> 0) or (events & ActionClass.ActionEventAll <> 0):
            return True
        else:
            return False

    def __updateEvents(self, events, filters):
        if (filters & ActionClass.ActionEventAll <> 0):
            ActionClass.__actionEvents = events
        elif len(events) > 0:
            # find events in global event list and update them, if not exist then add
            for item in events:                
                exist = False
                for global_event_item in ActionClass.__actionEvents:
                    if global_event_item.id == item.id:                                                
                        ActionClass.__actionEvents.remove(global_event_item)                        
                        break                    
                                                            
                ActionClass.__actionEvents.insert(0, item)
        else:
            for global_event_item in ActionClass.__actionEvents:
                if global_event_item.id & filters <> 0:
                    ActionClass.__actionEvents.remove(global_event_item)
                    
        
    def actionOnGate(self, param = ""):
	alarm = AlarmClass.AlarmClass()	
	threadTask = ActionThread.ActionThread()
	config = ConfigClass.ConfigClass()
	sensor = config.getDeviceSensor("gate", param)
	time = config.getDeviceSensorActionDuration("gate", param)
	url = alarm.getUpdateUrl(sensor, 1)	
	threadTask.addTask(ActionThread.Task("set", ActionThread.UpdateParam("gate",param)))
	threadTask.addTask(ActionThread.Task("request", ActionThread.RequestParam(url)))
	threadTask.addTask(ActionThread.Task("delay", ActionThread.DelayParam(time)))
	threadTask.addTask(ActionThread.Task("clear", ActionThread.UpdateParam("gate",param)))                
	threadTask.start()
	threadTask.suspend()
	return time


    def actionOnGatePerm(self, param = ""):
	alarm = AlarmClass.AlarmClass()	
	threadTask = ActionThread.ActionThread()
	config = ConfigClass.ConfigClass()
	sensor = config.getDeviceSensor("gate", param)
	time = config.getDeviceSensorActionDuration("gate", param)
	url = alarm.getUpdateUrl(sensor, 1)	
	threadTask.addTask(ActionThread.Task("set", ActionThread.UpdateParam("gate",param)))
	threadTask.addTask(ActionThread.Task("request", ActionThread.RequestParam(url)))
	threadTask.addTask(ActionThread.Task("delay", ActionThread.DelayParam(time)))

	threadTask.addTask(ActionThread.Task("request", ActionThread.RequestParam(url)))
	threadTask.addTask(ActionThread.Task("delay", ActionThread.DelayParam(2)))

	threadTask.addTask(ActionThread.Task("request", ActionThread.RequestParam(url)))

	threadTask.addTask(ActionThread.Task("clear", ActionThread.UpdateParam("gate",param)))                
	threadTask.start()
	threadTask.suspend()
	return time

                
    def actionOnSprinklerOn(self, param = ""):
	sprinkler = SprinklerClass.SprinklerClass()
	sprinkler.setSprinklerOn(param)
	return 0

    def actionOnSprinklerOff(self, param = ""):
	sprinkler = SprinklerClass.SprinklerClass()
	sprinkler.setSprinklerOff()
	return 0

    def actionOnSprinklerForceAuto(self, param = ""):
	sprinkler = SprinklerClass.SprinklerClass()
	sprinkler.setSprinklerForceAuto()
	return 5

    def actionOnPlay(self, param = ""):
        radio = RadioClass.RadioClass()
        radio.getRadioPlayRequest(param)
	return 0

    def actionOnPlayPVR(self, param = ""):
        radio = RadioClass.RadioClass()
        radio.playPVRChannel(int(param))
	return 0

    def actionOnVideoShare(self, param = ""):
        radio = RadioClass.RadioClass()
        radio.playYTAddonVideo(param)
	return 0

    def actionOnPlaySpotifyObject(self, param = ""):
        radio = RadioClass.RadioClass()
        radio.playSpotifyObject(param)
	return 0

    def actionOnPlaySpotifyDirectory(self, param = ""):
        radio = RadioClass.RadioClass()
        radio.playSpotifyDirectory(param)
	return 0

    def actionOnPlayMp3(self, param = ""):
        player = RadioClass.RadioClass()
        player.playMp3File(param)
	return 0

    def actionOnStop(self, param = ""):
        radio = RadioClass.RadioClass()
        radio.getRadioStopRequest()
	return 0

    def actionOnVolumeUp(self, param = ""):
        radio = RadioClass.RadioClass()
        radio.getRadioVolumeUpRequest() 
	return 0

    def actionOnVolumeDown(self, param = ""):
        radio = RadioClass.RadioClass()
        radio.getRadioVolumeDownRequest() 
	return 0

    def actionOnVolumeSet(self, param = ""):
        radio = RadioClass.RadioClass()
	try:
	    volume = int(param)
	except:
	    volume = 50

	radio.setRadioVolume(volume)
	return 0

    def actionOnGetActiveEvents(self, param = ""):
        # perform on timer tick from browser - currently do nothing
	return 0


#---------------------------------------------------------------------------------------------------------------
    def performAction(self,actionName="", param = ""):
	ActionClass.__mutex.acquire()

	try:
            method_name = 'actionOn' + actionName
            method = getattr(self, method_name)
            response = method(param)
	except:
	    response = "invalid command"

	ActionClass.__mutex.release()
	return response

    def getEvents(self, filters = ActionEventAll, returnOnlyRequestedEvents = False, returnOnlyActiveEvents = True):
        events = []
        calendarEvents = CalendarClass.CalendarClass()
        radioEvents = RadioClass.RadioClass()

	ActionClass.__mutex.acquire()

        if self.__isEventEnable(filters, ActionClass.ActionEventGeneric) == True:
            events = events + self.__config.getEvents(self.ActionEventGeneric, returnOnlyActiveEvents)

        if self.__isEventEnable(filters, ActionClass.ActionEventRadio) == True:
            events = events + radioEvents.getEventsData(self.ActionEventRadio)

        if self.__isEventEnable(filters, ActionClass.ActionEventCalendar) == True:
            events = events + calendarEvents.getEventsData(self.ActionEventCalendar)

        if returnOnlyRequestedEvents == False:
    	    self.__updateEvents(events, filters)
	    events = copy.deepcopy(ActionClass.__actionEvents)

	ActionClass.__mutex.release()

        return events
