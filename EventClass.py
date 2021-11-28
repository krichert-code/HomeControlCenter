#!/usr/bin/python
# -*- coding: utf-8 -*-


class EventClass:

    def __init__(
        self,
        desc,
        date='',
        id=-1,
        state='0',
        isHoliday='False',
        ):
        self.type = ''
        self.groupId = id
        self.desc = desc
        self.date = date
        self.state = state
        self.messageId = ''
        self.isHoliday = isHoliday
