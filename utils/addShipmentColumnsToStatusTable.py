import sys
sys.path.append('..')
from LocationsDB import LocationsDatabase

#####loc_db = LocationsDatabase('../database_files/test_locations.db')
loc_db = LocationsDatabase('../database_files/test_locations.db')

loc_db.cursor.execute('''ALTER TABLE status ADD serial_number TEXT default "";''')
loc_db.cursor.execute('''ALTER TABLE status ADD shipment_note TEXT default "";''')

loc_db.commitAndClose()
