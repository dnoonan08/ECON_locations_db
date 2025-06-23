import sys
sys.path.append('..')
from LocationsDB import LocationsDatabase

import pandas as pd

loc_db = LocationsDatabase('../database_files/testing_database.db')

d = pd.read_csv('../sorting_logs/sorting_logECOND-10801.log',header=None)
d.columns=['start_barcode','start_pos','end_barcode','end_pos']
d['start_tray'] = d.start_barcode.str[-5:].astype('int')
d['end_tray'] = d.end_barcode.str[-5:].astype('int')
d['chip_id'] = d.start_tray*100 + d.start_pos


for chip in d.itertuples():
    print(chip.chip_id,
          chip.start_tray,
          chip.start_pos,
          chip.end_tray,
          chip.end_pos,
          "",
          "2025-01-16 00:00:00")
    loc_db.sortChip(chip_id=chip.chip_id,
                    start_tray=chip.start_tray,
                    start_position=chip.start_pos,
                    new_tray=chip.end_tray,
                    new_position=chip.end_pos,
                    comments="",
                    timestamp="2025-01-16 00:00:00")


d = pd.read_csv('../sorting_logs/sorting_logECOND-10802.log',header=None)
d.columns=['start_barcode','start_pos','end_barcode','end_pos']
d['start_tray'] = d.start_barcode.str[-5:].astype('int')
d['end_tray'] = d.end_barcode.str[-5:].astype('int')
d['chip_id'] = d.start_tray*100 + d.start_pos


for chip in d.itertuples():
    print(chip.chip_id,
          chip.start_tray,
          chip.start_pos,
          chip.end_tray,
          chip.end_pos,
          "",
          "2025-01-16 00:00:00")
    loc_db.sortChip(chip_id=chip.chip_id,
                    start_tray=chip.start_tray,
                    start_position=chip.start_pos,
                    new_tray=chip.end_tray,
                    new_position=chip.end_pos,
                    comments="",
                    timestamp="2025-01-16 00:00:00")

loc_db.commitAndClose()
