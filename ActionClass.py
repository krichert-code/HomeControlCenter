from xml.dom import minidom
import ActionThread
import EventClass
import ConfigClass
import CalendarClass
import RadioClass
import SprinklerClass
import HeaterClass



class ActionClass(object):
    ActionEventAll       = 1 << 0
    ActionEventGeneric   = 1 << 1
    ActionEventCalendar  = 1 << 2
    ActionEventRadio     = 1 << 3
    ActionEventSprinkler = 1 << 4

    def __init__(self):
        self.__config = ConfigClass.ConfigClass()
        self.__actionEvents = []

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
                    

    def actionOnDoor(self, param = ""):
        url = self.__config.getSwitchURL("door")
        threadTask = ActionThread.ActionThread()

        threadTask.addTask("set","door", "Otwieranie furtki")
        threadTask.addTask("request",url)
        threadTask.addTask("delay",5)
        threadTask.addTask("clear","door", "No action")
        threadTask.start()
        threadTask.suspend()

    def actionOnGate0(self, param = ""):
        url = self.__config.getSwitchURL("garage")
        threadTask = ActionThread.ActionThread()

        threadTask.addTask("set","garage", "Otwieranie/Zamykanie bramy garazowej")
        threadTask.addTask("request",url)
        threadTask.addTask("delay",20)
        threadTask.addTask("clear","garage", "No action")
        threadTask.start()
        threadTask.suspend()
        
    def actionOnGate1(self, param = ""):
        url = self.__config.getSwitchURL("mainGate")
        threadTask = ActionThread.ActionThread()

        threadTask.addTask("set","mainGate", "Otwieranie bramy wjazdowej")
        threadTask.addTask("request",url)
        threadTask.addTask("delay",20)
        threadTask.addTask("clear","mainGate", "No action")
        threadTask.start()
        threadTask.suspend()

        

    def actionOnGate1Perm(self, param = ""):
        url = self.__config.getSwitchURL("mainGate")
        threadTask = ActionThread.ActionThread()

        threadTask.addTask("set","mainGate", "Otwieranie bramy wjazdowej")
        threadTask.addTask("request",url)
        threadTask.addTask("delay",25)
        threadTask.addTask("request",url)
        threadTask.addTask("delay",2)
        threadTask.addTask("request",url)
        threadTask.addTask("clear","mainGate", "No action")
        threadTask.start()
	threadTask.suspend()

                
    def actionOnSprinklerOn(self, param = ""):
	threadTask = ActionThread.ActionThread()
	sprinkler = SprinklerClass.SprinklerClass()

	url_off = sprinkler.getSprinklersOffRequest()
	url = sprinkler.getSprinklerOnRequest(param)
	status_val = sprinkler.getSprinklerStatus()
        threadTask.addTask("request", url_off)
	threadTask.addTask("delay", 1)
	if status_val <> int(param) and status_val >= 0:
    	    threadTask.addTask("request", url)
    	    threadTask.addTask("delay", 2)
        threadTask.addTask("notify")
        threadTask.start()
	threadTask.suspend()

	

    def actionOnPlay(self, param = ""):
        radio = RadioClass.RadioClass()
        radio.getRadioPlayRequest(param)

    def actionOnPlayMp3(self, param = ""):
        player = RadioClass.RadioClass()
        player.playMp3File(param)

    def actionOnStop(self, param = ""):
        radio = RadioClass.RadioClass()
        radio.getRadioStopRequest()

    def actionOnVolumeUp(self, param = ""):
        radio = RadioClass.RadioClass()
        radio.getRadioVolumeUpRequest() 

    def actionOnVolumeDown(self, param = ""):
        radio = RadioClass.RadioClass()
        radio.getRadioVolumeDownRequest() 

    def actionOnGetActiveEvents(self, param = ""):
        # get only activate events
	pass

#---------------------------------------------------------------------------------------------------------------
    def getEventsData(self,actionName, param = "", filters = ActionEventAll, returnOnlyRequestedEvents = False):
        events = []

        calendarEvents = CalendarClass.CalendarClass()
        radioEvents = RadioClass.RadioClass()
        sprinklerEvent = SprinklerClass.SprinklerClass()

        if actionName <> None:
            method_name = 'actionOn' + actionName
            method = getattr(self, method_name)
            method(param)

        if self.__isEventEnable(filters, ActionClass.ActionEventRadio) == True:
            events = events + radioEvents.getEventsData(self.ActionEventRadio)

        if self.__isEventEnable(filters, ActionClass.ActionEventSprinkler) == True:
            events = events + sprinklerEvent.getEventsData(self.ActionEventSprinkler)


        if self.__isEventEnable(filters, ActionClass.ActionEventGeneric) == True:
            events = events + self.__config.getEvents(self.ActionEventGeneric)

        if self.__isEventEnable(filters, ActionClass.ActionEventCalendar) == True:
            events = events + calendarEvents.getEventsData(self.ActionEventCalendar)

        self.__updateEvents(events, filters)

        if returnOnlyRequestedEvents == True:
            return events
        else:
            return ActionClass.__actionEvents


