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
    
    color = ListProperty([1.,1.,1.,1.])
    textures = ObjectProperty(None, allownone = True)
    active_frame = NumericProperty(0)
    duration = NumericProperty(0)
    dir_vector = ListProperty([])
    frame_delay = NumericProperty(0)
    warehouse = ObjectProperty(None)

    def __init__(self, **kwargs):
        # remove when there are more ways of calling Particle

        super(Particle,self).__init__(**kwargs)


    def animate_particle(self):

        self.frames = len(self.textures) if self.textures is not None else 1
        if self.frames > 1:
            # Clock.schedule_interval(self.increment_frame,self.frame_delay)
            Clock.schedule_once(self.increment_frame,self.frame_delay)
        if self.duration > 0:
            anim = Animation(pos = (self.x + self.dir_vector[0], self.y + self.dir_vector[1]), duration=self.duration)
            anim.bind(on_complete = self.remove)
            anim.start(self)
        

    def remove(self, instance, value):
        self.reset()
        self.warehouse.get_particle(self)

    def increment_frame(self, dt):        
        if self.active_frame < self.frames - 1: 
            self.active_frame += 1
            self.color[3] *= 0.8
            Clock.schedule_once(self.increment_frame,self.frame_delay)
        
    def reset(self):
        self.dir_vector = Vector(0,0)
        self.duration = 0 
        self.size = (0,0)
        self.pos = (0,0)
        self.frames = 0
        self.active_frame = 0
        self.textures = None
        self.color = [1.,1.,1.,1.]

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

    def __init__(self,image_folder,image_location,warehouse=None,**kwargs):
        super(ParticleEmitter,self).__init__(**kwargs)
        self.warehouse = warehouse
        self.warehouse.register_emitter(self)


        # create list of textures
        # basename = 'VFX_SmokeParticle'
        # atlas = Atlas('VFX/smoke_particles.atlas')
        basename = image_folder
        atlas = Atlas(image_location)
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
        particle_width = 32
        duration = 3.
        frame_delay = duration/len(self.texture_list)*.9

        particle = self.request_particle_from_warehouse()
        if particle is not None:
            x = self.x + (self.width - particle_width)/2. + randint(-self.scatter_init, self.scatter_init) 
            y = self.y + (self.height - particle_width)/2. + randint(-self.scatter_init, self.scatter_init)
            particle.warehouse = self.warehouse 
            particle.pos = self.pos
            particle.size = (particle_width, particle_width)
            particle.textures = self.texture_list
            particle.frame_delay = frame_delay
            particle.duration = duration
            particle.dir_vector = Vector(0 + randint(-self.scatter_end, self.scatter_end),300 + randint(-self.scatter_end, self.scatter_end))
            particle.animate_particle()



    def request_particle_from_warehouse(self):
        return self.warehouse.send_particle_to_emitter()

    def direct_particle(self):
        pass

class Particle_Warehouse():

    def __init__(self, number_of_particles, parent=None):
        self.parent = parent
        self.particles = []
        for x in range(number_of_particles):
            self.particles.append(Particle(dir_vector = Vector(0,0), duration = 0, size = (0,0), size_hint = (None,None), pos = (0,0)))
            self.parent.add_widget(self.particles[-1])

        self.emitters =[]


    def register_emitter(self,emitter):
        self.emitters.append(emitter)
        self.balance_load()

    def send_particle_to_emitter(self):
        try:
            return self.particles.pop()
        except IndexError:
            return None
        

    def get_particle(self, particle):
        self.particles.append(particle)

    def balance_load(self):
        number_of_emitters = len(self.emitters)
        particles_for_each_emitter = len(self.particles)/number_of_emitters
        # send_particle_to_emitter(particles)
        pass


class ParticleEngineApp(App):
    def build(self):
        # 'atlas://VFX/smoke_particles/VFX_SmokeParticle'
        fl = FloatLayout(pos=(0,0),size=Window.size)
        fl.add_widget(CBL_DebugPanel(pos=(0,0),size=(100,50)))
        pw = Particle_Warehouse(200, parent = fl)
        e = ParticleEmitter(image_folder = 'VFX_SmokeParticle', image_location = 'VFX/VFX-Set1_32.atlas', warehouse=pw, pos = (200,200))
        e2 = ParticleEmitter(image_folder = 'VFX_Explosion', image_location = 'VFX/VFX-Set1_32.atlas', warehouse=pw, pos = (600,200))
        #e3 = ParticleEmitter(image_folder = 'VFX_Explosion', image_location = 'VFX/VFX-Set1_32.atlas', warehouse=pw, pos = (400,200))
        return fl
        return fl


if __name__ == '__main__':
    ParticleEngineApp().run()
