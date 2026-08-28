#!/usr/bin/python
# -*- coding: utf-8 -*-
import ConfigClass
import EventClass
import requests
import json
import os
import time
import copy
from requests.auth import HTTPBasicAuth
from youtubesearchpython import *
import requests
import re


class RadioClass(object):

    __media = None

    def __init__(self, mediaInterface = None):
        config = ConfigClass.ConfigClass()
        if (mediaInterface != None):
            RadioClass.__media = mediaInterface

    def getRadioChannels(self):
        response = {}
        config = ConfigClass.ConfigClass()

        response['radio'] = config.getRadioStations()
        response['tv'] = []
        response['mp3'] = self.getFiles()
        if (RadioClass.__media != None):
            response['volume'] = RadioClass.__media.apiMediaGetVolume()
        else:
            response['volume'] = 0
        return response

    def getPlaylistLinks(self, url):
        url="https://youtube.com/" + url[url.rfind("watch"):]
        links = []

        list_id = url[url.find("list="):url.rfind("&")]
        pattern = "v=.{11}"r"\\u0026"+list_id

        result = set()

        resp = requests.get(url)
        if resp.status_code == 200:
            html = resp.text

            while(True):
                obj = re.search(pattern,html)
                if (obj == None):
                    break
                idx_s = obj.span()[0]
                idx_e = obj.span()[1]

                link = "https://www.youtube.com/"+html[idx_s:idx_s+13]
                result.add(link)
                html=html[idx_e:]
                obj=None

            links = list(result)
        return links


    def isYTPlaylist(self, link):
        if link.find('list') != -1:
            return True
        return False

    def getYTsearch(self, text):
        result = []
        customSearch = VideosSearch(str(text), limit = 30)

        for entry in customSearch.result()['result']:
            entry_data = {}
            entry_data['title'] = entry['title']
            entry_data['duration'] = entry['duration']
            entry_data['link'] = entry['link']
            entry_data['icon'] = entry['thumbnails'][0]['url']
            result.append(entry_data)
        return result


    def getFiles(self, path=''):
        files = []
        config = ConfigClass.ConfigClass()
        if len(path) == 0:
            path = config.getMp3Directory()

        try:
            entries = os.listdir(path)
        except OSError:
            entries = []

        for entry in entries:
            subdir = os.path.join(path, entry)
            if not os.path.isdir(subdir):
                continue
            try:
                if any(f.lower().endswith('.mp3')
                       for f in os.listdir(subdir)
                       if os.path.isfile(os.path.join(subdir, f))):
                    files.append(entry)
            except OSError:
                continue

        files.sort()
        return files

    def playRadioStream(self, id):
        if (RadioClass.__media != None):
            config = ConfigClass.ConfigClass()
            name, url = config.getRadioStationUrl(id)
            self.__media.apiMediaPlayRadioStream(name, url)

    def playMp3File(self, directory):
        config = ConfigClass.ConfigClass()
        path = config.getMp3Directory() + "/" + directory
        isDirectory = os.path.isdir(path)
        if isDirectory == True and RadioClass.__media != None:
            self.__media.apiMediaPlayMp3(path)

    def mediaStop(self):
        if (RadioClass.__media != None):
            RadioClass.__media.apiMediaStop()
            
    def playNextFromPlaylist(self):
        if (RadioClass.__media != None):
            RadioClass.__media.apiMediaPlayNext()

    def playYT(self, data, isPlaylist=False):
        if isPlaylist and RadioClass.__media != None:
            RadioClass.__media.apiMediaPlayYoutubeList(data)
        elif RadioClass.__media != None:
            RadioClass.__media.apiMediaPlayYoutube(data)

    def setRadioVolume(self, volume):
        try:
            if (RadioClass.__media != None):
                RadioClass.__media.apiMediaVolume(volume)
        except:
            pass

    def getRadioVolume(self):
        volume = 0
        try:
            if (RadioClass.__media != None):
                volume = RadioClass.__media.apiMediaGetVolume()
        except:
            pass
        return volume

    def isPlayerEnabled(self):
        isEnabled = False
        try:
            if (RadioClass.__media != None):
                isEnabled = RadioClass.__media.apiMediaGetState() == "playing"
            else:
                isEnabled = False
        except:
            isEnabled = False
        finally:
            return isEnabled

    def getEventsData(self, id):
        events = []
        event_text = ''

        if (RadioClass.__media != None and RadioClass.__media.apiMediaGetState() == "playing"):
            event_text = RadioClass.__media.apiMediaGetMetaData()
            if event_text is not None:
                state = EventClass.EventClass(event_text, '', id)
                state.type = 'radio'
                events.append(state)

        return events
