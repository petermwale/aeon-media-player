import sys
from os import environ
from os.path import join
from sys import exit as Exit
from pygame import init, quit as Quit
from pygame.display import set_mode, set_caption, set_icon, update, Info
from pygame.image import load
from pygame.event import get
from pygame.time import Clock
from pyglet import clock
from pygame.locals import *
from const import *
from timer import Timer


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except:
        base_path  = abspath(".")

    return join(base_path, relative_path)


environ["SDL_VIDEO_CENTERED"] = "1" # Put Window at the center
init() # Initialize Pygame system modules

class App:
    
    ROOT = TOP_LEVEL = True

    def onCreate(self, info, title="App", size=(640, 480), icon=None):
        #info = pygame.display.Info()
        self.fullscreen_size = info.current_w, info.current_h
        self.screen = set_mode(size, RESIZABLE)
        self.size = size
        self.setTitle(title)

        if icon is not None:
            self.setIcon(icon)
            
        self.x = self.y = 0            
        self.children = []
        
        self.grabbed_child = None
        self.is_fullscreen = False
        self.mouse_click_count = 0
        
        self.name = self.__class__.__name__.lower()         
        self.clock = Clock()
        self.timer = Timer()

    def setTitle(self, title):
        set_caption(title)

    def setIcon(self, icon):
        try:
            set_icon(load(icon).convert_alpha())
        except:
            pass
        
    def switchFullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        if self.is_fullscreen:
            self.last_size = self.size
            self.resizeWin(self.fullscreen_size, True)
        else:
            self.resizeWin(self.last_size)

    def resizeWin(self, size, fullscreen=False):
        self.screen = set_mode(size, FULLSCREEN  if fullscreen else RESIZABLE)
        self.size = size
        
    def addWidget(self, child):
        child.child_pos = len(self.children)
        self.children.append(child)

    def get_child(self, child_pos):
        if child_pos < 0:
            return None
        try:
            return self.children[child_pos]
        except IndexError:
            return None
        
    def removeWidget(self, child):
        self.children.remove(child)
        
    def drawWidgets(self):
        for child in self.children:
            child.draw()

    def refresh(self):
        for child in self.children:
            child.refresh()
            
    def keyDown(self, key, char):
        if self.grabbed_child is not None:
            self.grabbed_child.keyDown(key, char)
            return
        for child in self.children:
            child.keyDown(key, char)
            
    def keyUp(self, key):
        if self.grabbed_child is not None:
            self.grabbed_child.keyUp(key)
            return
        for child in self.children:
            child.keyUp(key)
            
    def dropFile(self, file):
        if self.grabbed_child is not None:
            self.grabbed_child.dropFile(file)
            return
        for child in self.children:
            child.dropFile(file)        
            
    def mouseDown(self, pos, btn, double_click):
        if self.grabbed_child is not None:
            self.grabbed_child.mouseDown(pos, btn, double_click)
            return
        for child in self.children:
            child.mouseDown(pos, btn, double_click)
            
    def mouseUp(self, pos, btn):
        if self.grabbed_child is not None:
            self.grabbed_child.mouseUp(pos, btn)
            return
        for child in self.children:
            child.mouseUp(pos, btn)
            
    def mouseMoved(self, pos):
        if self.grabbed_child is not None:
            self.grabbed_child.mouseMoved(pos)
            return
        for child in self.children:
            child.mouseMoved(pos)
            
    def mouseDragged(self, pos):
        if self.grabbed_child is not None:
            self.grabbed_child.mouseDragged(pos)
            return
        for child in self.children:
            child.mouseDragged(pos)

    def mouseWheel(self, y):
        if self.grabbed_child is not None:
            self.grabbed_child.mouseWheel(y)
            return
        for child in self.children:
            child.mouseWheel(y)

    def quit(self):
        Quit()
        Exit()

    def run(self, info=None):
        if info is None:
            info = Info()
        self.onCreate(info)
        while True:
            for event in get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    self.quit()
                elif event.type == VIDEORESIZE:
                    self.resizeWin(event.size)
                elif event.type == MOUSEMOTION:
                    self.mouseMoved(event.pos)
                    if event.buttons[0]:
                        self.mouseDragged(event.pos)
                elif event.type == MOUSEBUTTONDOWN:
                    self.mouseDown(event.pos, event.button, True if self.mouse_click_count < 20 else False)
                    self.mouse_click_count = 0
                elif event.type == MOUSEBUTTONUP:
                    self.mouseUp(event.pos, event.button)
                elif event.type == MOUSEWHEEL:
                    self.mouseWheel(event.y)
                elif event.type == KEYDOWN:
                    if event.key == K_f:
                        self.switchFullscreen()
                    self.keyDown(event.key, event.unicode)
                elif event.type == KEYUP:
                    self.keyUp(event.key)
                elif event.type == DROPFILE:
                    self.dropFile(event.file)
                    
            self.clock.tick(120)
            clock.tick(1)
            self.timer.tick()
            self.mouse_click_count += 1
            self.screen.fill(WHITE)
            self.drawWidgets()
            update()