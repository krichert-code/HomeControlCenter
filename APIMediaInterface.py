class APIMediaInterface:
    def apiMediaPlaylistUpdate(self, playlist=[]):
        """Method is called when playall was called."""
        pass

    def apiMediaPlay(self, url):
        """Method is called when play was called."""
        pass

    def apiMediaPlayYoutube(self, url):
        """Method is called when play youtube was called."""
        pass

    def apiMediaStop(self):
        """Method is called when stop  was called."""
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
