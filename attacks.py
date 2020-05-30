import pygame as pg
from os import path
from settings import *
vec = pg.math.Vector2
from random import choice, randrange


class Attacks(pg.sprite.Sprite):
    def __init__(self, game, user):
        self.game = game
        self.groups = game.attack_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.user = user
    
    
class PlayerAttack(Attacks):
    def __init__(self, game, user):        
        Attacks.__init__(self, game, user)

        self.w = 50
        self.h = 10
        self.image = pg.Surface((self.w, self.h))
        self.image.fill(white)
        self.rect = self.image.get_rect()
        self.frames = 0
        self.a_frames = 100
        
    def update(self):
        if self.char.facing_right:
            self.rect.x = self.char.rect.x + self.char.rect.width
            self.rect.y = self.char.rect.y
        else:
            self.rect.x = self.char.rect.x - self.w
            self.rect.y = self.char.rect.y
            
        hits = pg.sprite.spritecollide(self, self.game.attackable_sprites, False)
        print(hits)
        if hits:
            for hit in hits:
                if hit.dammaged == False:
                    hit.health -= 1
                    hit.dammaged = True
                    if self.char.rect.x > hit.rect.x:
                        hit.vel.x = -5
                    else:
                        hit.vel.x = 5
                    hit.vel.y = -5
        else:
            self.frames += 1
            if self.frames > self.a_frames:
                self.frames = 0
                self.char.attacking = False
                pg.sprite.Sprite.kill(self)


class Scan(Attacks):
    def __init__(self, game, user):    
        Attacks.__init__(self, game, user)

        self.w = 64
        self.h = 80
        self.image = pg.Surface((self.w, self.h))
        self.image.fill(red)
        self.rect = self.image.get_rect()
        self.frames = 0
        self.a_frames = 100
           
            
            
    def update(self):
        if self.user.facing_right:
            self.rect.x = self.user.rect.x + self.user.rect.width + 15
            self.rect.y = self.user.rect.y
        else:
            self.rect.x = self.user.rect.x - self.w - 15
            self.rect.y = self.user.rect.y
            
        hits = pg.sprite.spritecollide(self, self.game.attackable_sprites, False)
        if hits:
            self.user.transform(hits[0].form)
            self.user.attacking = False
        else:
            self.frames += 1
            if self.frames > self.a_frames:
                self.frames = 0
                self.user.attacking = False
                pg.sprite.Sprite.kill(self)
                
                
                
                
                
                