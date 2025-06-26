#!/usr/bin/python

import numpy as np
import pandas as pd

import sys
sys.path.append('..')
from LocationsDB import LocationsDatabase
from GradesDB import GradesDatabase

from datetime import datetime
import os

_cwd = os.path.dirname(os.path.abspath(__file__))

loc_db = LocationsDatabase(f'{_cwd}/database_files/ECON_Locations_DB.db')
df = loc_db.getCurrentLocations()

grades_db = GradesDatabase(f'{_cwd}/database_files/test_grade_database.db')
df_grades = grades_db.loadGradesDatrabase()


df = df.merge(df_grades[['chip_id','quality']],on='chip_id',how='outer').fillna(-1)
df.quality = df.quality.astype(int)

grades_D = {-1:'NoTest',
          0:'Fail',
          1:'Fail',
          2:'Fail',
          3:'Fail',
          4:'Fail 1.2V',
          5:'Up 1.14',
          6:'Down 1.08',
          7:'Strange 1.05',
          8:'Charm 1.03',
          9:'Beauty 1.01',
          10:'Truth 0.99',
         }
grades_T = {-1:'NoTest',
          0:'Fail',
          1:'Pass',
           }

df['grade'] = np.where(df.chip_id>1000000,
                       df.quality.map(grades_D),
                       df.quality.map(grades_T))

d = df.groupby(['current_tray','grade'])[['chip_id']].count().reset_index()



d = d.pivot(columns='grade',index='current_tray',values='chip_id').reset_index()
d.columns.name=None
d = d.fillna(0).astype(int)

d_T = d[d.current_tray<10000][['current_tray','Pass','Fail','NoTest']]
d_D = d[d.current_tray>=10000][['current_tray','Truth 0.99','Beauty 1.01','Charm 1.03','Strange 1.05','Down 1.08','Up 1.14','Fail 1.2V','Fail','NoTest']]

d_D.set_index('current_tray',inplace=True)
d_T.set_index('current_tray',inplace=True)

d_D['Total'] = d_D.sum(axis=1)
d_T['Total'] = d_T.sum(axis=1)

_location = df.groupby(['current_tray'])[['location']].first()
d_D['Location'] = _location['location']
d_T['Location'] = _location['location']

#mark preseries
d_D['Preseries'] = 0
d_T['Preseries'] = 0
d_T.loc[[8007,8008,8009,8010,8011,8012],['Pass','Fail','NoTest']] = 0
d_T.loc[[8007,8008,8009,8010,8011,8012],'Preseries'] = d_T.loc[[8007,8008,8009,8010,8011,8012],'Total']
d_D.loc[[18007,18008,18009,18010,18011,18012],['NoTest']] = 0
d_D.loc[[18007,18008,18009,18010,18011,18012],'Preseries'] = d_D.loc[[18007,18008,18009,18010,18011,18012],'Total']


d_D['isSorted'] = d_D.index>17000
d_T['isSorted'] = (d_T.Pass==d_T.Total) | (d_T.Fail==d_T.Total) | (d_T.Preseries==d_T.Total)

d_D = d_D[['Truth 0.99',
           'Beauty 1.01',
           'Charm 1.03',
           'Strange 1.05',
           'Down 1.08',
           'Up 1.14',
           'Fail 1.2V',
           'Fail',
           'NoTest',
           'Preseries',
           'Total',
           'Location',
           'isSorted']]
d_T = d_T[['Pass', 'Fail', 'NoTest', 'Preseries', 'Total', 'Location', 'isSorted']]




import gspread
gc = gspread.service_account()
sh = gc.open("ECON Status")

availability = sh.get_worksheet(0)
econd = sh.get_worksheet(1)
econt = sh.get_worksheet(2)
econd_timeseries = sh.get_worksheet(3)
econt_timeseries = sh.get_worksheet(4)

n_D_sorted = d_D[(d_D.Location=='WH14') & (d_D.isSorted)].sum().values[:11].astype(int).tolist()
n_D_unsorted = d_D[(d_D.Location=='WH14') & (~d_D.isSorted)].sum().values[:11].astype(int).tolist()
n_D_shipped = d_D[(d_D.Location!='WH14')].sum().values[:11].astype(int).tolist()

n_T_sorted = d_T[(d_T.Location=='WH14') & (d_T.isSorted)].sum().values[:5].astype(int).tolist()
n_T_unsorted = d_T[(d_T.Location=='WH14') & (~d_T.isSorted)].sum().values[:5].astype(int).tolist()
n_T_shipped = d_T[(d_T.Location!='WH14')].sum().values[:5].astype(int).tolist()

availability.update([n_D_sorted,n_D_unsorted,n_D_shipped],'B5')
availability.update([n_T_sorted,n_T_unsorted,n_T_shipped],'B12')

#availability.update([['Last Updated:',datetime.now().strftime("%Y-%m-%d %H:%M")]],'A1')
econd_timeseries.append_row([datetime.now().strftime("%Y-%m-%d %H:%M")] + np.array([n_D_sorted,n_D_unsorted,n_D_shipped]).T.flatten().tolist())
econt_timeseries.append_row([datetime.now().strftime("%Y-%m-%d %H:%M")] + np.array([n_T_sorted,n_T_unsorted,n_T_shipped]).T.flatten().tolist())

econd.update([['Last Updated:',datetime.now().strftime("%Y-%m-%d %H:%M")]],'A1')
econd.update([d_D.reset_index().columns.values.tolist()] + d_D.reset_index().values.tolist(),'A3')

econt.update([['Last Updated:',datetime.now().strftime("%Y-%m-%d %H:%M")]],'A1')
econt.update([d_T.reset_index().columns.values.tolist()] + d_T.reset_index().values.tolist(),'A3')
