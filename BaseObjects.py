from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, BooleanProperty, ListProperty, StringProperty, ObjectProperty
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