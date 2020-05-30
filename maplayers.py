import pygame as pg
from settings import *
vec = pg.math.Vector2
from random import choice, randrange



class Layer:
    def __init__(self, layer, map):
        self.layer = layer
        self.map = map
        self.tiles = {}
        self.animated_tiles = []

            
class Animations:
    def __init__(self, frames, x, y, duration):
        self.points = [vec(x, y)]
        self.duration = duration
        self.frames = frames
        self.image = self.frames[0]
        self.current_frame = 0
        self.last_update = 0
            
            
    def update(self):
        now = pg.time.get_ticks()
        if now - self.last_update > self.duration:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]       
        

            
        
        
class DayNightCycle:
    def __init__(self, game):
        self.game = game
        self.last_update = 0
        self.times = ('morning', 'day', 'evening', 'night')
        self.current_time = 1
        self.time = self.times[self.current_time]
        self.alpha = 300
        
    def update(self):
        if self.alpha == 300 or self.alpha == 0:
            now = pg.time.get_ticks()
            if now - self.last_update > 100000:
                self.last_update = now
                self.current_time = (self.current_time + 1) % len(self.times)
                self.time = self.times[self.current_time]
                
        if self.time == 'evening':
            self.alpha -= 1
            self.game.day_sky.set_alpha(self.alpha)
        elif self.time == 'morning':
            self.alpha += 1
            self.game.day_sky.set_alpha(self.alpha)
        
        
        return self.time
        
        
        
        
        
        
        
        
        