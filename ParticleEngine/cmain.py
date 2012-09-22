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
from random import random, randint
import re

class Particle(InstructionGroup):
    counter = 0

    def __init__(self,pos=None, size = None, parent=None, texture=None,**kwargs):
        super(Particle,self).__init__()
        
        self.parent = parent
        self.texture = texture
        self.rect = Rectangle(pos=pos, size=size, texture = self.texture)
        self.color_code = (random(), random(), random(), random())
        self.color = Color(*self.color_code)
        self.update_color(0)
        self.update_pos(0)
        

    def update_pos(self,dt):
        self.rect.pos = (self.rect.pos[0] + randint(-5,5), self.rect.pos[1] + randint(-5,5))
        Clock.schedule_once(self.update_pos,.05)
        self.counter += 1

    def update_color(self,dt):

        self.color_code = [x * .99 for x in self.color_code[:2]]+[1.]+[.99*self.color_code[3]]
        newcolor = Color(*self.color_code)
        self.remove(self.color)
        self.color = newcolor
        self.insert(0, self.color)



        Clock.schedule_once(self.update_color,.05)





class ParticleEmitter(Widget):

    def __init__(self,image_basename,image_location,debug=None,**kwargs):
        super(ParticleEmitter,self).__init__(**kwargs)

        self.debug = debug
        self.rectx = self.x + self.width/2.
        self.recty = self.y + self.height/2.


        basename = image_basename
        atlas = Atlas(image_location)
        all_keys = atlas.textures.keys()
        wanted_keys = filter(lambda x: x.startswith(basename),all_keys)

        if len(wanted_keys) > 1:
            pattern = re.compile(r'[0-9]+$')
            print wanted_keys
            wanted_keys.sort(key=lambda x: int(pattern.search(x).group()))

        self.texture_list = [atlas[key] for key in wanted_keys]
        
        if self.debug is not None: self.debug.particles = 50
        for d in xrange(50):
            self.draw_new_particle(0)



    def remove(self,rect):
        self.canvas.remove(rect)
        self.debug.particles -= 1

    def draw_new_particle(self,dt):
        with self.canvas:
            rect = Particle(pos=(self.rectx,self.recty), size=(64,64), texture=self.texture_list[6], parent = self)
        rect.update_pos(None)



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
