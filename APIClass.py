#!/usr/bin/python
# -*- coding: utf-8 -*-
import HeaterClass
import ActionClass
import ConfigClass
import RadioClass
import SprinklerClass
import HeaterClass
import SwitchClass
import InfoClass
import RoomClass
import EnergyClass
import json
import psutil
from subprocess import Popen
import APIInterface
import threading


class APIClass:

    def __init__(self):
        self.__mutex = threading.Lock()
        self.__apiObj = APIInterface.APIInterface()
        self.__media = None 

    def registerAPIInterface(self, objAPI, mediaAPI):
        self.__mutex.acquire()
        self.__apiObj = objAPI
        self.__media = RadioClass.RadioClass(mediaAPI)
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
        response = self.__media.getRadioChannels()
        return json.dumps(response)

    def APIgetYTSearchResult(self, json_req):
        response =  {}
        response['videos'] = self.__media.getYTsearch(json_req['search'])
        return json.dumps(response)

    def APIVolumeSet(self, json_req):
        param = json_req['volume']
        self.__media.setRadioVolume(param)
        return self.APIevents()

    def APIVolumeUp(self, json_req):
        volume = self.__media.getRadioVolume()
        if (volume < 100):
            volume = volume + 5
            self.__media.setRadioVolume(volume)
        return self.APIevents()

    def APIVolumeDown(self, json_req):
        volume = self.__media.getRadioVolume()
        if (volume > 0):
            volume = volume - 5
            self.__media.setRadioVolume(volume)
        return self.APIevents()
    
    def APIPlayPVR(self, json_req):
        param = json_req['channel']
        self.__media.playRadioStream(param)
        return self.APIevents()

    def APIPlayMp3(self, json_req):
        param = json_req['folder']
        self.__media.playMp3File(param)
        return self.APIevents()

    def APIVideoShare(self, json_req):
        ytlist = False

        if 'playlist' in json_req:
            playlist = json_req['playlist']
            ytlist = True
        elif 'link' in json_req:
            url = json_req['link']
            if (self.__media.isYTPlaylist(url) == True):
                playlist = self.__media.getPlaylistLinks(url)
                ytlist = True

        if ytlist == True:
            self.__media.playYT(playlist, isPlaylist=True)
        else:
            self.__media.playYT(url)
            
        return self.APIevents()

    def APIStop(self, json_req):
        if 'next' in json_req:
            # play next song from playlist local source or youtube playlist
            self.__media.playNextFromPlaylist()
        else:
            # just stop
            self.__media.mediaStop()
        return self.APIevents()

    def APIinfo(self, json_req):
        infoObj = InfoClass.InfoClass()
        response = infoObj.getInfoData()
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

        self.__mutex.acquire()
        #print ("---------alarm = " + str(self.__apiObj.isAlarmArmed()))
        if (self.__apiObj.isAlarmArmed() == True):
            response['alarm'] = 1
            #print ("---------ARMED")
        else:
            response['alarm'] = 0
            #print ("------------------------------------NO ARMED")
        self.__mutex.release()
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

    def APISprinklerOn(self, json_req):
        param = json_req['id']
        return self.APIGenericCMD(json_req['action'], param)

    def APISprinklerForceAuto(self, json_req):
        return self.APIGenericCMD(json_req['action'])

    def APISprinklerOff(self, json_req):
        return self.APIGenericCMD(json_req['action'])

    def APIGate(self, json_req):
        param = json_req['id']
        return self.APIGenericCMD(json_req['action'], param)

    def APIGatePerm(self, json_req):
        param = json_req['id']
        return self.APIGenericCMD(json_req['action'], param)

    def APItoggleLight(self, json_req):
        obj = SwitchClass.SwitchClass()
        ip = json_req['ip']
        response = obj.toggleSwitchState(ip)
        return json.dumps(response)

    def APIGetRooms(self, json_req):
        streaming_in_progress = False
        for proc in psutil.process_iter():
            if proc.name() == 'ffmpeg':
                streaming_in_progress = True
                break

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
