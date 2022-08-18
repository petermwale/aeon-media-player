import sys
from os import listdir, environ
from os.path import exists, isfile, join, split, expanduser, abspath
from sys import exit as Exit, platform

if "win" in platform:
    from wmi import WMI
    
from form import Form
from widget import Panel, Button, List, Label
from pygame.locals import *
from const import *

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except:
        base_path  = abspath(".")

    return join(base_path, relative_path)


class File(Form):
    
    """This module is, in essence, a 'File Chooser'. It pops up a file dialog and allows the user,
        to view and select a media [It only filters folders, audio & video files.] from the PC or other 
        storage devices connected to the computer and to play them. And in the future version, it will
        allow users to access media files over a network e.g FTP or HTTP.
        """
    
    def __init__(self, parent, title="Open Media", size=(850, 650), fun=None):
        super(File, self).__init__(parent, title, size)
        self.fun1 = fun # function called when user selects a file [by hitting RETURN/ENTER] or clicking 'Open'
        self.fun2 = lambda file: self.status.setValue(file) # function called when user scrolls list box.
        
        self.files = [] # list of files - which are shown on the 'list box' - they are kept here internally.
        self.index = 0 # position of 'current selected' file/folder.
        
        panel = Panel(self.container, bg1=SILVER, size_hint=(None, 23))
        panel.pack(side=TOP, expand_x=YES)
        
        btn = Button(panel, image1=resource_path("./././data/image/back.png"), fun=self.goBack, size_hint=(20, 20)) # go up
        # one level of directory tree Button
        btn.config({"ipadx": 1})
        btn.pack(side=LEFT)
        
        btn = Button(panel, image1=resource_path("./././data/image/forward.png"), fun=self.goForward, size_hint=(20, 20)) # go down
        # one level of directory tree Button
        btn.config({"ipadx": 10})
        btn.pack(side=LEFT)
        
        self.label = Label(panel, fg1=BLACK) # label which shows 'current directory'
        self.label.config({"ipadx": 10, "padx": 155})
        self.label.pack(side=LEFT, expand_x=YES)
        
        panel = Panel(self.container, bg1=GREEN)
        panel.config({"pady": 50})
        panel.pack(side=TOP, expand_x=YES, expand_y=YES)
        
        panel2 = Panel(panel, bg1=SILVER, size_hint=(150, None))
        panel2.config({"ipady": 1})
        panel2.pack(side=LEFT, expand_y=YES)
        
        def goDesktop(): # show the 'desktop' folders & media
            if "win" in platform: # We are on Windows":
                self.goDrive(join(environ["USERPROFILE"], "Desktop"))
            elif "linux" in platform  or "darwin" in platform: # We are on Linux or Mac / OSX
                self.goDrive(join(expanduser("~"), "Desktop"))
            self.files.clear()
            self.label.setValue("Desktop")
        
        def goDrives(): # show internal & external 'storage devices' of the PC
            """Lists contents of a drive path/folder. Filters only folders, audios & videos"""
            self.listBox.clear()
            if "win" in platform: # We are on Windows":
                c = WMI()
                drives = [(drive.Caption + "/", drive.VolumeName) for drive in c.Win32_LogicalDisk()]
                for letter, label in drives:
                    self.listBox.insert(letter.upper() ,resource_path( "data/image/drive.png"), label=f"{label} ({letter.upper()})")
            elif "linux" in platform: # We are on Linux
                self.listBox.insert("/", resource_path("data/image/drive.png"), label="Root")
                self.goDrive(f"/media/{environ['USER']}/", is_drive=True, clear=False)
            elif "darwin" in platform: # We are on Mac/OSX
                for drive in listdir("/Volumes"):
                    self.listBox.insert(drive, resource_path("data/image/drive.png"), label=drive)
            self.files.clear()
            self.label.setValue("This PC")    
        
        btn = Button(panel2, image1=resource_path("./././data/image/desktop.png"), fun=goDesktop) # show the 'desktop' Button
        btn.config({"ipady": 45})
        btn.pack(side=TOP)
        
        btn = Button(panel2, image1=resource_path("./././data/image/pc.png"), fun=goDrives) # show 'storage devices' Button
        btn.config({"ipady": 105})
        btn.pack(side=TOP)
        
        btn = Button(panel2, image1=resource_path("./././data/image/web.png")) # show 'network' folders/media Button
        btn.config({"ipady": 310})
        btn.pack(side=TOP)
        
        self.listBox = List(panel, bg1=WHITE, select_fg1=BLACK, select_fg2=GREEN, select_bg1=WHITE, select_bg2=SILVER, fun1=self.goDrive, fun2=self.fun2) # 'list box' to show folders/media
        self.listBox.config({"ipadx": 1, "padx": 156, "ipady": 1})
        self.listBox.pack(side=LEFT, expand_y=YES, expand_x=YES)
        
        panel = Panel(self.container, bg1=SILVER, size_hint=(None, 23))
        panel.pack(side=BOTTOM, expand_x=YES)
        
        self.status = Label(panel, fg1=BLACK, align=LEFT) # show 'selected' folder/media when user scrolls list box
        self.status.config({"wrapLength": 87})
        self.status.pack(side=LEFT)
        
        btn = Button(panel, text="Cancel", size_hint=(50, 20), fun=self.destroy) # cancel file selection Button
        btn.config({"ipady": 2})
        btn.pack(side=RIGHT)
        
        def Open():
            if self.listBox.selected is not None:
                self.goDrive(self.listBox.selected.track)           
        
        btn = Button(panel, text="Open", size_hint=(40, 20), fun=Open) # confirm file selection Button
        btn.config({"ipadx": 1, "ipady": 2})
        btn.pack(side=RIGHT)
        
    def goBack(self):
        """Go up one level of directory tree
        """
        if self.files and self.index > 0:
            self.index -= 1
            self.goDrive(self.files[self.index])
            
    def goForward(self):
        """Go down one level of directory tree
        """
        if self.files and self.index < len(self.files)-1:
            self.index += 1
            self.goDrive(self.files[self.index])        
        
    def go(self, file):
        """Opens selected file
        """
        if self.fun1 is not None:
            self.fun1(file)
        self.destroy() 
        
    def goDrive(self, path, is_drive=False, clear=True):
        """Lists contents of a directory [folders, audio & video files]
        """
        if isfile(path):
            self.go(path)
            return
        if clear:
            self.listBox.clear()
        try:
            for name in listdir(path): # files/folders in  directory named 'path'
                if name.startswith((".", "/", "$")):
                    continue
                obj = join(path, name)
                if isfile(obj):
                    if not (self.getRoot().isAudio(obj) or self.getRoot().isVideo(obj)):
                        continue # skip the file if its not an audio or video
                    if self.getRoot().isAudio(obj):
                        icon = resource_path("./././data/image/audio.png")
                    else:
                        icon = resource_path("./././data/image/video.png")
                else:
                    icon = resource_path("./././data/image/drive.png") if is_drive else resource_path("./././data/image/folder.png")
                self.listBox.insert(obj, icon)
            if not self.files:
                self.index = 0
                self.files.append(path)
            else:
                if path not in self.files:
                    for i in range(len(self.files) - 1 - self.index):
                        self.files.pop()
                    self.files.append(path)
                    self.index += 1
            self.label.setValue(split(path)[1] if len(path) > 3 else path)
            self.status.setValue("")
        except Exception as err:
            print(f"Error reading path '{path}':", err)
            
    def keyDown(self, key, char):
        if key == K_LEFT: # key bindings - calls 'self.goBack'
            self.goBack()
        elif key == K_RIGHT:
            self.goForward() # calls 'self.goForward'
        super().keyDown(key, char)