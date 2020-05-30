import pygame as pg
from os import path
from settings import *
from attacks import *
from specials import *
vec = pg.math.Vector2
from random import choice, randrange



class Normal:
    def __init__(self, player, game):
        self.player = player
        self.game = game
        self.NAME = 'Normal' #display name of form
        self.AMAX_land = 35 #max accelerration on land
        self.AMAX_water = 13 #max acceleration in water
        
        self.VMAX_walk = 3
        self.VMAX_run = 4.86
        self.VMAX_swim = 0
        self.VMAX_fast_swim = 4.5
        
        self.JUMP_land = -20 #max jump on land
        self.JUMP_water = -15 #max jump in water
        self.MASS = 10
        self.FRIC = fric * self.MASS
        self.max_b_frames = 600 #max time player can spend underwater
        self.SWIM = -5
        
        self.rect = pg.Rect(0, 0, 60, 60)
        self.rects = {'main': self.rect}
        
        self.load_images()
        
        self.SPECIAL = Scan
        self.ATTACK = Scan
        
        self.current_jump_frame = 0
        self.current_move_frame = 0
        self.last_update = 0
    
    def load_images(self):
        gi = self.game.spritesheet.get_image
        self.right_frames = [gi(0, 0, 64, 64), gi(64, 0, 64, 64), gi(128, 0, 64, 64)]
        for frame in self.right_frames:
            frame.set_colorkey(red)
        self.left_frames = [gi(0, 64, 64, 64), gi(64, 64, 64, 64), gi(128, 64, 64, 64)]
        for frame in self.left_frames:
            frame.set_colorkey(red)
        self.jump_frames = [gi(0, 192, 64, 85), gi(64, 192, 64, 88), gi(128, 192, 64, 71), gi(0, 280, 64, 53), gi(64, 280, 64, 44)]
        for frame in self.jump_frames:
            frame.set_colorkey(red)
            
    def animate(self):
        now = pg.time.get_ticks()
        bottom = self.player.rect.bottom
        #walking animation
        if self.player.on_solid:
            self.current_jump_frame = 0
            if now - self.last_update > 275:
                self.last_update = now
                self.current_move_frame = (self.current_move_frame + 1) % len(self.left_frames)
                if self.player.facing_right:
                    self.player.image = self.right_frames[self.current_move_frame]
                else:
                    self.player.image = self.left_frames[self.current_move_frame]
                
        #jumping
        #elif self.player.jumping and self.player.vel.y < 0 and not self.player.ducking:
        #     if now - self.last_update > 75:
        #        self.last_update = now
        #        self.player.angle += 5
        #        self.current_jump_frame = (self.current_jump_frame + 1) % len(self.jump_frames)
        #        self.player.image = self.jump_frames[self.current_jump_frame]
        #        self.player.image = pg.transform.rotate(self.player.image, self.player.angle)
        #elif self.player.falling:
        #    if now - self.last_update > 1:
        #        self.last_update = now
        #        self.player.image = self.jump_frames[-1]
        #        if self.player.angle < 360:
        #            self.player.angle += 30
        #        else:
        #            self.player.angle = 0
        #        self.player.image = pg.transform.rotate(self.player.image, self.player.angle)
        ##ducking
        #if self.player.ducking:
        #    if now - self.last_update > 100:
        #        self.last_update = now
        #        self.player.image = self.jump_frames[-1]
        self.player.rect.bottom = bottom
        self.player.pos.y = self.player.rect.topleft[1]  
            
            
class Snake:
    def __init__(self, player, game):
        self.game = game
        self.player = player
        self.NAME = 'Snake'
        self.AMAX_land = 10
        self.AMAX_water = 20
        self.VMAX = 3
        self.JUMP_land = -10
        self.JUMP_water = -3
        self.MASS = 10
        self.FRIC = fric * self.MASS
        self.max_b_frames = 1
        self.load_images()
        self.SPECIAL = Scan
        self.ATTACK = Scan
        
        self.current_jump_frame = 0
        self.current_move_frame = 0
        self.last_update = 0
        self.counter = 0
        
    def load_images(self):
        self.right_frames = [self.game.spritesheet.get_image(0, 128, 64, 16)]
        for frame in self.right_frames:
            frame.set_colorkey(white)
        self.left_frames = []
        for frame in self.right_frames:
            frame.set_colorkey(white)
            self.left_frames.append(pg.transform.flip(frame, True, False))
        self.climb_frames = []
        for frame in self.right_frames:
            frame.set_colorkey(white)
            self.climb_frames.append(pg.transform.rotate(frame, 90))
            
            
    def animate(self):
        now = pg.time.get_ticks()
        #walking animation
        if now - self.last_update > 275:
            self.last_update = now
            self.current_move_frame = (self.current_move_frame + 1) % len(self.left_frames)
            bottom = self.player.rect.bottom
            #walking
            if self.player.vel.x > 0 and self.player.on_solid:
                self.player.image = self.right_frames[self.current_move_frame]
            elif self.player.vel.x < 0 and self.player.on_solid:
                self.player.image = self.left_frames[self.current_move_frame]
            elif self.player.climbing:
                self.player.image = self.climb_frames[self.current_move_frame]
            self.player.rect = self.player.image.get_rect()
            self.player.rect.bottom = bottom
