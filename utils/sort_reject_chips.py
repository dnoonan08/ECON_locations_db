import sys
sys.path.append('..')
from LocationsDB import LocationsDatabase

#left commented out on git to avoid accidentally running, update path when needed
#####loc_db = LocationsDatabase('../database_files/test_locations.db')

loc_db.setChipGrade(chip_id=1001209, grade="Reject", comments="Manual pin inspection", timestamp="2025-06-09 16:43:00")
loc_db.rejectChip(chip_id=1001209, start_tray=18042, start_position=86, new_tray=19000, new_position=1, comments="Manual pin inspection", timestamp="2025-06-09 16:43:00")

loc_db.setChipGrade(chip_id=1004588, grade="Reject", comments="Manual pin inspection", timestamp="2025-06-09 16:43:00")
loc_db.rejectChip(chip_id=1004588, start_tray=18042, start_position=6, new_tray=19000, new_position=2, comments="Manual pin inspection", timestamp="2025-06-09 16:43:00")

loc_db.setChipGrade(chip_id=1002009, grade="Reject", comments="Manual pin inspection", timestamp="2025-06-09 16:43:00")
loc_db.rejectChip(chip_id=1002009, start_tray=18042, start_position=42, new_tray=19000, new_position=3, comments="Manual pin inspection", timestamp="2025-06-09 16:43:00")

loc_db.setChipGrade(chip_id=1008749, grade="Reject", comments="Manual pin inspection", timestamp="2025-06-09 16:43:00")
loc_db.rejectChip(chip_id=1008749, start_tray=18029, start_position=17, new_tray=19000, new_position=4, comments="Manual pin inspection", timestamp="2025-06-09 16:43:00")

loc_db.setChipGrade(chip_id=1011852, grade="Reject", comments="Manual pin inspection", timestamp="2025-06-09 16:43:00")
loc_db.rejectChip(chip_id=1011852, start_tray=18019, start_position=9, new_tray=19000, new_position=5, comments="Manual pin inspection", timestamp="2025-06-09 16:43:00")

loc_db.setChipGrade(chip_id=1013645, grade="Reject", comments="Manual pin inspection", timestamp="2025-06-09 16:43:00")
loc_db.rejectChip(chip_id=1013645, start_tray=18021, start_position=9, new_tray=19000, new_position=6, comments="Manual pin inspection", timestamp="2025-06-09 16:43:00")

loc_db.setChipGrade(chip_id=1009145, grade="Reject", comments="Manual pin inspection", timestamp="2025-06-09 16:43:00")
loc_db.rejectChip(chip_id=1009145, start_tray=18025, start_position=82, new_tray=19000, new_position=7, comments="Manual pin inspection", timestamp="2025-06-09 16:43:00")

loc_db.setChipGrade(chip_id=1003982, grade="Reject", comments="Manual pin inspection", timestamp="2025-06-09 16:43:00")
loc_db.rejectChip(chip_id=1003982, start_tray=18031, start_position=54, new_tray=19000, new_position=8, comments="Manual pin inspection", timestamp="2025-06-09 16:43:00")

loc_db.sortChip(chip_id=1001903, start_tray=10019, start_position=3, new_tray=18031, new_position=54, comments="Replacement for reject", timestamp="2025-06-09 17:32:00")
loc_db.sortChip(chip_id=1001906, start_tray=10019, start_position=6, new_tray=18025, new_position=82, comments="Replacement for reject", timestamp="2025-06-09 17:32:00")
loc_db.sortChip(chip_id=1001964, start_tray=10019, start_position=64, new_tray=18021, new_position=9, comments="Replacement for reject", timestamp="2025-06-09 17:32:00")
loc_db.sortChip(chip_id=1001971, start_tray=10019, start_position=71, new_tray=18019, new_position=9, comments="Replacement for reject", timestamp="2025-06-09 17:32:00")
loc_db.sortChip(chip_id=1001280, start_tray=10012, start_position=80, new_tray=18029, new_position=17, comments="Replacement for reject", timestamp="2025-06-09 17:32:00")
loc_db.sortChip(chip_id=1001284, start_tray=10012, start_position=84, new_tray=18042, new_position=6, comments="Replacement for reject", timestamp="2025-06-09 17:32:00")
loc_db.sortChip(chip_id=1002115, start_tray=10021, start_position=15, new_tray=18042, new_position=42, comments="Replacement for reject", timestamp="2025-06-09 17:32:00")
loc_db.sortChip(chip_id=1002122, start_tray=10021, start_position=22, new_tray=18042, new_position=86, comments="Replacement for reject", timestamp="2025-06-09 17:32:00")

loc_db.commitAndClose()
