#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests
import threading
import time
import ConfigClass


class RequestParam:

    def __init__(self, url):
        self.url = url


class DelayParam:

    def __init__(self, delay):
        self.delay = delay


class UpdateParam:

    def __init__(self, type, id):
        self.type = type
        self.id = id


class NotifyParam:

    def __init__(self):
        pass


class Task:

    def __init__(self, requestType, param):
        self.requestType = requestType
        self.param = param


class ActionThread(threading.Thread):

    __mutex = None

    def __init__(self):
        threading.Thread.__init__(self)
        self.__response = ''
        self.__taskList = []
        self.__event = threading.Event()

        self.__event.clear()

        if ActionThread.__mutex == None:
            ActionThread.__mutex = threading.Lock()

    def suspend(self):
        self.__event.wait()

    def addTask(self, task):
        self.__taskList.append(task)

    def getResponse(self):
        return self.__response

    def run(self):
        exit = False
        forceClean = False

        for task in self.__taskList:

            ActionThread.__mutex.acquire()

            if task.requestType == 'request':
                try:

                    # If no response then initialize 'cleaning' - set forceClean

                    req = requests.get(task.param.url, verify=False,
                            timeout=10)
                    self.__response = req.text
                except requests.exceptions.RequestException:
                    req = None
                    self.__response = ''
                finally:
                    if req == None:
                        forceClean = True

            if task.requestType == 'set':

                # After set state event to waiting thread have to be send
                # Waiting thread may collect and disaply active events

                config = ConfigClass.ConfigClass()
                if config.getStatus(task.param.type, task.param.id) \
                    == '1':
                    exit = True
                ret_val = config.changeStatus(task.param.type,
                        task.param.id, '1')
                if self.__event != None:
                    self.__event.set()

            if task.requestType == 'clear':
                config = ConfigClass.ConfigClass()
                ret_val = config.changeStatus(task.param.type,
                        task.param.id, '0')

            # Below events don't need to be in critical section

            ActionThread.__mutex.release()

            if task.requestType == 'delay' and forceClean == False:
                time.sleep(task.param.delay)

            if task.requestType == 'notify' and self.__event != None:
                self.__event.set()

            if exit == True:
                break
