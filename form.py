from widget import Panel, Label, Button
from const import *


class Form(Panel):

    def __init__(self, parent, title="Form", size=(850, 650)):
        super(Form, self).__init__(parent, bg1=BLACK, size_hint=size)

        panel = Panel(self, bg1=BLACK, size_hint=(None, 25))
        panel.pack(side=TOP, expand_x=YES)

        self.title = Label(panel, text=title, fg1=WHITE, bg1=BLACK, align=LEFT)
        self.title.config({"padx": 2})
        self.title.pack(side=LEFT, expand_x=YES)

        btn = Button(panel, text="X", fg1=WHITE, bg1=GREY, bg2=RED, size_hint=(23, 23), fun=self.destroy)
        btn.config({"ipadx": 2, "ipady": 1})
        btn.pack(side=RIGHT)
        
        self.container = Panel(self, bg1=WHITE)
        self.container.config({"ipadx":3, "padx":4, "pady": 30})
        self.container.pack(side=TOP, expand_x=YES, expand_y=YES)
        
    def setTitle(self, title):
        self.title.setValue(title)
        
    def show(self):
        self.pack()
        self.grab()