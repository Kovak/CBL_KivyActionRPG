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
from functools import partial
import re

class Particle(InstructionGroup):
    refresh_time = .05
    frame = 0

    def __init__(self, initial_params, param_changes, parent, draworder_var, **kwargs):
        # these parameters are necessary for Rectangle
        super(Particle,self).__init__()
        self.rect = Rectangle(pos=(initial_params['x'],initial_params['y']),size=(initial_params['width'],initial_params['height']),texture=initial_params['texture_list'][0])
        self.add(self.rect)
        print 'rectangle index:', self.indexof(self.rect)
        self.draw_order = draworder_var
        self.parent = parent
        self.dx = self.refresh_time * initial_params['velocity_x']
        self.dy = self.refresh_time * initial_params['velocity_y']
        self.width_gen = (x for x in param_changes['width'])
        self.color_a_gen = (x for x in param_changes['color_a'])
        #I used the conversion from 255 to 1.0 scale here so that we can format the input in such a way as to
        #make sense to the artists who will most likely be using these tools
        #I guess we could make the conversion at another time also, but it's kinda nice because it works with
        #the current way the scatter works
        #self.color_code = (initial_params['color_r']/255., initial_params['color_g']/255., initial_params['color_b']/255., initial_params['color_a']/255.)
        self.color_code = (random(), random(), random(), random())
        self.update_pos(None)
        self.update_width(None)
        self.color = Color(*self.color_code)
        self.insert(0, self.color)
        print 'color index:', self.indexof(self.color)
        self.color_index = self.indexof(self.color)
        Clock.schedule_once(self.update_color,.5)


    def update_pos(self,dt):
        self.rect.pos = (self.rect.pos[0] + self.dx, self.rect.pos[1] + self.dy)
        Clock.schedule_once(self.update_pos,self.refresh_time)

    def update_width(self,dt):
        try:
            val, time = self.width_gen.next()
        except:
            return False
        self.size = (self.rect.size[0]+val, self.rect.size[1])
        Clock.schedule_once(self.update_width,time)

        

    def update_color(self, dt):
        try:
            val, time = self.color_a_gen.next()
        except:
            return False
        self.color_code = (self.color_code[0], self.color_code[1], self.color_code[2], val/255. )
        print "parent removing color at index,", self.indexof(self.color)
        index = self.indexof(self.color)
        self.remove(self.color)
        newcolor = Color(*self.color_code)
        self.color = newcolor
        self.insert(index , self.color)
        print 'inserted new color at index', self.indexof(self.color)
        Clock.schedule_once(self.update_color,time)


class ParticleGroup(InstructionGroup):
    
    def __init__(self, initial_params, param_changes = None, scatterdict = None, batch_size = 100, **kwargs):
        super(ParticleGroup,self).__init__()
        if scatterdict is None: scatterdict = {}
        for x in xrange(batch_size):
            # r = Particle(initial_params, None)
            # self.add(r)
            draworder_var = x
            p = Particle(self.randomize_params(initial_params,scatterdict),param_changes,self, draworder_var)
            


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

    def __init__(self, image_basename, image_location, emmitter_type = 'smoke', particle_groups = 2, pos = (400, 200), **kwargs):
        super(ParticleEmitter,self).__init__()
        assert emmitter_type in ['smoke']

        if emmitter_type == 'smoke':
            initial_params = {'velocity_x': 0,
                'velocity_y': 50,
                'texture_list': self.get_texture_list('VFX_Smoke','VFX/VFX_Set1_64.atlas'),
                'x': self.x,
                'y': self.y,
                'width': 64,
                'height': 64,
                'color_r': 205,
                'color_g': 205,
                'color_b': 205,
                'color_a': 255,}
            param_changes = {'width': [(20,.5),(20,.5),(20,.5),(40,.5)], 'color_a': [(255, 2.), (200, 2.), (100, 2.), (0, 2.)]}
            scatterdict = {'width': 0, 'velocity_x': 5, 'x': 50, 'y': 50, 'color_r': 50, 'color_g': 50, 'color_b': 50}
        for x in xrange(particle_groups): 
            self.emit_particle_group(initial_params, param_changes, scatterdict)

    def emit_particle_group(self, initial_params, param_changes, scatterdict):
        with self.canvas:
            p = ParticleGroup(initial_params, param_changes=param_changes, scatterdict=scatterdict)

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

    def update(self, dt):
        self.fps = str(int(Clock.get_fps()))
        Clock.schedule_once(self.update)

    def on_touch_down(self,touch):
        if self.collide_point(*touch.pos):
            self.update(0)

class LowLevelParticleEngineApp(App):
    def build(self):
        # 'atlas://VFX/smoke_particles/VFX_SmokeParticle'
        fl = FloatLayout(pos=(0,0),size=Window.size)
        db_panel = CBL_DebugPanel(pos=(0,0),size=(100,50),size_hint = (None,None))
        fl.add_widget(db_panel)
        fl.add_widget(ParticleEmitter(image_basename = 'VFX-Explosion', image_location = 'VFX/VFX_Set1_64.atlas', debug=db_panel, pos=(200,200),size=(128,128),size_hint=(None,None)))
        return fl



if __name__ == '__main__':
    LowLevelParticleEngineApp().run()
