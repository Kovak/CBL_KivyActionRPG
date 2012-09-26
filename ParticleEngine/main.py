import kivy
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, BooleanProperty, ListProperty, StringProperty, ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.app import App
from kivy.graphics import Color, Rectangle, Callback
from kivy.graphics.instructions import InstructionGroup
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.vector import Vector
from kivy.atlas import Atlas
from random import random, randint, uniform
from collections import deque
from functools import partial
import re

class Particle(InstructionGroup):
    refresh_time = .08
    frame = 0

    def __init__(self, initial_params, param_changes, parent = None, dormant = False, **kwargs):
        # these parameters are necessary for Rectangle
        super(Particle,self).__init__()
        self.rect = Rectangle(pos=(initial_params['x'],initial_params['y']),size=(initial_params['width'],initial_params['height']),texture=initial_params['texture'])
        self.add(self.rect)

        self.color_code = (1., 1., 1., 1.)
        self.color = Color(*self.color_code)
        self.insert(0, self.color)

        self.initial_params = initial_params
        self.param_changes = param_changes
        self.parent = parent
        self.dormant = dormant

        if not dormant:
            self.activate()


    def activate(self):
        self.rect.pos = (self.initial_params['x'],self.initial_params['y'])
        self.rect.size  = (self.initial_params['width'],self.initial_params['height'])
        self.rect.texture = self.initial_params['texture']

        self.change_color((self.initial_params['color_r'],self.initial_params['color_g'],self.initial_params['color_b'],self.initial_params['color_a']))

        self.dormant = False
        self.dx = self.refresh_time * self.initial_params['velocity_x']
        self.dy = self.refresh_time * self.initial_params['velocity_y']

        Clock.schedule_once(self.kill,self.initial_params['lifetime'])

        if 'width' in self.param_changes:
            self.width_gen = (x for x in self.param_changes['width'])
            self.update_width(None)
        if 'height' in self.param_changes:
            self.height_gen = (x for x in self.param_changes['height'])
            self.update_height(None)
        if 'texture' in self.param_changes:
            self.texture_gen = (x for x in self.param_changes['texture'])
            self.update_texture(None)
        if 'color_a' in self.param_changes:
            self.color_a_gen = (x for x in self.param_changes['color_a'])
            self.update_color_a(None)
        
        self.update_pos(None)


    def update_pos(self,dt):
        self.rect.pos = (self.rect.pos[0] + self.dx, self.rect.pos[1] + self.dy)
        Clock.schedule_once(self.update_pos,self.refresh_time)

    def update_width(self,dt):
        try:
            val, time = self.width_gen.next()
        except StopIteration:
            return False
        self.rect.size = (self.rect.size[0]+val, self.rect.size[1])
        Clock.schedule_once(self.update_width,time)

    def update_height(self,dt):
        try:
            val, time = self.height_gen.next()
        except StopIteration:
            return False
        self.rect.size = (self.rect.size[0], self.rect.size[1]+val)
        Clock.schedule_once(self.update_height,time)

    def update_texture(self,dt):
        try:
            val, time = self.texture_gen.next()
        except StopIteration:
            return False
        self.rect.texture = val
        Clock.schedule_once(self.update_texture,time)

    def update_color_a(self,dt):
        try:
            val, time = self.color_a_gen.next()
        except StopIteration:
            return False
        a = self.color_code[3]+(val/255.)
        if a < 0: a = 0
        self.change_color((self.color_code[0], self.color_code[1], self.color_code[2], a))
        Clock.schedule_once(self.update_color_a,time)

    def change_color(self,color_code):
        # is there not a faster way to do this that works?
        self.color_code = color_code
        index = self.indexof(self.color)
        self.remove(self.color)
        self.color = Color(*self.color_code)
        self.insert(index, self.color)


    def kill(self,dt):
        # self.dormant = True
        # Clock.unschedule(self.update_pos)
        # Clock.unschedule(self.update_width)
        # Clock.unschedule(self.update_texture)
        # Clock.unschedule(self.update_height)
        # Clock.unschedule(self.update_color_a)
        self.parent.reap_particle(self)


class ParticleEmitter(Widget):

    def __init__(self, emmitter_type = 'smoke', num_particles = 30, **kwargs):
        super(ParticleEmitter,self).__init__(**kwargs)
        assert emmitter_type in ['smoke']
        self.emmitter_type = emmitter_type
        self.num_particles = num_particles
        self.counter = 0
        Clock.schedule_once(self.setup_window)
        
        

    def setup_window(self,dt):
        print self.size
        if self.emmitter_type == 'smoke':
            texture_list = self.get_texture_list('VFX-Explosion','VFX/VFX_Set1_64.atlas')
            self.initial_params = {'velocity_x': 0,
                                    'velocity_y': 200,
                                    'texture': texture_list[0],
                                    'x': self.pos[0],
                                    'y': self.pos[1],
                                    'lifetime': 1.5,
                                    'width': 64,
                                    'height': 64,
                                    'color_r': 0.,
                                    'color_g': 0.,
                                    'color_b': 1.,
                                    'color_a': 1.,}
            self.param_changes = {'texture': zip(texture_list[1:],[0.3]*(len(texture_list)-1)),
                                'width': [(8,.5),(8,.5),(8,.5),(8,.25),(8,.25),(8,.25),(8,.25)],
                                'height': [(8,.5),(8,.5),(8,.5),(8,.25),(8,.25),(8,.25),(8,.25),],}
                                # 'color_a': [(-50,.2),(-50,.2),(-50,.2),(-50,.2),(-50,.2),]}
            self.scatterdict = {'velocity_x': 100, 
                            'velocity_y': 20, 
                            'lifetime': .1, 
                            'x': 10,
                            'y': 10}
            self.slate = InstructionGroup()
            self.canvas.add(self.slate)
        

        self.emit_rate = self.initial_params['lifetime']/float(self.num_particles*1.1)
        Clock.schedule_once(self.emit_particle)

    def emit_particle(self, dt):
        self.slate.add(Particle(self.randomize_params(),self.param_changes,parent=self,dormant=False))
            # p = ParticleGroup(initial_params, param_changes=param_changes, scatterdict=scatterdict, batch_size = batch_size)
        # self.counter += 1
        if self.counter < self.num_particles: Clock.schedule_once(self.emit_particle,self.emit_rate)

    def get_texture_list(self, image_basename, image_location):
        basename = image_basename
        atlas = Atlas(image_location)
        all_keys = atlas.textures.keys()
        wanted_keys = filter(lambda x: x.startswith(basename),all_keys)

        if len(wanted_keys) > 1:
            pattern = re.compile(r'[0-9]+$')
            wanted_keys.sort(key=lambda x: int(pattern.search(x).group()))

        return [atlas[key] for key in wanted_keys]

    def reap_particle(self,particle):
        # these lines are only necessary if particle is moving or we want to alter effect. we will want to find a way to not run them in other cases.
        # particle.initial_params = self.randomize_params()
        # particle.param_changes = self.param_changes
        # particle.activate()
        self.slate.remove(particle)

    def randomize_params(self):
        params = self.initial_params.copy()
        for key in params.keys():
            try:
                if key in self.scatterdict:
                    params[key] = params[key] * uniform(1-self.scatterdict[key],1+self.scatterdict[key]) if self.scatterdict[key] < 1 else params[key] + randint(int(-self.scatterdict[key]),int(self.scatterdict[key]))
                else:
                    params[key] *= uniform(0.9,1.1)
            except:
                pass
        return params

class CBL_DebugPanel(BoxLayout):
    fps = StringProperty(None)
    particles = NumericProperty(0)

    def __init__(self,**kwargs):
        super(CBL_DebugPanel,self).__init__(**kwargs)
        self.update(None)

    def update(self, dt):
        self.fps = str(int(Clock.get_fps()))
        Clock.schedule_once(self.update)


class LowLevelParticleEngineApp(App):
    def build(self):
        # 'atlas://VFX/smoke_particles/VFX_SmokeParticle'
        fl = FloatLayout(pos=(0,0),size=Window.size)
        db_panel = CBL_DebugPanel(pos=(0,0),size=(100,50),size_hint = (None,None))
        fl.add_widget(db_panel)
        for d in xrange(4):
            fl.add_widget(ParticleEmitter(emitter_type = 'smoke', num_particles=50, debug=db_panel, pos=(randint(100,Window.width - 100),randint(100,Window.height - 100)),size=(128,128),size_hint=(None,None)))
        return fl



if __name__ == '__main__':
    LowLevelParticleEngineApp().run()
