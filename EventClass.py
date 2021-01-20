class EventClass:
    def __init__(self, desc, date = "", id = -1, state = "0", isHoliday="False"):
        self.name = ""
        self.id = id
        self.desc = desc
        self.date = date
        self.state = state
	self.messageId = ""
        self.icon = 'gate'
	self.style= "text"
	self.isHoliday = isHoliday

    def setHoliday(self):
	self.isHoliday = True

    def setEventName(self, name):
        self.name = name

    def setEventIcon(self, icon):
        self.icon = icon

    def setStyle(self, style):
	self.style = style

    def setEventMessageId(self, id):
        self.messageId = id
