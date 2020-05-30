import pygame as pg
from settings import *
from maplayers import *
from objects import *
from enemies import *
vec = pg.math.Vector2
import pytmx

class Map:
    def __init__(self, game, filename, x=0, y=0):
        self.game = game
        tm = pytmx.load_pygame(filename, pixelalpha=True)
        self.width = tm.width * tm.tilewidth
        self.height = tm.height * tm.tileheight
        self.tmxdata = tm
        self.name = filename[4:]
        self.game.current_areas[self.name] = self
        self.pos = vec(x, y)
        self.foreground = Layer('fore', self)
        self.midground = Layer('mid', self)
        self.background = Layer('back', self)
        
        self.new_maps = eval(self.tmxdata.properties.get('new_maps'))
        
        self.loaded_objects = []
        self.unloaded_objects = []
        self.render()
        self.load_map_objects()
        
        
        
    def render(self):
        ti = self.tmxdata.get_tile_image_by_gid
        for layer in self.tmxdata.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    props = self.tmxdata.get_tile_properties_by_gid(gid)
                    if props:
                        frames = []
                        for animation_frame in props['frames']:
                            image = self.tmxdata.get_tile_image_by_gid(animation_frame.gid)
                            frames.append(image) 
                        if 'fore' in str(layer.name):
                            for tile in self.foreground.animated_tiles:
                                if tile.frames == frames:
                                    tile.points.append(vec(x * self.tmxdata.tilewidth + self.pos.x, y * self.tmxdata.tileheight + self.pos.y))
                                    break
                            self.foreground.animated_tiles.append(Animations(frames, x * self.tmxdata.tilewidth + self.pos.x, y * self.tmxdata.tileheight + self.pos.y, 150))
                        elif 'back' in str(layer.name):
                            for tile in self.background.animated_tiles:
                                if tile.frames == frames:
                                    tile.points.append(vec(x * self.tmxdata.tilewidth + self.pos.x, y * self.tmxdata.tileheight + self.pos.y))
                                    break
                            self.background.animated_tiles.append(Animations(frames, x * self.tmxdata.tilewidth + self.pos.x, y * self.tmxdata.tileheight + self.pos.y, 150))
                        else:
                            for tile in self.midground.animated_tiles:
                                if tile.frames == frames:
                                    tile.points.append(vec(x * self.tmxdata.tilewidth + self.pos.x, y * self.tmxdata.tileheight + self.pos.y))
                                    break
                            self.midground.animated_tiles.append(Animations(frames, x * self.tmxdata.tilewidth + self.pos.x, y * self.tmxdata.tileheight + self.pos.y, 150))
                        continue
                    tile = ti(gid)
                    if tile:
                        if 'fore' in str(layer.name):
                            if tile in self.foreground.tiles:
                                self.foreground.tiles[tile].append(vec(x * self.tmxdata.tilewidth + self.pos.x, y * self.tmxdata.tileheight + self.pos.y))
                            else:
                                self.foreground.tiles[tile] = [vec(x * self.tmxdata.tilewidth + self.pos.x, y * self.tmxdata.tileheight + self.pos.y)]
                        elif 'back' in str(layer.name):
                            if tile in self.background.tiles:
                                self.background.tiles[tile].append(vec(x * self.tmxdata.tilewidth + self.pos.x, y * self.tmxdata.tileheight + self.pos.y))
                            else:
                                self.background.tiles[tile] = [vec(x * self.tmxdata.tilewidth + self.pos.x, y * self.tmxdata.tileheight + self.pos.y)]
                        else:
                            if tile in self.midground.tiles:
                                self.midground.tiles[tile].append(vec(x * self.tmxdata.tilewidth + self.pos.x, y * self.tmxdata.tileheight + self.pos.y))
                            else:
                                self.midground.tiles[tile] = [vec(x * self.tmxdata.tilewidth + self.pos.x, y * self.tmxdata.tileheight + self.pos.y)]
                            
                                  


    def load_map_objects(self):
        for object in self.tmxdata.objects:
            if object.id not in self.game.perm_del_objects+self.game.temp_del_objects+self.game.load_del_objects:
                print(self.game.perm_del_objects)
                if object.name:
                    if object.name != 'player':
                        self.loaded_objects.append(eval('{}(self.game, self, object, object.x + self.pos.x, object.y + self.pos.y)'.format(object.name)))
                    
    def update(self):
        if self.new_maps:
            if self.game.screen_track.pos.x > self.pos.x + self.width or self.game.screen_track.pos.x + width < self.pos.x or\
               self.game.screen_track.pos.y + height < self.pos.y or self.game.screen_track.pos.y > self.pos.y + self.height:
                for object in self.loaded_objects:
                    pg.sprite.Sprite.kill(object)
                del self.game.current_areas[self.name]
                return
            if self.game.screen_track.pos.x + width > self.pos.x + self.width and self.new_maps['right'] not in self.game.current_areas:
                Map(self.game, path.join(self.game.map_folder, self.new_maps['right']), self.pos.x + self.width, self.pos.y)
            if self.game.screen_track.pos.x < self.pos.x and self.new_maps['left'] not in self.game.current_areas:
                Map(self.game, path.join(self.game.map_folder, self.new_maps['left']), self.pos.x - self.width, self.pos.y)
            if self.game.screen_track.pos.y < self.pos.y and self.new_maps['up'] not in self.game.current_areas:
                Map(self.game, path.join(self.game.map_folder, self.new_maps['up']), self.pos.x, self.pos.y - self.height)
            if self.game.screen_track.pos.y + height > self.pos.y + self.height and self.new_maps['down'] not in self.game.current_areas:
                Map(self.game, path.join(self.game.map_folder, self.new_maps['down']), self.pos.x, self.pos.y + self.height)
                
                
               
class Screen:
    def __init__(self, game, screen):
        self.game = game
        self.screen = screen
        self.camera = Camera(self)
        self.pos = vec(0, 0)
        self.rect = pg.Rect(0, 0, width, height)
        
    def update(self, player):
        x = player.pos.x - (width / 2)
        y = player.pos.y - (height / 2)
        #hits = pg.sprite.spritecollide(self, self.game.scrollstop, False)
        #if hits:
        #    print(self.pos)
        #    if hits[0].dir == 'xl':
        #        x = max(hits[0].pos.x, x)
        #    elif hits[0].type == 'xr':
        #        x = min(hits[0].pos.x - width, x)
        #    if hits[0].dir == 'yu':
        #        y = max(hits[0].pos.y, y)
        #    elif hits[0].dir == 'yd':
        #        y = min(hits[0].pos.y - height, y)
        self.pos = vec(x, y)
        self.rect.x = self.pos.x
        self.camera.update(x, y, player)
        self.screen.fill(clear)

    def draw(self, layer):
        for tile in layer.tiles:
            for point in layer.tiles[tile]:
                if self.pos.x - tilesize < point.x <= self.pos.x + width and self.pos.y - tilesize < point.y <= self.pos.y + height:
                    self.screen.blit(tile, (point.x - self.pos.x, point.y - self.pos.y))
        for tile in layer.animated_tiles:
            for point in tile.points:
                if self.pos.x - tilesize < point.x <= self.pos.x + width and self.pos.y - tilesize < point.y <= self.pos.y + height:
                    tile.update()
                    self.screen.blit(tile.image, (point.x - self.pos.x, point.y - self.pos.y))
        
class Camera:
    def __init__(self, screen):
        self.screen = screen
        self.camera = pg.Rect(0, 0, width, height)
    
    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)
        
    def apply_rect(self, rect):
        return rect.move(self.camera.topleft)
        
    def update(self, x, y, target):
        x = -target.rect.x + int(width / 2)
        y = -target.rect.y + int(height / 2)
        
        #limit scrolling to map size
        #x = min(0, x) #left
        #y = min(0, y) #top
        #x = max(-(self.width - width), x) #right
        #y = max(-(self.height - height), y) #bottom
        self.camera = pg.Rect(x, y, width, height)
        

    