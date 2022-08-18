#! /usr/bin/env python3

import sys
from os import environ
from os.path import abspath, join
from sys import exit as Exit
from pygame import init, quit as Quit
from pygame.display import set_mode, update, Info
from pygame.image import load
from pygame.font import Font
from pygame.event import get
from pygame.time import get_ticks, Clock
from pygame.locals import KEYDOWN, K_ESCAPE, NOFRAME
from const import SILVER
from aeon import Aeon

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except:
        base_path  = abspath(".")

    return join(base_path, relative_path)


environ["SDL_VIDEO_CENTERED"] = "1" # Put Pygame Window at the center

"""This module is a 'splash screen'"""

def setup():
    global screen, clock, image, text1, text2, info
    info = Info()
    screen = set_mode((650, 480), NOFRAME)
    clock = Clock()
    image = load(resource_path("data/image/icon.png"))
    font1 = Font(resource_path("data/fonts/calibri.ttf"), 25)
    font2 = Font(resource_path("data/fonts/calibri.ttf"), 18)
    text1 = font1.render("Aeon Media Player", True, SILVER)
    text2 = font2.render("Courtesy of Sub-Zero Inc. © 2021 By Peter Mwale.", True, SILVER)
    
def run():
    while True:
        for event in get():
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                Quit()
                Exit()
        
        clock.tick(120)  
        
        if get_ticks() % 750 == 0:
           break
                      
        screen.fill((50,65,50))
        w1, h1 = screen.get_size()
        w2, h2 = image.get_size()
        screen.blit(image, (w1 // 2 - w2 // 2, h1 // 2 - h2 // 2))
        #screen.blit(text1, (5, 5))
        screen.blit(text2, (5, h1 - text1.get_height() - 2))
        update()
        
    Aeon().run(info)
        
if __name__ == "__main__":
    setup()
    run()
