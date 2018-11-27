class EventClass:
    name = ""
    id = -1
    name = ""
    desc = ""
    date = ""
    state = ""
    icon = ""
            
    def __init__(self, desc, date = "", id = -1, state = "0"):
        #self.name = name
        self.id = id
        self.desc = desc
        self.date = date
        self.state = state
	self.icon = 'calendar'

    def setEventName(self, name):
	self.name = name

    def setEventIcon(self, icon):
	self.icon = icon