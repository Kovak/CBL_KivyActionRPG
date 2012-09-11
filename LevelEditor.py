import kivy
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, BooleanProperty, ListProperty, StringProperty, ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.atlas import Atlas
from kivy.app import App
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.factory import Factory
import time

class WorldObject(Widget):
    def __init__(self,atlas,name,frames):
        self.atlas = atlas
        self.name = name
        self.frames = frames

        try:
            self.icon = Atlas(atlas)[name]
            self.icon_str = str('atlas://' + atlas + '/'+ name)
        except KeyError:
            self.icon = Atlas(atlas)[name + "-1"]
            self.icon_str = str('atlas://' + atlas + '/'+ name + '-1')

    def __str__(self):
        return self.name

class Subtile():
    def __init__(self,atlas,material_name,position,frames):
        self.atlas = atlas
        self.material_name = material_name
        self.position = [[True,True],[True,True]] if position is None else position
        self.frames = frames

        # Caution: this parses the atlas URL and may or may not be compatible with windows. I do not know. This code ought to be refactored to be the same as WorldObject anyway
        atlas_stripped = atlas[8:].rpartition('/')[0]+'.atlas'

        try:
            self.icon = Atlas(atlas_stripped)['Tile-' + material_name]
            self.icon_str = str(atlas + 'Tile-' + material_name)
        except KeyError:
            self.icon = Atlas(atlas_stripped)['Tile-' + material_name + "-1"]
            self.icon_str = str(atlas + 'Tile-' + material_name + '-1')        

    def __str__(self):
        return self.material_name + ': ' + str(self.position)


class Tile(Widget):
    layers = NumericProperty(0)
    update_now = BooleanProperty(False)

    def __init__(self,typelist,gridpos=None,**kwargs):
        self.typelist = typelist
        self.gridpos = gridpos
        self.layers = len(typelist)
        self.source_images = []
        self.source_frames = []
        self.update_source_images()

        super(Tile,self).__init__(**kwargs)

    def on_touch_down(self,touch):
        if not self.collide_point(touch.x, touch.y):
            return False

        # get new tile characteristics from parent class, which is aware of surrounding tiles.
        # self.atlas, self.interior, self.position_code, self.exterior, self.frames = self.parent.tile_touch(self)
        self.parent.tile_touch(self)
        return True

    def on_touch_move(self,touch):
        if not self.collide_point(touch.x, touch.y):
            return False

        # get new tile characteristics from parent class, which is aware of surrounding tiles.
        # self.atlas, self.interior, self.position_code, self.exterior, self.frames = self.parent.tile_touch(self)
        self.parent.tile_touch(self)
        return True


    def update_source_images(self):
         # sorry this is ugly guys, but it works, it's fast, and it's pretty clear what's going on.
        for idx,t in enumerate(self.typelist):
            if t.position == [[True,True],[True,True]]:
                position = None
                orientation = None
            elif t.position == [[True,False],[False,False]]:
                position = "3"
                orientation = 'Interior'
            elif t.position == [[False,True],[False,False]]:
                position = "1"
                orientation = 'Interior'
            elif t.position == [[False,False],[True,False]]:
                position = "9"
                orientation = 'Interior'
            elif t.position == [[False,False],[False,True]]:
                position = "7"
                orientation = 'Interior'
            elif t.position == [[True,True],[False,False]]:
                position = "2"
                orientation = 'Interior'
            elif t.position == [[False,False],[True,True]]:
                position = "8"
                orientation = 'Interior'
            elif t.position == [[True,False],[True,False]]:
                position = "6"
                orientation = 'Interior'
            elif t.position == [[False,True],[False,True]]:
                position = "4"
                orientation = 'Interior'
            elif t.position == [[False,True],[True,True]]:
                position = "3"
                orientation = 'Exterior'
            elif t.position == [[True,False],[True,True]]:
                position = "1"
                orientation = 'Exterior'
            elif t.position == [[True,True],[False,True]]:
                position = "9"
                orientation = 'Exterior'
            elif t.position == [[True,True],[True,False]]:
                position = "7"
                orientation = 'Exterior'
            
            if position is None:
                new_source_image = t.atlas + 'Tile-' + t.material_name
            else:
                new_source_image = t.atlas + 'Tile-' + t.material_name + '-Position' + position + '-' + orientation

            try:
                self.source_images[idx] = new_source_image
                self.source_frames[idx] = t.frames
            except IndexError:
                self.source_images.append(new_source_image)
                self.source_frames.append(t.frames)

            self.update_now = not self.update_now

        self.layers = len(self.typelist)

    def get_current_frame(self,layer,framecounter):
        try:
            return self.source_images[layer] + '-' + str(framecounter % self.source_frames[layer] + 1) if self.source_frames[layer] > 1 else self.source_images[layer]
        except:
            return ""

    def add_segment(self,tile_type):
        try:
            existing_subtile_idx = [x.material_name for x in self.typelist].index(tile_type.material_name)
        except ValueError:
            existing_subtile_idx = None

        if existing_subtile_idx is not None:
            o = self.typelist[existing_subtile_idx].position
            n = tile_type.position

            print "This is tile",self.gridpos
            print "Adding subtile", tile_type.material_name,", old position was ",o,"new position is",n

            new_position = [[o[0][0] or n[0][0], o[0][1] or n[0][1]],
                [o[1][0] or n[1][0], o[1][1] or n[1][1]]]

            self.typelist[existing_subtile_idx].position = new_position

            # now send to top
            self.typelist[existing_subtile_idx], self.typelist[-1] = self.typelist[-1], self.typelist[existing_subtile_idx]
        else:
            print "This is tile",self.gridpos
            print "Adding subtile", tile_type.material_name, "at position",tile_type.position
            self.typelist.append(tile_type)

        # if the top of the typelist is a full tile, remove the stuff under it
        if self.typelist[-1].position == [[True, True],[True,True]]:
            print "adjusting typelist: old is",self.typelist
            self.typelist = [self.typelist[-1]]

        self.update_source_images()
        print "layers:",self.layers


class Screen(FloatLayout):
    rows = NumericProperty(6)
    cols = NumericProperty(9)
    tiles = ObjectProperty(None)
    active_frame = NumericProperty(0)
    parent = ObjectProperty(None)

    def __init__(self,tileset,fill=None,**kwargs):
        # get reference to parent (ScreenEditor) and grab atlas/tilenames
        # self.parent = parent
        # self.atlas = parent.atlas
        # self.tile_names = parent.tile_names
        # self.tile_frame_dict = parent.tile_frame_dict

        self.tileset = tileset

        


        super(Screen,self).__init__(**kwargs)

        ###This is super fucked up because width appears to be 1, even though it explicitly gets set to the right value. Looks like we need schedule_once to fix this; but I don't know why we didn't need it when using a GridLayout
        self.tile_width = self.width/self.cols

        ### it works fine if you set it to a constant afterward.
        self.tile_width = 77

        #start the animation counter
        Clock.schedule_interval(self.increment_active_frame, 1.0)
        
        #fill must always be provided until there is a load system
        assert fill is not None

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
            self.tiles = [Tile([self.tileset[0]],parent=self,size=(self.tile_width,self.tile_width), x = self.x + self.tile_width*j,y=self.y+self.tile_width*i,size_hint = (None,None),gridpos = (i,j)) for i in xrange(int(self.rows)) for j in xrange(int(self.cols))]
            for ctile in self.tiles:
                self.add_widget(ctile)


    def increment_active_frame(self, dt):
        self.active_frame += 1

    def tile_touch(self,tile):
        new_base_type = self.parent.current_tile_type
        all_surrounding_tiles = self.get_surrounding_tiles(*tile.gridpos)

        position_matrix = [
            [[[False,True],[False,False]],[[True,True],[False,False]],[[True,False],[False,False]]],
            [[[False,True],[False,True]],[[True,True],[True,True]],[[True,False],[True,False]]],
            [[[False,False],[False,True]],[[False,False],[True,True]],[[False,False],[True,False]]]]

        for r,row in enumerate(position_matrix):
            for c,position in enumerate(row):
                active_tile = all_surrounding_tiles[r][c]

                if active_tile is None:
                    continue

                active_tile.add_segment(Subtile(new_base_type.atlas,new_base_type.material_name,position,new_base_type.frames))

    def tile_touch_OBSELETE(self,tile):
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

    def __init__(self, tileset, objectset, **kwargs):
        self.tileset = tileset
        self.current_tile_type = self.tileset[0]

        super(ScreenEditor,self).__init__(**kwargs)
        
        self.draw_buttons(tileset,objectset)

        self.screen = Screen(
            self.tileset,
            parent = self,
            fill = self.current_tile_type,
            x = self.x + self.button_width + 2*self.spacing,
            y = self.y + self.spacing,
            width = self.width - self.button_width - 3*self.spacing,
            height = self.height - 2*self.spacing,
            spacing = 0,
            padding = 0,
            )


        self.add_widget(self.screen)


    def draw_buttons(self,buttons,objects):

        bl = BoxLayout(
            orientation = 'vertical',
            spacing = self.spacing,
            size_hint_y = None, 
            height = len(buttons+objects)*(self.spacing + self.button_height) + self.spacing,
            )


        for t in buttons:
            b = Button(text="", id = t.material_name, background_normal = t.icon_str, background_down = t.icon_str, size_hint_y = None, height = self.button_height)
            b.bind(on_release = self.button_callback)
            bl.add_widget(b)

        for o in objects:
            b = Button(text="", id = o.name, background_down = o.icon_str, background_normal = o.icon_str, size_hint_y = None, height = self.button_height)
            b.bind(on_release = self.button_callback)
            bl.add_widget(b)

        sv = ScrollView(size_hint = (None, None), width=self.button_width, height = self.height, x = self.x + self.spacing,
            y = self.y + self.spacing)
        sv.add_widget(bl)
        self.add_widget(sv)

    def button_callback(self, instance):

        if instance.id in [x.material_name for x in self.tileset]:
            self.current_tile_type = self.tileset[[x.material_name for x in self.tileset].index(instance.id)]

class ScreenEditorWidget(Widget):
    def __init__(self):
        super(ScreenEditorWidget,self).__init__()
        
        tileset = [Subtile('atlas://ArtAssets/TileSets/Tileset-SeaGrass_Forest_128/','Grass',None,1),
            Subtile('atlas://ArtAssets/TileSets/Tileset-SeaGrass_Forest_128/','Sand',None,1),
            Subtile('atlas://ArtAssets/TileSets/Tileset-SeaGrass_Forest_128/','Water',None,4),
            Subtile('atlas://ArtAssets/TileSets/Tileset-SeaGrass_Forest_128/','Dirt',None,1)]

        atlas='ArtAssets/WorldObjects/WorldObjects-SeaGrass_Forest-Set1_128.atlas'
        objects = self.get_world_objects(atlas)

        mainwidget = ScreenEditor(
            tileset,
            objects,
            pos = (0, 0), 
            size = (Window.width, Window.height))

        self.add_widget(mainwidget)

    def get_world_objects(self,atlas):
        '''Reads all world objects from supplied atlas. Returns a list of WorldObjects'''
        # split all keys into tile groups (i.e., make xx-1 xx-2 xx-3 and xx-4 into the same object)
        objects = []
        for key in Atlas(atlas).textures.keys():
            keysplit = key.rpartition('-')
            #try to cast the last section of the name after - as an int. if this works it's an animated frame
            try:
                fnum = int(keysplit[-1])
                # now add the section of the name prior to the '-' as a key to objects if it's not there already, otherwise increment frames by 1.

                if keysplit[0] not in [x.name for x in objects]:
                    objects.append(WorldObject(atlas,keysplit[0],1))
                else:
                    objects[[x.name for x in objects].index(keysplit[0])].frames += 1

            except ValueError:
                print "error raised:", key
                objects.append(WorldObject(atlas,key,1))

        return objects


class ScreenEditorApp(App):
    def build(self):
        main = ScreenEditorWidget()
        #Clock.schedule_interval(main.update, 1.0/60.0)
        return main


if __name__ == '__main__':
    ScreenEditorApp().run()