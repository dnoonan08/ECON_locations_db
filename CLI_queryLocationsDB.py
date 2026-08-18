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
@click.option("--grade",is_flag=True, help="Get the grades table for a given chip or tray")
@click.option("--xcs",is_flag=True, help="Generate XCS file for tray")
@click.option("--to_sort",is_flag=True, help="Get a summary for all trays to be sorted")
@click.option("--sorted",is_flag=True, help="Get a summary for all trays that have been sorted")
@click.option("--locations_db", default="fasic-chiptest.fnal.gov", help="Address of locations database host.")
def main(tray, chip, get_next_tray, location, history, status, grade, xcs, to_sort, sorted, locations_db):

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
            if fname:
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
            d.index.name = 'Tray Pos.'
            print(d.sort_index())
            print(f'Total chips: {len(d)}')
            return
        else:
            print('Must specify either a chip or tray number to query')
            return

    if grade:
        if chip!=0:
            d_grade = loc_db.loadGradesDatabase().set_index('chip_id')
            print(d_grade.loc[chip])
            return
        elif tray!=0:
            # d = loc_db.getChipsInTray(tray)
            d_grade = loc_db.getCurrentGrades().set_index('chip_id')
            d = loc_db.getChipsInTray(tray)[['current_position','chip_id']].set_index('chip_id')
            d = d.merge(d_grade,left_index=True,right_index=True).reset_index().set_index('current_position')
            d.index.name = 'Tray Pos.'
            pd.set_option('display.max_columns', None)
            pd.set_option('display.width', 240)
            columnList = ['chip_id',
                          'fraction',
                          '0.95V',
                          '0.97V',
                          '0.99V',
                          '1.01V',
                          '1.03V',
                          '1.05V',
                          '1.08V',
                          '1.14V',
                          '1.2V',
                          'quality',
                          'BIST',
                          'time',
                          ]
            print(d.sort_index()[columnList])
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

    if to_sort or sorted:
        df_grades = loc_db.getCurrentGrades().set_index('chip_id')
        df = loc_db.getCurrentLocations().set_index('chip_id')
        from LocationsDB import ECOND_grade_map, ECONT_grade_map

        df.loc[1000000:,'Grade'] = df_grades.loc[1000000:].quality.map(ECOND_grade_map)
        df.loc[:1000000,'Grade'] = df_grades.loc[:1000000].quality.map(ECONT_grade_map)

        d = df.groupby(['current_tray','Grade'])[['entry_type']].count().reset_index().pivot(index='current_tray',columns='Grade',values='entry_type').fillna(0).astype(int)
        d['K'] = d[['K','Q','W','X','Y']].sum(axis=1)
        d = d[['A','B','D','F','H','K']].copy(deep=True)
        d.columns = ['A','B','D','F','H','Fail']
        d['location'] = df[['current_tray','location']].drop_duplicates().set_index('current_tray')[['location']]

        if to_sort:
            print('ECON-D trays to be sorted')
            print(d[(d[['A','B','D','F']].sum(axis=1)>0) & (d.location=='WH14')].loc[10000:16500])
        else:
            sortedTrays = d[(d[['A','B','D','F','H']].sum(axis=1)==90) & (d.location=='WH14')].loc[18000:19000]
            _a=list(sortedTrays.index[sortedTrays.values[:,0]==90])
            _b=list(sortedTrays.index[sortedTrays.values[:,1]==90])
            _d=list(sortedTrays.index[sortedTrays.values[:,2]==90])
            _f=list(sortedTrays.index[sortedTrays.values[:,3]==90])
            _h=list(sortedTrays.index[sortedTrays.values[:,4]==90])

            partials = d[(d.Fail==0)&(d[['A','B','D','F']].sum(axis=1)<90)&(d.location=='WH14')].loc[18030:18999]
            partial_a = list(partials.index[partials.values[:,0]>0])[-1] if partials.values[:,0].sum()>0 else []
            partial_b = list(partials.index[partials.values[:,1]>0])[-1] if partials.values[:,1].sum()>0 else []
            partial_d = list(partials.index[partials.values[:,2]>0])[-1] if partials.values[:,2].sum()>0 else []
            partial_f = list(partials.index[partials.values[:,3]>0])[-1] if partials.values[:,3].sum()>0 else []
            partial_h = list(partials.index[partials.values[:,4]>0])[-1] if partials.values[:,4].sum()>0 else []

            print(f'Grade A: {len(_a)} Tray{"s" if len(_a)>1 else " "} - {_a}')
            print(f'Grade B: {len(_b)} Tray{"s" if len(_b)>1 else " "} - {_b}')
            print(f'Grade D: {len(_d)} Tray{"s" if len(_d)>1 else " "} - {_d}')
            print(f'Grade F: {len(_f)} Tray{"s" if len(_f)>1 else " "} - {_f}')
            print(f'Grade H: {len(_h)} Tray{"s" if len(_h)>1 else " "} - {_h}')

            print()
            print('Partial Trays')
            print(f'    A: {partial_a}, B: {partial_b}, D: {partial_d}, F: {partial_f}, H: {partial_h}')


if __name__=="__main__":
    main()
