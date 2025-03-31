#!/usr/bin/python
# -*- coding: utf-8 -*-
import HeaterClass
import CalendarClass
import ActionClass
import ConfigClass
import RadioClass
import SprinklerClass
import HeaterClass
import ScheduleClass
import SwitchClass
import InfoClass
import RoomClass
import EnergyClass
import os
import json
import psutil
from subprocess import Popen
import MediaInterface
import threading


class APIClass:

    methods = {}

    def __init__(self):
        self.__mutex = threading.Lock()
        self.__mediaObj = 0

    def registerMedia(self, media):
        self.__mutex.acquire()
        self.__mediaObj = media
        self.__mutex.release()


    def APItemperature(self, json_req):
        obj = HeaterClass.HeaterClass()
        response = obj.getCurrentTemperature()
        return json.dumps(response)

    def APIenergy(self, json_req):
        obj = EnergyClass.EnergyClass()
        response = obj.getCurrentProduceEnergy()
        return json.dumps(response)

    def APIversion(self, json_req):
        response = {}
        response['name'] = 'Home Control Center'
        response['version'] = '1.0'
        return json.dumps(response)

    def APIgetMediaChannels(self, json_req):
        obj = RadioClass.RadioClass()
        response = obj.getPVRStations()
        return json.dumps(response)

    def APIgetSpotifyData(self, json_req):
        obj = RadioClass.RadioClass()
        print( json_req)
        if json_req['searchTextExist'] == True:
            response = \
                obj.getSpotifyObjectFromSearch(json_req['searchText'])
        elif json_req['currentDirectoryExist'] == True:
            response = \
                obj.getSpotifyObject(json_req['currentDirectoryText'])
        else:
            response = obj.getSpotifyObject()
        return json.dumps(response)

    def APIgetYTSearchResult(self, json_req):
        obj = RadioClass.RadioClass()
        response =  {}
        response['videos'] = obj.getYTsearch(json_req['search'])
        return json.dumps(response)

    def APIinfo(self, json_req):
        infoObj = InfoClass.InfoClass()
        response = infoObj.getInfoData()
        return json.dumps(response)

    def APIschedule(self, json_req):
        obj = ScheduleClass.ScheduleClass()
        response = {}
        response['DirectionA'] = obj.getJsonFromKoleo('A', 0)
        response['DirectionB'] = obj.getJsonFromKoleo('B', 0)
        return json.dumps(response)

    def APIheaterCharts(self, json_req):
        obj = HeaterClass.HeaterClass()
        response = obj.getHeaterInfo()
        return json.dumps(response)

    def APIgetGardenSettings(self, json_req):
        obj = SprinklerClass.SprinklerClass()
        response = obj.getSettings()
        return json.dumps(response)

    def APItoggleCec(self, json_req):
        obj = RadioClass.RadioClass()
        response = obj.toggleCEC()
        return json.dumps(response)

    def APIsetGardenSettings(self, json_req):
        response = {}
        config = ConfigClass.ConfigClass()
        config.saveSettingsData(2, json_req)
        response['state'] = 'OK'
        return json.dumps(response)

    def APIsetHeaterSettings(self, json_req):
        response = {}
        config = ConfigClass.ConfigClass()
        config.saveSettingsData(1, json_req)
        response['state'] = 'OK'
        return json.dumps(response)

    def APIsetAlarmSettings(self, json_req):
        response = {}
        config = ConfigClass.ConfigClass()
        config.saveSettingsData(0, json_req)
        response['state'] = 'OK'
        return json.dumps(response)

    def APIstatus(self, json_req=''):        
        evn = ActionClass.ActionClass()
        temp = HeaterClass.HeaterClass()
        eng = EnergyClass.EnergyClass()
        
        events = evn.getEvents()        
        temperature = temp.getCurrentTemperature()
        energy = eng.getCurrentProduceEnergy()
        
        response = {}
        resEvents = []
        duration = 0
        for event in events:
            row = {}
            row['eventGroup'] = event.groupId
            row['eventDesc'] = event.desc
            row['eventType'] = event.type
            row['eventDate'] = event.date
            resEvents.append(row)

        response['events'] = resEvents
        response['temperature'] = temperature
        response['energy'] = energy
        
        return json.dumps(response)

    def APIevents(self, json_req=''):
        obj = ActionClass.ActionClass()
        events = obj.getEvents()
        response = {}
        resEvents = []
        duration = 0
        for event in events:
            row = {}
            row['eventGroup'] = event.groupId
            row['eventDesc'] = event.desc
            row['eventType'] = event.type
            row['eventDate'] = event.date
            resEvents.append(row)
        response['events'] = resEvents
        response['eventDuration'] = duration
        return json.dumps(response)

    def APIGenericCMD(self, cmd, param=''):
        action = ActionClass.ActionClass()
        duration = action.performAction(cmd, param)
        return self.APIevents()

    def APIVolumeSet(self, json_req):
        param = json_req['volume']
        return self.APIGenericCMD(json_req['action'], param)

    def APIPlayPVR(self, json_req):
        param = json_req['channel']
        return self.APIGenericCMD(json_req['action'], param)

    def APIPlayMp3(self, json_req):
        param = json_req['folder']
        return self.APIGenericCMD(json_req['action'], param)

    def APIPlaySpotifyObject(self, json_req):
        param = json_req['link']
        return self.APIGenericCMD(json_req['action'], param)

    def APIPlaySpotifyDirectory(self, json_req):
        param = json_req['link']
        return self.APIGenericCMD(json_req['action'], param)

    def APIVideoShare(self, json_req):
        if 'link' in json_req:
            param = json_req['link']
            return self.APIGenericCMD(json_req['action'], param)
        playlist = json_req['playlist']
        self.__mutex.acquire()
        self.__mediaObj.mediaPlaylistUpdate(playlist)
        self.__mutex.release()
        return self.APIevents()

    def APISprinklerOn(self, json_req):
        param = json_req['id']
        return self.APIGenericCMD(json_req['action'], param)

    def APIGate(self, json_req):
        param = json_req['id']
        return self.APIGenericCMD(json_req['action'], param)

    def APIGatePerm(self, json_req):
        param = json_req['id']
        return self.APIGenericCMD(json_req['action'], param)

    def APIStop(self, json_req):
        if 'next' not in json_req:
            self.__mutex.acquire()
            self.__mediaObj.mediaPlaylistUpdate()
            self.__mutex.release()
        if 'sourceIsLocal' in json_req:
            return self.APIGenericCMD(json_req['action'], json_req['sourceIsLocal'])
        else:
            return self.APIGenericCMD(json_req['action'], False)

    def APIVolumeUp(self, json_req):
        return self.APIGenericCMD(json_req['action'])

    def APIVolumeDown(self, json_req):
        return self.APIGenericCMD(json_req['action'])

    def APISprinklerForceAuto(self, json_req):
        return self.APIGenericCMD(json_req['action'])

    def APISprinklerOff(self, json_req):
        return self.APIGenericCMD(json_req['action'])

    def APItoggleLight(self, json_req):
        obj = SwitchClass.SwitchClass()
        ip = json_req['ip']
        response = obj.toggleSwitchState(ip)
        return json.dumps(response)

    def __checkIfProcessRunning(processName):
        for proc in psutil.process_iter():
            try:
                print( proc.name())
                if processName.lower() in proc.name().lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied,
                    psutil.ZombieProcess):
                pass
        return False

    def APIGetRooms(self, json_req):
        streaming_in_progress = False
        for proc in psutil.process_iter():
            if proc.name() == 'ffmpeg':
                streaming_in_progress = True
                break

        #if streaming_in_progress == False:
        #    command = ['/HomeControlCenter/play.sh']
        #    proc = Popen(
        #        command,
        #        shell=True,
        #        stdin=None,
        #        stdout=None,
        #        stderr=None,
        #        close_fds=True,
        #        )

        obj = RoomClass.RoomClass()
        response = obj.getRoomsData()
        return json.dumps(response)

    def invoke(self, json_req):
        try:
            method_name = 'API' + json_req['action']
            #print( "Method : " + method_name)
            method = getattr(self, method_name)
            response = method(json_req)
        except Exception as e:
            print("API Class :" + str(e))
            response = {'error': 'invalid command'}
            response = json.dumps(response)

        return response
