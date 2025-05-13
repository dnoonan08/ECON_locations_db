import sys
sys.path.append('..')
from LocationsDB import LocationsDatabase

#left commented out on git to avoid accidentally running, update path when needed
#####loc_db = LocationsDatabase('../database_files/test_locations.db')

loc_db.sortChip(chip_id=1009411, start_tray=10094, start_position=11, new_tray=99999, new_position=1, comments="For LDMX Prototypes", timestamp="2025-03-25 16:00:00")
loc_db.sortChip(chip_id=1009418, start_tray=10094, start_position=18, new_tray=99999, new_position=2, comments="For LDMX Prototypes", timestamp="2025-03-25 16:00:00")
loc_db.sortChip(chip_id=1009467, start_tray=10094, start_position=67, new_tray=99999, new_position=3, comments="For LDMX Prototypes", timestamp="2025-03-25 16:00:00")
loc_db.sortChip(chip_id=   7201, start_tray=   72, start_position= 1, new_tray= 9999, new_position=1, comments="For LDMX Prototypes", timestamp="2025-03-25 16:00:00")
loc_db.sortChip(chip_id=   7202, start_tray=   72, start_position= 2, new_tray= 9999, new_position=2, comments="For LDMX Prototypes", timestamp="2025-03-25 16:00:00")
loc_db.sortChip(chip_id=   7203, start_tray=   72, start_position= 3, new_tray= 9999, new_position=3, comments="For LDMX Prototypes", timestamp="2025-03-25 16:00:00")
loc_db.sortChip(chip_id=   7205, start_tray=   72, start_position= 5, new_tray= 9999, new_position=4, comments="For LDMX Prototypes", timestamp="2025-03-25 16:00:00")
loc_db.sortChip(chip_id=   7206, start_tray=   72, start_position= 6, new_tray= 9999, new_position=5, comments="For LDMX Prototypes", timestamp="2025-03-25 16:00:00")
loc_db.sortChip(chip_id=   7207, start_tray=   72, start_position= 8, new_tray= 9999, new_position=6, comments="For LDMX Prototypes", timestamp="2025-03-25 16:00:00")

loc_db.commitAndClose()
