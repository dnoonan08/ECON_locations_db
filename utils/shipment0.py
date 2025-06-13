import sys
sys.path.append('..')
from LocationsDB import LocationsDatabase

#left commented out on git to avoid accidentally running, update path when needed
loc_db = LocationsDatabase('../test_database.db')

# Manually moving chips with bent pins out of sorted trays and into a new reject tray. Also re-grade as rejects
# Rejected Up-1.14-5
loc_db.setChipGrade(chip_id=1005509, grade="Reject", comments="Manual pin inspection", timestamp="2025-06-09 16:43:00")
loc_db.rejectChip(chip_id=1005509, start_tray=18034, start_position=47, new_tray=19000, new_position=9, comments="Manual pin inspection", timestamp="2025-06-12 12:38:00")

loc_db.setChipGrade(chip_id=1005540, grade="Reject", comments="Manual pin inspection", timestamp="2025-06-09 16:43:00")
loc_db.rejectChip(chip_id=1005540, start_tray=18034, start_position=50, new_tray=19000, new_position=10, comments="Manual pin inspection", timestamp="2025-06-12 12:38:00")

loc_db.setChipGrade(chip_id=1005848, grade="Reject", comments="Manual pin inspection", timestamp="2025-06-09 16:43:00")
loc_db.rejectChip(chip_id=1005848, start_tray=18034, start_position=1, new_tray=19000, new_position=11, comments="Manual pin inspection", timestamp="2025-06-12 12:38:00")

loc_db.setChipGrade(chip_id=1004009, grade="Reject", comments="Manual pin inspection", timestamp="2025-06-09 16:43:00")
loc_db.rejectChip(chip_id=1004009, start_tray=18033, start_position=10, new_tray=19000, new_position=12, comments="Manual pin inspection", timestamp="2025-06-12 12:38:00")

# Manually replacing chips that have been reject with unsorted chips
loc_db.setChipGrade(chip_id=1011308, grade="Up", comments="1.14V", timestamp="2025-06-12 13:10:00")
loc_db.sortChip(chip_id=1011308, start_tray=10113, start_position=8, new_tray=18033, new_position=10, comments="Manual replacement for reject", timestamp="2025-06-12 13:10:00")

loc_db.setChipGrade(chip_id=1011310, grade="Up", comments="1.14V", timestamp="2025-06-12 13:10:00")
loc_db.sortChip(chip_id=1011310, start_tray=10113, start_position=10, new_tray=18034, new_position=1, comments="Manual replacement for reject", timestamp="2025-06-12 13:10:00")

loc_db.setChipGrade(chip_id=1011347, grade="Up", comments="1.14V", timestamp="2025-06-12 13:10:00")
loc_db.sortChip(chip_id=1011347, start_tray=10113, start_position=47, new_tray=18034, new_position=47, comments="Manual replacement for reject", timestamp="2025-06-12 13:10:00")

loc_db.setChipGrade(chip_id=1011353, grade="Up", comments="1.14V", timestamp="2025-06-12 13:10:00")
loc_db.sortChip(chip_id=1011353, start_tray=10113, start_position=53, new_tray=18034, new_position=50, comments="Manual replacement for reject", timestamp="2025-06-12 13:10:00")

# Change location to be shipment destination
loc_db.shipTrays(trays=[18014, 18019, 18021, 18025, 18029, 18031, 18042],destination="Poly/Baylor")#strange 1.05
loc_db.shipTrays(trays=[18035, 18022, 18015, 18041, 18043],destination="Poly/Baylor")#charm 1.03
loc_db.shipTrays(trays=[32,33,34,35,36,37,38], destination="Poly/Baylor")#ECONTs
loc_db.shipTrays(trays=[18016, 18023],destination="UMN")#beauty 1.01
loc_db.shipTrays(trays=[18033, 18034, 18036, 18037], destination="ALICE/CERN")#up 1.14

loc_db.commitAndClose()