from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, BooleanProperty, ListProperty, StringProperty, ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.atlas import Atlas

class WorldObject(Widget):
    parent = ObjectProperty(None)
    gridpos = ListProperty([0,0])

    def __init__(self,atlas,name,frames,**kwargs):
        self.atlas = atlas
        self.atlas_str = str('atlas://' + atlas + '/')
        self.name = name
        self.frames = frames
        self.update_now = False

        try:
            self.icon = Atlas(atlas)[name]
            self.icon_str = str(self.atlas_str + name)
        except KeyError:
            self.icon = Atlas(atlas)[name + "-1"]
            self.icon_str = str(self.atlas_str + name + '-1')

        super(WorldObject,self).__init__(**kwargs)

    def get_current_frame(self,framecounter):
        return self.atlas_str + self.name + '-' + str(framecounter % self.frames + 1) if self.frames > 1 else self.atlas_str + self.name

    def __str__(self):
        return self.name

class Subtile(Widget):
    def __init__(self,atlas,material_name,position,frames,subtile_id=None):
        self.atlas = atlas
        self.material_name = material_name
        self.position = [[True,True],[True,True]] if position is None else position
        self.frames = frames
        self.subtile_id = subtile_id
        
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

    def __init__(self,tileset,init_tile_list,**kwargs):
        # get reference to parent (ScreenEditor) and grab atlas/tilenames
        # self.parent = parent
        # self.atlas = parent.atlas
        # self.tile_names = parent.tile_names
        # self.tile_frame_dict = parent.tile_frame_dict
        self.init_tile_list = init_tile_list
        self.tileset = tileset

        super(Screen,self).__init__(**kwargs)

        #start the animation counter
        Clock.schedule_interval(self.increment_active_frame, 1.0)
        Clock.schedule_once(self.setup_window)
        
        self.world_objects = []

    def setup_window(self,dt):
        self.tile_width = min(self.width/self.cols,self.height/self.rows)


        self.tiles = [Tile(self.init_tile_list[int(i*self.cols+j)],parent=self,size=(self.tile_width,self.tile_width), x = self.x + self.tile_width*j,y=self.y+self.tile_width*i,size_hint = (None,None),gridpos = (i,j)) for i in xrange(int(self.rows)) for j in xrange(int(self.cols))]
        for ctile in self.tiles:
            self.add_widget(ctile)

    def increment_active_frame(self, dt):
        self.active_frame += 1

    def tile_touch(self,tile):
        new_base_type = self.parent.current_tile_type

        if isinstance(new_base_type,WorldObject):
            self.add_world_object(new_base_type,tile)
            return 

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


    def add_world_object(self,base_object,tile):
        o = WorldObject(base_object.atlas,base_object.name,base_object.frames,pos=tile.pos, gridpos = tile.gridpos,size=tile.size,size_hint=(None,None),parent=self)
        world_object_gridpositions = [x.gridpos for x in self.world_objects]

        if o.gridpos in world_object_gridpositions:
            old = self.world_objects[world_object_gridpositions.index(o.gridpos)] 
            # old.atlas = o.atlas
            # old.name = o.name
            # old.frames = o.frames
            old.__init__(o.atlas,o.name,o.frames,pos=tile.pos, gridpos = tile.gridpos,size=tile.size,size_hint=(None,None),parent=self)
            old.update_now = not old.update_now
        else:
            self.world_objects.append(o)
            self.add_widget(o)
        

    def get_surrounding_tiles(self,col,row):
        tiles = [[None,None,None],[None,None,None],[None,None,None]]
        for r_idx,r in enumerate([row - 1, row, row + 1]):
            for c_idx,c in enumerate([col - 1, col, col + 1]):
                if r >= 0 and c >= 0 and r < self.cols and c < self.rows:
                    tiles[c_idx][r_idx] = self.tiles[self.cols*c + r]
                else:
                    pass

        return tiles

class CBLPopup(Popup):
    '''Subclass of Popup that allows both content text (CBLPopup.text) and a list of buttons (CBLPopup.buttons). Calls parent_callback(button) when button is pressed'''
    
    def __init__(self,parent_callback,text=None,buttons=None,**kwargs):
        self.parent_callback = parent_callback
        bl = BoxLayout(orientation='vertical',spacing = 5, padding = 5)
        if text is not None: 
            bl.add_widget(Label(text=text))

        if buttons is not None:
            for button_text in buttons:
                b = Button(text=button_text)
                b.bind(on_release=self.button_press)
                bl.add_widget(b)
            self.auto_dismiss = False
        else:
            self.auto_dismiss = True

        
        self.content = bl

        super(CBLPopup,self).__init__(**kwargs)

    def button_press(self,instance):
        self.parent_callback(instance)
        self.dismiss()