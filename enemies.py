#sprite classes for platform game
import pygame as pg
from os import path
from settings import *
from forms3 import *
vec = pg.math.Vector2
from random import choice, randrange

class Enemies:
    def __init__(self, game, map, object, x, y):
        self.game = game
        self.map = map
        self.object = object
        self.angle = 0
        self.pos = vec(x, y)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.objective = ''
        #move
        self.left = False
        self.right = False
        self.up = False
        self.down = False
        #direction when no imput is given
        self.facing_right = True
        self.facing_left = False
        #running
        self.running = False
        # jumping
        self.jumping = False
        self.jump_cut = False
        self.falling = False
        # swimming
        self.swimming = False
        self.floating = False
        
        self.on_solid = False
        #attack stuff
        self.attacking = False
        #enemies
        self.dammaged = False
        #duck
        self.ducking = False
        #climb
        self.climbing = False
        #track
        self.on_track = False
        #special
        self.specialing = False
    
    
    
    
    
    def platform_collision(enemy, dir):
        hits = pg.sprite.spritecollide(enemy, enemy.game.platforms, False)
        if hits:
            for hit in hits:
                hit.collide_player(enemy, dir)
        else:
            enemy.on_solid = False
        return hits
        
    def water_collision(enemy):
        hits = pg.sprite.spritecollide(enemy, enemy.game.water, False)
        if hits:
            hits[0].collide_player(enemy)
        else:
            enemy.swimming = False
            enemy.floating = False
            enemy.ACC = enemy.form.AMAX_land
        return hits
            
    def climb_collision(enemy):
        hits = pg.sprite.spritecollide(enemy, enemy.game.climbers, False)
        if hits:
            hits[0].collide_player(enemy)
        else:
            enemy.climbing = False
        return hits
    
    def hazard_collision(enemy):
        if not enemy.dammaged:
            hits = pg.sprite.spritecollide(enemy, enemy.game.hazards, False)
            if hits:
                hits[0].collide_player(enemy)
            return hits
            
            
            
            
class TestForm(Enemies, pg.sprite.Sprite):
    def __init__(self, game, map, object, x, y):
        Enemies.__init__(self, game, map, object, x, y)
        self.groups = game.attackable_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.form = Snake(self, self.game)
        self.rect = pg.Rect(x, y, 1, 1)
            
            
            
class Enemy1(Enemies, pg.sprite.Sprite):
    def __init__(self, game, map, object, x, y):
        Enemies.__init__(self, game, map, object, x, y)
        self.groups = game.moving_sprites, game.enemies, game.attackable_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.status = 'load'
        self.new_form = Snake
        self.form = self.new_form(self.game, self)
        self.image = self.form.right_frames[0]
        self.rect = self.image.get_rect()
        self.rect.x = x

    def collide_player(self, player):
        player.current_health -= 1
        player.dammaged = True
        if player.rect.centerx < self.rect.centerx:
            player.vel.x = -15
            player.vel.y = -5
        else:
            player.vel.x = 15
            player.vel.y = -5
            
    def special_collision(self):
        hits = pg.sprite.spritecollide(self, self.game.water, False)
        if hits:
            self.pos.y = hits[0].rect.top - self.rect.height
            self.rect.y = self.pos.y
            self.vel.y = 0
            
    def update(self):
        self.form.animate()
        if not self.swimming:
            self.acc = vec(0, grav)
        else:
            self.acc = vec(0, grav * 0.4)
        # equations of motion
        self.vel += self.acc * self.game.dt
        self.pos += self.vel + 0.5 * self.acc * self.game.dt ** 2
        
        self.scan()
        self.move_switches()
        self.move()
        self.rect.x = self.pos.x
        Enemies.platform_collision(self, 'x')
        self.rect.y = self.pos.y
        Enemies.platform_collision(self, 'y')
        Enemies.climb_collision(self)
        self.special_collision()
        self.dammaged_status()
        
        #max speed adjustments
        if self.vel.y > 0:
            self.vel.y = min(self.vel.y, 20)

        
        
    def scan(self):
        if not self.on_track and self.objective == '':
            closest = vec(10000000, 10000000)
            for point in self.game.points:
                if point.type == 'land':
                    if abs(point.pos.x - self.pos.x) < closest.x and abs(point.pos.y - self.pos.y) < closest.y:
                        closest = point.pos
            self.objective = closest
        
        
    def move_switches(self):
        if not self.on_track:
            if self.objective.x > self.pos.x:
                self.right = True
                self.left = False
            elif self.objective.x < self.pos.x:
                self.left = True
                self.right = False
        hits = pg.sprite.spritecollide(self, self.game.points, False)
        if hits:
            if hits[0].type == 'land':
                print(self.down)
                self.on_track = True
                if self.right:
                    i = 'right'
                else:
                    i = 'left'
                if hits[0].action[i] == 'right':
                    self.right = True
                    self.left = False
                    self.up = False
                    self.down = False
                elif hits[0].action[i] == 'left':
                    self.left = True
                    self.right = False
                    self.up = False
                    self.down = False
                if hits[0].action[i] == 'up':
                    self.up = True
                    self.down = False
                    self.left = False
                    self.right = False
                elif hits[0].action[i] == 'down':
                    self.down = True
                    self.up = False
                    self.left = False
                    self.right = False
                if hits[0].action[i] == 'jump':
                    self.jumping = True
                if hits[0].action[i] == 'special':
                    self.specialing = True
                
                    
            
        
                
    def move(self):
        if (self.right or self.left) and self.vel.x == 0:
            self.vel.y = self.form.JUMP_land
        if self.right:
            self.vel.x = self.form.VMAX
        elif self.left:
            self.vel.x = - self.form.VMAX
        if self.climbing:
            if self.up:
                self.vel.y = -8
            else:
                self.vel.y = 8
  
            
    def dammaged_status(self):
        if self.dammaged:
            self.i_frames += 1
            if self.i_frames > 35:
                self.i_frames = 0
                self.dammaged = False
            if self.health == 0:
                #print('yeet')
                self.game.object_remove(self)
                         