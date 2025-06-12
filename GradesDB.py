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

    def loadGradesDatrabase(self):
        """Load full database to a pandas dataframe"""
        df_ = pd.read_sql_query("SELECT * from grades", self.conn,index_col='index')
        return df_

    ### to add,
    ###    - function to look up grade of specific chip
    ###    - function to assign grade for a specific chip
    ###    - any other function we need when accessing the grades database
