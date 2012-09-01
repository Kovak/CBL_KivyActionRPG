import kivy
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, BooleanProperty, ListProperty, StringProperty, ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.atlas import Atlas
from kivy.app import App
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.factory import Factory

class Tile(Widget):
    source_image = StringProperty(None)
    atlas = StringProperty(None)
    interior = StringProperty(None,allownone = True)
    exterior = StringProperty(None,allownone = True)
    position_code = StringProperty(None,allownone = True)
    tile_type = StringProperty(None)
    frames = NumericProperty(1)
    is_animated = BooleanProperty(False)
    parent = ObjectProperty(None)

    def __init__(self, atlas, interior, exterior, position_code, frames, parent, gridpos, **kwargs):
        
        # guys is this actually necessary? i've been doing it in all my python code since I learned python a year ago, but I feel like there's gotta be a better way.
        self.atlas = atlas
        self.interior = interior
        self.exterior = exterior
        self.position_code = position_code
        self.frames = frames

        if frames == 1:
            self.is_animated = False
        else:
            self.is_animated = True

        self.parent = parent
        self.gridpos = gridpos

        self.update_source_text()

        super(Tile,self).__init__(**kwargs)

    def test(self,active_frame):
        return self.source_image + '-' + str(active_frame % self.frames + 1) if self.is_animated else self.source_image

    def update_source_text(self):
        if self.interior == self.exterior or self.exterior is None:
            self.source_image = self.atlas + 'Tile-' + self.interior
        else:
            self.source_image = self.atlas + 'Tile-' + self.interior + '-' + self.exterior + '-Position' + self.position_code


    def on_touch_down(self,touch):
        if not self.collide_point(touch.x, touch.y):
            return False
        
        # get new tile characteristics from parent class, which is aware of surrounding tiles.
        # self.atlas, self.interior, self.position_code, self.exterior, self.frames = self.parent.get_new_tiles(self)
        self.parent.get_new_tiles(self)
        return True

class Screen(GridLayout):
    rows = NumericProperty(12)
    cols = NumericProperty(18)
    tiles = ObjectProperty(None)
    active_frame = NumericProperty(0)

    def __init__(self,parent,fill=None,**kwargs):
        # get reference to parent (ScreenEditor) and grab atlas/tilenames
        self.parent = parent
        self.atlas = parent.atlas
        self.tile_names = parent.tile_names
        self.tile_frame_dict = parent.tile_frame_dict

        super(Screen,self).__init__(**kwargs)

        #start the animation counter
        Clock.schedule_interval(self.increment_active_frame, 0.5)
        
        #fill must always be provided until there is a load system
        assert fill is not None

        if fill is not None:
            self.tiles = [Tile(self.atlas,
                fill,
                None,
                None,
                self.tile_frame_dict[fill],
                self,
                (i,j),
                size=(self.width/self.cols,self.width/self.cols),
                size_hint=(None,None),
                ) for i in xrange(int(self.rows)) for j in xrange(int(self.cols))]
            for tile in self.tiles:
                self.add_widget(tile)


    def increment_active_frame(self, dt):
        self.active_frame += 1

    def get_new_tiles(self,tile):
        print "current position:", tile.gridpos
        new_base_type = self.parent.current_tile_type

        print "new tile will have base type", new_base_type
        all_surrounding_tiles = self.get_surrounding_tiles(*tile.gridpos)

        position_matrix = [[7,8,9],[4,5,6],[1,2,3]]
        for r,row in enumerate(position_matrix):
            for c,position_code in enumerate(row):
                active_tile = all_surrounding_tiles[r][c]
                old_interior = active_tile.interior
                if position_matrix[r][c] == 5:
                    active_tile.interior = new_base_type
                    active_tile.exterior = None
                    active_tile.position_code = None
                    active_tile.frames = self.tile_frame_dict[new_base_type]
                    active_tile.is_animated = False if active_tile.frames == 1 else True
                    active_tile.update_source_text()
                    
                else:
                    active_tile.interior = new_base_type
                    active_tile.position_code = str(position_matrix[r][c])
                    active_tile.exterior = old_interior
                    active_tile.frames = max(self.tile_frame_dict[active_tile.exterior],self.tile_frame_dict[active_tile.interior])
                    active_tile.is_animated = False if active_tile.frames == 1 else True
                    active_tile.update_source_text()

    def get_surrounding_tiles(self,col,row):
        tiles = [[None,None,None],[None,None,None],[None,None,None]]
        for r_idx,r in enumerate([row - 1, row, row + 1]):
            for c_idx,c in enumerate([col - 1, col, col + 1]):
                if r >= 0 and c >= 0 and r < self.cols and c < self.rows:
                    tiles[c_idx][r_idx] = self.tiles[self.cols*c + r]
                else:
                    pass

        return tiles


class ScreenEditor(FloatLayout):

    button_width = NumericProperty(80)
    button_height = NumericProperty(80)
    spacing = NumericProperty(10)
    level = ObjectProperty(None)

    current_tile_type = StringProperty(None)
    current_tile_frames = NumericProperty(1)

    def __init__(self, atlas, tile_names, tile_frame_dict, **kwargs):
        self.atlas = atlas
        self.tile_names = tile_names
        self.tile_frame_dict = tile_frame_dict
        self.current_tile_type = tile_names[0]

        super(ScreenEditor,self).__init__(**kwargs)
        
        self.draw_buttons(tile_names)

        self.screen = Screen(self,
            fill=tile_names[2],
            x = self.x + self.button_width + 2*self.spacing,
            y = self.y + self.spacing,
            width = self.width - self.button_width - 3*self.spacing,
            height = self.height - 2*self.spacing,
            spacing = 0,
            padding = 0,
            )

        self.add_widget(self.screen)


    def draw_buttons(self,buttons):

        bl = BoxLayout(
            orientation = 'vertical',
            x = self.x + self.spacing,
            y = self.top - len(buttons)*(self.spacing + self.button_height) - self.spacing, 
            spacing = self.spacing,
            size_hint = (None,None), 
            height = len(buttons)*(self.spacing + self.button_height) + self.spacing,
            width = self.button_width + 2*self.spacing,
            )


        for button in buttons:
            b = Button(text=button, size_hint = (None, None), width=self.button_width, height = self.button_height)
            b.bind(on_release = self.button_callback)
            bl.add_widget(b)

        self.add_widget(bl)

    def button_callback(self, instance):

        if instance.text in self.tile_names:
            self.current_tile_type = instance.text
            print "Changing active tile to %s" % (instance.text,)


class ScreenEditorWidget(Widget):
    def __init__(self):
        super(ScreenEditorWidget,self).__init__()
        mainwidget = ScreenEditor(
            'atlas://ArtAssets/TileSets/SeaGrass_Forest_Tileset_128/',
            ['Grass','Sand','Water','Dirt'], 
            {'Grass': 1,'Sand': 1,'Water': 4, 'Dirt': 1},
            pos = (0, 0), 
            size = (Window.width, Window.height))
        self.add_widget(mainwidget)


class ScreenEditorApp(App):
    def build(self):
        main = ScreenEditorWidget()
        #Clock.schedule_interval(main.update, 1.0/60.0)
        return main


if __name__ == '__main__':
    ScreenEditorApp().run()