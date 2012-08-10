import kivy
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, BooleanProperty, ListProperty, StringProperty, ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.atlas import Atlas
from kivy.app import App
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.factory import Factory


class CBL_Tile(Widget):
    source_image = StringProperty(None)
    is_animated = BooleanProperty(False)
    has_collision = BooleanProperty(False)
    collision_pos = ListProperty(None)
    collision_size = ListProperty(None)


    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y) and self.parent.parent.current_tile_type != None:
            if self.parent.parent.current_tile_type == 'atlas://ArtAssets/TileSets/SeaGrass_Forest_Tileset_128/Tile-Water-':
                self.is_animated = True
                print 'setting is animated'
            else:
                self.is_animated = False
            self.source_image = self.parent.parent.current_tile_type
    def on_touch_move(self, touch):
        if self.collide_point(touch.x, touch.y) and self.parent.parent.current_tile_type != None:
            if self.parent.parent.current_tile_type == 'atlas://ArtAssets/TileSets/SeaGrass_Forest_Tileset_128/Tile-Water-':
                self.is_animated = True
                print 'setting is animated'
            else:
                self.is_animated = False
            self.source_image = self.parent.parent.current_tile_type
            

class CBL_Level(GridLayout):
    tiles = ListProperty(None)
    anim_frame = NumericProperty(1)

    def on_anim_frame(self, instance, value):
        for each in self.tiles:
            if each.is_animated:
                each.anim_frame = self.anim_frame

    def init_all_grass(self):
        self.tiles = []
        print self.tiles
        x_it = 0
        while x_it < self.cols * self.rows:
            self.tiles.append(CBL_Tile(source_image = 'atlas://ArtAssets/TileSets/SeaGrass_Forest_Tileset_128/Tile-Grass', parent = self.parent))
            x_it += 1

    def add_tiles(self):
        self.clear_widgets()
        for each in self.tiles:
            self.add_widget(each)

    def update(self, dt):   
        wasfour = False
        if self.anim_frame == 4:
            self.anim_frame = 1
            wasfour = True
        if self.anim_frame < 4 and not wasfour:
            self.anim_frame += 1 
        Clock.schedule_once(self.update, 1.0)


class CBL_Edit_Level_Screen(FloatLayout):
    button_width = NumericProperty(80)
    button_height = NumericProperty(80)
    spacing = NumericProperty(10)
    level = ObjectProperty(None)
    tile_types = ['atlas://ArtAssets/TileSets/SeaGrass_Forest_Tileset_128/Tile-Grass', 'atlas://ArtAssets/TileSets/SeaGrass_Forest_Tileset_128/Tile-Dirt', 'atlas://ArtAssets/TileSets/SeaGrass_Forest_Tileset_128/Tile-Sand', 'atlas://ArtAssets/TileSets/SeaGrass_Forest_Tileset_128/Tile-Water-']
    current_tile_type = StringProperty(None)

    def on_touch_down(self, touch):
        super(CBL_Edit_Level_Screen, self).on_touch_down(touch)


    def button_callback(self, value):
        print 'button called', value.text
        if value.text == 'Init Grass':
            print self.size
            print 'level size', self.level.size
            print 'level pos', self.level.pos
            print self.button_width
            self.level.init_all_grass()
            self.level.add_tiles()
            pass
        if value.text == 'Grass':
            self.current_tile_type = self.tile_types[0]
            print self.current_tile_type
        if value.text == 'Dirt':
            self.current_tile_type = self.tile_types[1]
            print self.current_tile_type
        if value.text == 'Sand':
            self.current_tile_type = self.tile_types[2]
            print self.current_tile_type
        if value.text == 'Water':
            self.current_tile_type = self.tile_types[3]
            print self.current_tile_type
       
    
Factory.register('CBL_Edit_Level_Screen', CBL_Edit_Level_Screen)
Factory.register('CBL_Level', CBL_Level)

class CBL_Levels_Test(Widget):
    def __init__(self):
        Widget.__init__(self)
        mainwidget = CBL_Edit_Level_Screen(pos = (10, 10), size = (Window.width-20, Window.height - 20))
        self.add_widget(mainwidget)
        Clock.schedule_once(mainwidget.level.update, .5)

    def update(self, dt):
        pass
        
class CBL_LevelsApp(App):
    def build(self):
        game = CBL_Levels_Test()
        Clock.schedule_interval(game.update, 1.0/60.0)
        return game


if __name__ == '__main__':
    CBL_LevelsApp().run()