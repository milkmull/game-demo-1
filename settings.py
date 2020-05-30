import pygame as pg
#main colors
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
orange = (255, 165, 0)
clear = (0, 0, 0, 0)
gold = (255,223,0)

SPRITESHEET = 'jump1.png'


#game options
width = 1024
height = 768

fps = 60
screen_size = (width, height)
title = 'game'
font_name = 'arial'

tilesize = 64

#save file stuff
all_collected_forms = []
max_health = 3
max_forms = 2


#player properties

grav = 65
fric = -1.2

def create_text(message, size=115, font='freesansbold.ttf', color=white):
    text_font = pg.font.Font(font, size)
    text = text_font.render(message, size, color)
    return text
    
def blank():
    pass