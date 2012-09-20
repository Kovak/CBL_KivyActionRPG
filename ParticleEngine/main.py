import kivy
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, BooleanProperty, ListProperty, StringProperty, ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.app import App
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.vector import Vector
from kivy.atlas import Atlas
from random import random, randint
import re

class Particle(Widget):
    
    color = ListProperty([0,.8,.7,1.])
    textures = ObjectProperty(None)
    active_frame = NumericProperty(0)

    def __init__(self, **kwargs):
        # remove when there are more ways of calling Particle

        super(Particle,self).__init__(**kwargs)
        self.frames = len(self.textures) if self.textures is not None else 1

        # if self.frames > 1:
        #     Clock.schedule_interval(self.increment_frame,frame_delay)
        # if duration > 0:
        #     anim = Animation(pos = (self.x + dir_vector[0], self.y + dir_vector[1]), duration=duration)
        #     anim.bind(on_complete = self.delete)
        #     anim.start(self)

    def delete(self, instance, value):
        self.parent.remove_widget(self)

    def increment_frame(self, dt):
        if random() < .4:
            return
        if self.active_frame < self.frames - 1: 
            # print self.active_frame
            self.active_frame += 1
            self.color[3] *= 0.8

    def on_touch_down(self,touch):
        return False
    
    def on_touch_move(self,touch):
        return False

    def on_touch_up(self,touch):
        return False

class CBL_DebugPanel(BoxLayout):
    fps = StringProperty(None)

    def update(self, dt):
        self.fps = str(int(Clock.get_fps()))
        Clock.schedule_once(self.update)



class ParticleEmitter(Widget):
    
    scatter_init = NumericProperty(10)
    scatter_end = NumericProperty(30)

    def __init__(self,**kwargs):
        super(ParticleEmitter,self).__init__(**kwargs)

        # create list of textures
        basename = 'VFX_SmokeParticle'
        atlas = Atlas('VFX/smoke_particles.atlas')
        all_keys = atlas.textures.keys()
        wanted_keys = filter(lambda x: x.startswith(basename),all_keys)

        if len(wanted_keys) > 1:
            pattern = re.compile(r'[0-9]+$')
            print wanted_keys
            wanted_keys.sort(key=lambda x: int(pattern.search(x).group()))

        self.texture_list = [atlas[key] for key in wanted_keys]

        Clock.schedule_interval(self.emit_particle, 0.1)

    def on_touch_down(self,touch):
        if self.collide_point(*touch.pos):
            touch.grab(self)

    def on_touch_move(self,touch):
        if touch.grab_current is self:
            self.center = touch.pos

    def emit_particle(self,dt):
        particle_width = 64
        duration = 3.
        frame_delay = 0.1

        p = Particle(textures = self.texture_list,
            frame_delay = frame_delay,
            x = self.x + (self.width - particle_width)/2. + randint(-self.scatter_init, self.scatter_init), 
            y = self.y + (self.height - particle_width)/2. + randint(-self.scatter_init, self.scatter_init), 
            dir_vector = Vector(0 + randint(-self.scatter_end, self.scatter_end),300 + randint(-self.scatter_end, self.scatter_end)),
            duration = duration,
            parent=self, 
            size = (particle_width,particle_width), 
            size_hint = (None, None))
        self.add_widget(p)

class Particle_Warehouse():

    def __init__(self, number_of_particles, parent=None):
        self.parent = parent
        self.particles = []
        for x in range(number_of_particles):
            self.particles.append(Particle(dir_vector = Vector(0,0), duration = 0, size = (0,0), size_hint = (None,None), pos = (0,0)))
            self.parent.add_widget(self.particles[-1])


class ParticleEngineApp(App):
    def build(self):
        # 'atlas://VFX/smoke_particles/VFX_SmokeParticle'
        fl = FloatLayout(pos=(0,0),size=Window.size)
        fl.add_widget(CBL_DebugPanel(pos=(0,0),size=(100,50)))
        pw = Particle_Warehouse(5000, parent = fl)
        return fl


if __name__ == '__main__':
    ParticleEngineApp().run()
