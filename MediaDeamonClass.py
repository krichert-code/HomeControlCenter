import random
import threading
import time
import ConfigClass
import APIMediaInterface
import logging
import yt_dlp
import vlc
import time
from pathlib import Path

class Media:
    SOURCE_NONE = 0
    SOURCE_MP3 = 1
    SOURCE_STREAM = 2
    SOURCE_YOUTUBE = 3

    def __init__(self):
        self.__player = vlc.MediaPlayer()
        self.__list_player = vlc.MediaListPlayer()
        self.__list_player.set_media_player(self.__player)

        self.__sourcePlaying = Media.SOURCE_NONE
        self.__url = ""
        self.__player.audio_set_volume(50)
        self.__ytTitle = None

    def __stop(self):
        self.__player.stop()
        self.__list_player.stop()
        media_list = vlc.MediaList()
        self.__list_player.set_media_list(media_list)
    
    def playYT(self, url):
        ydl_opts = {
           "format": "bestaudio",
           "quiet": True,
        }

        self.__sourcePlaying = Media.SOURCE_YOUTUBE
        self.__stop()

        self.__url = url

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = info["url"]
            self.__ytTitle = info["title"]

        # setting media to the
        self.__player.set_media(vlc.Media(audio_url))
        self.__player.play()


    def playStream(self, name, url):
        self.__sourcePlaying = Media.SOURCE_STREAM
        self.__url = name
        self.__stop()
        self.__player.set_media(vlc.Media(url))
        self.__player.play()

    def playMp3File(self, directory):
        folder = Path(directory)
        if not folder.is_dir():
            return

        files = sorted(
            str(f) for f in folder.iterdir()
            if f.is_file() and f.suffix.lower() == '.mp3'
        )
        if not files:
            return

        self.__sourcePlaying = Media.SOURCE_MP3
        random.shuffle(files)
        self.__url = directory

        media_list = vlc.MediaList()
        for f in files:
            media_list.add_media(vlc.Media(f))

        self.__stop()
        self.__list_player.set_media_list(media_list)
        self.__list_player.play()

    def playNext(self):
        if self.__list_player.is_playing():
            self.__list_player.next()
                
    def setVolume(self, volume):
        self.__player.audio_set_volume(volume)

    def getVolume(self):
        return self.__player.audio_get_volume()

    def getTitle(self):
        if self.__sourcePlaying == Media.SOURCE_MP3:
            media = self.__player.get_media()
            if media is not None:
                return media.get_meta(vlc.Meta.Title)
        elif self.__sourcePlaying == Media.SOURCE_YOUTUBE:
            return self.__ytTitle
        elif self.__sourcePlaying == Media.SOURCE_STREAM:
            return self.__url
        
        return None
    
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
        self.__sourcePlaying = Media.SOURCE_NONE
        self.__player.stop()


# ------------------------------------------------------------------------------------------------------------------------


class MediaDeamonClass(threading.Thread, APIMediaInterface.APIMediaInterface):
                
    def __init__(self):
        threading.Thread.__init__(self)
        self.__stopEvent = False
        self.__media = Media()
        self.__state = "unknown"
        self.__ytPlaylist = []

    def apiMediaPlayMp3(self, path):
        """Method is called when play was called."""
        self.__media.stop()
        time.sleep(1)
        self.__media.playMp3File(path)

    def apiMediaPlayRadioStream(self, name, url):
        """Overrides APIMediaInterface.apiMediaPlay()"""        
        self.__media.stop()
        time.sleep(1)
        self.__media.playStream(name, url)

    def apiMediaPlayYoutube(self, url):
        """Overrides APIMediaInterface.apiMediaPlayYoutube()"""
        self.__media.stop()
        time.sleep(1)
        self.__media.playYT(url)

    def apiMediaStop(self):
        """Overrides APIMediaInterface.apiMediaStop()"""
        self.__ytPlaylist.clear()
        self.__media.stop()

    def apiMediaPlayNext(self):
        """Overrides APIMediaInterface.apiMediaPlayNext()"""
        if len(self.__ytPlaylist) > 0:
            self.__media.stop()
        else:
            self.__media.playNext()

    def apiMediaVolume(self, volume):
        """Overrides APIMediaInterface.apiMediaVolume()"""
        self.__media.setVolume(volume)

    def apiMediaGetVolume(self):
        """Overrides APIMediaInterface.apiMediaGetVolume()"""
        return self.__media.getVolume()

    def apiMediaGetState(self):
        """Method is called when get state was called."""
        return self.__state

    def apiMediaGetMetaData(self):
        """Method is called when get media metadata was called."""
        title = self.__media.getTitle()
        if title is not None:
            return title + " [" + str(self.__media.getVolume()) + "%]"
        return None

    def apiMediaPlayYoutubeList(self, playlist):
        """Overrides APIMediaInterface.apiMediaPlayYoutubeList()"""
        self.__media.stop()
        time.sleep(1)
        self.__ytPlaylist = playlist

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
                if self.__state == "stopped" and len(self.__ytPlaylist) > 0:
                    next_url = self.__ytPlaylist.pop(0)
                    self.__media.playYT(next_url)
            except Exception as e:
                logging.error('Media deamon exception : ' + str(e))
