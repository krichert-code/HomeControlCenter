class EventClass:
    def __init__(self, desc, date = "", id = -1, state = "0"):
        self.name = ""
        self.id = id
        self.desc = desc
        self.date = date
        self.state = state
        self.icon = 'gate'

    def setEventName(self, name):
        self.name = name

    def setEventIcon(self, icon):
        self.icon = icon