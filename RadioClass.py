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
#from yt_dlp import YoutubeDL
import requests
import re
#import cec


class StationClass:

    def __init__(
        self,
        id,
        name,
        post_data,
        ):
        self.id = id
        self.name = name
        self.post_data = post_data


class Mp3Class:

    def __init__(
        self,
        file,
        label,
        type,
        ):
        self.file = file
        self.label = label
        if type == 'file':
            self.icon = 'img/play.png'
            self.action = 'PlayMp3'
            self.box = 'infoBox'
        else:
            self.icon = 'img/folder.png'
            self.action = 'Chdir'
            self.box = 'content'


class RadioClass(object):

    __stations = []
    __initialized = 0
    __settings = ''
    __tv = 0
    __current_directory = ''
    __headers = {'content-type': 'application/json'}
    __play_req = {
        'jsonrpc': '2.0',
        'id': '1',
        'method': 'Player.Open',
        'params': {'item': {'file': 'PLAY_REQUEST'}},
        }
    __play_req_dir = {
        'jsonrpc': '2.0',
        'id': '1',
        'method': 'Player.Open',
        'params': {'item': {'directory': 'PLAY_REQUEST'}, 'options': {'repeat':'all', 'shuffled':True}},
        }
    __play_req_next = {
        'jsonrpc': '2.0',
        'method': 'Player.GoTo',
        'params': { 'playerid': 1, 'to': 'next' },
        'id': 1,
       }
    __stop_req = {
        'jsonrpc': '2.0',
        'method': 'Player.Stop',
        'params': {'playerid': 1},
        'id': '1',
        }
    __get_volume_req = {
        'jsonrpc': '2.0',
        'method': 'Application.GetProperties',
        'params': {'properties': ['volume']},
        'id': 1,
        }
    __get_event_req = {
        'jsonrpc': '2.0',
        'method': 'Player.GetItem',
        'params': {'properties': ['title', 'artist'], 'playerid': 1},
        'id': 1,
        }
    __set_volume_req = {
        'jsonrpc': '2.0',
        'method': 'Application.SetVolume',
        'params': {'volume': 0},
        'id': 1,
        }
    __get_player_state_req = {'jsonrpc': '2.0',
                              'method': 'Player.GetActivePlayers',
                              'id': 1}
    __get_files_req = {
        'jsonrpc': '2.0',
        'method': 'Files.GetDirectory',
        'params': {'directory': 'PATH', 'media': 'files'},
        'id': 1,
        }

    __get_pvr_radio_channels = {
        'jsonrpc': '2.0',
        'method': 'PVR.GetChannels',
        'params': {'channelgroupid': 2},
        'id': 1,
        }
    __get_pvr_tv_channels = {
        'jsonrpc': '2.0',
        'method': 'PVR.GetChannels',
        'params': {'channelgroupid': 1},
        'id': 1,
        }
    __play_req_pvr = {
        'jsonrpc': '2.0',
        'id': '1',
        'method': 'Player.Open',
        'params': {'item': {'channelid': 0}},
        }
    __play_req_yt = {
        'jsonrpc': '2.0',
        'method': 'Player.Open',
        'params': {'item': {'file': 'VIDEO_ID'}},
        'id': 1,
        }

    __get_spotify_directory_req = {
        'jsonrpc': '2.0',
        'method': 'Files.GetDirectory',
        'params': {'directory': 'plugin://plugin.audio.spotify/',
                   'media': 'files'},
        'id': '1',
        }
    __get_spotify_search_req = {
        'jsonrpc': '2.0',
        'method': 'Files.GetDirectory',
        'params': {'directory': "plugin://plugin.audio.spotify/?action=search_artists&artistid='SEARCH_REQUEST'",
                   'media': 'files'},
        'id': '1',
        }

    __play_sporify_object_req = {
        'jsonrpc': '2.0',
        'method': 'Player.Open',
        'params': {'item': {'file': 'SPOTIFY_LINK'}},
        'id': 1,
        }
    __play_sporify_directory_req = {
        'jsonrpc': '2.0',
        'method': 'Player.Open',
        'params': {'item': {'directory': 'SPOTIFY_LINK'}},
        'id': 1,
        }

    # Depricatated get method :
    # __set_volume_req = "/jsonrpc?request={%22jsonrpc%22: %222.0%22, %22method%22: %22Application.SetVolume%22, %22params%22: {%22volume%22: VOLUME_VALUE}, %22id%22: 1}"
    # __get_event_req = "params%22:%20{%20%22properties%22:%20[%22title%22,%22artist%22],%20%22playerid%22:%201%20},%20%22id%22:%221%22}"
    # __get_volume_req = "/jsonrpc?request={%22jsonrpc%22:%222.0%22,%22method%22:%22Application.GetProperties%22,%22params%22:{%22properties%22:[%22volume%22]},%22id%22:1}"
    # __stop_req = "/jsonrpc?request={%22jsonrpc%22:%222.0%22,%22method%22:%22Player.Stop%22,%22params%22:{%20%22playerid%22:1},%22id%22:%221%22}"
    # __play_req = "/jsonrpc?request={%22jsonrpc%22:%222.0%22,%22id%22:%221%22,%22method%22:%22Player.Open%22,%22params%22:{%22item%22:{%22file%22:%22PLAY_REQUEST%22}}}
    __media = None
    def __init__(self, mediaInterface = None):
        config = ConfigClass.ConfigClass()
        if (mediaInterface != None):
            RadioClass.__media = mediaInterface

        if RadioClass.__initialized == 0:
            RadioClass.__settings = config.getRadioSettings()

            #cec.init()
            #RadioClass.__tv = cec.Device(cec.CECDEVICE_TV)

            RadioClass.__initialized = 1

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

    def __getPlayerVolume(self):
        req = self.__getRadioDevice() + '/jsonrpc'

        payload = RadioClass.__get_volume_req
        volume = requests.post(req, data=json.dumps(payload),
                               headers=RadioClass.__headers,
                               auth=HTTPBasicAuth('kodi', 'kodi'),
                               verify=False, timeout=3)

        data = json.loads(volume.text)
        value = data['result']['volume']
        return value

    def __getRadioDevice(self):
        return 'http://' + RadioClass.__settings

    def __getRadioStation(self, name):
        for station in RadioClass.__stations:
            if station.name == name:
                break
        return station

    def getPVRRadioStations(self):
        post_data = copy.deepcopy(RadioClass.__get_pvr_radio_channels)
        req = self.__getRadioDevice() + '/jsonrpc'
        resp = requests.post(req, data=json.dumps(post_data),
                             headers=RadioClass.__headers,
                             auth=HTTPBasicAuth('kodi', 'kodi'),
                             verify=False, timeout=10)
        data = json.loads(resp.text)
        return data['result']['channels']

    def getPVRTVStations(self):
        post_data = copy.deepcopy(RadioClass.__get_pvr_tv_channels)
        req = self.__getRadioDevice() + '/jsonrpc'
        resp = requests.post(req, data=json.dumps(post_data),
                             headers=RadioClass.__headers,
                             auth=HTTPBasicAuth('kodi', 'kodi'),
                             verify=False, timeout=10)
        data = json.loads(resp.text)
        return data['result']['channels']

    def playPVRChannel(self, channel):
        post_data = copy.deepcopy(RadioClass.__play_req_pvr)
        post_data['params']['item']['channelid'] = channel
        req = self.__getRadioDevice() + '/jsonrpc'
        d = requests.post(req, data=json.dumps(post_data),
                          headers=RadioClass.__headers, verify=False,
                          auth=HTTPBasicAuth('kodi', 'kodi'),
                          timeout=10)
        resp = {}
        resp['channelid'] = channel
        return resp

    def getSpotifyObject(self,
                         directory='plugin://plugin.audio.spotify/'):
        post_data = \
            copy.deepcopy(RadioClass.__get_spotify_directory_req)
        post_data['params']['directory'] = directory
        req = self.__getRadioDevice() + '/jsonrpc'
        resp = requests.post(req, data=json.dumps(post_data),
                             headers=RadioClass.__headers,
                             verify=False, timeout=30)
        data = json.loads(resp.text)
        response_data = {}
        response_data['result'] = data['result']['files']
        response_data['directory'] = directory
        return response_data

    def getSpotifyObjectFromSearch(self, searchText):
        post_data = copy.deepcopy(RadioClass.__get_spotify_search_req)
        post_data['params']['directory'] = \
            "plugin://plugin.audio.spotify/?action=search_artists&artistid='" \
            + searchText + "'"
        req = self.__getRadioDevice() + '/jsonrpc'
        resp = requests.post(req, data=json.dumps(post_data),
                             headers=RadioClass.__headers,
                             verify=False, timeout=30)
        data = json.loads(resp.text)
        response_data = {}
        response_data['result'] = data['result']['files']
        response_data['directory'] = post_data['params']['directory']
        return response_data

    def playSpotifyObject(self, link):
        post_data = copy.deepcopy(RadioClass.__play_sporify_object_req)
        post_data['params']['item']['file'] = link
        req = self.__getRadioDevice() + '/jsonrpc'
        resp = requests.post(req, data=json.dumps(post_data),
                             headers=RadioClass.__headers,
                             verify=False, timeout=30)
        response_data = {}
        return response_data

    def playSpotifyDirectory(self, link):
        post_data = \
            copy.deepcopy(RadioClass.__play_sporify_directory_req)
        post_data['params']['item']['directory'] = link
        req = self.__getRadioDevice() + '/jsonrpc'
        resp = requests.post(req, data=json.dumps(post_data),
                             headers=RadioClass.__headers,
                             verify=False, timeout=30)
        response_data = {}
        return response_data


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

    def playYTAddonVideo(self, link):
        #print("!!!!!!LINK = " + link)

        post_data = copy.deepcopy(RadioClass.__play_req_yt)
        if link.find('list') == -1:
            link="https://youtu.be/" + link[link.rfind("v=")+2:]

            post_data['params']['item']['file'] = \
                'plugin://plugin.video.youtube/play/?screensaver=true&video_id=' \
                + link[link.rindex('/') + 1:]
        else:
            return
#            link="https://youtube.com/" + link[link.rfind("watch"):]
#            post_data['params']['item']['file'] = \
#                'plugin://plugin.video.youtube/play/?order=default&playlist_id=' \
#                + link[link.rindex('=') + 1:]

#        print("!!!!!!PLUGIN = " + post_data['params']['item']['file'])

        resp = {}
        resp['status'] = 0
        try:
            req = self.__getRadioDevice() + '/jsonrpc'
            d = requests.post(req, data=json.dumps(post_data),
                              headers=RadioClass.__headers,
                              verify=False, timeout=30)
        except:
            resp['status'] = 1
        return resp

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

    def getRadioStations(self):
        return RadioClass.__stations

    def getParentDirectory(self):
        directory = RadioClass.__current_directory
        if directory[len(directory) - 1] == '/':
            directory = directory[:directory.rfind('/')]
        directory = directory[:directory.rfind('/')]
        return directory

    def getCurrentDirectory(self):
        return RadioClass.__current_directory

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
        config = ConfigClass.ConfigClass()
        name, url = config.getRadioStationUrl(id)
        self.__media.apiMediaPlayRadioStream(name, url)


    def playMp3File(self, directory):
        config = ConfigClass.ConfigClass()
        path = config.getMp3Directory() + "/" + directory
        isDirectory = os.path.isdir(path)
        if isDirectory == True:
            self.__media.apiMediaPlayMp3(path)

    def getRadioPlayRequest(self, name):
        station = self.__getRadioStation(name)
        try:
            req = self.__getRadioDevice() + '/jsonrpc'
            requests.post(req, data=json.dumps(station.post_data),
                          headers=RadioClass.__headers, verify=False,
                          timeout=10)
            time.sleep(1)
        except:
            req = None

    def mediaStop(self):
        self.__media.apiMediaStop()

    def getRadioStopRequest(self):
        try:
            req = self.__getRadioDevice() + '/jsonrpc'
            payload = RadioClass.__stop_req
            for idx in range(0, 2):
                payload['params']['playerid'] = idx
                requests.post(req, data=json.dumps(payload),
                              headers=RadioClass.__headers,
                              verify=False, timeout=3)
                time.sleep(1)
        except:
            req = None
            
    def playNextFromPlaylist(self):
        self.__media.apiMediaPlayNext()

    def playYT(self, data, isPlaylist=False):
        if isPlaylist:
            self.__media.apiMediaPlayYoutubeList(data)
        else:
            self.__media.apiMediaPlayYoutube(data)

    def getRadioNextRequest(self):
        try:
            req = self.__getRadioDevice() + '/jsonrpc'
            payload = RadioClass.__play_req_next
            for idx in range(0, 2):
                payload['params']['playerid'] = idx
                requests.post(req, data=json.dumps(payload),
                              headers=RadioClass.__headers,
                              verify=False, timeout=3)
                time.sleep(1)
        except:
            req = None

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
