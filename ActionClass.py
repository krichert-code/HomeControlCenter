from xml.dom import minidom
import ActionThread
import EventClass
import ConfigClass
import CalendarClass
import RadioClass
import SprinklerClass



class ActionClass(object):
    __config = None
    __actionEvents = []
    ActionEventAll       = 1 << 0
    ActionEventGeneric   = 1 << 1
    ActionEventCalendar  = 1 << 2
    ActionEventRadio     = 1 << 3
    ActionEventSprinkler = 1 << 4

    def __init__(self):
        self.__config = ConfigClass.ConfigClass()
	
        
    def __isEventEnable(self, events, eventID):
        if (events & eventID <> 0) or (events & ActionClass.ActionEventAll <> 0):
            return True
        else:
            return False

    def __updateEvents(self, events, filters):
        print "++++++++++++++++" + str (len(events))
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
	threadTask.addTask.suspend()

                
    def actionOnGetSprinklersStatus(self, param = ""):
        internalEventList = []

        internalEventList.append(self.__config.getEvent("Sprinkler1"))
        internalEventList.append(self.__config.getEvent("Sprinkler2"))
        internalEventList.append(self.__config.getEvent("Sprinkler3"))

        # remove events not related to sprinklers
        for item in internalEventList:
            # update icon depands on device state
            if item.state == "0":
                item.icon="img/off_mobile.png"
            else:
                item.icon="img/on_mobile.png"

        return internalEventList


    def __actionOnSprinkler(self, name):
        #on/off sprinkler and update status in xml
        taskList = []
        event = threading.Event()
        url = self.__config.getSwitchURL(name)
        url_off_all = self.__config.getSwitchURL("SprinklerOff")

        xmlEvent = self.__config.getEvent(name)

        taskList.append(Task("request",url_off_all))
	
        if xmlEvent.state == "0":
            taskList.append(Task("set",name))
	    taskList.append(Task("delay",5))
	    taskList.append(Task("request",url))
        else:
            taskList.append(Task("notify"))

        event.clear()
        ActionThread(event, taskList).start()
        event.wait()


    def actionOnSprinkler1(self, param = ""):
        self.__actionOnSprinkler("Sprinkler1")

    def actionOnSprinkler2(self, param = ""):
        self.__actionOnSprinkler("Sprinkler2")

    def actionOnSprinkler3(self, param = ""):
        self.__actionOnSprinkler("Sprinkler3")

    def actionOnPlay(self, param = ""):
        threadTask = ActionThread.ActionThread()
        radio = RadioClass.RadioClass()
        radio_req = radio.getRadioPlayRequest(param)
        threadTask.addTask("request",radio_req)
        threadTask.addTask("delay",1)
        threadTask.addTask("notify")
        threadTask.start()
	threadTask.suspend()


    def actionOnStop(self, param = ""):
        threadTask = ActionThread.ActionThread()

        radio = RadioClass.RadioClass()
        radio_req = radio.getRadioStopRequest()
        threadTask.addTask("request",radio_req)            
        threadTask.addTask("delay",1)
        threadTask.addTask("notify")
        threadTask.start()
        threadTask.suspend()

    def actionOnVolumeUp(self, param = ""):
        threadTask = ActionThread.ActionThread()

        radio = RadioClass.RadioClass()
        radio_req = radio.getRadioVolumeUpRequest() 
        threadTask.addTask("request",radio_req)        
        threadTask.start()

    def actionOnVolumeDown(self, param = ""):
        threadTask = ActionThread.ActionThread()

        radio = RadioClass.RadioClass()
        radio_req = radio.getRadioVolumeDownRequest() 
        threadTask.addTask("request",radio_req)        
        threadTask.start()

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


