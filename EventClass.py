class EventClass:
    name = ""
    desc = ""
    date = ""
    state = ""
    icon = ""
            
    def __init__(self, desc, date, name = "calendar", state = "0"):
        self.name = name
	self.desc = desc
        self.date = date
	self.state = state
        self.icon = type