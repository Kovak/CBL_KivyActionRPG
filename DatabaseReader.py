import sqlite3
from BaseObjects import Subtile

class DatabaseReader():

    def __init__(self,dblocation):
        """Attempts to open world database at dblocation. If create = True, sets up a new world database at dblocation."""
        print dblocation
        self.conn = sqlite3.connect(dblocation)
        self.c = self.conn.cursor()

        try:
            self.format_db()
        except sqlite3.OperationalError:
            pass

        self.link_tileids_to_subtiles()

    def __del__(self):
        self.c.close()

    def format_db(self):
        self.c.execute('CREATE TABLE all_objects (objectid INTEGER PRIMARY KEY, atlas STRING, name STRING, frames INTEGER)')
        self.c.execute('CREATE TABLE all_tiles (tileid INTEGER PRIMARY KEY, atlas STRING, name STRING, frames INTEGER)')
        self.conn.commit()


    def link_tileids_to_subtiles(self):
        tiles = {}
        for row in self.c.execute('SELECT tileid, atlas, name, frames FROM all_tiles'):
            tiles[row[0]] = Subtile(row[1],row[2],None,row[3],subtile_id=row[0])
        self.tile_dict = tiles

    def add_map(self,label,rows=6,cols=9):
        assert label.isalnum()

        tile_table_name = 'map_' + label + '_tiles'
        objects_table_name = 'map_' + label + '_objects'
        layout_table_name = 'map_' + label + '_layout'
        config_table_name = 'map_' + label + '_config'

        self.c.execute('CREATE TABLE '+ tile_table_name + ' (screenid INTEGER, r INTEGER, c INTEGER, tileid INTEGER, layer INTEGER)')
        self.c.execute('CREATE TABLE '+ objects_table_name + ' (screenid INTEGER, r INTEGER, c INTEGER, objectid INTEGER, x NUMERIC, y NUMERIC, layer INTEGER)')
        self.c.execute('CREATE TABLE '+ layout_table_name + ' (r INTEGER, c INTEGER, screenid INTEGER)')
        self.c.execute('CREATE TABLE '+ config_table_name + ' (field TEXT, value STRING)')

        t = (rows,)
        self.c.execute('INSERT INTO '+config_table_name+' VALUES ("rows",?)',t)
        r = (cols,)
        self.c.execute('INSERT INTO '+config_table_name+' VALUES ("cols",?)',r)

        self.conn.commit()

    def get_map_row_col(self,map_label):
        config_table_name = 'map_' + map_label + '_config'

        # get rows and columns from config table
        rows, cols = None, None
        for entry in self.c.execute('SELECT field,value FROM '+config_table_name):
            if entry[0] == 'rows':
                rows = int(entry[1])
            elif entry[0] == 'cols':
                cols = int(entry[1])
        assert (rows is not None and cols is not None)

        return rows,cols

    def add_screen(self,tile_array,objects_array,map_label,relative_to,position):
        """Adds a screen within supplied map. Placed at position 'position' (4,8,6, or 2) relative to screenid 'relative_to'. 
        If relative_to is None, assumes this is the first map of the world and sets at (0,0). Returns the screen ID of the screen"""

        tile_table_name = 'map_' + map_label + '_tiles'
        objects_table_name = 'map_' + map_label + '_objects'
        layout_table_name = 'map_' + map_label + '_layout'

        # get rows and columns from config table
        rows, cols = self.get_map_row_col(map_label)


        if position is None:
            self.c.execute('INSERT INTO '+layout_table_name+' (r, c, screenid) VALUES (0,0,1)')
            screenid = 1
        else:
            # insert all the code for relative screen placement here
            screenid = None

        for idx, tile_code in enumerate(tile_array):
            r_idx = int(idx / cols)
            c_idx = int(idx % cols)
            for layer, subtile in enumerate(tile_code):
                t = (screenid,r_idx,c_idx,subtile,layer)
                self.c.execute('INSERT INTO '+tile_table_name+' (screenid, r, c, tileid, layer) VALUES (?,?,?,?,?)',t)

        self.conn.commit()
        return screenid

    def get_screen(self,map_label,screenid):
        tile_table_name = 'map_' + map_label + '_tiles'
        
        rows, cols = self.get_map_row_col(map_label)
        tile_props = {}

        tile_props = self.c.execute('SELECT tileid,layer,r,c FROM ' + tile_table_name + ' WHERE screenid=?',(screenid,)).fetchall()
      
            # tileid = entry[0]
            # layer = entry[1]
            # r = int(entry[2])
            # c = int(entry[3])
            # tile_props[(r,c)] = [(tileid,layer)]
        # sort by r,c and finally layer. NEED TO REWRITE THIS IN SQL
        tile_props.sort(key=lambda x: x[1])
        tile_props.sort(key=lambda x: x[3])
        tile_props.sort(key=lambda x: x[2])

        screen = [[self.tile_dict[x[0]]] for x in tile_props]

        return screen

    def get_map(self,map_label):
        tile_table_name = 'map_' + map_label + '_tiles'
        objects_table_name = 'map_' + map_label + '_objects'
        layout_table_name = 'map_' + map_label + '_layout'

        # get rows and columns from config table
        rows, cols = self.get_map_row_col(map_label)
        layout = self.c.execute('SELECT r,c,screenid FROM ' + layout_table_name).fetchall()

        r_dim = abs(max([x[0] for x in layout)]) - min([x[0] for x in layout)])) + 1
        c_dim = abs(max([x[1] for x in layout)]) - min([x[1] for x in layout)])) + 1

    
        

    def add_tileset(self,tileset):
        for t in tileset:
            a = {"atlas": t.atlas,
                "name": t.material_name,
                "frames": t.frames,}
            # if the tile isn't already in all_tiles, add it
            if len(self.c.execute('SELECT tileid from all_tiles WHERE (atlas=:atlas and name=:name)',a).fetchall()) == 0:
                self.c.execute("""INSERT INTO all_tiles (atlas,name,frames) VALUES (:atlas,:name,:frames)""",a)
                self.conn.commit()

        self.link_tileids_to_subtiles()
