import sys
from os import listdir, environ
from os.path import isfile, join, abspath
from sys import platform, argv
from random import shuffle
from pygame.image import load
from pygame.transform import scale
from pygame.font import Font
from app import App
from widget import Panel, Label, Image, Button, List, Info
from controls import AudioControl, VideoControl
from file import File
from manager import main, get, load as loadDatabase
from const import *

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except:
        base_path  = abspath(".")

    return join(base_path, relative_path)


class MenuItem(Panel):
    
    def __init__(self, parent, text, image, fun=None):
        super(MenuItem, self).__init__(parent, size_hint=(None, 100), fg1=MENU_BG_COLOR_LIGHT, fg2=SILVER, bg1=SILVER, bg2=MENU_BG_COLOR_LIGHT)
        self.active = False
        self.fun = fun
        
        self.font = Font(resource_path("data/fonts/calibri.ttf"), 45)
        self.text = text
        
        image = load(resource_path(image)).convert_alpha()
        self.image1 = scale(image, (65, 65))
        self.image2 = scale(image, (95, 95))

    def mouseDown(self, pos, btn, double_click):
        if self.isHovering() and self.fun is not  None:
            self.fun()
            self.active = False

    def mouseMoved(self, pos):
        if self.isHovering():
            self.active = True
        else:
            self.active = False

    def draw(self):
        super().draw()
        if self.active:
            text = self.font.render(self.text, True, self.fg2)
            self.screen.blit(text, (self.x + 10, self.y + 50 - text.get_height() // 2))
            self.screen.blit(self.image2, (self.x + self.size[0] - 100, self.y + 50 - self.image2.get_height() // 2))
            self.bg = self.bg2
        else:
            text = self.font.render(self.text, True, self.fg)
            self.screen.blit(text, (self.x + 10, self.y + 50 - text.get_height() // 2))
            self.screen.blit(self.image1, (self.x + self.size[0] - 100, self.y + 50 - self.image1.get_height() // 2))
            self.bg = self.bg1

class Menu(Panel):

    def __init__(self, parent):
        super(Menu, self).__init__(parent, bg1=GREY, size_hint=(400, 600))

        label = Label(self, text="Main Menu", fg1=MENU_BG_COLOR_LIGHT, bg1=SILVER, height=45)
        label.config({"ipady": -320, "ipadx": -1})
        label.pack(side=LEFT)

        menu = MenuItem(self, "Open File", resource_path("data/image/folder.png"), fun=File(self, fun=self.getRoot().tools["playlist"].dropFile).show)
        menu.pack(side=TOP, expand_x=YES)

        menu = MenuItem(self, "Playlist", resource_path("data/image/playlist.png"), fun=lambda: self.getRoot().setCurrent(self.getRoot().tools.get("playlist")))
        menu.pack(side=TOP, expand_x=YES)

        menu = MenuItem(self, "Songs", resource_path("data/image/songs.png"), fun=lambda: self.getRoot().setCurrent(self.getRoot().tools.get("songs")))
        menu.config({"ipady": 101})
        menu.pack(side=TOP, expand_x=YES)

        menu = MenuItem(self, "Videos", resource_path("data/image/video.png"), fun=lambda: self.getRoot().setCurrent(self.getRoot().tools.get("videos")))
        menu.config({"ipady": 202})
        menu.pack(side=TOP, expand_x=YES)

        menu = MenuItem(self, "Settings", resource_path("data/image/settings.png"), fun=lambda: self.getRoot().setCurrent(self.getRoot().tools.get("settings")))
        menu.config({"ipady": 303})
        menu.pack(side=TOP, expand_x=YES)

        menu = MenuItem(self, "About", resource_path("data/image/info.png"), fun=lambda: self.getRoot().setCurrent(self.getRoot().tools.get("about")))
        menu.config({"ipady": 404})
        menu.pack(side=TOP, expand_x=YES)

class Container(Panel):

    def __init__(self, parent, text, image, text2):
        super(Container, self).__init__(parent, bg1=MENU_BG_COLOR)

        if self.name.startswith(("about", "settings")):
            self.config({"bg": MENU_BG_COLOR_LIGHT})

        panel = Panel(self, size_hint=(None, 100), bg1=MENU_BG_COLOR)
        panel.pack(side=TOP, expand_x=YES)

        image = Image(panel, image, size_hint=(100, 100))
        image.pack(side=LEFT, expand_x=YES, expand_y=YES)

        label = Label(panel, text=text, height=45, fg1=WHITE, bg1=MENU_BG_COLOR)
        label.pack(side=LEFT)
        
        label = Label(panel, text=text2, height=20, fg1=WHITE, bg1=MENU_BG_COLOR)
        #label.config({"ipady": 30, "ipadx": -100})
        label.pack()
        
        btn = Button(panel, text="Go to Menu", fg1=WHITE, fg2=GREEN, bg1=MENU_BG_COLOR, bg2=BLACK, size_hint=(85, 23), fun=lambda: self.getRoot().setCurrent(self.getRoot().home))
        btn.config({"ipadx": 20})
        btn.pack(side=RIGHT)

class Playlist(Container):
    
    def __init__(self, parent, label="Playlist", image=resource_path("data/image/playlist.png"), text2="Songs & Videos you play will be here."):
        super(Playlist, self).__init__(parent, label, image, text2)   
        self.mediaList = []  
        self._mediaList = []
        self.index = 0    
        self.shuffled = False
        
        self.listBox = List(self, bg1=WHITE, select_fg1=BLACK, select_fg2=GREEN, select_bg1=WHITE, select_bg2=SILVER, fun1=self.openFile)
        self.listBox.config({"pady": 126})
        self.listBox.pack(side=TOP, expand_x=YES, expand_y=YES)
        
        self.refresh()
            
        panel = Panel(self, size_hint=(None, 23), bg1=MENU_BG_COLOR)
        panel.pack(side=BOTTOM, expand_x=YES)
        
        def openFile():
            if self.listBox.selected is not None:
                self.openFile(self.listBox.selected.track)
                
        def shufflePlaylist():
            self.shuffled = not self.shuffled
            if not self.shuffled:
                shuffle(self.mediaList)
                self.btn.config({"text": "Unshaffle"})
            else:
                self.mediaList = self._mediaList[:]
                self.btn.config({"text": "Shaffle"})
                
            self.loadMedia()
        
        btn = Button(panel, text="Play", size_hint=(33, 20), fg1=WHITE, bg1=MENU_BG_COLOR_LIGHT, bg2=BLACK, fun=openFile)
        btn.config({"ipady": 2})
        btn.pack(side=LEFT)
        
        self.btn = Button(panel, text="Shuffle", size_hint=(50, 20), fg1=WHITE, bg1=MENU_BG_COLOR_LIGHT, bg2=BLACK, fun=shufflePlaylist)
        self.btn.config({"ipady": 2, "ipadx": 3})
        #self.btn.pack(side=LEFT)
        
        def switchTo():
            if self.getRoot().last_was_playing is not None:
                self.getRoot().setCurrent(self.getRoot().last_was_playing)
                
        btn = Button(panel, text="Now playing", size_hint=(90, 20), fg1=WHITE, fg2=GREEN, bg1=MENU_BG_COLOR_LIGHT, bg2=BLACK, fun=switchTo)
        btn.config({"ipadx": 5})
        btn.pack(side=LEFT)
        
    def openFile(self, file):        
        for index, media in enumerate(self.mediaList):
            if media == file:
                self.index = index
                
        self.getRoot().openFile(self.mediaList[self.index], show=True if self.getRoot().isVideo(file) else False)
        self.getRoot().now_playing = self
        
    def dropFile(self, file):
        if self.getRoot().isAudio(file) or self.getRoot().isVideo(file):
            # add file to playlist & database!
            if file not in self.mediaList:
                self.listBox.insert(file, resource_path("data/image/icon.png") if self.getRoot().isAudio(file) else resource_path("data/image/video.png"))
                self.mediaList.append(file)
                self._mediaList = self.mediaList[:]
                
            for index, media in enumerate(self.mediaList):
                if media == file:
                    self.index = index
                
            self.getRoot().openFile(file)
            self.getRoot().now_playing = self
            
    def getNextMedia(self):
        if not self.mediaList:
            return None
        x = self.index + 1
        self.index = x if x <= len(self.mediaList)-1 else 0
        return self.mediaList[self.index]
    
    def getPrevMedia(self):
        if not self.mediaList:
            return None
        x = self.index - 1
        self.index = x if x >= 0 else len(self.mediaList)-1
        return self.mediaList[self.index]
        
    def getMedia(self):
        self._mediaList = get(typ="media")   
        if self.name.startswith("song"):
            self._mediaList = [x for x in self._mediaList if self.getRoot().isAudio(x)]
        elif self.name.startswith("video"):
            self._mediaList = [x for x in self._mediaList if self.getRoot().isVideo(x)]
        self.mediaList = self._mediaList
        return self._mediaList
        
    def loadMedia(self):
        self.getMedia()
        self.listBox.clear()
        for media in self.mediaList:
            self.listBox.insert(media, resource_path("data/image/icon.png") if self.getRoot().isAudio(media) else resource_path("data/image/video.png"))

    def refresh(self):
        if self.name.startswith("play"):
            return
        #files = get(typ="media")
        #if not files:
         #   self.listBox.clear()
          #  return
        self.loadMedia()

class Songs(Playlist):
    
    def __init__(self, parent):
        super(Songs, self).__init__(parent, "Songs", resource_path("data/image/songs.png"), "Songs on your PC.")

class Videos(Playlist):
    
    def __init__(self, parent):
        super(Videos, self).__init__(parent, "Videos", resource_path("data/image/video.png"), "Videos on your PC.")
                        
class Settings(Container):

    def __init__(self, parent):
        super(Settings, self).__init__(parent, "Settings", resource_path("data/image/settings.png"), "Customize your settings here.")
        panel = Panel(self, bg1=MENU_BG_COLOR)
        panel.pack(side=TOP, expand_x=YES, expand_y=YES)

        def popup():
            try:
                main()
            except:
                pass

        btn = Button(panel, text="Scan my PC for media files", fun=popup, fg1=WHITE, bg1=MENU_BG_COLOR_LIGHT, bg2=BLACK, size_hint=(200, 40))
        btn.pack()

class About(Container):
    
    def __init__(self, parent):
        super(About, self).__init__(parent, "About", resource_path("data/image/info.png"), "About *Aeon Media Player*")
        user_name = environ["USERNAME"] if "win" in platform else environ["USER"]
        
        text = [
            "", "", "", "LICENCE",
            f"This software is licenced to *{user_name}* and you can share with your friends!",
            "*Aeon Media Player* is meant to be a small & light-weight media player, much like VLC!",
            "This Software was written by *Peter Mwale* using the Python (visit 'http://python.org' for more info) programming language.",
            "I made use of the following Python libraries: Pygame ('http://pygame.org') for the GUI, Pyglet ('http://pyglet.org')",
            "for audio & video playback, eyeD3 ('http://eyed3.org') and mutagen ('http://mutagen.org') for extracing audio metadata.",
            "The source code of this software if FREE to use and/or modify (Open Source) [as long as you dont take credit for yourself],",
            "and may be found on github.", "", "",
            "USAGE", "For the basic usage of this app, please read the *readme.txt* file which should come together",
            "with this software. If you want to explore more features of the app, please request the video guide.","", "",
            "CREDIT", "Here is a list of websites from which i downloaded images used in this software:",
            "'http://pngtree.com'", "I do not take credit for the images i have used in anyway.", "", ""
            "CONTACTS", "You can always find me on the following platforms:",
            "Facebook: tony wat/ip man, Email: peteraugustinemwale@gmail.com, Github: @petermwale,",
            "Call/SMS/WhatsApp: +265997696464 / +265888732209 (not. on WhatsApp)", "", ""
            "Courtesy of Sub-Zero Inc. Copyright © 2021. By Peter Mwale"
            ]
        
        for index, text in enumerate(text):
            info = Info(self, text=text, fg1=WHITE, height=20)
            info.config({"ipady": 15 * index - 235})
            info.pack()
        
        panel = Panel(self, bg1=MENU_BG_COLOR, size_hint=(None, 20))
        panel.pack(side=BOTTOM, expand_x=YES)

class Home(Panel):

    def __init__(self, parent):
        super(Home, self).__init__(parent, bg1=MENU_BG_COLOR)
        menu = Menu(self)
        menu.pack()
        panel = Panel(self, size_hint=(None, 25), bg1=MENU_BG_COLOR)
        panel.pack(side=BOTTOM, expand_x=YES)

class Aeon(App):
    
    def onCreate(self, info):
        super(Aeon, self).onCreate(info, title="Aeon Media Player", size=(1000, 700), icon=resource_path("data/image/icon.png"))
        self.tools = {"playlist": Playlist(self), "songs": Songs(self), "videos": Videos(self),
                      "settings": Settings(self), "about": About(self)}        
        self.form = None
        self.last_was_playing = None
        self.home = Home(self)
        self.audioControl = AudioControl(self)
        self.videoControl = VideoControl(self)
        self.setCurrent(self.home)
        
        if len(argv) > 1:
            for file in argv[1:]:
                self.tools.get("playlist").dropFile(file)
        
    def isAudio(self, file):
        return isfile(file) and file.lower().endswith((".mp3", ".wav", ".amr", ".m4a", ".mid", ".ogg", ".aac"))
    
    def isVideo(self, file):
        return isfile(file) and file.lower().endswith((".mp4", ".flv", ".mkv", ".avi", ".mpg"))
        
    def openFile(self, file, show=True):
        if self.isVideo(file):
            if show:
                self.setCurrent(self.videoControl)
            self.videoControl.Play(file)
        elif self.isAudio(file):
            if show:
                self.setCurrent(self.audioControl)
            self.audioControl.Play(file)
        
    def setCurrent(self, form):
        if self.form is not None:
            self.form.unpack()
        form.pack(expand_x=YES, expand_y=YES)
        #if form.name.startswith(("song", "video")):
         #   form.refresh()
        self.form = form
        
if __name__ == "__main__":
    Aeon().run()