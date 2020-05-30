#sprite classes for platform game
import pygame as pg
from os import path
from settings import *
vec = pg.math.Vector2
from random import choice, randrange

class New_Object:
    def __init__(self, width, height, type=''):
        self.width = width
        self.height = height
        self.type = type

class Object:
    def __init__(self, game, map, object, x, y):
        self.object = object
        self.game = game
        self.map = map
        self.rect = pg.Rect(x, y, object.width, object.height)
        self.pos = vec(x, y)

class Block1(Object, pg.sprite.Sprite):
    def __init__(self, game, map, object, x, y):
        Object.__init__(self, game, map, object, x, y)
        self.groups = game.platforms, game.solids
        pg.sprite.Sprite.__init__(self, self.groups)
    
    def collide_player(self, player, dir):
        if dir == 'x':
            if player.vel.x > 0:
                player.pos.x = self.rect.left - player.rect.width
            elif player.vel.x < 0:
                player.pos.x = self.rect.right
            player.vel.x = 0
        if dir == 'y':
            if player.vel.y >= 0:
                player.pos.y = self.rect.top - player.rect.height
                player.on_solid = True
            elif player.vel.y < 0:
                player.pos.y = self.rect.bottom
                player.jumping = False
            player.vel.y = 0
        player.adjust_rects(dir)
                
                


class Ramps(Object, pg.sprite.Sprite):
    def __init__(self, game, map, object, x, y):  
        Object.__init__(self, game, map, object, x, y)
        self.groups = game.platforms, game.solids
        pg.sprite.Sprite.__init__(self, self.groups)
        self.angle = object.height / object.width
        self.type = object.type
        self.rects = []
        self.create_ramp()   
            
    def create_ramp(self):
        if 'U' not in self.type:
            if self.type == 'R':
                for x in range(self.rect.x, self.rect.right, 1):
                    height = (x - self.rect.x) * self.angle 
                    rect = pg.Rect(x, self.rect.bottom - height, 1, height)
                    self.rects.append(rect)
                #self.rects.append(pg.Rect(self.rect.right - 2, self.rect.y, 2, 1)) #stops from sticking at top of ramp when block is ahead
            elif self.type == 'L':
                for x in range(self.rect.right, self.rect.x, -1):
                    height = (self.rect.right - x) * self.angle
                    rect = pg.Rect(x, self.rect.bottom - height, 1, height)
                    self.rects.append(rect) 
                self.rects.append(pg.Rect(self.rect.x, self.rect.y, 2, 1))
        else:
            if self.type == 'UR':
                for x in range(self.rect.x, self.rect.right, 1):
                    height = (x - self.rect.x) * self.angle
                    rect = pg.Rect(x, self.rect.y, 1, height)
                    self.rects.append(rect)
            elif self.type == 'UL':
                for x in range(self.rect.right, self.rect.x, -1):
                    height = (self.rect.right - x) * self.angle
                    rect = pg.Rect(x, self.rect.y, 1, height)
                    self.rects.append(rect)
                    
    def check_for_hits(self, player, dir): #moves player rect where it wants to go, returns a list of solids that it hits
        if dir == 'y':
            if 'U' not in self.type:
                player.rect.y -= 1
                hits = pg.sprite.spritecollide(player, self.game.solids, False)
                player.rect.y += 1
            else:
                player.rect.y += 1
                hits = pg.sprite.spritecollide(player, self.game.solids, False)
                player.rect.y -= 1
        elif dir == 'x':
            if player.vel.x < 0:
                player.rect.x -= 1
                hits = pg.sprite.spritecollide(player, self.game.solids, False)
                player.rect.x += 1
            elif player.vel.x > 0:
                player.rect.x += 1
                hits = pg.sprite.spritecollide(player, self.game.solids, False)
                player.rect.x -= 1
            else:
                hits = []
        if self in hits:
            hits.remove(self)
        for hit in hits:
            if isinstance(hit, Ramps):
                if hit.type == self.type and (hit.rect.bottom == self.rect.top or hit.rect.top == self.rect.bottom):
                    hits.remove(hit)
                else:
                    i = 0
                    while i in range(len(hit.rects)):
                        if hit.rects[i].colliderect(player.rect):
                            break
                        else:
                            i += 1
                    if i == len(hit.rects):
                        hits.remove(hit)
            elif isinstance(hit, Block1) and hit.rect.top == self.rect.top:
                hits.remove(hit)
        print(hits)
        return hits
                  
    def collide_player(self, player, dir): 
        for rect in self.rects: #loop through every rect
            if rect.colliderect(player.rect): #check if it hits the player
                hits = self.check_for_hits(player, dir)
                if not hits:
                    if player.rect.centery + 5 < rect.top and player.vel.y >= 0: #puts player on top of ramp
                        if rect.height == self.rect.height - 1:
                            player.pos.y = self.rect.y - player.rect.height
                        else:
                            player.pos.y = rect.top - player.rect.height
                        player.adjust_rects(dir)
                        player.vel.y = 0
                        player.on_solid = True
                        print(1)
                        
                    elif player.rect.centery - 5 > rect.bottom and player.vel.y <= 0: #puts player on bottom of ramp
                        player.pos.y = rect.bottom
                        player.adjust_rects(dir)
                        player.vel.y = 0
                        if (self.type == 'UR' and player.vel.x > 0) or (self.type == 'UL' and player.vel.x < 0): #keeps from sticking to bottom
                            player.vel.x = 0
                        player.jumping = False
                        print(2)
                    else:
                        if player.vel.x >= 0 and player.rect.centerx < rect.x: #puts player on left and right side of ramp
                            player.pos.x = rect.left - player.rect.width
                        elif player.vel.x < 0 and player.rect.centerx > rect.right:
                            player.pos.x = rect.right
                        player.adjust_rects(dir)
                        player.vel.x = 0
                        print(3)
                        return
                        
                    #if self.rects[-1].colliderect(player.rect) and player.vel.x == 0:
                    #    player.pos.x += 2
                    #    player.vel.x = 2
                    #    player.adjust_rects(dir)
                else:
                    if player.vel.x < 0: #stops player when solid is hit while on ramp
                        player.pos.x = rect.right
                    elif player.vel.x > 0:
                        player.pos.x = rect.left - player.rect.width
                    player.adjust_rects(dir)
                    player.vel.x = 0
                    return
        else:
            if player.jumping:
                player.on_solid = False
                
        print(player.vel.x)
                
    def check_if_on_top(self, player):
        for rect in self.rects:
            if rect.colliderect(player.rect) and player.rect.centery < rect.top:
                return True
        return False
        
        
class Water(Object, pg.sprite.Sprite):
    def __init__(self, game, map, object, x, y):
        Object.__init__(self, game, map, object, x, y)
        self.groups = game.water
        pg.sprite.Sprite.__init__(self, self.groups)
            
    def collide_player(self, player):
        player.falling = False
            
        if player.in_water and (not player.floating) and (player.right or player.left or player.up or player.down):
            player.swimming = True
        else:
            player.swimming = False
            
        hits = 0
        for water in self.game.water:
            if water.rect.colliderect(pg.Rect(player.rect.x, player.rect.y - 1, player.rect.width, 1)):
                hits += 1
                break

        if (self.rect.top + 5 > player.rect.centery >= self.rect.top - 5) and (player.vel.x != 0 or player.up) and not (player.jumping) and not hits:
            player.floating = True
            player.pos.y = self.rect.top - player.rect.height // 2
            player.adjust_rects(dir)
            player.vel.y = 0
        else:
            player.floating = False


class Semisolid(Object, pg.sprite.Sprite):
    def __init__(self, game, map, object, x, y):
        Object.__init__(self, game, map, object, x, y)
        self.groups = game.platforms
        pg.sprite.Sprite.__init__(self, self.groups)
        self.type = object.type
    
    def collide_player(self, player, dir):
        if dir == 'y':
            if self.type == 'up':
                if player.rect.centery + 5 < self.rect.top and player.vel.y > 0:
                    player.pos.y = self.rect.top - player.rect.height
                    player.adjust_rects(dir)
                    player.vel.y = 0
                    player.on_solid = True
            elif self.type == 'down':
                if player.vel.y < 0 and player.rect.centery - 5 > self.rect.bottom:
                    player.pos.y = self.rect.top
                    player.adjust_rects(dir)
                    player.vel.y = 0
                    player.jumping = False
        elif dir == 'x':
            if self.type == 'left':
                if player.vel.x > 0 and player.rect.right > self.rect.left:
                    player.pos.x = self.rect.left - player.rect.width
                    player.adjust_rects(dir)
                    player.vel.x = 0
            elif self.type == 'right':
                if player.vel.x < 0 and player.rect.x < self.rect.right:
                    player.pos.x = self.rect.right
                    player.adjust_rects(dir)
                    player.vel.x = 0             
                
                
class SemiDrop(Object, pg.sprite.Sprite):
    def __init__(self, game, map, object, x, y):
        Object.__init__(self, game, map, object, x, y)
        self.groups = game.platforms
        pg.sprite.Sprite.__init__(self, self.groups)
    
    def collide_player(self, player, dir):
        if not player.climbing:
            if dir == 'y':
                if (not player.down) and player.vel.y > 0 and player.rect.bottom <= self.rect.top + 20:
                    player.rect.bottom = self.rect.top
                    player.vel.y = 0
                    player.pos.y = player.rect.y
                    player.on_solid = True
                
                
                
class Spikes(Object, pg.sprite.Sprite):
    def __init__(self, game, map, object, x, y):
        Object.__init__(self, game, map, object, x, y)
        self.groups = game.hazards
        pg.sprite.Sprite.__init__(self, self.groups)
    
    def collide_player(self, player, dir):
        if dir == 'y':
            player.current_health -= 1
            if player.vel.x >= 0:
                player.vel.x = -13
            elif player.vel.x < 0:
                player.vel.x = 13
            if player.vel.y < 0:
                player.vel.y = 13
            elif player.vel.y >= 0:
                player.vel.y = -13
            player.dammaged = True



class Ladder(Object, pg.sprite.Sprite):
    def __init__(self, game, map, object, x, y):
        Object.__init__(self, game, map, object, x, y)
        self.groups = game.climbers
        pg.sprite.Sprite.__init__(self, self.groups)
        SemiDrop(self.game, self.map, New_Object(tilesize + tilesize // 2, tilesize // 4), x - tilesize // 4, y)
        
    def collide_player(self, player):
        if player.climbing:
            player.vel.x = 0
            if player.up:
                player.vel.y = -8
            elif player.down:
                player.vel.y = 8
            if not (player.up or player.down):
                player.vel.y = 0
                player.acc.y = 0
        if (self.rect.centerx - 15 < player.rect.centerx <= self.rect.centerx + 15) and (player.up or (player.down and not player.on_solid)):
            player.climbing = True
            player.jumping = False
            player.pos.x = self.rect.centerx - player.rect.width // 2
            player.adjust_rects(dir)
        if (player.left or player.right):
            player.climbing = False                          


class Tree(pg.sprite.Sprite):
    def __init__(self, game, map, object, x, y):
        Object.__init__(self, game, map, object, x, y)
        self.groups = game.platforms
        pg.sprite.Sprite.__init__(self, self.groups)
        self.name = 'tree'
        
    def collide_player(self, player):
        if (player.rect.centery + 5 <= self.rect.top) and not (player.down):
            player.vel.y = 0
            player.pos.y = self.rect.top - player.rect.height
            player.rect.y = player.pos.y
            player.on_solid = True
            player.climbing = False
        
        
class Point(pg.sprite.Sprite):
    def __init__(self, game, map, object, x, y):
        Object.__init__(self, game, map, object, x, y)
        self.groups = game.points
        pg.sprite.Sprite.__init__(self, self.groups)
        self.type = object.type
        self.action = eval(object.action)
        
class Collectable(Object, pg.sprite.Sprite):
    def __init__(self, game, map, object, x, y):
        Object.__init__(self, game, map, object, x, y)
        self.groups = game.collectables, game.moving_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.image = pg.Surface((10, 10))
        self.image.fill(gold)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        self.status = 'perm'
        
    def collide_player(self, player):
        self.game.object_remove(self)
        
        
        
    
        


        
        
#class Scrollstop(pg.sprite.Sprite):
#    def __init__(self, game, map, info, x, y):
#        self.groups = game.scrollstop
#        pg.sprite.Sprite.__init__(self, self.groups)
#        self.game = game
#        self.map = map
#        self.id = info.id
#        self.rect = pg.Rect(x, y, 1, 1)
#        self.pos = vec(x, y)
#        self.dir = info.type
        
        
# class New_Area(pg.sprite.Sprite):
#     def __init__(self, game, map, info, x, y):
#         self.groups = game.invis
#         pg.sprite.Sprite.__init__(self, self.groups)
#         self.game = game
#         self.map = map
#         self.id = info.id
#         self.new_map = '{}.tmx'.format(info.map)
#         self.pos = vec(x, y)
#         
#         
#     def load_area(self):
#         map = Map(self.game, path.join(self.game.map_folder, self.map), self.map.pos.x + self.map.width, 0)
#         self.game.current_areas.append(map)
        
            
                    
                    
                    
    