from sys import platform
from threading import Thread
from datetime import datetime
from wx import Image as WX_IMAGE, Bitmap
from PIL import Image as PIL_IMAGE
from pygame.image import frombuffer, tostring
from pygame.transform import scale
from pyglet import clock
from pyglet.window import Window
from pyglet.media import Player, load as loadMedia
from pyglet.gl import Config


class Movie:

    def __init__(self, parent):
        self.parent = parent
        self.player = Player()
        config = Config(major_version=3, minor_version=3, forward_compatible=True)
        config.compat_profile = True
        self.win = Window(visible=False, config=config)
        self.playbackPaused = False
        self.videoLength = 0
        self.runThread()

        @self.win.event    
        def on_draw():
            if not self.player.get_texture():
                return
            try:
                texture = self.player.get_texture()
                data = texture.get_image_data()
                pixels = data.get_data("RGBA", data.width * 4)
                pyImage = frombuffer(pixels, (data.width, data.height), "RGBA")
                pyImage = self.stretch(pyImage)
                pilImage = PIL_IMAGE.frombuffer("RGBA", (pyImage.get_width(), pyImage.get_height()), tostring(pyImage, "RGBA"))
                wxImage = WX_IMAGE(pilImage.size[0], pilImage.size[1])
                wxImage.SetData(pilImage.convert("RGB").tobytes())
                bitmap = Bitmap(wxImage)
                self.parent.frame.SetBitmap(bitmap)
                self.parent.frame.Center()
            except Exception as err:
                print("Error creating texture:", err)
                self.parent.GetParent().Destroy()

    def stretch(self, image):    
        """Returns a resized image to fit window (screen) size """
        w1, h1 = self.parent.GetSize()
        w2, h2 = image.get_size()
        
        scale_factor = 0.94 # Scale factor used to resize image

        if w2 * h2 > w1 * h1: # Image is greater than screen size
            while w2 > w1 or h2 > h1:
                w2 *= scale_factor
                h2 *= scale_factor
                image = scale(image, (int(w2), int(h2)))
                w2, h2 = image.get_size()
        else: # Image is smaller than screen size
            while w2 < w1 and h2 < h1:
                w2 /= scale_factor
                h2 /= scale_factor
                image = scale(image, (int(w2), int(h2)))
                w2, h2 = image.get_size()
                
        return image

    def play(self, video):
        if self.player.playing:
            self.player.pause()
        audioPlayer = self.parent.GetParent().forms.get("audioControl").mediaPlayer.player
        if audioPlayer.playing:
            audioPlayer.pause()
        self.player = Player()
        self.player.volume = self.parent.parent.volume
        try:
            movie = loadMedia(video)
            self.duration = movie.duration
            self.videoLength = movie.duration
            self.player.queue(movie)
            self.player.play()
        except Exception as err:
            print("Error playing video:", err)
            return
        self.source = video
        self.parent.controls.time.SetMin(0)
        self.parent.controls.time.SetMax(int(self.videoLength))
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
        if self.videoLength < 60 ** 2:
            Hour = ""
        self.parent.controls.ellapsed.SetLabel(Hour + Min + ":" + Sec)
        Min, Sec = divmod(self.videoLength-self.player.time, 60)
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
        if self.videoLength < 60 ** 2:
            Hour = ""
        self.parent.controls.remain.SetLabel("-" + Hour + Min + ":" + Sec)

    def check(self):
        self.updateTime()
        #print(self.player.time)
        if self.player.playing and self.videoLength and self.player.time > self.videoLength and not self.playbackPaused:
            if self.parent.parent.loopIndex == 0:
                self.parent.GoNext()
            elif self.parent.parent.loopIndex == 1:
                self.play(self.source)
            else:
                self.player.pause()

    def tick(self, arg):
        while True:
            clock.tick(1)
            #print(datetime.now())
            self.win.switch_to()
            self.win.dispatch_events()
            self.win.dispatch_event("on_draw")

    def runThread(self):
        Thread(target=self.tick, args=[None], daemon=True).start()