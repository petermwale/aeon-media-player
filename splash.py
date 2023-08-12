import wx
from os.path import abspath, join
from main import main as RunApp

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except:
        base_path  = abspath(".")

    return join(base_path, relative_path)

class App(wx.App):

    def OnInit(self):
        wx.Log.SetActiveTarget(wx.LogStderr())
        win = Window()
        win.Show()
        return True

class Window(wx.Frame):

    def __init__(self):
        super(Window, self).__init__(None, size=(700, 500), style=wx.CAPTION ^ wx.MAXIMIZE_BOX | wx.RESIZE_BORDER)
        self.Center()
        Panel(self)

class Panel(wx.Panel):

    def __init__(self, parent):
        super(Panel, self).__init__(parent)
        wx.StaticBitmap(self, bitmap=wx.Bitmap(resource_path("data/image/icon.png"), wx.BITMAP_TYPE_PNG), pos=(5, 100))
        text = wx.StaticText(self, label="Aeon Media Player", pos=(300, 100))
        text.SetFont(text.GetFont().MakeBold())
        text = wx.StaticText(self, label="Copyright (c) 2023 by Peter Mwale", pos=(5, 400))
        text.SetFont(text.GetFont().MakeBold())
        wx.CallLater(3000, self.GetParent().Destroy)

if __name__ == "__main__":
    App().MainLoop()
    RunApp()
