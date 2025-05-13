import sys
sys.path.append('..')
from LocationsDB import LocationsDatabase

#left commented out on git to avoid accidentally running, update path when needed
#####loc_db = LocationsDatabase('../database_files/test_locations_update.db')

loc_db.cursor.execute('UPDATE status SET grade = "Truth" WHERE grade is "Top" and comments is "0.99V"')
loc_db.cursor.execute('UPDATE status SET grade = "Beauty" WHERE grade is "Bottom" and comments is "1.01V"')
loc_db.cursor.execute('UPDATE status SET grade = "Strange" WHERE grade is "Charm" and comments is "1.05V"')
loc_db.cursor.execute('UPDATE status SET grade = "Down" WHERE grade is "Charm" and comments is "1.08V"')

loc_db.commitAndClose()
