#!/usr/bin/python3

import numpy as np
import click

from LocationsDB import LocationsDatabase

import pandas as pd
pd.set_option('display.max_rows', 100)


@click.command()
@click.option("--tray",default=0, show_default=True, help="Tray number to query")
@click.option("--chip",default=0, show_default=True, help="Chip number to query")
@click.option("--get_next_tray",is_flag=True, help="Query the database to determine the next tray number in the sequence")
@click.option("--location",is_flag=True, help="Check the current location of a given chip or tray")
@click.option("--history",is_flag=True, help="Get the full history of a chip")
@click.option("--status",is_flag=True, help="Get the status table for a given chip or tray")
@click.option("--sorting_tray_summary",is_flag=True, help="Get a summary for all sorting trays")
@click.option("--locations_db", default="/asic/projects/E/ECON_PROD_TESTING/ECON_locations_db/database_files/ECON_Locations_DB.db", help="Log file to log chip movements.")
def main(tray, chip, get_next_tray, location, history, status, sorting_tray_summary, locations_db):

    loc_db = LocationsDatabase(locations_db)

    if get_next_tray:
        full_barcode_list = loc_db.getCurrentLocations().current_tray.unique().tolist()
        full_barcode_list += loc_db.getCurrentLocations().initial_tray.unique().tolist()
        full_barcode_list = np.unique(full_barcode_list)

        ECONT_initial = full_barcode_list[full_barcode_list<7000].max() + 1
        ECONT_sorting = full_barcode_list[(full_barcode_list<9900) & (full_barcode_list>=7000)].max() + 1
        ECOND_initial = full_barcode_list[(full_barcode_list>=10000) & (full_barcode_list<17000)].max() + 1
        ECOND_sorting = full_barcode_list[(full_barcode_list>=17000) & (full_barcode_list<19900)].max() + 1

        print("Next tray numbers to use:")

        print(f"    ECON-T checkin: ECONT-{ECONT_initial:05d}")
        print(f"           sorting: ECONT-{ECONT_sorting:05d}")
        print(f"    ECON-D checkin: ECOND-{ECOND_initial:05d}")
        print(f"           sorting: ECOND-{ECOND_sorting:05d}")

    if history:
        if chip!=0:
            print(loc_db.getChip(chip))
            return
        else:
            print('The unique chip_id you want to get the history of must be specified')
            return

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
