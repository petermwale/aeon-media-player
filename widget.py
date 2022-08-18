import sys
from os.path import isfile, split as Split, abspath, join
from textwrap import wrap
from pygame.mouse import get_pos
from pygame import Surface, SRCALPHA
from pygame.image import load
from pygame.font import Font
from pygame.draw import circle, rect
from pygame.transform import scale, rotate
from pygame.locals import *
from const import *
from tags import getTrackInfo

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except:
        base_path  = abspath(".")

    return join(base_path, relative_path)


class Widget:

    def __init__(self, parent, fg1=WHITE, fg2=BLACK, bg1=SILVER, bg2=GREEN, size_hint=(None, None), border=0):
        self.parent = parent
        self.screen = parent.screen
        
        self.bg1 = bg1
        self.bg2 = bg2
        self.bg = self.bg1
        
        self.fg1 = fg1
        self.fg2 = fg2
        self.fg = fg1
        
        self.size_hint = size_hint
        self.size = (0, 0)
        self.border = border
        self.pos = self.x, self.y = (0, 0)
        
        self.name = self.__class__.__name__.lower()   
        self.toplevel = True     
        self.children = []
        
        self.ipadx = self.ipady = self.padx = self.pady = 0
        
    def config(self, properties):
        for property, value in properties.items():
            setattr(self, property, value)
        
    def addWidget(self, child):
        child.child_pos = len(self.children)
        self.children.append(child)
        
    def removeWidget(self, child):
        self.children.remove(child)
        
    def getRoot(self):
        parent = self.parent
        while True:
            if hasattr(parent, "ROOT"):
                return parent
            parent = parent.parent
        
    def pack(self, side=CENTER, expand_x=NO, expand_y=NO):
        self.config({"side": side, "expand_x": expand_x, "expand_y": expand_y})
        if self not in self.parent.children:
            self.parent.addWidget(self)
            
    def grab(self):
        self.getRoot().grabbed_child = self
        
    def ungrab(self):
        self.getRoot().grabbed_child = None
        
    def unpack(self):
        self.parent.removeWidget(self)
        
    def destroy(self):
        self.unpack()     
        self.ungrab()
        
    def keyDown(self, key, char):
        for child in self.children:
            child.keyDown(key, char)
            
    def keyUp(self, key):
        for child in self.children:
            child.keyUp(key)
            
    def dropFile(self, file):
        for child in self.children:
            child.dropFile(file)
            
    def mouseDown(self, pos, btn, double_click):
        for child in self.children:
            child.mouseDown(pos, btn, double_click)
            
    def mouseUp(self, pos, btn):
        for child in self.children:
            child.mouseUp(pos, btn)
            
    def mouseMoved(self, pos):
        for child in self.children:
            child.mouseMoved(pos)
            
    def mouseDragged(self, pos):
        for child in self.children:
            child.mouseDragged(pos)

    def mouseWheel(self, y):
        for child in self.children:
            child.mouseWheel(y)
     
    def isHovering(self):
        x, y = get_pos()
        return x > self.x and x < self.x + self.size[0] and y > self.y and y < self.y + self.size[1]
    
    def refresh(self):
        pass     
    
    def get_child(self, child_pos):
        if child_pos < 0:
            return None
        try:
            return self.children[child_pos]
        except IndexError:
            return None
        
    def draw(self):
        for child in self.children:
            child.draw()
            
    def initDraw(self):        
        # calculate Widget size
        if self.expand_x == YES:
            self._w = self.parent.size[0]
        else:
            self._w = self.size_hint[0]
        if self.expand_y == YES:
            self._h = self.parent.size[1]
        else:
            self._h = self.size_hint[1]
            
        self.size = (self._w-self.padx, self._h-self.pady)
        
        if hasattr(self, "image"):
            self.size = self.image.get_size()
        
        # calculate Widget position
        if self.side == CENTER:
            self.x = self.parent.x + self.parent.size[0] // 2 - self.size[0] // 2 + self.ipadx
            self.y = self.parent.y + self.parent.size[1] // 2 - self.size[1] // 2 + self.ipady
        elif self.side == LEFT:
            obj = self.parent.get_child(self.child_pos-1)
            if obj is not None and obj.side == LEFT: self.x = obj.x + obj.size[0] + self.ipadx + 1
            else:  self.x = self.parent.x + self.ipadx + 2
            self.y = self.parent.y + self.parent.size[1] // 2 - self.size[1] // 2 + self.ipady - 1
        elif self.side == RIGHT:
            obj = self.parent.get_child(self.child_pos-1)
            if obj is not None and obj.side == RIGHT: self.x = obj.x - self.size[0] - self.ipadx - 1 #obj.x + obj.size[0] + 1
            else: self.x = self.parent.x + self.parent.size[0] - self.size[0] - self.ipadx - 1
            self.y = self.parent.y + self.parent.size[1] // 2 - self.size[1] // 2 + self.ipady - 1
        elif self.side == TOP:
            obj = self.parent.get_child(self.child_pos-1)
            if obj is not None and obj.side == TOP: ipady = obj.size[1] + 1
            else: ipady = 0
            self.x = self.parent.x + self.parent.size[0] // 2 - self.size[0] // 2
            self.y = self.parent.y + 1 + ipady + self.ipady
        elif self.side == BOTTOM:
            obj = self.parent.get_child(self.child_pos-1)
            if obj is not None and obj.side == BOTTOM: ipady = obj.size[1] #+ 1
            else: ipady = 1
            self.x = self.parent.x + self.parent.size[0] // 2 - self.size[0] // 2
            self.y = self.parent.y + self.parent.size[1] - self.size[1] - ipady - self.ipady
        
        self.pos = (self.x, self.y)
        
class Panel(Widget):
    
    def __init__(self, *args, **kwargs):
        super(Panel, self).__init__(*args, **kwargs)
        self.transparent = False
        self.alpha = 100

    def draw(self):
        self.initDraw()
        if self.transparent:
            surf = Surface(self.size, SRCALPHA)
            surf.set_alpha(self.alpha)
            self.screen.blit(surf, self.pos)
        else:
            rect(self.screen, self.bg, (*self.pos, *self.size), self.border)
            super().draw()
        
class Image(Widget):
    
    def __init__(self, parent, source, auto_resize=False, size_hint=None):
        super(Image, self).__init__(parent)
        try:
            self._image = load(resource_path(source)).convert_alpha()
        except:
            self._image = load(resource_path("data/image/art.png")).convert_alpha()
            
        self.image = self._image.copy()
        self.auto_resize = auto_resize

        if size_hint is not None:
            self.resize(size_hint)
        
        self.side = CENTER
        self.expand_x = self.expand_y = YES
        
    def getColor(self):
        w, h = self.image.get_size()
        for x in range(w):
            for y in range(h):
                if x == w // 2 and y == h // 2:
                    return self.image.get_at((x, y))
        
    def resize(self, size_hint=(610, 610)):
        self.image = scale(self._image, size_hint)
        
    def rotate(self):
        pass
        
    def draw(self):
        self.initDraw()
        if self.auto_resize:
            self.resize(self.parent.size)
        w, h = self.image.get_size()
        self.screen.blit(self.image, (self.x, self.y))

class Vinyl(Widget):
    
    def __init__(self, parent, source):
        super(Vinyl, self).__init__(parent)
        self.image = load(resource_path(source)).convert_alpha()
        self.resize()
        self.disc = self.vinyl()
        self.disc1 = self.vinyl()
        self.angle = 0
        self.side = CENTER
        self.expand_x = self.expand_y = YES

    def resize(self, size=(395, 395)):
        self.resized = scale(self.image, size)
        #self.disk = self.vinyl()
        self.disk1 = self.vinyl()

    def getColor(self):
        w, h = self.image.get_size()

        for x in range(w):
            for y in range(h):
                if x == w // 2 and y == h // 2:
                    return self.image.get_at((x, y))

    def vinyl(self):
        width, height = self.getRoot().size

        blank = Surface((width, height))
        blank.fill(self.getColor())
        w1, h1 = blank.get_size()

        w2, h2 = self.resized.get_size()
        blank.blit(self.resized, (w1 // 2 - w2 // 2, h1 // 2 - h2 // 2))

        circle(blank, BLACK, (width // 2, height // 2), 280, 70)
        circle(blank, SILVER, (width // 2, height // 2), 250, 1)
        #pygame.draw.circle(blank, SILVER, (width/2, height/2), 25)
        #pygame.draw.circle(blank, SILVER, (width/2, height/2), 220, 1)
        return blank

    def draw(self):
        w, h = self.disc.get_size()
        #self.initDraw()
        x, y = self.getRoot().size
        x = x/2-w/2
        y = y/2-h/2
        self.screen.blit(self.disc, (x, y))

    def rotate(self):
        x = self.angle + 1
        self.angle = x if x <= 360 else 0
        self.disc = rotate(self.disc1, -self.angle)
        
class Label(Widget):
    
    def __init__(self, parent, text="", height=18, fg1=WHITE, fg2=SILVER, bg1=SILVER, bg2=SILVER, align=CENTER):
        self.font = Font(resource_path("data/fonts/calibri.ttf"), height)
        super(Label, self).__init__(parent, fg1=fg1, fg2=fg2, bg1=bg1, bg2=bg2, size_hint=(self.font.render(" " + text + " ", True, WHITE).get_width(), height))
        
        self.text = text
        self.align = align
        self.wrapLength = 0
        
    def setValue(self, value):
        self.text = value
        
    def draw(self):
        self.initDraw()
        rect(self.screen, self.bg, (*self.pos, *self.size))
        
        def wrapText(text):
            if self.font.render(text, True, self.fg).get_width() > Surface(self.size).get_width(): 
                text = text[:self.wrapLength] + "..."
            return text
        
        text = self.font.render(wrapText(self.text), True, self.fg)
        w, h = text.get_size()
        
        if self.align == CENTER:
            x = self.x + self.size[0] // 2 - w // 2
            y = self.y + self.size[1] // 2 - h // 2
        elif self.align == LEFT:
            x = self.x + 2
            y = self.y + self.size[1] // 2 - h // 2
        elif self.align == RIGHT:
            x = self.x + self.size[0] - w - 2
            y = self.y + self.size[1] // 2 - h // 2
            
        self.screen.blit(text, (x, y))

class Info(Label):
    
    def __init__(self, *args, **kwargs):
        super(Info, self).__init__(*args, **kwargs)
        self.force_color = True
        
    def draw(self):
        self.initDraw()
        
        if not self.force_color:
            if any([x > 100 for x in self.parent.bg[:-3]]):
                self.fg = BLACK
            else:
                self.fg = WHITE
        
        text = self.font.render(self.text, True, self.fg)
        w, h = text.get_size()
        
        if self.align == CENTER:
            x = self.x + self.size[0] // 2 - w // 2
            y = self.y + self.size[1] // 2 - h // 2
        elif self.align == LEFT:
            x = self.x + 2
            y = self.y + self.size[1] // 2 - h // 2
        elif self.align == RIGHT:
            x = self.x + self.size[0] - w - 2
            y = self.y + self.size[1] // 2 - h // 2
            
        self.screen.blit(text, (x, y))
        
class tListItem(Widget):
    
    def __init__(self, parent, text, icon, split=False, artist="artist", album="album", title="title", label=None, fg1=BLACK, fg2=LIGHT_GREEN, bg1=GREY, bg2=GREEN):
        super(tListItem, self).__init__(parent, fg1=fg1, fg2=fg2, bg1=bg1, bg2=bg2)
        self.index = len(self.parent.items)
        self.track = text
        self.text = Split(text)[1] if label is None else label
        self.icon = scale(load(resource_path(icon)).convert_alpha(), (25, 25))
        self.split = split
        
        self.artist = artist
        self.album = album
        self.title = title if title != "title" else Split(text)[1]

        self.fg = self.fg1
        self.bg = self.bg1
        self.x = self.y = 0

    def mouseMoved(self, pos):
        x, y = pos
        if x > self.x and x < self.x + self.parent.size[0] and y > self.y and y < self.y + 35:
            self.grab()
        else:
            self.ungrab()

        if self.parent.selected is not None:
            self.parent.selected.grab()

    def mouseDown(self, pos, btn, double_click):
        x, y = pos
        if btn == LEFT_CLICK and x > self.x and x < self.x + self.parent.size[0] and y > self.y and y < self.y + 35:
            self.parent.ungrabAll()
            self.grab()
            try:
                self.parent.index = self.offset
            except:
                pass
            if double_click:
                self.parent.fun1(self.track)

    def grab(self):
        self.fg = self.fg2
        self.bg = self.bg2

    def ungrab(self):
        self.fg = self.fg1
        self.bg = self.bg1

    def draw(self, index):
        self.y =  self.parent.y + index * 35 + 1
        if self.index >= 1:
            self.y += index * 1
        self.x = self.parent.x + 1
        rect(self.screen, self.bg, (self.x, self.y, self.parent.size[0] - 2, 35))
        self.screen.blit(self.icon, (self.x, self.y + 3))
        
        def wrapText(text):
            _text = text
            index = len(text)
            widget_width = Surface((self.parent.size[0]-2, 35)).get_width()-45
            
            def getTextWidth(text):
                return self.parent.font.render(text, True, self.fg).get_width()
            
            if getTextWidth(text) > widget_width :
                while getTextWidth(text) > widget_width:
                    index -= 1
                    text = _text[:index]
                text += "..."
            return text
        
        if self.split:            
            title = self.parent.font.render(wrapText(self.title), True, self.fg)
            label = self.parent.font.render(wrapText(self.artist + " - " + self.album, True, self.fg))
            self.screen.blit(title, (self.x + 30, self.y + 6))
            self.screen.blit(label, (self.x + 30, self.y + 20))
        else:
            text = self.parent.font.render(wrapText(self.text), True, self.fg)
            self.screen.blit(text, (self.x + 30, self.y + 10))
            
class List(Widget):
    def __init__(self, parent, fun1=None, fun2=None, bg1=WHITE, bg2=GREEN, 
                 select_fg1=BLACK, select_fg2=LIGHT_GREEN, select_bg1=GREY, select_bg2=GREEN, size_hint=(None, None)):
        super(List, self).__init__(parent, bg1=bg1, bg2=bg2, size_hint=size_hint)
        self.fun1 = fun1
        self.fun2 = fun2
        self.select_fg1 = select_fg1
        self.select_fg2 = select_fg2
        self.select_bg1 = select_bg1
        self.select_bg2 = select_bg2
        self.font = Font(resource_path("data/fonts/calibri.ttf"), 15)
        self.items = []

        self.start = 0
        self.end = 0

        self.index = 0
        self.selected = None

    def mouseMoved(self, pos):
        for item in self.items:
            item.mouseMoved(pos)

    def mouseDown(self, pos, btn, double_click):
        for item in self.items:
            item.mouseDown(pos, btn, double_click)

    def mouseWheel(self, y):
        if y < 0:
            self.scroll()
        elif y > 0:
            self.scroll(UP)

    def keyDown(self, key, char):
        if key == K_DOWN:
            self.scroll()
        elif key == K_UP:
            self.scroll(UP)
        elif key == K_RETURN:
            if self.fun1 is not None and self.selected is not None:
                self.fun1(self.selected.track)

    def ungrabAll(self):
        for item in self.items:
            item.ungrab()

    def scroll(self, direction=DOWN):
        if not self.items:
            return

        self.ungrabAll()

        if direction == DOWN:
            x = self.index + 1
            self.index = x if x <= len(self.items)-1 else len(self.items)-1
        elif direction == UP:
            x = self.index - 1
            self.index = x if x >= 0 else 0

        try:
            self.selected = self.items[self.index]
            self.selected.grab()
        except:
            pass

        if direction == DOWN and self.selected is not None:
            try:
               can_scroll = self.index >= self.start + self.size[1] // 35 - 1
               more_items = len(self.items) - self.selected.index + 1 > 0
            except:
               return

            if can_scroll and more_items:
                self.start += 1
                
        elif direction == UP and self.selected is not None:
            try:
                can_scroll = self.selected.offset <= 0
                more_items = self.selected.index > 0# len(self.items) - (len(self.items) - self.selected.index+2) > 0 #self.selected.index > 0
            except:
                return

            if can_scroll and more_items:
                self.start -= 1
                
        if self.fun2 is not None:
            self.fun2(self.selected.text)

    def insert(self, text, icon=None, split=False, artist="artist", album="album", title="title", label=None):
        self.items.append(tListItem(self, text, icon, split, artist, album, title, label, fg1=self.select_fg1,
                                    fg2=self.select_fg2, bg1=self.select_bg1, bg2=self.select_bg2))
        self.items.sort(key=lambda item: isfile(item.track))
        
    def clear(self):
        self.items = []
        self.start = 0

    def draw(self):
        self.initDraw()
        rect(self.screen, self.bg, (*self.pos, *self.size))
        for child in self.children:
            child.draw()
        a = self.start
        b = a + self.size[1] // 35 - 1
        for index, item in enumerate(self.items[a:b]):
            item.offset = index
            item.draw(index)
            
class Button(Widget):
    
    def __init__(self, parent, text="", image1=None, image2=None, size_hint=(30, 20), fg1=None, fg2=None, bg1=None, bg2=None, fun=None, resize=False):
        _size_hint = size_hint
        if image1 is not None:
            size_hint = load(resource_path(image1)).convert_alpha().get_size()
        super(Button, self).__init__(parent, size_hint=size_hint, bg1=bg1, bg2=bg2)
        self.text = text
        self.fg1 = fg1 if fg1 is not None else WHITE
        self.fg2 = fg2 if fg2 is not None else GREEN

        self.bg1 = bg1 if bg1 is not None else BLACK
        self.bg2 = bg2 if bg2 is not None else BLACK

        self.font = Font(resource_path("data/fonts/calibri.ttf"), 15)

        self.fg = self.fg1
        self.bg = self.bg1

        self.image1 = load(image1) if image1 is not None else image1
        self.image2 = load(image2) if image2 is not None else self.image1

        if resize:
            self.image1 = scale(self.image1, _size_hint)
            self.image2 = scale(self.image2, _size_hint)

        self._image = self.image1
        #pygame.image.save(pygame.image.load("data/image/pause.png").convert_alpha().subsurface(4, 4, 17, 17), "pause2.png")
        self.fun = fun
        #self.w, self.h = self.font.render(self.text, True, self.fg).get_size()
        
    def mouseMoved(self, pos):
        if self.isHovering():
            self.bg = self.bg2
        else:
            self.bg = self.bg1
            
    def mouseDown(self, pos, btn, double_click):
        if self.isHovering():
            self.fg = self.fg2        
            
    def mouseUp(self, pos, btn):
        if self.isHovering() and self.fun is not None:
            self.fun()
        self.fg = self.fg1

    def draw(self):
        self.initDraw()
        if self.image1 is None:
            rect(self.screen, self.bg, (*self.pos, *self.size))
            text = self.font.render(self.text, True, self.fg)
            w, h = text.get_size()
            self.screen.blit(text, (self.x + self.size[0] / 2 - w / 2, self.y + self.size[1] / 2 - h / 2))
        else:
            w, h = self._image.get_size()
            self.screen.blit(self._image, (self.x + self.size[0] / 2 - w / 2, self.y + self.size[1] / 2 - h / 2))

class Slider(Widget):

    def __init__(self, parent, size_hint=(None, 4), value=0, _from=0, to=100, fg1=GREEN, bg1=WHITE, fun1=None, fun2=None):
        super(Slider, self).__init__(parent, size_hint=size_hint, fg1=fg1, bg1=bg1)
        self.parent = parent

        self._from = _from
        self.to = to
        self.value = value
        self.fun1 = fun1
        self.fun2 = fun2
        self.canShow = False
        
    def mouseDown(self, pos, btn, double_click):
        if btn == LEFT_CLICK and self.isHovering() and not double_click and self.fun1 is not None:
            self.fun1((pos[0] - self.x) / self.size[0])

    def mouseMoved(self, pos):
        if self.isHovering():
            self.canShow = True
            if self.fun2 is not None:
                self.fun2((pos[0] - self.x) / self.size[0])
        else:
            self.canShow = False
    
    def setValue(self, value):
        self.value = value

    def getValue(self):
        return self.value

    def draw(self):
        self.initDraw()
        self.pos = (self.x, self.y - 1)
        
        rect(self.screen, self.bg, (*self.pos, *self.size))
        
        if self.value > 0:
            rect(self.parent.screen, self.fg, (*self.pos, (self.value / self.to) * self.size[0], self.size[1]))
            #if self.canShow:
             #   pygame.draw.circle(self.screen, self.fg, (int(self.x + (self.value / self.to) * self.size[0]), self.y + 1), 9)