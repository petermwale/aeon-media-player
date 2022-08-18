
from os.path import split
from pygame.image import frombuffer
from pygame.transform import scale
from pyglet.window import Window
from pyglet.media import Player, load
from widget import Widget, Image
from const import BLACK


class Movie(Widget):
    """Controls video playback"""
    
    def __init__(self, parent):
        super(Movie, self).__init__(parent)
        self.player = Player()
        self.win = Window(visible=False)
        
    def stretch(self, image):
        """Returns a resized image to fit window (screen) size """
        w1, h1 = self.screen.get_size()
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
    
    def play(self, file):
        if self.player.playing:
            self.player.pause()
        self.player = Player()
        try:
            source = load(file) 
        except Exception as err:
            print(f"Error loading media '{file}':", err)  
            return
        self.source = file
        self.player.queue(source)
        self.player.play()
        
        if self.getRoot().audioControl.player.playing:
            self.getRoot().audioControl.player.pause()
        
        self.getRoot().setTitle("{0} | Aeon Media Player".format(split(file)[1]))
        self.videoLength = source.duration
        self.parent.controls.seeker.config({"to": self.videoLength})

        self.getRoot().timer.reset()
        self.getRoot().timer.bind(self.check, 1)
        
        @self.win.event
        def on_draw():
            texture = self.player.get_texture()
            data = texture.get_image_data()
            pixels = data.get_data("RGBA", data.width * 4)
            image = self.stretch(frombuffer(pixels, (data.width, data.height), "RGBA")) 
            w1, h1 = self.screen.get_size()
            w2, h2 = image.get_size()             
            self.screen.fill(BLACK)
            self.screen.blit(image, (w1 // 2 - w2 // 2, h1 // 2 - h2 // 2))

    def check(self):
        if self.player.source and self.player.time > self.videoLength and not self.parent.playback_paused:
            if self.parent.repeat_mode == "all":
                self.parent.goNext()
            elif self.parent.repeat_mode == "one":
                self.play(self.source)
            else:
                self.player.pause()
        
    def draw(self):
        self.win.switch_to()
        self.win.dispatch_events()
        self.win.dispatch_event("on_draw")
        
        self.check()
        
        if not self.player.playing:
            return
        
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
            self.parent.controls.ellapsed.config({"ipadx": 2})
            self.parent.controls.duration.config({"ipadx": 3})
            self.parent.controls.seeker.config({"padx": 191, "ipadx": 1})
            Hour = ""
        else:
            self.parent.controls.ellapsed.config({"ipadx": 8})
            self.parent.controls.duration.config({"ipadx": 9})
            self.parent.controls.seeker.config({"padx": 220, "ipadx": 10})
                
        self.parent.controls.ellapsed.setValue(Hour + Min + ":" + Sec)
        
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
                
        self.parent.controls.duration.setValue("-" + Hour + Min + ":" + Sec)        
        self.parent.controls.seeker.setValue(self.player.time)