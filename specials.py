import pygame as pg
from os import path
from settings import *
from player import *
vec = pg.math.Vector2
from random import choice, randrange

class Specials:
    
    def player_special(player):
        if player.specific_collision('x', player.game.blocks):
            keys = pg.key.get_pressed()
            player.acc.y = 0
            if keys[pg.K_UP]:
                player.acc.y = -player.form.AMAX_land
                player.acc.y += player.vel.y * player.form.FRIC
            elif keys[pg.K_DOWN]:
                player.acc.y = player.form.AMAX_land
            else:
                if player.vel.x == 0:
                    player.vel = vec(0, 0)