class EventClass:
    name = ""
    date = ""
    icon = ""
            
    def __init__(self, name, date, type="calendar"):
        self.name = name
        self.date = date
        self.icon = type