import sqlite3
from datetime import datetime

import pandas as pd


class GradesDatabase:
    def __init__(self,filename):
        self.conn = sqlite3.connect(filename)
        self.cursor = self.conn.cursor()

    def commitAndClose(self):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()

    def loadGradesDatabase(self):
        """Load full database to a pandas dataframe"""
        df_ = pd.read_sql_query("SELECT * from grades", self.conn,index_col='index')
        return df_

    def getCurrentGrades(self):
        """Loads the database selecting only the latest grades when there are multiple values"""
        df_ = self.loadGradesDatabase().reset_index(drop=True)
        df_.time = pd.to_datetime(df_.time)
        df_.sort_values('time',inplace=True)
        keep = (df_.groupby('chip_id')['time'].idxmax())
        return df_.loc[keep]

    def getChip(self,chip_id):
        df_ = pd.read_sql_query(f"SELECT * from grades WHERE chip_id = {chip_id}", self.conn,index_col='index')
        return df_

    def setChipGrade(self, chip_id, fraction, err_rate_0p99, err_rate_1p01, err_rate_1p03, err_rate_1p05, err_rate_1p08, err_rate_1p14, err_rate_1p20, err_rate_1p26, err_rate_1p32, quality, timestamp=None):
        chip_type='D' if chip_id>=1000000 else 'T'
        _barcode = f'ECON{chip_type}-{int(chip_id/100):05d}'
        _position = chip_id%100

        sql_cmd_insert = '''INSERT INTO grades (barcode,position,fraction,"0.99V","1.01V","1.03V","1.05V","1.08V","1.14V","1.2V","1.26V","1.32V",quality,chip_id,time)
                            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) '''
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        data = (_barcode, _position, fraction, err_rate_0p99, err_rate_1p01, err_rate_1p03, err_rate_1p05, err_rate_1p08, err_rate_1p14, err_rate_1p20, err_rate_1p26, err_rate_1p32, quality, chip_id, timestamp)
        self.cursor.execute(sql_cmd_insert,data)

    ### to add,
    ###    - function to look up grade of specific chip
    ###    - function to assign grade for a specific chip
    ####      setChipGradE(chip_id, fraction     0.99V     1.01V         1.03V     1.05V     1.08V     1.14V          1.2V  1.26V  1.32V  quality)
    ###    - any other function we need when accessing the grades database
