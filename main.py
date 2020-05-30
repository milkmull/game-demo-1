import pygame as pg
import random
import sys
import os 
from settings import *
from player import *
from tilemap import *
from maplayers import *
from objects import *
from enemies import *


class Game:
    #initialize game window
    def __init__(self):
        self.running = True
        # initialize py game and create window
        pg.init()
        self.screen = pg.display.set_mode(screen_size)
        self.screen_track = Screen(self, self.screen)
        pg.display.set_caption(title)
        self.clock = pg.time.Clock()
        self.starting_map = 'big.tmx'
        self.entity_count = 0
        self.load_data()
        
    def load_data(self):
        game_folder = os.path.dirname(__file__)
        self.map_folder = os.path.join(game_folder, 'map')
        self.image_folder = os.path.join(game_folder, 'img')
        self.spritesheet = Spritesheet(path.join(self.image_folder, SPRITESHEET))
        #objects that go away forever
        self.perm_del_objects = []
        

        #self.day_sky = pg.Surface((self.map.width, self.map.height))
        #self.day_sky.fill(blue)
        #self.night_sky = pg.Surface((self.map.width, self.map.height))
        #self.night_sky.fill(black)


        
    # start new game
    def new(self):
        self.player_sprite = pg.sprite.Group()
        self.moving_sprites = pg.sprite.Group()
        self.platforms = pg.sprite.Group()
        self.solids = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.invis = pg.sprite.Group()
        self.attack_sprites = pg.sprite.Group()
        self.water = pg.sprite.Group()
        self.screen_sprites = pg.sprite.Group()
        self.attackable_sprites = pg.sprite.Group()
        self.climbers = pg.sprite.Group()
        self.hazards = pg.sprite.Group()
        self.points = pg.sprite.Group()
        self.scrollstop = pg.sprite.Group()
        self.collectables = pg.sprite.Group()
        #objects that delete for a period of time
        self.temp_del_objects = []
        #objects that delete until a new area is loaded
        self.load_del_objects = []
        #spawn player
        self.current_areas = {}
        
        Map(self, path.join(self.map_folder, self.starting_map))
        for object in self.current_areas[self.starting_map].tmxdata.objects:
            if object.name == 'player':
                self.player = Player(self, object.x, object.y)
        #self.time_of_day = DayNightCycle(self)
        
        
            
                
                
    def object_remove(self, object):
        if object.status == 'none':
            return
        if object.status == 'perm':
            self.perm_del_objects.append(object.object.id)
        if object.status == 'temp':
            self.temp_del_objects(object.object.id)
        if object.status == 'load':
            self.load_del_objects.append(object.object.id)
        pg.sprite.Sprite.kill(object)
            
        
        
    # run game loop
    def run(self):
        self.playing = True
        while self.playing:
            self.dt = self.clock.tick(fps) / 1000
            self.events()
            self.update()
            self.draw()
            
    def quit(self):
        pg.quit()
        sys.exit()
        
        
        
    # game loop update
    def update(self):
        #update info
        for sprite in self.moving_sprites:
            if self.player.pos.x + width > sprite.pos.x >= self.player.pos.x - width or self.player.pos.y + width < sprite.pos.y <= self.player.pos.y - width:
                sprite.update()

        self.attack_sprites.update()
        
        #self.time = self.time_of_day.update()

        if self.player.current_health == 0:
            self.new()
        self.player.update()

        temp_dic = self.current_areas.copy()
        for area in temp_dic.values():
            area.update()
        temp_dic = ''
        self.screen_track.update(self.player)
                

    # game loop draw
    def draw(self):
        # render update on screen (draw)
     
        for area in self.current_areas.values():
            self.screen_track.draw(area.background)
            self.screen_track.draw(area.midground)

        for sprite in self.moving_sprites:
            self.screen.blit(sprite.image, self.screen_track.camera.apply(sprite))
        
        for sprite in self.attack_sprites:
            self.screen.blit(sprite.image, self.screen_track.camera.apply(sprite))
            
        self.screen.blit(self.player.image, self.screen_track.camera.apply(self.player))
        
        for area in self.current_areas.values():
            self.screen_track.draw(area.foreground)
            
        for sprite in self.screen_sprites:
            sprite.draw()
            
        pg.display.flip()
   
        
    #game loop events
    def events(self):
        #process input
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()   
            if event.type == pg.KEYDOWN:
                #quit
                if event.key == pg.K_ESCAPE:
                    self.quit()
                # jump
                if event.key == pg.K_SPACE:
                    self.player.jumpcheck = True
                # move left
                if event.key == pg.K_LEFT:
                    self.player.left = True
                    self.player.right = False
                # move right
                if event.key == pg.K_RIGHT:
                    self.player.right = True
                    self.player.left = False
                # attack
                if event.key == pg.K_a:
                    self.player.attacking = True
                    
                if event.key == pg.K_q:
                    self.player.selecting = True
                    
                if event.key == pg.K_UP:
                    self.player.up = True
                    self.player.down = False
                    
                if event.key == pg.K_DOWN:
                    self.player.down = True
                    self.player.up = False
                    
                if event.key == pg.K_r:
                    self.perm_del_objects = []
                    self.new()
                    
                    
            if event.type == pg.KEYUP:
                if event.key == pg.K_SPACE:
                    self.player.jump_cut = True
                if event.key == pg.K_LEFT:
                    self.player.left = False
                if event.key == pg.K_RIGHT:
                    self.player.right = False
                if event.key == pg.K_UP:
                    self.player.up = False
                if event.key == pg.K_DOWN:
                    self.player.down = False
                if event.key == pg.K_q:
                    self.player.selecting = False
                    self.player.switched = False
                    
                    
    
        

    def pause(self):
        pass
                
        
                
                    
                    
                    
    def show_start_screen(self):
        pass
        
        
    def show_go_screen(self):
        pass
        
        
    
        
g = Game()
g.show_start_screen()
while g.running:
    g.new()
    g.run()
    g.show_go_screen()
    
