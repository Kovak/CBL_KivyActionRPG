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

class BGMaterial():
    def __init__(self,atlas,material_name,frames):
        self.atlas = atlas
        self.material_name = material_name
        self.frames = frames

class Tile(Widget):
    parent = ObjectProperty(None)

    def __init__(self,basetype,posarray=None,**kwargs):
        if posarray is None:
            self.posarray = [[True,True],[True,True]]
        else:
            self.posarray = posarray

        self.basetype = basetype
        self.update_source_image()

        super(Tile,self).__init__(**kwargs)

    def get_current_frame(self,framecounter):
        return self.source_image + '-' + str(framecounter % self.basetype.frames + 1) if self.basetype.frames > 1 else self.source_image

    def update_source_image(self):
        # sorry this is ugly guys, but it works, it's fast, and it's pretty clear what's going on.
        if self.posarray == [[True,True],[True,True]]:
            position = None
            orientation = None
        elif self.posarray == [[True,False],[False,False]]:
            position = "3"
            orientation = 'Interior'
        elif self.posarray == [[False,True],[False,False]]:
            position = "1"
            orientation = 'Interior'
        elif self.posarray == [[False,False],[True,False]]:
            position = "9"
            orientation = 'Interior'
        elif self.posarray == [[False,False],[False,True]]:
            position = "7"
            orientation = 'Interior'
        elif self.posarray == [[True,True],[False,False]]:
            position = "2"
            orientation = 'Interior'
        elif self.posarray == [[False,False],[True,True]]:
            position = "8"
            orientation = 'Interior'
        elif self.posarray == [[True,False],[True,False]]:
            position = "6"
            orientation = 'Interior'
        elif self.posarray == [[False,True],[False,True]]:
            position = "4"
            orientation = 'Interior'
        elif self.posarray == [[False,True],[True,True]]:
            position = "3"
            orientation = 'Exterior'
        elif self.posarray == [[True,False],[True,True]]:
            position = "1"
            orientation = 'Exterior'
        elif self.posarray == [[True,True],[False,True]]:
            position = "9"
            orientation = 'Exterior'
        elif self.posarray == [[True,True],[True,False]]:
            position = "7"
            orientation = 'Exterior'
        
        if position is None:
            self.source_image = self.basetype.atlas + 'Tile-' + self.basetype.material_name
        else:
            self.source_image = self.basetype.atlas + 'Tile-' + self.basetype.material_name + '-Position' + position + '-' + orientation

class CompositeTile(Widget):
    """This class is not being used right now. It fucked everything up with the positions. Instead, the Screen Object is going to contain an array of lists of Tile objects."""
    active_frame = NumericProperty(0)

    def __init__(self,basetypes,posarrays = None,**kwargs):
        if posarrays is None:
            posarrays = [None for b in basetypes]

        super(CompositeTile,self).__init__(**kwargs)

        for idx,basetype in enumerate(basetypes):
            t = Tile(basetype,posarray = posarrays[idx],parent=self,size=self.size,size_hint=(None,None))
            self.add_widget(t)





class OldTile(Widget):
    source_image = StringProperty(None)
    atlas = StringProperty(None)
    interior = StringProperty(None,allownone = True)
    exterior = StringProperty(None,allownone = True)
    position_code = NumericProperty(None)
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

        super(OldTile,self).__init__(**kwargs)

    def test(self,active_frame):
        return self.source_image + '-' + str(active_frame % self.frames + 1) if self.is_animated else self.source_image

    def update_source_text(self):
        if self.interior == self.exterior or self.exterior is None:
            self.source_image = self.atlas + 'Tile-' + self.interior
        else:
            self.source_image = self.atlas + 'Tile-' + self.interior + '-' + self.exterior + '-Position' + str(int(self.position_code))

    def on_touch_down(self,touch):
        if not self.collide_point(touch.x, touch.y):
            return False
        
        # get new tile characteristics from parent class, which is aware of surrounding tiles.
        # self.atlas, self.interior, self.position_code, self.exterior, self.frames = self.parent.get_new_tiles(self)
        self.parent.get_new_tiles(self)
        return True

    def on_touch_move(self,touch):
        if not self.collide_point(touch.x, touch.y):
            return False
        
        # get new tile characteristics from parent class, which is aware of surrounding tiles.
        # self.atlas, self.interior, self.position_code, self.exterior, self.frames = self.parent.get_new_tiles(self)
        self.parent.get_new_tiles(self)
        return True

class Screen(FloatLayout):
    rows = NumericProperty(6)
    cols = NumericProperty(9)
    tiles = ObjectProperty(None)
    active_frame = NumericProperty(0)

    def __init__(self,parent,fill=None,**kwargs):
        # get reference to parent (ScreenEditor) and grab atlas/tilenames
        self.parent = parent
        self.atlas = parent.atlas
        self.tile_names = parent.tile_names
        self.tile_frame_dict = parent.tile_frame_dict

        


        super(Screen,self).__init__(**kwargs)

        ###This is super fucked up because width appears to be 1, even though it explicitly gets set to the right value. Looks like we need schedule_once to fix this; but I don't know why we didn't need it when using a GridLayout
        self.tile_width = self.width/self.cols

        ### it works fine if you set it to a constant afterward.
        self.tile_width = 75
        print "tile width", self.pos, self.size

        #start the animation counter
        Clock.schedule_interval(self.increment_active_frame, 1.0)
        
        #fill must always be provided until there is a load system
        assert fill is not None

        grass = BGMaterial(parent.atlas,'Grass',1)
        sand = BGMaterial(parent.atlas,'Sand',1)

        if fill is not None:
            # self.tiles = [Tile(self.atlas,
            #     fill,
            #     fill,
            #     5,
            #     self.tile_frame_dict[fill],
            #     self,
            #     (i,j),
            #     size=(self.width/self.cols,self.width/self.cols),
            #     size_hint=(None,None),
            #     ) for i in xrange(int(self.rows)) for j in xrange(int(self.cols))]
            self.tiles = [Tile(grass,parent=self,size=(self.tile_width,self.tile_width), x = self.x + self.tile_width*j,y=self.y+self.tile_width*i,size_hint = (None,None)) for i in xrange(int(self.rows)) for j in xrange(int(self.cols))]
            for ctile in self.tiles:
                self.add_widget(ctile)


    def increment_active_frame(self, dt):
        self.active_frame += 1

    def get_new_tiles(self,tile):
        new_base_type = self.parent.current_tile_type

        all_surrounding_tiles = self.get_surrounding_tiles(*tile.gridpos)

        position_matrix = [[7,8,9],[4,5,6],[1,2,3]]
        position_addition_table = [
        [1,2,2,4,5,-7,4,-3,5],
        [2,2,2,-9,5,-7,-9,5,-7],
        [2,2,3,-9,5,6,5,-1,6],
        [4,-9,-9,4,5,5,4,-3,-3],
        [5,5,5,5,5,5,5,5,5],
        [-7,-7,6,5,5,6,-1,-1,6],
        [4,-7,5,4,5,-1,7,8,8],
        [-3,5,-1,-3,5,-1,8,8,8],
        [5,-7,6,-3,5,6,8,8,9]
        ]

        for r,row in enumerate(position_matrix):
            for c,position_code in enumerate(row):
                active_tile = all_surrounding_tiles[r][c]

                if active_tile is None:
                    continue

                old_interior = active_tile.interior
                old_exterior = active_tile.exterior
                new_interior = new_base_type
                old_position = active_tile.position_code
                new_position = position_code

                # if it's an "inverse" tile, change it back to a normal tile before processing

                # if old_exterior == new_interior and old_interior != new_interior:
                #     active_tile.exterior = active_tile.interior = old_exterior = old_interior
                #     active_tile.position_code = old_position = 5
                #     print "Caught one!"



                if old_interior == new_interior:

                    sum_position = position_addition_table[old_position-1][new_position-1]

                    if sum_position == 5:
                        active_tile.interior = active_tile.exterior = new_interior
                        active_tile.position_code = 5
                    else:

                        if sum_position < 0:
                            active_tile.interior = old_exterior
                            active_tile.exterior = new_interior
                        else:
                            active_tile.interior = new_interior
                            # unnecessary but just to show what's going on
                            # active_tile.exterior = old_exterior

                        active_tile.position_code = abs(sum_position)
                else:
                    if new_position == 5:
                        active_tile.interior = active_tile.exterior = new_interior
                    else:
                        active_tile.exterior = old_exterior
                        active_tile.interior = new_interior
                    active_tile.position_code = new_position


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
            fill=tile_names[0],
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

class ScreenEditorWidget(Widget):
    def __init__(self):
        super(ScreenEditorWidget,self).__init__()
        mainwidget = ScreenEditor(
            'atlas://ArtAssets/TileSets/Tileset-SeaGrass_Forest_128/',
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