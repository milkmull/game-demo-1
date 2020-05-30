#sprite classes for platform game
import pygame as pg
from os import path
from settings import *
from forms3 import *
vec = pg.math.Vector2
from random import choice, randrange


class Spritesheet:
    def __init__(self, filename):
        self.spritesheet = pg.image.load(filename).convert()
        
    def get_image(self, x, y, w, h):
        image = pg.Surface((w, h))
        image.blit(self.spritesheet, (0, 0), (x, y, w, h))
        return image


class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):        
        self.groups = game.player_sprite
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game

        self.forms_dic = {} #dec containing keys of strings that represent forms and values of pictures of each form. eval used to create new form from list
        self.form = Normal(self, self.game) #players current form
        self.forms_dic[self.form.NAME] = self.form.right_frames[0]
        self.selecting = False #true when selecting a new form from form menue
        self.switched = False #indicates that player has made the selection. prevents switching between forms continuously
        
        self.current_health = max_health #current health based on max health var in settings. Update when new heart is found?
        
        self.health_display = Health_Bar(self, self.game) #displays player's current health
        self.breath_display = Breath_Timer(self, self.game) #displays player's current breath, changes when under water
        self.form_display = Form_Select(self, self.game)
        Collectable_Counter(self, self.game)
        
        self.angle = 0 #player's current image rotation angle
        
        self.assign_form_variables(self.form)
        self.rect.center = (x, y)

        self.pos = vec(x, y)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        #movement
        self.left = False #if player is pressing left
        self.right = False #if player is pressing right
        self.up = False #if player is pressing up
        self.down = False #if player.is pressing down

        self.facing_right = True #remembers last input to determin which way the animation frame should be facing
        self.facing_left = False

        self.running = False #if player is running
        self.run_timer = {'timer': 0, 'right': False, 'left': False, 'check': False}
        
        self.jumpcheck = False #when player presses jump, checks if jump is possible
        self.jumping = False #when player is moving up in air
        self.jump_cut = False #when player lets go of jump
        self.falling = False #when player is moving down in air
        
        self.jump_timer = {'early': 999, 'fall': 999}
        
        self.on_solid = False #when standing on platform
        
        self.scanning = False
        self.attacking = False
        self.dammaged = False #when player has taken dammage
        self.i_frames = 0 #invincibility frame counter for after taking dammage

        self.ducking = False

        self.climbing = False #when player is climbing

        self.current_b_frames = 0 #keeps track of time underwater
        self.swimming = False #when character is moving while under the water
        self.floating = False #when character is floating, chanceled out by pressing down
        self.in_water = False #when player is touching water, indicates when water phyics are turned on
        self.underwater = False #used for breath counter
       
    def move(self):
        if self.in_water:
            ACC = self.AMAX_water
        else:
            ACC = self.AMAX_land
            
        if self.right:
            self.acc.x = ACC
            self.facing_right = True
            self.facing_left = False
        elif self.left:
            self.acc.x = -ACC
            self.facing_left = True
            self.facing_right = False
        if self.in_water:
            if self.up:
                self.acc.y = -ACC
            elif self.down and not self.on_solid:
                self.acc.y = ACC
            
    def run(self):
        if self.left and not (self.run_timer['check'] and self.run_timer['left']):
            self.run_timer['left'] = True
            self.run_timer['right'] = False
            self.run_timer['timer'] = 0
            self.run_timer['check'] = False
        elif self.right and not (self.run_timer['check'] and self.run_timer['right']):
            self.run_timer['right'] = True
            self.run_timer['left'] = False
            self.run_timer['timer'] = 0
            self.run_timer['check'] = False
            
        if not (self.right or self.left) and (self.run_timer['right'] or self.run_timer['left']):
            self.run_timer['check'] = True
            
        if ((self.left and self.run_timer['left']) or (self.right and self.run_timer['right'])) and self.run_timer['check'] and self.run_timer['timer'] <= 10:
            self.running = True
            
        if self.run_timer['timer'] > 10:
            self.run_timer = {'timer': 0, 'right': False, 'left': False, 'check': False}
            if self.running and not (self.right or self.left):
                self.running = False
                
        if self.vel.x == 0:
            self.running = False
            
        self.run_timer['timer'] += 1
    
        if self.running and not self.in_water:
            self.AMAX_land = self.form.AMAX_land * 1.8
        else:
            self.AMAX_land = self.form.AMAX_land             
    
    def duck(self):
        if self.on_solid and self.down:
            self.ducking = True
        else:
            self.ducking = False
                      
    def jump(self):
        if self.jumpcheck and self.falling:
            self.jump_timer['early'] = 0
        self.jump_timer['early'] += 1
        
        if self.on_solid:
            self.jump_timer['fall'] = 0
        self.jump_timer['fall'] += 1
        
        if self.in_water:
            JUMP = self.JUMP_water
        else:
            JUMP = self.JUMP_land
        
        if self.jumpcheck:
            if self.underwater:
                if self.right and self.vel.x > 0:
                    self.vel.x = -self.SWIM
                    self.vel.y = -1
                elif self.left and self.vel.x < 0:
                    self.vel.x = self.SWIM
                    self.vel.y = -1
                elif self.down:
                    self.vel.y = -self.SWIM
                else:
                    self.vel.y = self.SWIM
                        
            elif self.on_solid or self.jump_timer['fall'] <= 5:
                self.vel.y = JUMP - 0.5 * abs(self.vel.x)
                self.jumping = True
                
            elif self.floating:
                if self.up:
                    self.vel.y = JUMP - 0.5 * abs(self.vel.x)
                    self.jumping = True
                elif self.right:
                    self.vel.x = -self.SWIM
                elif self.left:
                    self.vel.x = self.SWIM

            self.jumpcheck = False
                
        elif self.jump_timer['early'] <= 6:
            if (self.on_solid and not self.in_water) or self.floating:
                self.vel.y = JUMP - 0.5 * abs(self.vel.x)
                self.jumping = True
                
            self.jumpcheck = False
 
        elif self.vel.y > 0 and not (self.in_water or self.climbing or self.dammaged or self.on_solid):
            self.falling = True 
            self.jumping = False
                
        elif self.vel.y == 0 and not (self.in_water or self.climbing or self.on_solid):
            self.jumping = False
            self.falling = False
            
        if self.jump_cut:
            if self.vel.y < -3 and not self.on_solid:
                self.vel.y = -3
            self.jump_cut = False

    def attack(self):
        if self.attacking and not self.climbing:
            self.form.ATTACK(self.game, self)  

    def select_form(self):
        forms = self.form_display.selection
        if forms:
            if len(forms) == 1:
                if self.up:
                    self.transform(switch_form=forms[0])
            elif len(forms) == 2:
                if self.up:
                    self.transform(switch_form=forms[0])
                elif self.right:
                    self.transform(switch_form=forms[1])
            elif len(forms) == 3:
                if self.up:
                    self.transform(switch_form=forms[0])
                elif self.right:
                    self.transform(switch_form=forms[1])
                elif self.up:
                    self.transform(switch_form=forms[2])
            elif len(forms) == 4:
                if self.up:
                    self.transform(switch_form=forms[0])
                elif self.right:
                    self.transform(switch_form=forms[1])
                elif self.up:
                    self.transform(switch_form=forms[2])
                elif self.down:
                    self.transform(switch_form=forms[3])

    def transform(self, scanned_form='', switch_form=''):
        #print(scanned_form, switch_form)
        if scanned_form:
            if self.form.NAME != scanned_form.NAME: #make sure player is not already in that form
                if scanned_form.NAME not in self.forms_dic.keys(): #make sure form is not already in their forms dic
                    if len(self.forms_dic.values()) < max_forms: #make sure player is not exceding their form limit
                        self.forms_dic[scanned_form.NAME] = scanned_form.right_frames[0]
                    else:
                        for key in list(self.forms_dic)[::-1]:
                            if key != 'Normal':
                                self.forms_dic.pop(key)
                                self.forms_dic[scanned_form.NAME] = scanned_form.right_frames[0]
                self.form = eval('{}(self, self.game)'.format(scanned_form.NAME))
        else:
            self.form = eval('{}(self, self.game)'.format(switch_form))
            self.switched = True
        self.assign_form_variables(self.form)
        bottom = self.rect.bottom
        if self.facing_right:
            self.image = self.form.right_frames[0]
        elif self.facing_left:
            self.image = self.form.left_frames[0]
        self.rect = self.image.get_rect()
        self.rect.bottom = bottom
        self.pos.y = self.rect.topleft[1]   
        
      

    def collisions(self, dir):
        plat_hits = pg.sprite.spritecollide(self, self.game.platforms, False)
        if plat_hits:
            for hit in plat_hits:
                hit.collide_player(self, dir)
        else:
            self.on_solid = False
            
        if not self.dammaged:
            enemy_hits = pg.sprite.spritecollide(self, self.game.enemies, False)
            if enemy_hits:
                enemy_hits[0].collide_player(self)
                
        if not self.dammaged:
            hazzard_hits = pg.sprite.spritecollide(self, self.game.hazards, False)
            if hazzard_hits:
                hazzard_hits[0].collide_player(self, dir)
        
        invis_hits = pg.sprite.spritecollide(self, self.game.invis, False)
        for hit in invis_hits:
            hit.collide_player(self)

        water_hits = pg.sprite.spritecollide(self, self.game.water, False)
        if water_hits:
            for hit in water_hits:
                if hit.rect.collidepoint(self.rect.center):
                    self.in_water = True
                    break
                else:
                    self.in_water = False
            for hit in water_hits:
                if hit.rect.colliderect(pg.Rect(self.rect.x + 5, self.rect.y, self.rect.width - 10, 1)):
                    self.underwater = True
                    break
                else:
                    self.underwater = False
            for hit in water_hits:
                hit.collide_player(self)
        else:
            self.swimming = False
            self.floating = False
            self.in_water = False
            self.underwater = False
            
        climb_hits = pg.sprite.spritecollide(self, self.game.climbers, False)
        if climb_hits:
            climb_hits[0].collide_player(self)
        else:
            self.climbing = False
            
        collectable_hits = pg.sprite.spritecollide(self, self.game.collectables, False)
        if collectable_hits:
            for hit in collectable_hits:
                hit.collide_player(self)

    def damage_timer(self):
        if self.dammaged:
            self.i_frames += 1
            if self.i_frames > 100:
                self.i_frames = 0
                self.dammaged = False
             
             
    def update(self):
        self.animate()
        self.acc = vec(0, grav)
        if (not self.selecting) or self.switched:
            self.move()
            self.run()
            self.jump()
            #self.duck()
            self.attack()
        else:
            self.select_form()

        if self.in_water:
            self.acc.x += self.vel.x * self.FRIC * 0.4
            self.acc.y += self.vel.y  * self.FRIC * 0.4
        elif self.climbing:
            self.acc *= 0
        else:
            self.acc.x += self.vel.x * self.FRIC
        self.vel += self.acc * self.game.dt
        self.pos += self.vel + 0.5 * self.acc * (self.game.dt ** 2)

        for dir in ['x', 'y']:
            self.adjust_rects(dir)
            self.collisions(dir)
        #speed adjust
        self.adjust_speed()
        #timers
        self.damage_timer()
        self.breath_display.update()
        
        #print(self.forms_list)
        self.actions()
            
    def adjust_speed(self):
        if abs(self.vel.x) < 0.1:
            self.vel.x = 0
        if abs(self.vel.y) < 0.1:
            self.vel.y = 0
        if abs(self.acc.x) < 0.1:
            self.acc.x = 0
        if abs(self.acc.y) < 0.1:
            self.acc.y = 0
            
        if not self.in_water:
            #max fall speed
            if self.falling:
                self.vel.y = min(self.vel.y, 20)
        elif self.vel.y > 0 and not self.down:
            self.vel.y = min(self.vel.y, 1)
            
    def adjust_rects(self, dir):
        if dir == 'x':
            self.rect.x = self.pos.x
        if dir == 'y':
            self.rect.y = self.pos.y

        
        

        

                
                
                
        
        
        
    def actions(self):
        #print('jumping', self.jumping)
        #print('falling', self.falling)
        #print('swimming', self.swimming)
        #print('on_solid', self.on_solid)
        #print('floating', self.floating)
        #print('in water', self.in_water)
        #print('pos', self.pos)
        #print('attacking', self.attacking)
        print('vel', self.vel)
        #print('acc', self.acc)
        print('')
        pass
        
    def assign_form_variables(self, form):
        self.image = form.right_frames[0]
        self.rect = form.rect
        self.rects = form.rects
        
        self.AMAX_land = form.AMAX_land
        self.AMAX_water = form.AMAX_water
        self.JUMP_land = form.JUMP_land
        self.JUMP_water = form.JUMP_water
        self.MASS = form.MASS
        self.FRIC = form.FRIC
        self.max_b_frames = form.max_b_frames
        self.SWIM = form.SWIM
        
        self.SPECIAL = form.SPECIAL
        self.ATTACK = form.ATTACK
        self.animate = form.animate
          
        
        
        
class Form_Select(pg.sprite.Sprite):
    def __init__(self, player, game):
        self.groups = game.screen_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.player = player
        self.selection = []
        
    def draw(self):
        self.selection = []
        if self.player.selecting:
            forms = list(self.player.forms_dic)
            forms.remove(self.player.form.NAME)
            if forms:
                c = (width // 2, height // 2)
                config = [(c[0], c[1] - (2 * tilesize)), (c[0] + (2 *tilesize), c[1]), (c[0] - (2 *tilesize), c[1]), (c[0], c[1] + (2 * tilesize))]
                config = config[:len(forms)]
                for form, pos in zip(forms, config):
                    self.game.screen.blit(self.player.forms_dic[form], pos) 
                    self.selection.append(form) #up, right, left, down
        


    

          
#on-screen sprites    
class Health_Bar(pg.sprite.Sprite):
    def __init__(self, player, game):
        self.groups = game.screen_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.player = player
        self.image = game.spritesheet.get_image(64, 128, 64, 64)
        self.image.set_colorkey(black)   
        
    def draw(self):
        i = 0
        for health in range(self.player.current_health):
            self.game.screen.blit(self.image, (i,0))
            i += 10          
            
class Breath_Timer(pg.sprite.Sprite):
    def __init__(self, player, game):
        self.groups = game.screen_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.player = player
        self.outline_image = pg.Surface((110, 20))
        self.outline_image.fill(white)
        
    def update(self):
        if self.player.underwater:
            self.player.current_b_frames += 1
            if self.player.current_b_frames == self.player.max_b_frames:
                self.player.current_health = 0
        elif self.player.current_b_frames > 0:
            self.player.current_b_frames -= 5
        
    def draw(self):
        self.game.screen.blit(self.outline_image, (20, 100))
        fill = int((abs(self.player.current_b_frames - self.player.max_b_frames) / self.player.max_b_frames) * 100)
        percent_image = pg.Surface((fill, 10))
        if fill > 50:
            percent_image.fill(blue)
        elif fill > 25:
            percent_image.fill(orange)
        else:
            percent_image.fill(red)
        self.game.screen.blit(percent_image, (25, 105))
        
class Collectable_Counter(pg.sprite.Sprite):
    def __init__(self, player, game):
        self.groups = game.screen_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.player = player
        self.message1 = '{} / {}'
        self.message2 = 'your time: {}'
        self.done = False
        
    def draw(self):
        if len(self.game.perm_del_objects) / len(self.game.perm_del_objects + list(self.game.collectables)) != 1:
            message = self.message1.format(len(self.game.perm_del_objects), len(self.game.perm_del_objects + list(self.game.collectables)))
        elif not self.done:
            self.time = pg.time.get_ticks() / 1000
            self.done = True
        if self.done:
            message = self.message2.format(self.time)
        
        text = create_text(message, 30)
        
        self.game.screen.blit(text, (25, 130))
        
        


    



        
            




