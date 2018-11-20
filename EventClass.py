class EventClass:
    name = ""
    id = -1
    desc = ""
    date = ""
    state = ""
    icon = ""
            
    def __init__(self, desc, date, id, state = "0"):
        #self.name = name
        self.id = id
        self.desc = desc
        self.date = date
        self.state = state
        self.icon = type