import sqlite3
import ezdxf

class DxfDataBase:
    def __init__(self, db_path='dxf_database.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS dxf_files_table (
                id INTEGER PRIMARY KEY, 
                manufacturer TEXT, 
                "set" TEXT,
                code TEXT, 
                path TEXT,
                UNIQUE(manufacturer, "set", code, path)
                )
            ''')
        
    def insert(self, manufacturer, set, code, path):
        self.cursor.execute('''
            INSERT OR REPLACE INTO dxf_files_table (manufacturer, "set", code, path) VALUES (?, ?, ?, ?)
            ''', (manufacturer, set, code, path))
        self.conn.commit()


    def get_dxf_file(self, manufacturer, set, code):
        self.cursor.execute('''
            SELECT path FROM dxf_files_table WHERE manufacturer = ? AND "set" = ? AND code = ?
            ''', (manufacturer, set, code))
        return self.cursor.fetchone()[0]
    
    def remove_dxf_file(self, manufacturer, set, code):
        self.cursor.execute('''
            DELETE FROM dxf_files_table WHERE manufacturer = ? AND "set" = ? AND code = ?
            ''', (manufacturer, set, code))
        self.conn.commit()

    def get_all_manufacturers(self):
        self.cursor.execute('''
            SELECT DISTINCT manufacturer FROM dxf_files_table
            ''')
        return self.cursor.fetchall()
    
    def get_sets_by_manufacturer(self, manufacturer):
        self.cursor.execute('''
            SELECT DISTINCT "set" FROM dxf_files_table WHERE manufacturer = ?
            ''', (manufacturer,))
        return self.cursor.fetchall()
    
    def get_codes_by_manufacturer_and_set(self, manufacturer, set):
        self.cursor.execute('''
            SELECT code FROM dxf_files_table WHERE manufacturer = ? AND "set" = ?
            ''', (manufacturer, set))
        return self.cursor.fetchall()
    
    def get_code_dimensions(self, manufacturer, set, code):

        # Get the path of the dxf file
        

        try:
            # Open the dxf file
            filename = self.get_dxf_file(manufacturer, set, code)
            dxf_doc = ezdxf.readfile(filename)
        except:
            return None, None

        # Get the lower and upper limits of the model space
        lower_limit = dxf_doc.header['$EXTMIN']
        upper_limit = dxf_doc.header['$EXTMAX']

        # Calculate and return the height and width of the profile
        height = upper_limit[1] - lower_limit[1]
        width = upper_limit[0] - lower_limit[0]

        return height, width
    
    def close(self):
        self.conn.close()

