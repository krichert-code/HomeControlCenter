class APIMediaInterface:

    def apiMediaPlayRadioStream(self, name, url):
        """Method is called when play was called."""
        pass

    def apiMediaPlayYoutube(self, url):
        """Method is called when play youtube was called."""
        pass

    def apiMediaPlayYoutubeList(self, playlist):
        """Method is called when play youtube playlist was called."""
        pass

    def apiMediaPlayMp3(self, directory):
        """Method is called when play was called."""
        pass

    def apiMediaStop(self):
        """Method is called when stop  was called."""
        pass

    def apiMediaPlayNext(self):
        """Method is called when play next was called."""
        pass

    def apiMediaVolume(self, volume):
        """Method is called when volume up/down was called."""
        pass

    def apiMediaGetVolume(self):
        """Method is called when get volume was called."""
        pass

    def apiMediaGetState(self):
        """Method is called when get state was called."""
        pass

    def apiMediaGetMetaData(self):
        """Method is called when get media metadata was called."""
        pass
