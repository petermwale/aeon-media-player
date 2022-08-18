import sys
from os.path import split, abspath, join
from pygame.mouse import set_visible, get_rel
from pygame.time import get_ticks
from pygame.image import load as loadImage
from pygame.locals import K_f, K_n, K_p, K_m, K_v, K_SPACE, K_UP, K_DOWN
from pyglet.media import Player, load
from widget import Panel, Button, Info, Slider, Label, Image, Vinyl
from movie import Movie
from tags import getAlbumArt, getTrackInfo
from const import *

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except:
        base_path  = abspath(".")

    return join(base_path, relative_path)


class Controls(Panel):
        
    def __init__(self, parent):
        super(Controls, self).__init__(parent, size_hint=(None, 45))

        label1 = Info(self, fg1=WHITE, align=LEFT, text="Repeat: All")
        label1.config({"ipady": 48, "ipadx": 2})
        label1.pack(side=BOTTOM, expand_x=YES)

        label2 = Info(self, fg1=BLACK, align=LEFT, text="Repeat: All")
        label2.config({"ipady": 30, "ipadx": 2})
        label2.pack(side=BOTTOM, expand_x=YES)

        self.labels = [label1, label2]
        
        panel = Panel(self, bg1=SILVER, size_hint=(None, 20))
        panel.pack(expand_x=YES)
        
        btn = Button(panel, image1=resource_path("data/image/prev.png"), fun=self.parent.goPrev)
        btn.config({"ipadx": 1})
        btn.pack(side=LEFT)
        
        
        self.btnPlay = Button(panel, image1=resource_path("data/image/pause.png"), fun=self.parent.play)
        self.btnPlay.config({"ipadx": 1})
        self.btnPlay.pack(side=LEFT)
        
        btn = Button(panel, image1=resource_path("data/image/next.png"), fun=self.parent.goNext)
        btn.config({"ipadx": 2})
        btn.pack(side=LEFT)
        
        self.ellapsed = Label(panel, text="00:00", fg1=BLACK)
        self.ellapsed.config({"ipadx": 2})
        self.ellapsed.pack(side=LEFT)
        
        self.seeker = Slider(panel, fg1=GREEN, fun1=self.parent.seek, fun2=self.parent.peek)
        self.seeker.pack(side=LEFT, expand_x=YES)
        
        def show():
            self.getRoot().setCurrent(self.getRoot().now_playing)
            set_visible(True)
        
        btn = Button(panel, text="::", size_hint=(20, 15), fun=show)
        btn.config({"ipadx": 2})
        btn.pack(side=RIGHT)
        
        btn = Button(panel, text="r", size_hint=(20, 15), fun=self.parent.toggleRepeat)
        btn.config({"ipadx": 2})
        btn.pack(side=RIGHT)
        
        self.duration = Label(panel, text="00:00", fg1=BLACK)
        self.duration.config({"ipadx": 3})
        self.duration.pack(side=RIGHT)
        
        self.count = 0
        
    def keyDown(self, key, char):
        if key == K_SPACE:
            self.parent.play()
        elif key == K_p:
            self.parent.goPrev(show=True)
        elif key == K_n:
            self.parent.goNext(show=True)
        
    def draw(self):
        self.count += 1
        if self.count < 200 or self.isHovering():
            super().draw()
            set_visible(True)
        else:
            set_visible(False)

class VolumeControl(Panel):
    
    def __init__(self, parent):
        super(VolumeControl, self).__init__(parent, bg1=BLACK, size_hint=(250, 250), border=0)  
        
        panel = Panel(self, bg1=GREY, border=3)
        panel.config({"ipadx": -1, "padx":-3, "ipady":-1, "pady":-3})
        panel.pack(expand_x=YES, expand_y=YES)
        
        self.level = 50
        self.label = Info(self, text="50%", fg1=SILVER, height=100)
        self.label.pack()
        
        self.count = 200
        
        def setVolume(val):
            if val * 100 > self.level:
                self.setVolume(1)
            elif val * 100 < self.level:
                self.setVolume(-1)            
        
        self.slider = Slider(self, fg1=SILVER, bg1=GREY, size_hint=(None, 9), value=50, to=100, fun1=setVolume)
        self.slider.config({"ipadx": 5, "padx": 6, "ipady": 5})
        self.slider.pack(side=BOTTOM, expand_x=YES)
        
    def setVolume(self, level):
        if level > 0:
            x = self.level + 5
            self.level = x if x <= 100 else 100
        elif level < 0:
            x = self.level - 5
            self.level = x if x >= 0 else 0
        if self.parent.name.startswith("audio"):
            self.parent.player.volume = self.level / 100
        elif self.parent.name.startswith("video"):
            self.parent.movie.player.volume = self.level / 100
            
        self.slider.setValue(self.level)
        self.label.setValue(f"{self.level} %")
        self.count = 0
        
    def keyDown(self, key, char):
        if self.count < 200:
            super().keyDown(key, char)
        
    def draw(self):
        self.count += 1
        if self.count < 200:
            super().draw()
                     
class MediaControl(Panel):
    
    def __init__(self, *args, **kwargs):
        super(MediaControl, self).__init__(*args, **kwargs)
        
        self.volumeControl = VolumeControl(self)        
        self.controls = Controls(self)
        self.album_art = "image"

        self.repeat_modes = ["all", "one", "off"]
        self.repeat_mode_index = 0
        self.repeat_mode = self.repeat_modes[self.repeat_mode_index]

    def toggleRepeat(self):
        x = self.repeat_mode_index + 1
        self.repeat_mode_index = x if x <= 2 else 0
        self.repeat_mode = self.repeat_modes[self.repeat_mode_index]

        if self.repeat_mode == "all":
            for label in self.controls.labels:
                label.setValue("Repeat: All")
        elif self.repeat_mode == "one":
            for label in self.controls.labels:
                label.setValue("Repeat: One")
        else:
            for label in self.controls.labels:
                label.setValue("Repeat: Off")
        
    def goPrev(self, show=False):
        media = self.getRoot().now_playing.getPrevMedia()
        if media is not None:
            if self.getRoot().isAudio(media):
                self.getRoot().audioControl.Play(media) 
                if show:
                    self.getRoot().setCurrent(self.getRoot().audioControl)
            elif self.getRoot().isVideo(media):
                self.getRoot().videoControl.movie.play(media)
                if show:
                    self.getRoot().setCurrent(self.getRoot().videoControl)

    
    def goNext(self, show=False):
        media = self.getRoot().now_playing.getNextMedia()
        if media is not None:
            if self.getRoot().isAudio(media):
                self.getRoot().audioControl.Play(media) 
                if show:
                    self.getRoot().setCurrent(self.getRoot().audioControl)
            elif self.getRoot().isVideo(media):
                self.getRoot().videoControl.movie.play(media)  
                if show:
                    self.getRoot().setCurrent(self.getRoot().videoControl)                   
        
    def mouseMoved(self, pos):
        self.controls.count = 0
        
    def mouseDown(self, pos, btn, double_click):
        if double_click:
            self.getRoot().switchFullscreen()
        super().mouseDown(pos, btn, double_click)
        
    def mouseDragged(self, pos):
        x, y = get_rel()
        val = -1 if y > 0 else 1 if y < 0 else 0
        self.volumeControl.setVolume(val)
    
    def keyDown(self, key, char):
        if key == K_f:
            pass#self.getRoot().switchFullscreen()
        elif key == K_UP and not self.name.startswith("media"):
            self.volumeControl.setVolume(1)
        elif key == K_DOWN and not self.name.startswith("media"):
            self.volumeControl.setVolume(-1)
        elif key == K_m:
            self.getRoot().setCurrent(self.getRoot().now_playing)
            set_visible(True)
        elif key == K_v and self.name.startswith("audio"):
            if self.album_art == "image":
                self.album_art = "vinyl"
            elif self.album_art == "vinyl":
                self.album_art = "image"
                
            if self.album_art == "vinyl":
                self.children[self.art.child_pos] = Vinyl(self, self.album_art_path)
                self.children[self.art.child_pos].resize()
                self.config({"bg": self.children[self.art.child_pos].getColor()})
            elif self.album_art == "image":
                self.children[self.art.child_pos] = Image(self, self.album_art_path)
                self.children[self.art.child_pos].resize()
                self.config({"bg": self.children[self.art.child_pos].getColor()})
        super().keyDown(key, char)
        
    def dropFile(self, file):
        self.getRoot().tools.get("playlist").dropFile(file)

class AudioControl(MediaControl):
     
    def __init__(self, parent):
        super(AudioControl, self).__init__(parent)
        
        self.player = Player() 
               
        self.art = Image(self, resource_path("data/image/art.png"))
        self.art.resize()
        self.art.pack(expand_x=YES, expand_y=YES)
        
        self.label = Info(self, fg1=BLACK, align=LEFT)
        self.label.config({"force_color": False})
        self.label.pack(side=TOP, expand_x=YES)
                
        self.config({"bg": self.art.getColor()})
        self.controls.pack(side=BOTTOM, expand_x=YES)
        self.volumeControl.pack()
        self.playback_paused = False
        
        def check():
            if self.player.source and self.player.time > self.trackLength and not self.playback_paused:
                if self.repeat_mode == "all":
                    self.goNext()
                elif self.repeat_mode == "one":
                    self.Play(self.source)
                else:
                    self.player.pause()
        
        self.getRoot().timer.bind(check, 1)
        
    def Play(self, file):
        if self.player.playing:
            self.player.pause()
            
        self.player = Player()
        try:
            source = load(file) 
        except Exception as err:
            print(f"Error loading media '{file}':", err)  
            return
        self.source = file
        
        self.info = getTrackInfo(file)
        self.info_index = 0        
        self.trackLength = self.info[-1]
        
        self.player.queue(source)
        self.player.play()
        self.playback_paused = False
        
        if self.getRoot().videoControl.movie.player.playing:
            self.getRoot().videoControl.movie.player.pause()
        
        self.getRoot().last_was_playing = self
        
        self.controls.btnPlay.config({"image": loadImage(resource_path("data/image/pause.png")).convert_alpha()})        
        self.getRoot().setTitle("{0} | Aeon Media Player".format(split(file)[1]))
        self.controls.seeker.config({"to": self.trackLength})
        
        self.album_art_path = getAlbumArt(file)        
        self.children[self.art.child_pos] = Vinyl(self, self.album_art_path) if \
            self.album_art == "vinyl" else Image(self, self.album_art_path)
        self.children[self.art.child_pos].resize()
        self.config({"bg": self.children[self.art.child_pos].getColor()})
            
    def play(self):
        if self.player.source and not self.player.playing:
            self.player.play()
            self.controls.btnPlay.config({"_image": loadImage(resource_path("data/image/pause.png")).convert_alpha()})
            self.playback_paused = False
        elif self.player.source and self.player.playing:
            self.player.pause()
            self.controls.btnPlay.config({"_image": loadImage(resource_path("data/image/play.png")).convert_alpha()})
            self.playback_paused = True

    def seek(self, val):
        
        def get_decimal_points(num):
            index = str(num).rfind(".")
            if index == -1:
                return 0
            return len(str(num)[index + 1:])
        
        if self.player.source:
            pos = round(val * self.trackLength, get_decimal_points(self.trackLength))
            print(pos, "of", self.trackLength)
            self.player.seek(pos)
            
    def peek(self, val):
        pass
        
    def draw(self):
        super().draw()
                
        if not self.player.playing:
            return
        
        if get_ticks() % 1300 == 0:
            x = self.info_index + 1  
            self.info_index = x if x < 3 else 00
            
        if get_ticks() % 3 == 0:
            self.children[self.art.child_pos].rotate()
                  
        self.label.setValue(self.info[:3][self.info_index])
        
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
            self.controls.ellapsed.config({"ipadx": 2})
            self.controls.duration.config({"ipadx": 3})
            self.controls.seeker.config({"padx": 191, "ipadx": 1})
            Hour = ""
        else:
            self.controls.ellapsed.config({"ipadx": 8})
            self.controls.duration.config({"ipadx": 9})
            self.controls.seeker.config({"padx": 220, "ipadx": 10})
                
        self.controls.ellapsed.setValue(Hour + Min + ":" + Sec)
        
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
            
        if self.trackLength < 60 ** 2:Hour = ""
                
        self.controls.duration.setValue("-" + Hour + Min + ":" + Sec)       
        self.controls.seeker.setValue(self.player.time)       
        self.art.rotate() 
        #self.getRoot().timer.bind(tick, 1)
 
class VideoControl(MediaControl):
     
    def __init__(self, parent):
        super(VideoControl, self).__init__(parent)
         
        self.movie = Movie(self)
        self.movie.pack(expand_x=YES, expand_y=YES)
        
        self.controls.pack(side=BOTTOM, expand_x=YES)
        self.volumeControl.pack()
        
        self.playback_paused = False
         
    def Play(self, file):
        self.movie.play(file)
        self.getRoot().last_was_playing = self
        
    def play(self):
        if self.movie.player.source and not self.movie.player.playing:
            self.movie.player.play()
            self.controls.btnPlay.config({"_image": loadImage(resource_path("data/image/pause.png")).convert_alpha()})
            self.playback_paused = False
        elif self.movie.player.source and self.movie.player.playing:
            self.movie.player.pause()
            self.controls.btnPlay.config({"_image": loadImage(resource_path("data/image/play.png")).convert_alpha()})
            self.playback_paused = True

    def seek(self, val):
        
        def get_decimal_points(num):
            index = str(num).rfind(".")
            if index == -1:
                return 0
            return len(str(num)[index + 1:])
        
        if self.movie.player.source:
            pos = round(val * self.movie.videoLength, get_decimal_points(self.movie.videoLength))            
            print(pos, "of", self.movie.videoLength)
            self.movie.player.seek(pos)
            
    def peek(self, val):
        if self.movie.player.source:
            print(val * self.movie.player.time)