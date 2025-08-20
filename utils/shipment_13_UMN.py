import sys
sys.path.append('..')
from LocationsDB import LocationsDatabase
from GradesDB import GradesDatabase

#left commented out on git to avoid accidentally running, update path when needed
loc_db = LocationsDatabase('../database_files/danny_Test_Locations.db')
grade_db = GradesDatabase('../database_files/danny_Test_Grades.db')

#manually moving chips out from charm trays that were rejected from visual inspection
Time = "2025-08-20 15:00:00"
loc_db.setChipGrade(chip_id=1008688, grade="Reject", comments="Manual pin inspection", timestamp=Time)
loc_db.rejectChip(chip_id=1008688, start_tray=18039, start_position=85, new_tray=19000, new_position=14, comments="Manual pin inspection", timestamp=Time)

loc_db.setChipGrade(chip_id=1008324, grade="Reject", comments="Manual pin inspection", timestamp=Time)
loc_db.rejectChip(chip_id=1008324, start_tray=18039, start_position=54, new_tray=19000, new_position=15, comments="Manual pin inspection", timestamp=Time)

loc_db.setChipGrade(chip_id=1000688, grade="Reject", comments="Manual pin inspection", timestamp=Time)
loc_db.rejectChip(chip_id=1000688, start_tray=18046, start_position=5, new_tray=19000, new_position=16, comments="Manual pin inspection", timestamp=Time)

#Move 20 chips from 18044 into 18050 (new ECOND tray), which will be shipped to UMN
chipsToMove = [[1013229, 18044, 51, 18050, 1],
               [1013265, 18044, 52, 18050, 2],
               [1001170, 18044, 53, 18050, 3],
               [1001184, 18044, 54, 18050, 4],
               [1001021, 18044, 55, 18050, 5],
               [1001023, 18044, 56, 18050, 6],
               [1001029, 18044, 57, 18050, 7],
               [1001082, 18044, 58, 18050, 8],
               [1000973, 18044, 59, 18050, 9],
               [1000801, 18044, 60, 18050, 10],
               [1000825, 18044, 61, 18050, 11],
               [1000835, 18044, 62, 18050, 12],
               [1000717, 18044, 63, 18050, 13],
               [1000735, 18044, 64, 18050, 14],
               [1000753, 18044, 65, 18050, 15],
               [1002018, 18044, 66, 18050, 16],
               [1000616, 18044, 67, 18050, 17],
               [1000632, 18044, 68, 18050, 18],
               [1000658, 18044, 69, 18050, 19],
               [1000665, 18044, 70, 18050, 20]]

for c in chipsToMove:
    chip_id, start_tray, start_pos, end_tray, end_pos = c
    loc_db.sortChip(chip_id=chip_id,
                    start_tray=start_tray,
                    start_position=start_pos,
                    new_tray=end_tray,
                    new_position=end_pos,
                    comments="Manually sorted to new tray before shipping",
                    timestamp=Time)

# Change location to be shipment destination
loc_db.shipTraysAndGenerateUploadCSV(
    trays=[18040, 18017, #top 0.99V (146 chips, 90 and 56)
           18038, 18050, #beauty 1.01V (160 chips, 90 and 20)
           18039, 18046, #charm 1.03V
           49, 50, 51 #ECONT
           ],
    destination="UMN",
    grade_db = grade_db,
    shipment_number = 13,
    shipment_note =  "For production of first HD wagons and pCM"
)

loc_db.commitAndClose()
