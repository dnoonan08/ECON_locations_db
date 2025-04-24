import sqlite3
from datetime import datetime

import pandas as pd


class LocationsDatabase:
    def __init__(self,filename):
        self.conn = sqlite3.connect(filename)
        self.cursor = self.conn.cursor()

    def commitAndClose(self):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()
        
    def checkin_chip(self,chip_id,chip_type,tray_number,chip_position,location,pkg_date,pkg_batch,status="",timestamp=None):
        """Add a new chip to the database"""
        sql_cmd_insert = '''INSERT INTO locations (chip_id,entry_type,initial_tray,initial_position,current_tray,current_position,location,comments,time)
                            VALUES(?,?,?,?,?,?,?,?,?) '''
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = (chip_id,'CHECKIN',tray_number,chip_position,tray_number,chip_position,location,status,str(datetime.now()))
        self.cursor.execute(sql_cmd_insert,data)

        sql_cmd_insert = '''INSERT INTO status (chip_id,chip_type,pkg_date,pkg_batch,grade,comments,time)
                            VALUES(?,?,?,?,?,?,?) '''
        data = (chip_id,chip_type,pkg_date,pkg_batch,"","",timestamp)
        self.cursor.execute(sql_cmd_insert,data)

    def chipInDatabase(self,id_value,tableName='locations'):
        """Does a chip with this id already exist in the database"""
        self.cursor.execute(f"SELECT 1 FROM {tableName} WHERE chip_id = ?", (id_value,))
        result = self.cursor.fetchone()
        return result is not None

    def loadLocationsDatabase(self):
        """Load full database to a pandas dataframe"""
        df_ = pd.read_sql_query("SELECT * from locations", self.conn)
        return df_

    def loadStatusDatabase(self):
        """Load full database to a pandas dataframe"""
        df = pd.read_sql_query("SELECT * from status", self.conn)
        return df

    def getCurrentLocations(self):
        """From pandas dataframe, return table which has the last entry from each chip"""
        df_ = self.loadLocationsDatabase()
        keep = (df_.groupby('chip_id')['time'].idxmax())
        return df_.loc[keep]

    def getChipTypeAndPkg(self,chip_id):
        """Returns the chip type, package date, package batch, and """
        self.cursor.execute("SELECT chip_type, pkg_date, pkg_batch FROM status WHERE chip_id = ?", (chip_id,))
        return self.cursor.fetchone()

    def checkPositionAlreadyFilled(self,new_tray,new_position):
        df_last = self.getCurrentLocations()
        return ((df_last.current_position==new_position) & (df_last.current_tray==new_tray)).sum()>0

    def checkForConflicts(self,trays_position_list):
        hasConflicts = False
        for t,p in trays_position_list:
            if checkPositionAlreadyFilled(self,t,p):
                hasConflicts = True
                print(f'Chip already in location {t}/{p:02d}')    
            if p<1 or p>90:
                hasConflicts = True
                print(f'New chip position {t}/{p:02d} is out of bounds for tray size')
        return hasConflicts

    def move_chip(self,chip_id,start_tray, start_position, new_tray, new_position,comments="",timestamp=None):
        sql_cmd_insert = '''INSERT INTO locations (chip_id,entry_type,initial_tray,initial_position,current_tray,current_position,location,comments,time)
                            VALUES(?,?,?,?,?,?,?,?,?) '''

        if timestamp is None:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        data = (chip_id,'SORT',int(start_tray),int(start_position), int(new_tray),int(new_position),"WH14",comments,timestamp)
        self.cursor.execute(sql_cmd_insert,data)

    def getChipsInTray(self,tray_number):
        df_ = self.getCurrentLocations()
        return df_[df_.current_tray==tray_number][['chip_id','current_tray','current_position']]