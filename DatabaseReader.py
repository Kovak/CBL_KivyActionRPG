import sqlite3

#just for testing
if __name__ == '__main__': import os

class DatabaseReader():

    def __init__(self,dblocation,create=False):
        """Attempts to open world database at dblocation. If create = True, sets up a new world database at dblocation."""
        
        self.conn = sqlite3.connect(dblocation)
        self.c = self.conn.cursor()

        if create:
            self.format_db()

    def __del__(self):
        self.c.close()

    def format_db(self):
        self.c.execute('CREATE TABLE all_objects (objectid INTEGER PRIMARY KEY, atlas STRING, name STRING, frames INTEGER)')
        self.c.execute('CREATE TABLE all_tiles (tileid INTEGER PRIMARY KEY, atlas STRING, name STRING, frames INTEGER)')
        self.conn.commit()

    def add_map(self,label):
        assert label.isalnum()

        tile_table_name = 'map_' + label + '_tiles'
        objects_table_name = 'map_' + label + '_objects'
        layout_table_name = 'map_' + label + '_layout'

        self.c.execute('CREATE TABLE '+ tile_table_name + ' (screenid INTEGER, r INTEGER, c INTEGER, tileid INTEGER, layer INTEGER)')
        self.c.execute('CREATE TABLE '+ objects_table_name + ' (screenid INTEGER, r INTEGER, c INTEGER, objectid INTEGER, x NUMERIC, y NUMERIC, layer INTEGER)')
        self.c.execute('CREATE TABLE '+ layout_table_name + ' (r INTEGER, c INTEGER, screenid INTEGER)')
        self.conn.commit()

    def add_screen(self,tiles_array,objects_array,map_label,relative_to,position):
        """Adds a screen within supplied map. Placed at position 'position' (4,8,6, or 2) relative to screenid 'relative_to'. If relative_to is None, assumes this is the first map of the world and sets at (0,0)"""

        tile_table_name = 'map_' + map_label + '_tiles'
        objects_table_name = 'map_' + map_label + '_objects'
        layout_table_name = 'map_' + map_label + '_layout'

        # can't do much more until I hook this to the level editor.


if __name__ == '__main__':
    try:
        d = DatabaseReader(os.path.join(os.path.dirname(__file__),'worlddb.sqlite'),create=True)
    except sqlite3.OperationalError:
        d = DatabaseReader(os.path.join(os.path.dirname(__file__),'worlddb.sqlite'))