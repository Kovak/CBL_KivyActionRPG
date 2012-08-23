import kivy
import math
from kivy.atlas import Atlas
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.lang import Builder
from kivy.uix.scatter import Scatter
from kivy.properties import AliasProperty, NumericProperty, BooleanProperty, ReferenceListProperty, ObjectProperty, ListProperty, StringProperty, BoundedNumericProperty
from kivy.vector import Vector
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.factory import Factory
from kivy.clock import Clock
from random import randint
from kivy.graphics.transformation import Matrix
from functools import partial
from kivy.uix.stencilview import StencilView
from kivy.core.window import Window
from kivy.graphics import Point, Color, Rectangle, Line
from kivy.event import EventDispatcher
from kivy.graphics.texture import Texture
from kivy.animation import Animation
from kivy.lang import Builder

class CBL_DebugPanel(BoxLayout):
    fps = StringProperty(None)

    def update(self, dt):
        self.fps = str(int(Clock.get_fps()))
        Clock.schedule_once(self.update)

class CBL_Collision_Widget(Widget):
    was_collided = BooleanProperty(False)
    self_prop = ObjectProperty(None)

    def reset_collided(self, dt):
        self.was_collided = False
        self.canvas.ask_update

    def on_was_collided(self, instance, value):
        Clock.schedule_once(self.reset_collided, .5)
        if isinstance(self.parent, CBL_Enemy):
            self.parent.got_collided = True
        if isinstance(self.parent, CBL_Player_Character):
            self.parent.got_collided = True

    def on_pos(self, instance, value):
        if not self.parent.is_deleting:
            self.parent.parent.check_collision(self)


class CBL_Projectile(Widget):
    distance = NumericProperty(0)
    direction = ListProperty(0)
    duration = NumericProperty(1.0)
    touch_up_pos = ListProperty(None)
    unit_speed = NumericProperty(50.0)
    has_fired = BooleanProperty(False)
    old_pos = ListProperty(None)
    is_deleting = BooleanProperty(False)

    def del_self(self, instance, value):
        print 'removing self'
        self.parent.remove_widget(self)

    def on_touch_down(self, touch):
        self.old_pos = list(self.pos)

    def get_pos(self):
        return self.pos

    def on_touch_move(self, touch):
        if not self.has_fired:
            self.pos = touch.x, touch.y
        
    def on_touch_up(self, touch):
        
        self.pos = self.old_pos
        touch_up_pos = (touch.x, touch.y)
        pos = self.pos
        self.distance = int(Vector(pos).distance(Vector(touch_up_pos))/self.unit_speed)
        self.direction = (pos[0] - touch_up_pos[0], pos[1] - touch_up_pos[1])
        self.touch_up_pos = touch_up_pos
        self.parent.spawn_spell_mode = False
        self.has_fired = True
        print 'touched_up spell'
        print self.move_anim

class CBL_Projectile_1(Widget):
    touches = []
    unit_speed = NumericProperty(30.0)
    duration = 1.0
    has_fired = BooleanProperty(False)
    old_pos = ListProperty(None)
    is_deleting = BooleanProperty(False)

    def del_self(self, instance, value):
        print 'removing self'
        self.parent.remove_widget(self)

    def on_touch_down(self, touch):
        if not self.has_fired:
            self.old_pos = list(self.pos)

    def on_touch_move(self, touch):
        if not self.has_fired:
            self.center = touch.x, touch.y
            self.touches.append((touch.x, touch.y))

    def create_animation(self, instance, value):
        if self.touches == []:
            print 'requesting delete'
            self.del_self(None, None)
        else:
            target = list(self.touches[0])
            self.target_pos = target
            self.touches.pop(0)

    def on_touch_up(self, touch):
        if not self.has_fired:
            self.pos = self.old_pos
            pos = self.pos
            self.create_animation(None, None)
            self.parent.spawn_spell_mode = False
            self.has_fired = True
            print 'touched_up spell'

class CBL_Enemy(Widget):
    target = ObjectProperty(None)
    unit_speed = NumericProperty(.9)
    target_moved = BooleanProperty(False)
    target_pos = ListProperty(None)
    got_collided = BooleanProperty(False)
    is_deleting = BooleanProperty(False)
    is_ready = BooleanProperty(False)


    def del_self(self, instance, value):
        print 'removing self'
        if self.is_ready and not self.is_deleting:
            self.is_deleting = True
            print self.parent
            self.parent.collision_objects.remove(self.collision_widget)
            self.parent.remove_widget(self)

    def on_got_collided(self, instance, value):
        self.del_self(None, None)
        self.got_collided = False


    def on_target_moved(self, instance, value):
        self.target_pos = self.target.pos
        self.target_moved = False
            

    def on_target_pos(self, instance, value):
        if self.move_anim != None:
            Animation.stop_all(self, 'pos')

    def stop_moving(self, instance, value):
        pass

class CBL_Animated_Sprite(Widget):
    self_prop = ObjectProperty(None)
    anim_frame = NumericProperty(1)
    anim_state = NumericProperty(0)
    anim_states = ListProperty(None)
    is_moving = BooleanProperty(False)
    source_image = StringProperty(None)
    
    def update_sprite_direction(self):
        is_moving = True
        XDistance = self.parent.target_pos[0] - self.pos[0]
        YDistance = self.parent.target_pos[1] - self.pos[1]
        rotation = math.atan2(YDistance, XDistance)
        rotationDeg = math.degrees(rotation)
        if rotationDeg < 0:
            rotationDeg = rotationDeg + 360
        if rotationDeg >= 45 and rotationDeg < 135:
            self.anim_state = 3
        if rotationDeg < 315 and rotationDeg >= 225: 
            self.anim_state = 1
        if rotationDeg < 45 and rotationDeg >= 0:
            self.anim_state = 7
        if rotationDeg >= 315 and rotationDeg <= 360:
            self.anim_state = 7
        if rotationDeg <225 and rotationDeg >= 135:
            self.anim_state = 5

    def stop_moving(self, instance, value):
        print 'stopping movement'
        self.anim_state -= 1
        self.is_moving = False

    def update(self, dt):   
        wasfour = False
        if self.anim_frame == 4:
            self.anim_frame = 1
            wasfour = True
        if self.anim_frame < 4 and not wasfour:
            self.anim_frame += 1 
        Clock.schedule_once(self.update, .350)

class CBL_Player_Touch_Widget(Widget):

    def on_touch_down(self, touch):
        super(CBL_Player_Touch_Widget, self).on_touch_down(touch)
        if self.collide_point(touch.x, touch.y):
            self.parent.parent.activeunit = self.parent
            print 'active unit set:', self.parent.parent.activeunit

class CBL_Player_Character(Widget):
    target_pos = ListProperty(None)
    unit_speed = NumericProperty(2.0)
    sprite_image = ObjectProperty(None)
    source_image = StringProperty(None)
    anim_states = ListProperty(None)
    has_me_targeted = ListProperty(None)
    has_moved_in_last_2_seconds = BooleanProperty(False)
    health = NumericProperty(10)
    is_deleting = BooleanProperty(False)
    got_collided = BooleanProperty(False)

    def on_health(self, instance, value):
        print self.health
        if self.health == 0:
            self.is_deleting = True
            self.parent.collision_objects.remove(self.collision_widget)
            self.parent.player_characters.remove(self)
            self.parent.remove_widget(self)

    def on_got_collided(self, instance, value):
        print 'was collided'
        if self.got_collided:
            self.health -= 1
            Clock.schedule_once(self.reset_got_collided, .350)
            print 'health is now: ', self.health
           
    def reset_got_collided(self, dt):
        self.got_collided = False

    def reset_has_moved_counter(self, dt):
        self.has_moved_in_last_2_seconds = False

    def on_target_pos(self, instance, value):
        print 'setting target', value
        print self.move_anim
        if self.move_anim != None:
            Animation.stop_all(self, 'pos')
        self.sprite_image.update_sprite_direction()

    def on_pos(self, instance, value):
        if not self.has_moved_in_last_2_seconds:
            self.has_moved_in_last_2_seconds = True
            for each in self.has_me_targeted:
                each.target_moved = True
            Clock.schedule_once(self.reset_has_moved_counter, .5)

class CBL_Stat_System(Widget):
    
    earth = BoundedNumericProperty(2, min=0, max=100)
    wind = BoundedNumericProperty(2, min=0, max=100)
    fire = BoundedNumericProperty(2, min=0, max=100)
    water = BoundedNumericProperty(2, min=0, max=100)

    earth_base = NumericProperty(1)
    earth_armor = NumericProperty(1)
    earth_multiplier = NumericProperty(2)
    water_multiplier = NumericProperty(1)
    armor_value = NumericProperty(1)
    attack_speed_base = NumericProperty(1)
    cooldown_base = NumericProperty(1)
    boot_value = NumericProperty(1)
    speed_base = NumericProperty(1)
    weapon_damage_value = NumericProperty(1)

    health = NumericProperty(10)
    mana = NumericProperty(1)
    armor = NumericProperty(1)
    spell_armor = NumericProperty(1)
    attack_speed = NumericProperty(1)
    cooldown = NumericProperty(1)
    speed = NumericProperty(1)
    attack_damage = NumericProperty(1)

    print 'earth is: ',earth
    print 'wind is: ',wind
    print 'fire is: ',fire
    print 'water is: ',water
  
class CBL_GameWorldScreen(Widget):
    activeunit = ObjectProperty(None, allownone = True)
    spritesheets = ListProperty(['atlas://Images/isaac64/', 'atlas://Images/isaac128/', 'atlas://Images/isaac256/'])
    resolution = NumericProperty(1)
    spawnmode = BooleanProperty(False)
    spawn_spell_mode = BooleanProperty(False)
    d_touch = ObjectProperty(None)
    button_width = NumericProperty(80)
    button_height = NumericProperty(80)
    spacing = NumericProperty(10)
    self_prop = ObjectProperty(None)
    collision_objects = ListProperty(None)
    player_characters = ListProperty(None)
    enemy_characters = ListProperty(None)
    spawn_enemy_mode = BooleanProperty(False)


    def check_collision(self, moving_widget):
        collision_list = list(self.collision_objects)
        if moving_widget in collision_list:
            collision_list.remove(moving_widget)
        for each in collision_list:
            if moving_widget.collide_widget(each):
                moving_widget.was_collided = True
                each.was_collided = True

    def create_enemy(self, touch):
        enemy_pos = self.to_widget(touch[0], touch[1])
        parent = self
        new_enemy = CBL_Enemy(pos = enemy_pos, parent = parent,  size = (32, 32))
        self.collision_objects.append(new_enemy.collision_widget)
        print self.collision_objects
        self.add_widget(new_enemy)
        if self.player_characters != []:
            new_enemy.target = self.player_characters[0]
            self.player_characters[0].has_me_targeted.append(new_enemy)
        new_enemy.is_ready = True
        self.spawn_enemy_mode = False

    
    def create_sprite(self, touch):
        spritepos = self.to_widget(touch[0], touch[1])
        print 'touch at',spritepos
        source_image = self.spritesheets[self.resolution]
        parent = self
        anim_states = ['isaacforwards_xcf-forwardidle-', 4, .34, 'isaacforwards_xcf-forwardwalk-', 4, .34, 'isaacbackward_xcf-backwardsidle-', 4, .34, 'isaacbackward_xcf-backwardswalk-', 4, .34, 
        'isaacleft_xcf-leftidle-', 4, .34,'isaacleft_xcf-leftwalk-', 4, .34,'isaacright_xcf-rightidle-', 4, .34,'isaacright_xcf-rightwalk-', 4, .34]
        newsprite = CBL_Player_Character(source_image = source_image, unit_speed = 1.0, anim_frame = 1, parent = parent, anim_states = anim_states, pos = spritepos, size = (128, 128))
        Clock.schedule_once(newsprite.sprite_image.update)
        self.collision_objects.append(newsprite.collision_widget)
        self.player_characters.append(newsprite)
        print 'collision objects:', self.collision_objects
        print 'sprite at', newsprite.pos
        self.add_widget(newsprite)
        self.spawnmode = False

    def create_spell(self):
        if self.activeunit:
            unit_pos = self.activeunit.pos
            spell_pos_1 = self.to_widget(unit_pos[0] + 76, unit_pos[1] + 16)
            spell_pos_2 = self.to_widget(unit_pos[0] - 42, unit_pos[1]+ 16)
            spell_pos_3 = self.to_widget(unit_pos[0] + 16, unit_pos[1] - 32)
            spell_pos_4 = self.to_widget(unit_pos[0] + 16, unit_pos[1] + 76)
            parent = self
            newspell = CBL_Projectile(parent = parent, pos = spell_pos_1, size = (32, 32))
            self.add_widget(newspell)
            newspell = CBL_Projectile(parent = parent, pos = spell_pos_2, size = (32, 32))
            self.add_widget(newspell)
            newspell = CBL_Projectile(parent = parent, pos = spell_pos_3, size = (32, 32))
            self.add_widget(newspell)
            newspell = CBL_Projectile(parent = parent, pos = spell_pos_4, size = (32, 32))
            self.add_widget(newspell)

    def create_spell2(self):
        if self.activeunit:
            unit_pos = self.activeunit.center
            spell_pos_1 = self.to_widget(unit_pos[0] + 64, unit_pos[1])
            parent = self
            newspell = CBL_Projectile_1(parent = parent, pos = spell_pos_1, size = (64, 64))
            #self.collision_objects.append(newspell.collision_widget)
            self.add_widget(newspell)       
     
    def on_touch_down(self,touch):
        print self.self_prop
        print 'touch down pos:', touch.x, touch.y
        super(CBL_GameWorldScreen, self).on_touch_down(touch)
        if self.spawnmode:
            self.create_sprite((touch.x, touch.y))
        if self.spawn_enemy_mode:
            self.create_enemy((touch.x, touch.y))
        
        if self.collide_point(touch.x, touch.y) and self.activeunit != None and not self.activeunit.collide_point(touch.x, touch.y):
            self.activeunit.target_pos = (touch.x, touch.y) 
            print 'set unit: ', self.activeunit, 'targetpos as: ', touch.x, touch.y

    def on_touch_move(self,touch):
        super(CBL_GameWorldScreen,self).on_touch_move(touch)
        
    def on_touch_up(self,touch):
        super(CBL_GameWorldScreen,self).on_touch_up(touch)
        
class MainScreen(FloatLayout):

    button_width = NumericProperty(80)
    button_height = NumericProperty(80)
    spacing = NumericProperty(10)
    
    def clear_target(self):
        self.input_widget.activeunit = None

    def on_touch_down(self,touch):
        if self.input_widget.collide_point(touch.x, touch.y) and not touch.x < self.x + self.button_width + self.spacing:
            self.input_widget.on_touch_down(touch)
        else: 
            super(MainScreen, self).on_touch_down(touch)    

    def spawn_sprite(self):
        self.input_widget.activeunit = None
        self.input_widget.spawnmode = True

    def spawn_enemy(self):
        self.input_widget.activeunit = None
        self.input_widget.spawn_enemy_mode = True

    def spawn_spell(self):
        self.input_widget.spawn_spell_mode = True

    def button_callback(self, value):
        print 'button called', value.text
        if value.text == '64-Bit':
            self.input_widget.resolution = 0
        if value.text =='128-Bit':
            self.input_widget.resolution = 1
        if value.text == 'Spawn':
            self.spawn_sprite()
        if value.text == 'Spawn Enemy':
            self.spawn_enemy()
        if value.text == 'Clear Target':
            self.clear_target()
        if value.text == 'Spell 1':
            self.input_widget.create_spell()
        if value.text == 'Spell 2':
            self.input_widget.create_spell2()


Factory.register('CBL_GameWorldScreen', CBL_GameWorldScreen)
Factory.register('CBL_DebugPanel', CBL_DebugPanel)
Factory.register('CBL_Collision_Widget', CBL_Collision_Widget)
Factory.register('CBL_Animated_Sprite', CBL_Animated_Sprite)
Factory.register('CBL_Player_Touch_Widget', CBL_Player_Touch_Widget)
Factory.register('CBL_Stat_System', CBL_Stat_System)


class Game(Widget):
    def __init__(self):
        Widget.__init__(self)
        mainwidget = MainScreen(pos = (10, 10), size = (Window.width-20, Window.height - 20))
        self.add_widget(mainwidget)

    def update(self, dt):
        pass
        
class CBL_GameApp(App):
    def build(self):
        game = Game()
        Clock.schedule_interval(game.update, 1.0/60.0)
        return game


if __name__ == '__main__':
    CBL_GameApp().run()