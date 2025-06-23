import sys
sys.path.append('..')
from LocationsDB import LocationsDatabase
from GradesDB import GradesDatabase

#left commented out on git to avoid accidentally running, update path when needed
loc_db = LocationsDatabase('../database_files/test_locations.db')
grade_db = GradesDatabase('../database_files/test_grade_database.db')

#moved three chips with bent pins back to initial location
loc_db.setChipGrade(chip_id=1002285, grade="Reject", comments="Manual pin inspection", timestamp="2025-01-28 12:00:00")
loc_db.rejectChip(chip_id=1002285, start_tray=18009, start_position=35, new_tray=10022, new_position=85, comments="Manual pin inspection", timestamp="2025-01-28 12:00:00")

loc_db.setChipGrade(chip_id=1002309, grade="Reject", comments="Manual pin inspection", timestamp="2025-01-28 12:00:00")
loc_db.rejectChip(chip_id=1002309, start_tray=18009, start_position=42, new_tray=10023, new_position=9, comments="Manual pin inspection", timestamp="2025-01-28 12:00:00")

loc_db.setChipGrade(chip_id=1002413, grade="Reject", comments="Manual pin inspection", timestamp="2025-01-28 12:00:00")
loc_db.rejectChip(chip_id=1002413, start_tray=18009, start_position=77, new_tray=10024, new_position=13, comments="Manual pin inspection", timestamp="2025-01-28 12:00:00")

# Change location to be shipment destination
loc_db.shipTraysAndGenerateUploadCSV(
    trays=[18007,18008,8007,8008
           ],
    destination="UMN",
    grade_db = grade_db,
    shipment_number = 7,
    shipment_note =  "Preseries HD wagons",
    timestamp="2025-01-31 12:00:00",
    is_preseries = True,
)


loc_db.shipTraysAndGenerateUploadCSV(
    trays=[18009,18010,8009,8010
           ],
    destination="UMN",
    grade_db = grade_db,
    shipment_number = 8,
    shipment_note =  "Preseries HD wagons",
    timestamp="2025-01-31 12:00:00",
    is_preseries = True,
)

loc_db.shipTraysAndGenerateUploadCSV(
    trays=[18011,18012,8011,8012],
    destination="Poly/Baylor",
    grade_db = grade_db,
    shipment_number = 9,
    shipment_note =  "Preseries for partial CMs",
    timestamp="2025-01-31 12:00:00",
    is_preseries = True,
)

loc_db.commitAndClose()
