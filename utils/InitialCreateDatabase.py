import sqlite3
def createLocationsDB(fname = 'example.db'):
    # Connect to the database (or create it if it doesn't exist)
    conn = sqlite3.connect(fname)

    # Create a cursor object to execute SQL commands
    cursor = conn.cursor()


    # Create a table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS locations (
            chip_id INTEGER,
            entry_type TEXT,
            initial_tray INT,
            initial_position INT,
            current_tray INT,
            current_position INT,
            location TEXT,
            comments TEXT,
            time TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS status (
            chip_id INTEGER,
            chip_type TEXT,
            pkg_date TEXT, 
            pkg_batch TEXT,
            grade TEXT,
            comments TEXT,
            time TEXT
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()

createLocationsDB('../database_files/ECON_Locations_DB.db')
