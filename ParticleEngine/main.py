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

from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.label import Label


class Particle(Rectangle):
    refresh_time = .05
    frame = 0

    def __init__(self, initial_params, param_changes, parent = None, dormant = False, **kwargs):
        # these parameters are necessary for Rectangle
        super(Particle,self).__init__(pos=(initial_params['x'],initial_params['y']),size=(initial_params['width'],initial_params['height']),texture=initial_params['texture'])
        self.initial_params = initial_params
        self.param_changes = param_changes
        self.parent = parent
        self.dormant = dormant

        if not dormant:
            self.activate()


    def activate(self):
        self.pos = (self.initial_params['x'],self.initial_params['y'])
        self.size  = (self.initial_params['width'],self.initial_params['height'])
        self.texture = self.initial_params['texture']
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
        
        self.update_pos(None)


    def update_pos(self,dt):
        self.pos = (self.pos[0] + self.dx, self.pos[1] + self.dy)
        Clock.schedule_once(self.update_pos,self.refresh_time)

    def update_width(self,dt):
        try:
            val, time = self.width_gen.next()
        except StopIteration:
            return False
        self.size = (self.size[0]+val, self.size[1])
        Clock.schedule_once(self.update_width,time)

    def update_height(self,dt):
        try:
            val, time = self.height_gen.next()
        except StopIteration:
            return False
        self.size = (self.size[0], self.size[1]+val)
        Clock.schedule_once(self.update_height,time)

    def update_texture(self,dt):
        try:
            val, time = self.texture_gen.next()
        except StopIteration:
            return False
        self.texture = val
        Clock.schedule_once(self.update_texture,time)

    def kill(self,dt):
        self.dormant = True
        Clock.unschedule(self.update_pos)
        Clock.unschedule(self.update_width)
        Clock.unschedule(self.update_texture)
        Clock.unschedule(self.update_height)
        self.parent.reap_particle(self)





class ParticleGroup(InstructionGroup):
    counter = 0

    def __init__(self, initial_params, param_changes = None, scatterdict = None, batch_size = 30, **kwargs):
        super(ParticleGroup,self).__init__()
        self.scatterdict = scatterdict if scatterdict is not None else {}
        self.initial_params = initial_params
        self.param_changes = param_changes if param_changes is not None else {}
        self.batch_size = batch_size
        self.emit_rate = initial_params['lifetime']/(batch_size*.75)

        # must be called with Clock schedule, or it goes ahead and adds all these particles prematurely
        Clock.schedule_once(self.init_particles)
        # Clock.schedule_once(self.emit_particle,.1)
        
    def emit_particle(self,dt):
        try:
            p = self.particles.pop()
            self.scatterdict = {'velocity_x': 'velocity_x_slider.value', 'velocity_y': velocity_y_slider.value, 'lifetime': .8}
            p.activate()
            self.add(p)
        except IndexError:
            print "empty"
            pass
        self.counter += 1
        if self.counter < self.batch_size: 
            Clock.schedule_once(self.emit_particle,self.emit_rate)

    def init_particles(self,dt):
        self.particles = deque([Particle(self.randomize_params(self.initial_params,self.scatterdict),self.param_changes,parent=self,dormant=True) for d in xrange(self.batch_size)],maxlen=self.batch_size)
        Clock.schedule_once(self.emit_particle)

    def reap_particle(self,pt):
        self.particles.appendleft(pt)
        self.remove(pt)

    def randomize_params(self,param_dict,scatterdict):
        params = param_dict.copy()
        for key in params.keys():
            try:
                if key in scatterdict:
                    params[key] = params[key] * uniform(1-scatterdict[key],1+scatterdict[key]) if scatterdict[key] < 1 else params[key] + randint(int(-scatterdict[key]),int(scatterdict[key]))
                else:
                    params[key] *= uniform(0.9,1.1)
            except:
                pass
        return params


class ParticleEmitter(Widget):

    
    # start_btn.bind(on_press=ParticleEmitter(image_basename = 'VFX-Explosion', image_location = 'VFX/VFX_Set1_64.atlas', debug=db_panel, pos=(200,200),size=(128,128),size_hint=(None,None)))

    def __init__(self, image_basename, image_location, emmitter_type = 'smoke', batches = 10, batch_size = 100,**kwargs):
        super(ParticleEmitter,self).__init__()
        assert emmitter_type in ['smoke']

        if emmitter_type == 'smoke':
            texture_list = self.get_texture_list('VFX-Explosion','VFX/VFX_Set1_64.atlas')
            self.initial_params = {'velocity_x': velocity_x_slider.value,
                'velocity_y': velocity_y_slider.value,
                'texture': texture_list[0],
                'x': 200,
                'y': 200,
                'lifetime': 4.,
                'width': 64,
                'height': 64,}
            self.param_changes = {'texture': zip(texture_list[1:],[0.6]*(len(texture_list)-1)),
                                'width': [(8,.5),(8,.5),(8,.5),(8,.25),(8,.25),(8,.25),(8,.25)],
                                'height': [(8,.5),(8,.5),(8,.5),(8,.25),(8,.25),(8,.25),(8,.25),]}
            self.scatterdict = {'velocity_x': 'velocity_x_slider.value', 'velocity_y': 200, 'lifetime': .8}
            self.batch_size = batch_size

        start_btn = Button(text = 'Start Emitter', font_size = 14, size = (100,100), size_hint = (None,None), pos = (600,50))
        self.add_widget(start_btn)
        start_btn.bind(on_press=self.initiate)

    def initiate(self,instance):
        batches = 10
        initial_params = self.initial_params
        param_changes = self.param_changes
        scatterdict = {'velocity_x': velocity_x_slider.value, 'velocity_y': velocity_y_slider.value, 'lifetime': .8}
        batch_size = self.batch_size 

        for b in range(batches):
            self.emit_particle_group(initial_params, param_changes, scatterdict, batch_size)
    



    def emit_particle_group(self, initial_params, param_changes, scatterdict, batch_size):
        with self.canvas:
            p = ParticleGroup(initial_params, param_changes=param_changes, scatterdict=scatterdict, batch_size = batch_size)

    def get_texture_list(self, image_basename, image_location):
        basename = image_basename
        atlas = Atlas(image_location)
        all_keys = atlas.textures.keys()
        wanted_keys = filter(lambda x: x.startswith(basename),all_keys)

        if len(wanted_keys) > 1:
            pattern = re.compile(r'[0-9]+$')
            print wanted_keys
            wanted_keys.sort(key=lambda x: int(pattern.search(x).group()))

        return [atlas[key] for key in wanted_keys]


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
        global velocity_x_slider
        velocity_x_slider = Slider(min=0,max=200,value=20,center=(650,600),size=(150,10),size_hint=(None,None))
        fl.add_widget(velocity_x_slider)
        global velocity_y_slider
        velocity_y_slider = Slider(min=0,max=200,value=20,center=(650,550),size=(150,10),size_hint=(None,None))
        fl.add_widget(velocity_y_slider)
        fl.add_widget(ParticleEmitter(image_basename = 'VFX-Explosion', image_location = 'VFX/VFX_Set1_64.atlas', debug=db_panel, pos=(200,200),size=(128,128),size_hint=(None,None)))
        return fl



if __name__ == '__main__':
    LowLevelParticleEngineApp().run()
