import requests
import threading
import time
import ConfigClass
import RadioClass
import CalendarClass
import HeaterClass
import ActionClass
import SprinklerClass
import EnergyClass
import APIMediaInterface
import APIInterface
import DBClass
import RPi.GPIO as GPIO
import json
import AlarmClass
import traceback
import logging
import SwitchClass
import RadioClass
import base64
import os
from datetime import date
from datetime import datetime
from datetime import timedelta
from astral.sun import sun
from astral import LocationInfo
from subprocess import Popen, PIPE

import yt_dlp
import vlc
import time



#url="https://www.youtube.com/watch?v=kqccmH8FTb8"


# --- Pobranie URL strumienia audio ---
#ydl_opts = {
#    "format": "bestaudio",
#    "quiet": True,
#}

#with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#    info = ydl.extract_info(url, download=False)
#    audio_url = info["url"]

#print("Stream URL:", audio_url)

# --- Odtwarzanie strumienia ---
#radio="http://31.192.216.10/RMFMAXXX48"
#player = vlc.MediaPlayer(audio_url)
#player.play()

#time.sleep(1)





# Pętla czekająca aż się skończy
#while True:
    # setting volume
#    player.audio_set_volume(50)

#    state = player.get_state()
#    if state in (vlc.State.Ended, vlc.State.Stopped, vlc.State.Error):
#        break
#    time.sleep(5.2)

    # stop play
    #player.stop()





#   def apiMediaPlaylistUpdate(self, playlist=[]):
#        """Method is called when playall was called."""
#        pass

#    def apiMediaPlay(self, url):
#        """Method is called when play was called."""
#        pass

#    def apiMediaStop(self):
#        """Method is called when stop  was called."""
#        pass

#    def apiMediaVolume(self, volume):
#        """Method is called when volume up/down was called."""
#        pass


#    def apiMediaGetVolume(self):
#        """Method is called when get volume was called."""
#        pass

#    def apiMediaGetState(self):
#        """Method is called when get state was called."""
#        pass



class Media:
    def __init__(self):
#        self.__radio = RadioClass.RadioClass()
        self.__player = vlc.MediaPlayer()
        self.__idx = 0
        self.__playlist = []
        self.__player.audio_set_volume(50)

    def initializePlaylistData(self, playlist):
#        self.__radio.getRadioStopRequest()
        self.__idx = 0
        self.__playlist.clear()
        self.__playlist = playlist
        #except Exception as e:
        #    logging.error('Media deamon exception(PlayAll) :' + str(e))

    def playYT(self, url):
        ydl_opts = {
           "format": "bestaudio",
           "quiet": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = info["url"]

        print("Stream URL:", audio_url)

        # setting media to the
        self.__player.set_media(vlc.Media(audio_url))

        self.__player.play()


    def playStream(self, url):
        print("Stream URL:", url)

        # setting media to the
        self.__player.set_media(vlc.Media(url))
        self.__player.play()

    def setVolume(self, volume):
        self.__player.audio_set_volume(volume)

    def getVolume(self):
        return self.__player.audio_get_volume()

    def getState(self):
        state = self.__player.get_state()
        if (state in (vlc.State.Ended, vlc.State.Stopped, vlc.State.Error)):
            return "stopped"
        elif (state == vlc.State.Playing):
            return "playing"
        elif (state == vlc.State.Paused):
            return "paused"
        else:
            return "unknown"

    
    def stop(self):
        self.__player.stop()


# ------------------------------------------------------------------------------------------------------------------------


class MediaDeamonClass(threading.Thread, APIMediaInterface.APIMediaInterface):
                
    def __init__(self):
        threading.Thread.__init__(self)
        self.__stopEvent = False
        self.__config = ConfigClass.ConfigClass()
        self.__media = Media()
        self.__state = "unknown"

    def apiMediaPlaylistUpdate(self, data = []):
        """Overrides APIMediaInterface.apiMediaPlaylistUpdate()"""
        self.__media.initializePlaylistData(data)

    def apiMediaPlay(self, url):
        """Overrides APIMediaInterface.apiMediaPlay()"""
        self.__media.stop()
        time.sleep(2)
        self.__media.playStream(url)

    def apiMediaPlayYoutube(self, url):
        """Overrides APIMediaInterface.apiMediaPlayYoutube()"""
        self.__media.stop()
        time.sleep(2)
        self.__media.playYT(url)

    def apiMediaStop(self):
        """Overrides APIMediaInterface.apiMediaStop()"""
        self.__media.stop()

    def apiMediaVolume(self, volume):
        """Overrides APIMediaInterface.apiMediaVolume()"""
        self.__media.setVolume(volume)

    def apiMediaGetVolume(self):
        """Overrides APIMediaInterface.apiMediaGetVolume()"""
        return self.__media.getVolume()

    def apiMediaGetState(self):
        """Method is called when get state was called."""
        return self.__state


    def stop(self):
        self.__stopEvent = True

    def run(self):
        log = logging.getLogger('werkzeug')

        logging.info('HCC media thread initialized')
        #log.setLevel(logging.ERROR)

        while not self.__stopEvent:
            try:
                time.sleep(1)
                self.__state = self.__media.getState()
            except Exception as e:
                logging.error('Media deamon exception : ' + str(e))
