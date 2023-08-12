import os, sys, random, wx
from os import environ, scandir, listdir
from os.path import isfile, isdir, exists, split, join, expanduser, abspath
from sys import platform
from random import choice
from threading import Thread
from wx import Bitmap, BitmapFromBuffer, BITMAP_TYPE_PNG, Timer
from wx.lib.scrolledpanel import ScrolledPanel
from wx.adv import AboutDialogInfo, AboutBox
from pyglet import clock
from pygame.display import set_mode
from  pygame.image import load, tostring
from pygame.transform import scale
if "win" in platform:
    from wmi import WMI
from movie import Movie
from sound import Sound
from tags import getAlbumArt, getTrackInfo
from database import CreatePlaylist, AddToPlaylist, RemovePlaylist, RenamePlaylist, GetPlaylists

mediaFormats = {
    "audios": (".mp3", ".wma", ".asf", ".sami", ".smi", ".aac", ".adts",".flac", ".ogg", ".opus", ".m4a", ".au", ".mp2", ".vorbis", ".wav"),
    "videos": (".3g2", ".3gp", "3gpp", ".3gp2", ".avi", ".mva", ".m4v", ".mov", ".mp4", ".divx", ".webm", ".wmv", ".xvid", ".mpg", ".flv", ".mkv")
    }

def IsAudio(file):
     return exists(file) and isfile(file) and file.lower().endswith(mediaFormats.get("audios"))

def IsVideo(file):
    return exists(file) and isfile(file) and file.lower().endswith(mediaFormats.get("videos"))

def IsMedia(file):
    return IsAudio(file) or IsVideo(file)

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except:
        base_path  = abspath(".")

    return join(base_path, relative_path)

class Drop(wx.DropTarget):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self._data = wx.DataObjectComposite()
        self.fdo = wx.FileDataObject()
        self._data.Add(self.fdo, True)
        self.SetDataObject(self._data)

    def OnData(self, xcord, ycord, data_result):
        if self.GetData():
            format = self._data.GetReceivedFormat()
            if format.GetType() == wx.DF_FILENAME:
                for file in self.fdo.GetFilenames():
                    if IsMedia(file):
                        self.parent.DropFile(file)
                    elif isdir(file):
                        files = [join(file, x) for x in listdir(file) if IsMedia(join(file, x))]
                        for index, x in enumerate(files):
                            if index == 0:
                                self.parent.forms.get("playlist").DropFile(x)
                            else:
                                self.parent.forms.get("playlist").DropFile(x, play=False)
    
class FormSwitcher(wx.BoxSizer):

    def __init__(self, parent, forms):
        super(FormSwitcher, self).__init__()
        self.parent = parent
        self.forms = forms

        for k, v in self.forms.items():
            self.Add(v, 1, wx.EXPAND)
            v.Hide()

        self.parent.Layout()

    def SwitchForm(self, name):
        form = self.forms.get(name)
        for k, v in self.forms.items():
            v.Hide()
        form.Show()
        self.parent.Layout()

class App(wx.App):
    
    def OnInit(self):
        wx.Log.SetActiveTarget(wx.LogStderr())
        self.win = Window()
        self.win.Show()
        return True
        
class Window(wx.Frame):
    
    def __init__(self):
        super(Window, self).__init__(None, title="Aeon Media Player", size=(900, 700))
        self.SetIcon(wx.Icon(resource_path("data/image/icon.png"), wx.BITMAP_TYPE_PNG))
        self.Center()
        drop = Drop(self)
        self.isFullscreen = False
        self.loopIndex = 0
        self.shuffleMode = False
        self.playlist = None
        self.mediaControl = None
        self.volume = 50
        self.mute = False
        self.timer = Timer(self, 1)
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)

        self.mediaFormats = {
            "audios": (".mp3", ".wma", ".asf", ".sami", ".smi", ".aac", ".adts",".flac", ".ogg", ".opus", ".m4a", ".au", ".mp2", ".vorbis", ".wav"),
            "videos": (".3g2", ".3gp", "3gpp", ".3gp2", ".avi", ".mva", ".m4v", ".mov", ".mp4", ".divx", ".webm", ".wmv", ".xvid", ".mpg", ".flv", ".mkv")
        }

        menuBar = wx.MenuBar(wx.MB_DOCKABLE)

        player = wx.Menu()
        _open = player.Append(-1, "Open File\tCtrl+O", "Select a media file to play")
        self.Bind(wx.EVT_MENU, self.OpenFile, _open)
        openFolder = player.Append(-1, "Open Folder\tCtrl+F", "Play media files in a folder")
        self.Bind(wx.EVT_MENU, self.openFolder, openFolder)
        #openURL = player.Append(-1, "Open URL\tCtrl+U", "Play media files on the internet")
        #self.Bind(wx.EVT_MENU, self.OpenURL, openURL)
        player.AppendSeparator()
        _quit = player.Append(-1, "Quit\tCtrl+Q", "Exit the media player")
        self.Bind(wx.EVT_MENU, lambda event: self.Destroy(), _quit)
        menuBar.Append(player, "&Player")
        playlist = wx.Menu()
        default = playlist.Append(-1, "Queue")
        self.Bind(wx.EVT_MENU, lambda event: self.SetCurrentForm("playlist"), default)
        playlist.AppendSeparator()
        songs = playlist.Append(-1, "Songs")
        self.Bind(wx.EVT_MENU, lambda event: self.SetCurrentForm("songs"), songs)
        artists = playlist.Append(-1, "Artists")
        self.Bind(wx.EVT_MENU, lambda event: self.SetCurrentForm("artists"), artists)
        albums = playlist.Append(-1, "Albums")
        self.Bind(wx.EVT_MENU, lambda event: self.SetCurrentForm("albums"), albums)
        videos = playlist.Append(-1, "Videos")
        self.Bind(wx.EVT_MENU, lambda event: self.SetCurrentForm("videos"), videos)
        playlist.AppendSeparator()
        favorites = playlist.Append(-1, "Favorites")
        self.Bind(wx.EVT_MENU, lambda event: self.SetCurrentForm("favorites"), favorites)
        menuBar.Append(playlist, "&Playlist")
        #options = wx.Menu()
        #toggle = options.Append(-1, "Switch fullscreen")
        #self.Bind(wx.EVT_MENU, ToggleFullScreen, toggle)
        #menuBar.Append(options, "&Options")
        tools = wx.Menu()
        settings = tools.Append(-1, "Settings")
        self.Bind(wx.EVT_MENU, lambda event: self.SetCurrentForm("settings"), settings)
        menuBar.Append(tools, "&Tools")
        help = wx.Menu()
        about = help.Append(-1, "About")
        self.Bind(wx.EVT_MENU, self.AboutPage, about)
        menuBar.Append(help, "&Help")
        
        self.SetMenuBar(menuBar)

        self.forms = {
            "playlist": PlayList(self),
            "songs": Songs(self),
            "artists": Artists(self),
            'albums':Albums(self),
            "videos": Videos(self),
            "mylist": MyList(self),
            "favorites": Favorites(self),
            "audioControl": AudioControl(self),
            "videoControl": VideoControl(self),
            "settings": Settings(self)
        }

        self.forms.get("playlist").listBox.SetDropTarget(drop)
        self.forms.get("audioControl").SetDropTarget(drop)
        self.forms.get("videoControl").SetDropTarget(drop)
        self.formSwitcher = FormSwitcher(self, self.forms)
        self.SetSizer(self.formSwitcher)
        self.mediaControl = None
        self.timer.Start(100)

        self.SetCurrentForm("playlist")
        wx.CallLater(1000, lambda: Thread(target=self.Scan, args=[None], daemon=True).start())

    def ToggleFullScreen(self, event):
        self.isFullscreen = not self.isFullscreen
        self.ShowFullScreen(self.isFullscreen)

    def IsAudio(self, file):
        return exists(file) and isfile(file) and file.lower().endswith(self.mediaFormats.get("audios"))

    def IsVideo(self, file):
        return exists(file) and isfile(file) and file.lower().endswith(self.mediaFormats.get("videos"))

    def IsMedia(self, file):
        return self.IsAudio(file) or self.IsVideo(file)

    def GetSupportedMediaFormats(self):
        """Returns all [internal] supported media files"""
        formats = []
        formats.extend(self.mediaFormats.get("audios"))
        formats.extend(self.mediaFormats.get("videos"))
        allFormats = "Media Files |"
        for extension in formats:
            allFormats += "*" + extension + ";"
        return allFormats

    def OpenFile(self, event):
        defaultDir = environ["USERPROFILE"] if "win" in platform else expanduser("~")
        wildcard = self.GetSupportedMediaFormats()
        dlg = wx.FileDialog(self, message="Open Media File", defaultDir=defaultDir, wildcard=wildcard, style=wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK and dlg.GetPath():
            self.forms.get("playlist").DropFile(dlg.GetPath())

    def openFolder(self, event):
        defaultDir = environ["USERPROFILE"] if "win" in platform else expanduser("~")
        wildcard = self.GetSupportedMediaFormats()
        dlg = wx.DirDialog(self, message="Open Folder", style=wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK and dlg.GetPath():
            files = [join(dlg.GetPath(), x) for x in listdir(dlg.GetPath()) if IsMedia(join(dlg.GetPath(), x))]
            for index, x in enumerate(files):
                if index == 0:
                    self.forms.get("playlist").DropFile(x)
                else:
                    self.forms.get("playlist").DropFile(x, play=False)           

    def OpenURL(self, event):
        url = wx.GetTextFromUser("Enter media URL:", "Open URL", "https://")

    def OpenMediaDialog(self, label):
        self.mediaDialog.Show(label)

    def DropFile(self, media):
        if self.IsAudio(media):
            if self.forms.get("audioControl").Play(media):
                self.SetCurrentForm("audioControl")
        elif self.IsVideo(media):
            if self.forms.get("videoControl").Play(media):
                self.SetCurrentForm("videoControl")

    def OnTimer(self, event):
        self.forms.get("audioControl").mediaPlayer.check()
        self.forms.get("videoControl").mediaPlayer.check()

    def SetCurrentForm(self, name):
        self.formSwitcher.SwitchForm(name)

    def Scan(self, args):
        def walk(path):
            print(f"Discovering '{path}'")
            if not path.startswith((".", "$")):
                #print(path)
                try:
                    for entry in scandir(path):
                        if entry.is_dir(follow_symlinks=False):
                            walk(entry.path)
                        else:
                            if IsAudio(entry.path):
                                #print(entry.path)
                                self.forms.get("songs").mediaList.append(entry.path)
                                self.forms.get("songs").listBox.Config()
                                artist, album, title, length = getTrackInfo(entry.path)
                                # add to artists
                                if artist not in self.forms.get("artists").media:
                                    self.forms.get("artists").media[artist] = []
                                else:
                                    self.forms.get("artists").media.get(artist).append(entry.path)
                                if artist not in self.forms.get("artists").mediaList:
                                    self.forms.get("artists").mediaList.append(artist)
                                # add to albums
                                if album not in self.forms.get("albums").media:
                                    self.forms.get("albums").media[artist] = []
                                else:
                                    self.forms.get("albums").media.get(album).append(entry.path)
                                if artist not in self.forms.get("albums").mediaList:
                                    self.forms.get("albums").mediaList.append(artist)
                                self.forms.get("artists").listBox.Config(ignoreList=True)
                                self.forms.get("albums").listBox.Config(ignoreList=True)
                            elif IsVideo(entry.path):
                                self.forms.get("videos").mediaList.append(entry.path)
                                self.forms.get("videos").listBox.Config()
                except:
                    pass

        paths = [environ["USERPROFILE"] if "win" in platform else expanduser("~")] # paths to search for media files on your PC.
        if "win" in platform:
            paths.extend([x.Caption for x in WMI().Win32_LogicalDisk() if not x.DriveType == 2]) # dont add 'removable' disks to 'paths' on Windows
        for x in paths:
            walk(x)

    def AboutPage(self, event):
        info = AboutDialogInfo()
        info.SetName("Aeon Media Player")
        info.SetVersion("Version 1.0.0")
        info.SetIcon(wx.Icon(resource_path("data/image/icon.png"), wx.BITMAP_TYPE_PNG))
        info.SetCopyright("Copyright (c) 2023 By Peter Mwale")
        info.SetDescription("Aeon is meant to be a small & light-weight media player and \nis an open source project you can contribute. Much like VLC!")
        info.SetWebSite("https://petermwale.com/the-developer/aeon-media-player", "WebSite")
        AboutBox(info)

class ListBox(wx.VListBox):

    def __init__(self, parent):
        super(ListBox, self).__init__(parent)
        self.parent = parent
        self.images = [wx.Bitmap(resource_path("data/image/song-thumb.png"), wx.BITMAP_TYPE_PNG), wx.Bitmap(resource_path("data/image/video-thumb.png"), wx.BITMAP_TYPE_PNG),
        wx.Bitmap(resource_path("data/image/artist-thumb.png"), wx.BITMAP_TYPE_PNG), wx.Bitmap(resource_path("data/image/album-thumb.png"), wx.BITMAP_TYPE_PNG), 
        wx.Bitmap(resource_path("data/image/playlist-thumb.png"), wx.BITMAP_TYPE_PNG)]
        self.imgHeight = self.images[1].GetHeight()
        self.selected = None
        self.ignoreList = False
        self.SetItemCount(len(self.parent.mediaList))

        def OnSelect(event):
            self.selected = self.parent.mediaList[event.GetSelection()]

        self.Bind(wx.EVT_LISTBOX, OnSelect)
        self.Bind(wx.EVT_KEY_DOWN, self.Go)

    def Go(self, event=None):
        if (event is None or event.GetKeyCode() == wx.WXK_RETURN) and self.selected:
            top = wx.GetApp().GetTopWindow()
            if self.parent.name.startswith(("songs", "videos", "mylist", "playlist")):
                top.DropFile(self.selected)
                self.parent.playlist = self
                for index, media in enumerate(self.parent.mediaList):
                    if media == self.selected:
                        self.parent.index = index
            elif self.parent.name.startswith(("artist", "album", "favorite")):
                top.forms.get("mylist").mediaList = [x for x in self.parent.media.get(self.selected)]
                top.forms.get("mylist").listBox.Config()
                top.forms.get("mylist").text1.SetLabel(self.selected + " | ")
                top.forms.get("mylist").text2.SetLabel(f"Songs by {self.selected}" if self.parent.name.startswith("artist") else f"Songs in {self.selected}")
                top.SetCurrentForm("mylist")
        if event is not None:
            event.Skip()

    def OnMeasureItem(self, index):
        """Called to get an items height"""
        # All our items are the same so index is ignored
        return self.imgHeight + 4

    def OnDrawSeparator(self, dc, rect, index):
        """Called to draw the item separator"""
        oldpen = dc.GetPen()
        dc.SetPen(wx.Pen(wx.BLACK))
        dc.DrawLine(rect.x, rect.y, rect.x + rect.width, rect.y)
        rect.Deflate(0, 2)
        dc.SetPen(oldpen)

    def OnDrawItem(self, dc, rect, index):
        """Called to draw the item"""
        # Draw the bitmap
        if self.ignoreList:
            if self.parent.name.startswith("artist"):
                bitmap = self.images[2]
            elif self.parent.name.startswith("album"):
                bitmap = self.images[3]
            else:
                bitmap = self.images[4]
        else:
            bitmap = self.images[1] if self.parent.GetParent().IsVideo(self.parent.mediaList[index]) else self.images[0]

        dc.DrawBitmap(bitmap, int(rect.x + 2), int(((rect.height - self.imgHeight) / 2) + rect.y))
        # Draw the label to the right of the bitmap
        textx = rect.x + 2 + self.imgHeight + 2
        lblrect = wx.Rect(textx, rect.y, rect.width - textx, rect.height)
        dc.DrawLabel(split(self.parent.mediaList[index])[1], lblrect, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)

    def Config(self, ignoreList=False):
        self.ignoreList = ignoreList
        self.parent.mediaList.sort()
        self.SetItemCount(len(self.parent.mediaList))

class Controls(wx.Panel):

    def __init__(self, parent):
        super(Controls, self).__init__(parent)
        self.SetBackgroundColour("Grey")
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        #vbox1 = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(hbox)
        #hbox = wx.BoxSizer(wx.HORIZONTAL)
        #vbox1.Add(hbox, 0, wx.EXPAND)
        btn = wx.BitmapButton(self, bitmap=wx.Bitmap(resource_path("data/image/prev.png"), wx.BITMAP_TYPE_PNG))
        self.Bind(wx.EVT_BUTTON, parent.GoPrev, btn)
        hbox.Add(btn, 0, wx.LEFT | wx.BOTTOM | wx.TOP, 3)
        self.btnPlay = wx.BitmapButton(self, bitmap=wx.Bitmap(resource_path("data/image/pause.png"), wx.BITMAP_TYPE_PNG))
        self.Bind(wx.EVT_BUTTON, parent.play, self.btnPlay)
        hbox.Add(self.btnPlay, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.TOP, 3)
        btn = wx.BitmapButton(self, bitmap=wx.Bitmap(resource_path("data/image/next.png"), wx.BITMAP_TYPE_PNG))
        self.Bind(wx.EVT_BUTTON, parent.GoNext, btn)
        hbox.Add(btn, 0, wx.LEFT | wx.BOTTOM, 3)
        btn = wx.BitmapButton(self, bitmap=wx.Bitmap(resource_path("data/image/stop.png"), wx.BITMAP_TYPE_PNG))
        self.Bind(wx.EVT_BUTTON, parent.Stop, btn)
        hbox.Add(btn, 0, wx.LEFT | wx.BOTTOM | wx.TOP, 3)
        self.ellapsed = wx.StaticText(self, label="--:--")
        self.ellapsed.SetFont(self.ellapsed.GetFont().MakeBold())
        self.ellapsed.SetForegroundColour("White")
        hbox.Add(self.ellapsed, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 3)
        self.time = wx.Slider(self)
        self.Bind(wx.EVT_SCROLL, parent.Seek, self.time)
        self.time.SetValue(0)
        hbox.Add(self.time, 1, wx.EXPAND | wx.LEFT, 3)
        self.remain = wx.StaticText(self, label="--:--")
        self.remain.SetFont(self.remain.GetFont().MakeBold())
        self.remain.SetForegroundColour("White")
        hbox.Add(self.remain, 0, wx.RIGHT, 3)
        #hbox = wx.BoxSizer(wx.HORIZONTAL)
        #vbox1.Add(hbox, 0, wx.EXPAND)
        #line = wx.Panel(self)
        #line.SetBackgroundColour("Red")
        #hbox.Add(line, 1, wx.EXPAND)
        vol = wx.Slider(self)
        vol.SetMin(0)
        vol.SetMax(100)
        vol.SetValue(50)
        self.Bind(wx.EVT_SCROLL, parent.Volume, vol)
        hbox.Add(vol, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 3)
        btn = wx.BitmapButton(self, bitmap=wx.Bitmap(resource_path("data/image/shuffle.png"), wx.BITMAP_TYPE_PNG))
        self.Bind(wx.EVT_BUTTON, parent.Shuffle, btn)
        hbox.Add(btn, 0, wx.LEFT | wx.BOTTOM, 3)
        btn = wx.BitmapButton(self, bitmap=wx.Bitmap(resource_path("data/image/repeat.png"), wx.BITMAP_TYPE_PNG))
        self.Bind(wx.EVT_BUTTON, parent.Repeat, btn)
        hbox.Add(btn, 0, wx.LEFT | wx.BOTTOM, 3)
        btn = wx.BitmapButton(self, bitmap=wx.Bitmap(resource_path("data/image/vol.png"), wx.BITMAP_TYPE_PNG))
        self.Bind(wx.EVT_BUTTON, parent.Mute, btn)
        hbox.Add(btn, 0, wx.LEFT | wx.BOTTOM, 3)

class PlayList(wx.Panel):

    def __init__(self, parent, image="data/image/playlist-icon.png", text1="Queue", text2="Songs and Videos you play will be here"):
        super(PlayList, self).__init__(parent)
        self.parent = parent
        self.name = self.__class__.__name__.lower()
        self.mediaList = []
        self._mediaList = []
        self.index = None

        vbox = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(vbox)
        panel = wx.Panel(self)
        #panel.SetSize(-1, 300)
        panel.SetBackgroundColour("Grey")
        vbox.Add(panel, 0, wx.EXPAND | wx.ALL, 3)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        panel.SetSizer(hbox)
        image = wx.StaticBitmap(panel, bitmap=wx.Bitmap(resource_path(image), wx.BITMAP_TYPE_PNG))
        hbox.Add(image)
        hbox.Add(wx.Panel(panel), 1)
        self.text1 = wx.StaticText(panel, style=wx.CENTER)#, label=text1 + " | ")
        #self.text1.SetFont(self.text1.GetFont().MakeBold())
        #self.text1.SetForegroundColour("White")
        #hbox.Add(self.text1)
        self.text2 = wx.StaticText(panel, label=text2)
        self.text2.SetForegroundColour("White")
        #self.text2.SetBackgroundColour("Red")
        hbox.Add(self.text2, 0, wx.CENTER)
        hbox.Add(wx.Panel(panel), 1)

        self.listBox = ListBox(self)
        vbox.Add(self.listBox, 1, wx.EXPAND | wx.ALL, 3)

        def NowPlaying(event):
            if self.GetParent().mediaControl is not None:
                if self.GetParent().mediaControl.name.startswith("audio"):
                    self.GetParent().SetCurrentForm("audioControl")
                else:
                    self.GetParent().SetCurrentForm("videoControl")

        def New(event):
            name = wx.GetTextFromUser("Enter playlist name:", "Create New Playlist", "Playlist1")
            if len(name) < 1 or name.isspace():
                wx.MessageBox("Please enter a name!", "Warn", wx.ICON_EXCLAMATION)
                return
            if name in self.mediaList:
                wx.MessageBox("Playlist already exists!", "Warn", wx.ICON_EXCLAMATION)
                return
            if CreatePlaylist(name):
                self.LoadMedia()
                self.parent.SetCurrentForm("favorites")
                wx.MessageBox(f"Created playlist '{name}'!", "Info")

        def Remove(event):
            if self.listBox.selected:
                dlg = wx.MessageDialog(None, f"Remove playlist '{self.listBox.selected}'?", "Remove Playlist", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
                if dlg.ShowModal() == wx.ID_YES and RemovePlaylist(self.listBox.selected):
                        self.LoadMedia()
                        self.parent.SetCurrentForm("favorites")
                        wx.MessageBox(f"Removed playlist '{self.listBox.selected}'!", "Info")

        def Rename(event):
            if self.listBox.selected:
                name = wx.GetTextFromUser("Enter playlist name:", "Rename PlayList", self.listBox.selected)
                if len(name) < 1 or name.isspace():
                    wx.MessageBox("Please enter a name!", "Warn", wx.ICON_EXCLAMATION)
                    return
                if name in self.mediaList:
                    wx.MessageBox("Playlist already exists!", "Warn", wx.ICON_EXCLAMATION)
                    return
                self.mediaList.append(name)
                self.media[name] = []
                self.listBox.Config(ignoreList=True)
                #if self.RenamePlaylist(name)
                    #self.LoadMedia()
                    #wx.MessageBox(f"Renamed playlist to '{name}'!", "Info")

        def Add(event):
            defaultDir = environ["USERPROFILE"] if "win" in platform else expanduser("~")
            wildcard = self.parent.GetSupportedMediaFormats()
            dlg = wx.FileDialog(self, message="Open Media File", defaultDir=defaultDir, wildcard=wildcard)
            if dlg.ShowModal() == wx.ID_OK and dlg.GetPath():
                if dlg.GetPath() in self.mediaList:
                    wx.MessageBox("Media already in playlist!", "Warn", wx.ICON_EXCLAMATION)
                else:
                    name = self.parent.forms.get('favorites').listBox.selected
                    self.mediaList.append(dlg.GetPath())
                    if AddToPlaylist(name, self.mediaList):
                        self.parent.forms.get("favorites").LoadMedia()
                        self.parent.forms.get("favorites").listBox.Go()
                        wx.MessageBox(f"Added media to playlist '{name}'", "Info")

        def Delete(event):
            if self.listBox.selected:
                dlg = wx.MessageDialog(None, f"Delete media from playlist?", "Delete Media", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
                if dlg.ShowModal() == wx.ID_YES:
                    self.mediaList.remove(self.listBox.selected)
                    if AddToPlaylist(self.parent.forms.get('favorites').listBox.selected, self.mediaList):
                        self.parent.forms.get("favorites").LoadMedia()
                        self.parent.forms.get("favorites").listBox.Go()
                        wx.MessageBox(f"Deleted media from playlist!", "Info")

        panel = wx.Panel(self)
        #panel.SetBackgroundColour("Green")
        vbox.Add(panel, 0, wx.EXPAND)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        panel.SetSizer(hbox)

        btn = wx.Button(panel, label="Play")
        self.Bind(wx.EVT_BUTTON, lambda event: self.listBox.Go(), btn)
        hbox.Add(btn)
        btn = wx.Button(panel, label="Now Playing")
        self.Bind(wx.EVT_BUTTON, NowPlaying, btn)
        hbox.Add(btn)

        if self.name.startswith("favorites"):
            hbox.Add(wx.Panel(panel), 1, wx.EXPAND)
            btn = wx.Button(panel, label="New")
            self.Bind(wx.EVT_BUTTON, New, btn)
            hbox.Add(btn)
            btn = wx.Button(panel, label="Remove")
            self.Bind(wx.EVT_BUTTON, Remove, btn)
            hbox.Add(btn)

        if self.name.startswith("mylist"):
            hbox.Add(wx.Panel(panel), 1, wx.EXPAND)
            btn = wx.Button(panel, label="Add")
            self.Bind(wx.EVT_BUTTON, Add, btn)
            hbox.Add(btn)
            btn = wx.Button(panel, label="Delete")
            self.Bind(wx.EVT_BUTTON, Delete, btn)
            hbox.Add(btn)

    def DropFile(self, media, play=True):
        if media not in self.mediaList:
            self.mediaList.append(media)
        self.listBox.Config()
        if play:
            self.GetParent().DropFile(media)
            for index, file in enumerate(self.mediaList):
                if file == media:
                    self.index = index
            self.parent.playlist = self

    def GetPrevMedia(self):
        if self.index is not None: 
            if self.parent.shuffleMode:
                while True:
                    x = choice(self.mediaList)
                    if len(self._mediaList) == len(self.mediaList):
                        self._mediaList.clear()
                    if x not in self._mediaList:
                        self._mediaList.append(x)
                        return x
            index = self.index - 1
            self.index = index if index >=0 else len(self.mediaList)-1
            return self.mediaList[self.index]
        return None

    def GetNextMedia(self):
        if self.index is not None:
            if self.parent.shuffleMode:
                while True:
                    x = choice(self.mediaList)
                    if len(self._mediaList) == len(self.mediaList):
                        self._mediaList.clear()
                    if x not in self._mediaList:
                        self._mediaList.append(x)
                        return x

            index = self.index + 1
            self.index = index if index < len(self.mediaList) else 0
            return self.mediaList[self.index]
        return None

class Songs(PlayList):

    def __init__(self, parent):
        super(Songs, self).__init__(parent, "data/image/songs-icon.png", "Songs", "Songs on your PC")

class Videos(PlayList):

    def __init__(self, parent):
        super(Videos, self).__init__(parent, "data/image/videos-icon.png", "Videos", "Videos on your PC")

class Artists(PlayList):

    def __init__(self, parent):
        super(Artists, self).__init__(parent, "data/image/artist-icon.png", "Artists", "Artists on your PC")
        self.media = {}

class Albums(PlayList):

    def __init__(self, parent):
        super(Albums, self).__init__(parent, "data/image/album-icon.png", "Albums", "Albums on your PC")
        self.media = {}

class MyList(PlayList):

    def __init__(self, parent):
        super(MyList, self).__init__(parent, "data/image/playlist-icon.png", "MyList", "List on your PC")

class Favorites(PlayList):

    def __init__(self, parent):
        super(Favorites, self).__init__(parent, "data/image/playlist-icon.png", "Favorites", "Favorite playlists")
        self.media = {}
        Thread(target=self.LoadMedia, args=[None], daemon=True).start()

    def LoadMedia(self, args=None, show=True):
        self.playlists = GetPlaylists()
        self.mediaList = []
        self.media = {}
        try:
            for name, media in self.playlists.items():
                self.media[name] = [x for x in media.split("?") if len(x) > 0]
                self.mediaList.append(name)
        except:
            pass
        self.listBox.Config(ignoreList=True)

class MediaControl(wx.Panel):

    def __init__(self, parent):
        super(MediaControl, self).__init__(parent)
        self.parent = parent
        self.name = self.__class__.__name__.lower()
        self.parent.Bind(wx.EVT_RIGHT_DOWN, self.Options)

    def Options(self, event):
        menu = wx.Menu()
        switch = menu.Append(-1, "Switch Fullscreen")
        self.Bind(wx.EVT_MENU, self.parent.ToggleFullScreen, switch)
        self.PopupMenu(menu, event.GetPosition())

    def play(self, event):
        if self.mediaPlayer.player.source:
            if self.mediaPlayer.player.playing:
                self.mediaPlayer.player.pause()
                self.controls.btnPlay.SetBitmap(wx.Bitmap(resource_path("data/image/play.png"), wx.BITMAP_TYPE_PNG))
                self.mediaPlayer.playbackPaused = True
            else:
                self.mediaPlayer.player.play()
                self.controls.btnPlay.SetBitmap(wx.Bitmap(resource_path("data/image/pause.png"), wx.BITMAP_TYPE_PNG))
                self.mediaPlayer.playbackPaused = False

    def GoPrev(self, event):
        if self.parent.playlist is not None:
            media = self.parent.playlist.GetPrevMedia()
            if media is not None:
                self.parent.DropFile(media)

    def GoNext(self, event):
        if self.parent.playlist is not None:
            media = self.parent.playlist.GetNextMedia()
            if media is not None:
                self.parent.DropFile(media)

    def Stop(self, event):
        self.parent.mediaControl.mediaPlayer.stop()
        self.parent.SetTitle("Aeon Media Player")
        self.parent.mediaControl = None
        self.parent.SetCurrentForm("playlist")

    def Shuffle(self, event):
        self.parent.shuffleMode = not self.parent.shuffleMode
        wx.MessageBox("Shuffle is On" if self.parent.shuffleMode else "Shuffle is Off", "Shuffle")

    def Repeat(self, event):
        index = self.parent.loopIndex + 1
        self.parent.loopIndex = index if index < 3 else 0
        if self.parent.loopIndex == 0:
            msg = "Loop All"
        elif self.parent.loopIndex == 1:
            msg = "Loop Single"
        else:
            msg = "Loop Off"
        wx.MessageBox(msg, "Loop")

    def Seek(self, event):
        mediaPlayer = self.parent.mediaControl.mediaPlayer
        mediaPlayer.player.seek((event.GetPosition() / mediaPlayer.duration) * mediaPlayer.duration)

    def Volume(self, event):
        self.parent.volume = event.GetPosition() / 100
        self.parent.mediaControl.mediaPlayer.player.volume = self.parent.volume
        if self.parent.volume > 0:
            self.parent.mute = False

    def Mute(self, event):
        if not self.parent.mute:
            self.parent.lastVolume = self.parent.mediaControl.mediaPlayer.player.volume
            self.parent.volume = 0
            self.parent.mediaControl.mediaPlayer.player.volume = self.parent.volume
            self.parent.mute = True
            wx.MessageBox("Muted", "Volume")
        else:
            self.parent.volume = self.parent.lastVolume
            self.parent.mediaControl.mediaPlayer.player.volume = self.parent.volume
            self.parent.mute = False
            wx.MessageBox("Unmuted", "Volume")

class AudioControl(MediaControl):

    def __init__(self, parent):
        super(AudioControl, self).__init__(parent)
        self.SetBackgroundColour("Green")
        vbox = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(vbox)
        self.info = wx.StaticText(self)
        self.info.SetFont(self.info.GetFont().MakeBold())
        self.info.SetForegroundColour("White")
        vbox.Add(self.info, 0, wx.EXPAND | wx.LEFT | wx.TOP, 3)
        self.info2 = wx.StaticText(self,)
        self.info2.SetFont(self.info.GetFont().MakeBold())
        self.info2.SetForegroundColour("Silver")
        vbox.Add(self.info2, 0, wx.EXPAND | wx.LEFT | wx.BOTTOM, 3)
        self.art = wx.StaticBitmap(self, bitmap=wx.Bitmap(resource_path("data/image/album-art.png"), wx.BITMAP_TYPE_PNG))
        vbox.Add(self.art, 1, wx.EXPAND)
        self.controls = Controls(self)
        vbox.Add(self.controls, 0, wx.EXPAND)
        self.mediaPlayer = Sound(self)
        
    def Play(self, audio):
        if self.mediaPlayer.play(audio):
            self.parent.SetTitle("{0} | Aeon Media Player".format(split(audio)[1]))
            try:
                image = load(getAlbumArt(audio))
                image = scale(image, (600, 600))
                image_data = tostring(image, "RGB")
                bitmap = wx.Bitmap.FromBuffer(image.get_width(), image.get_height(), image_data)
                self.art.SetBitmap(bitmap)
            except Exception as err:
                #wx.MessageBox(err, "Error")
                self.art.SetBitmap(Bitmap(resource_path("data/image/album-art.png"), wx.BITMAP_TYPE_PNG))
            artist, album, title, length = getTrackInfo(audio)
            self.info.SetLabel(title)
            self.info2.SetLabel(artist)
            self.controls.btnPlay.SetBitmap(wx.Bitmap(resource_path("data/image/pause.png"), wx.BITMAP_TYPE_PNG))
            self.parent.mediaControl = self
            return True
        return

class VideoControl(MediaControl):

    def __init__(self, parent):
        super(VideoControl, self).__init__(parent)
        self.SetBackgroundColour("Black")
        vbox = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(vbox)
        self.frame = wx.StaticBitmap(self, bitmap=wx.Bitmap(resource_path("data/image/no-frame.png"), wx.BITMAP_TYPE_PNG))
        self.mediaPlayer = Movie(self)
        vbox.Add(self.frame, 1, wx.EXPAND, 5)
        self.controls = Controls(self)
        vbox.Add(self.controls, 0, wx.EXPAND)

    def Play(self, video):
        if self.mediaPlayer.play(video):
            self.parent.SetTitle("{0} | Aeon Media Player".format(split(video)[1]))
            self.controls.btnPlay.SetBitmap(wx.Bitmap(resource_path("data/image/pause.png"), wx.BITMAP_TYPE_PNG))
            self.parent.mediaControl = self
            return True
        return

class Settings(ScrolledPanel):

    def __init__(self, parent):
        super(Settings, self).__init__(parent)
        self.settings = {"scan-for-media-in": "pc", "special-folders": [], "repeat-mode": "all", "suffle-mode": "off"}
        vbox = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(vbox)
        panel = wx.Panel(self)
        panel.SetBackgroundColour("Grey")
        vbox.Add(panel, 0, wx.EXPAND | wx.ALL, 3)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        panel.SetSizer(hbox)
        image = wx.StaticBitmap(panel, bitmap=wx.Bitmap(resource_path("data/image/settings-icon.png"), wx.BITMAP_TYPE_PNG))
        hbox.Add(image)
        text = wx.StaticText(panel, label="Settings | ")
        text.SetForegroundColour("White")
        text.SetFont(text.GetFont().MakeBold())
        hbox.Add(text)
        text = wx.StaticText(panel, label="Customize your settings here")
        text.SetForegroundColour("White")
        #text.SetBackgroundColour("Red")
        hbox.Add(text, 1)
        panel = wx.Panel(self)
        vbox.Add(panel, 0, wx.EXPAND)
        box = wx.StaticBox(panel, -1, label="Media Discovery")
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        panel.SetSizer(sizer)
        p = wx.Panel(panel)
        sizer.Add(p)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        p.SetSizer(hbox)
        #sizer.Add(hbox, 0, wx.EXPAND)
        text = wx.StaticText(p, label="Scan for media files in: ")
        hbox.Add(text, 0, wx.EXPAND)
        radio = wx.RadioButton(p, label="This PC")
        hbox.Add(radio)
        radio = wx.RadioButton(p, label="Special Folders")
        hbox.Add(radio)
        listBox =wx.ListBox(panel)
        sizer.Add(listBox, 1, wx.EXPAND)
        panel = wx.Panel(panel)
        sizer.Add(panel, 0, wx.EXPAND)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        panel.SetSizer(hbox)
        btn = wx.Button(panel, label="Add")
        hbox.Add(btn)
        btn = wx.Button(panel, label="Delete")
        hbox.Add(btn)
        vbox.Add(wx.Panel(self), 1, wx.EXPAND)
        btn = wx.Button(self, label="Save Changes")
        vbox.Add(btn)

def main():
    App().MainLoop()

if __name__ == "__main__":
    main()
