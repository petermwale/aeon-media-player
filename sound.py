from pyglet.media import Player, load as loadMedia


class Sound:

    def __init__(self, parent):
        self.parent = parent
        self.player = Player()
        self.playbackPaused = False
        self.trackLength = 0

    def play(self, audio):
        if self.player.playing:
            self.player.pause()
        videoPlayer = self.parent.GetParent().forms.get("videoControl").mediaPlayer.player
        if videoPlayer.playing:
            videoPlayer.pause()
        self.player = Player()
        self.player.volume = self.parent.parent.volume
        try:
            sound = loadMedia(audio)
            self.duration = sound.duration
            self.trackLength = sound.duration
            self.player.queue(sound)
            self.player.play()
        except Exception as err:
            print("Error playing audio:", err)
            return
        self.source = audio
        self.parent.controls.time.SetMin(0)
        self.parent.controls.time.SetMax(int(self.trackLength))
        return True

    def stop(self):
        self.player.pause()

    def updateTime(self):
        self.parent.controls.time.SetValue(int(self.player.time))
        Min, Sec = divmod(self.player.time, 60)
        Hour, Min = divmod(Min, 60)
        Sec = str(int(Sec))
        Min = str(int(Min))
        Hour = str(int(Hour))
        if len(Sec) < 2:
                Sec = "0" + Sec
        if len(Min) < 2:
            Min = "0" + Min
        if len(Hour) < 2:
            Hour = "0" + Hour + ":"
        if self.trackLength < 60 ** 2:
            Hour = ""
        self.parent.controls.ellapsed.SetLabel(Hour + Min + ":" + Sec)
        Min, Sec = divmod(self.trackLength-self.player.time, 60)
        Hour, Min = divmod(Min, 60)
        Sec = str(int(Sec))
        Min = str(int(Min))
        Hour = str(int(Hour))
        if len(Sec) < 2:
            Sec = "0" + Sec
        if len(Min) < 2:
            Min = "0" + Min
        if len(Hour) < 2:
            Hour = "0" + Hour + ":"
        if self.trackLength < 60 ** 2:
            Hour = ""
        self.parent.controls.remain.SetLabel("-" + Hour + Min + ":" + Sec)

    def check(self):
        self.parent.art.Center()
        self.updateTime()
        #print(self.player.time)
        if self.player.playing and self.trackLength and self.player.time > self.trackLength and not self.playbackPaused:
            if self.parent.parent.loopIndex == 0:
                self.parent.GoNext()
            elif self.parent.parent.loopIndex == 1:
                self.play(self.source)
            else:
                self.player.pause()