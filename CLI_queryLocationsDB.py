#!/usr/bin/python3

import numpy as np
import click

from LocationsDB import LocationsDatabase

import pandas as pd
pd.set_option('display.max_rows', 100)

def get_next_barcode(loc_db):
    full_barcode_list = loc_db.loadLocationsDatabase().current_tray.unique().tolist()
    full_barcode_list += loc_db.loadLocationsDatabase().initial_tray.unique().tolist()
    full_barcode_list = np.unique(full_barcode_list)

    ECONT_initial = full_barcode_list[full_barcode_list<6000].max() + 1
    ECONT_corners = {}
    for corner, start in [('Std', 0), ('5Pct', 100), ('10Pct', 200), ('15Pct', 300), ('SnSp', 400), ('SnFp', 500), ('FnSp', 600)]:
        cut = (full_barcode_list>=(6000+start)) & (full_barcode_list<(6100+start))
        if sum(cut)==0:
            ECONT_corners[corner] = 6001+start
        else:
            ECONT_corners[corner] = full_barcode_list[cut].max() + 1
    ECONT_sorting = full_barcode_list[(full_barcode_list<9000) & (full_barcode_list>=7000)].max() + 1
    ECONT_reject = full_barcode_list[(full_barcode_list<10000) & (full_barcode_list>=9000)].max() + 1


    ECOND_initial    = full_barcode_list[(full_barcode_list>=10000) & (full_barcode_list<16000)].max() + 1
    ECOND_corners = {}
    for corner, start in [('Std', 0), ('5Pct', 100), ('10Pct', 200), ('15Pct', 300), ('SnSp', 400), ('SnFp', 500), ('FnSp', 600)]:
        cut = (full_barcode_list>=(16000+start)) & (full_barcode_list<(16100+start))
        if sum(cut)==0:
            ECOND_corners[corner] = 16001+start
        else:
            ECOND_corners[corner] = full_barcode_list[cut].max() + 1
    ECOND_sorting = full_barcode_list[(full_barcode_list>=17000) & (full_barcode_list<19000)].max() + 1
    ECOND_reject = full_barcode_list[(full_barcode_list>=19000) & (full_barcode_list<20000)].max() + 1

    print("Next tray numbers to use:")

    print(f"    ECON-T checkin: ECONT-{ECONT_initial:05d}")
    print(f"           Std    : ECONT-{ECONT_corners['Std']:05d}")
    print(f"           5Pct   : ECONT-{ECONT_corners['5Pct']:05d}")
    print(f"           10Pct  : ECONT-{ECONT_corners['10Pct']:05d}")
    print(f"           15Pct  : ECONT-{ECONT_corners['15Pct']:05d}")
    print(f"           SnSp   : ECONT-{ECONT_corners['SnSp']:05d}")
    print(f"           SnFp   : ECONT-{ECONT_corners['SnFp']:05d}")
    print(f"           FnSp   : ECONT-{ECONT_corners['FnSp']:05d}")
    print(f"           sorting: ECONT-{ECONT_sorting:05d}")
    print(f"")
    print(f"    ECON-D checkin: ECOND-{ECOND_initial:05d}")
    print(f"           Std    : ECOND-{ECOND_corners['Std']:05d}")
    print(f"           5Pct   : ECOND-{ECOND_corners['5Pct']:05d}")
    print(f"           10Pct  : ECOND-{ECOND_corners['10Pct']:05d}")
    print(f"           15Pct  : ECOND-{ECOND_corners['15Pct']:05d}")
    print(f"           SnSp   : ECOND-{ECOND_corners['SnSp']:05d}")
    print(f"           SnFp   : ECOND-{ECOND_corners['SnFp']:05d}")
    print(f"           FnSp   : ECOND-{ECOND_corners['FnSp']:05d}")
    print(f"           sorting: ECOND-{ECOND_sorting:05d}")

@click.command()
@click.option("--tray",default=0, show_default=True, help="Tray number to query")
@click.option("--chip",default=0, show_default=True, help="Chip number to query")
@click.option("--get_next_tray",is_flag=True, help="Query the database to determine the next tray number in the sequence")
@click.option("--location",is_flag=True, help="Check the current location of a given chip or tray")
@click.option("--history",is_flag=True, help="Get the full history of a chip")
@click.option("--status",is_flag=True, help="Get the status table for a given chip or tray")
@click.option("--xcs",is_flag=True, help="Generate XCS file for tray")
@click.option("--sorting_tray_summary",is_flag=True, help="Get a summary for all sorting trays")
@click.option("--locations_db", default="/asic/projects/E/ECON_PROD_TESTING/ECON_locations_db/database_files/ECON_Locations_DB.db", help="Log file to log chip movements.")
def main(tray, chip, get_next_tray, location, history, status, xcs, sorting_tray_summary, locations_db):

    loc_db = LocationsDatabase(locations_db)

    if get_next_tray:
        get_next_barcode(loc_db)

    if history:
        if chip!=0:
            print(loc_db.getChip(chip))
            return
        else:
            print('The unique chip_id you want to get the history of must be specified')
            return

    if xcs:
        if tray!=0:
            print(f'Generating .xcs file for tray {tray:05d}')
            fname = loc_db.generateXCSForTray(tray)
            print(f'   {fname}')
            import os
            os.chmod(fname,0o660)
            return
        else:
            print('Must specify a tray number to generate the XCS file for')

    if location:
        if chip!=0:
            d = loc_db.getCurrentLocations()
            print(d[d.chip_id==chip])
            return
        elif tray!=0:
            d = loc_db.getChipsInTray(tray)
            print(d.set_index('chip_id'))
            print(f'Total chips: {len(d)}')
            return
        else:
            print('Must specify either a chip or tray number to query')
            return

    if status:
        if chip!=0:
            d = loc_db.getCurrentStatus()
            print(d[d.chip_id==chip])
            return
        elif tray!=0:
            d = loc_db.getStatusForTray(tray)
            print(d.set_index('chip_id'))
            print(f'Total chips: {len(d)}')
            return
        else:
            print('Must specify either a chip or tray number to query')
            return

    if tray!=0:
        d = loc_db.getChipsInTray(tray)
        d.sort_values('current_position',inplace=True)
        print(d.set_index('chip_id'))
        print(f'Total chips: {len(d)}')
        return

    if sorting_tray_summary:
        d = loc_db.getCurrentLocations()
        tray_list = d.current_tray.unique()
        tray_list.sort()

        print('ECON-T')
        for t in tray_list[((tray_list>8000) & (tray_list<10000))]:
            d = loc_db.getStatusForTray(t)
            print(f"Tray number {t:05d}: {len(d):02d} chips with grade {'/'.join(d.grade.unique())}")
        print('-'*40)
        print('ECON-D')
        for t in tray_list[((tray_list>18000) & (tray_list<20000))]:
            d = loc_db.getStatusForTray(t)
            print(f"Tray number {t:05d}: {len(d):02d} chips with grade {'/'.join((d.grade.str[:] +' '+ d.comments.str[:]).unique())}")

if __name__=="__main__":
    main()
