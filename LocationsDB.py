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
        data = (chip_id,'CHECKIN',tray_number,chip_position,tray_number,chip_position,location,status,str(timestamp))
        self.cursor.execute(sql_cmd_insert,data)

        sql_cmd_insert = '''INSERT INTO status (chip_id,chip_type,pkg_date,pkg_batch,grade,comments,time)
                            VALUES(?,?,?,?,?,?,?) '''
        data = (chip_id,chip_type,pkg_date,pkg_batch,"","",str(timestamp))
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
        df_.time = pd.to_datetime(df_.time)
        df_.sort_values('time',inplace=True)
        keep = (df_.groupby('chip_id')['time'].idxmax())
        return df_.loc[keep]

    def getCurrentStatus(self):
        """From pandas dataframe, return table which has the last entry from each chip"""
        df_ = self.loadStatusDatabase()
        df_.time = pd.to_datetime(df_.time)
        df_.sort_values('time',inplace=True)
        keep = (df_.groupby('chip_id')['time'].idxmax())
        return df_.loc[keep]

    def getChip(self,chip_id):
        """Returns the data from a specific chip"""
        return pd.read_sql_query(f"SELECT * FROM locations WHERE chip_id = {chip_id}",self.conn)

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

    def sortChip(self,chip_id,start_tray, start_position, new_tray, new_position,comments="",timestamp=None):
        sql_cmd_insert = '''INSERT INTO locations (chip_id,entry_type,initial_tray,initial_position,current_tray,current_position,location,comments,time)
                            VALUES(?,?,?,?,?,?,?,?,?) '''

        if timestamp is None:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        data = (chip_id,'SORTED',int(start_tray),int(start_position), int(new_tray),int(new_position),"WH14",comments,timestamp)
        self.cursor.execute(sql_cmd_insert,data)

    def setTestedStatus(self,chip_id,tray,position,comments="",timestamp=None):
        sql_cmd_insert = '''INSERT INTO locations (chip_id,entry_type,initial_tray,initial_position,current_tray,current_position,location,comments,time)
                            VALUES(?,?,?,?,?,?,?,?,?) '''

        if timestamp is None:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        data = (chip_id,'TESTED',int(tray),int(position), int(tray),int(position),"WH14",comments,timestamp)
        self.cursor.execute(sql_cmd_insert,data)

    def setChipGrade(self,chip_id,grade,comments="",timestamp=None):
        sql_cmd_insert = '''INSERT INTO status (chip_id,chip_type,pkg_date,pkg_batch,grade,comments,time)
                            VALUES(?,?,?,?,?,?,?) '''

        if timestamp is None:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.cursor.execute("SELECT * FROM status WHERE chip_id = ?",(chip_id,))
        chip_info = list(self.cursor.fetchone())
        data = (chip_info[0],chip_info[1],chip_info[2],chip_info[3],grade,comments,str(timestamp))
        self.cursor.execute(sql_cmd_insert,data)

    def getStatusForTray(self,tray_number):
        chip_list = self.getChipsInTray(tray_number).chip_id.values
        df_status = self.getCurrentStatus()
        return df_status[df_status.chip_id.isin(chip_list)]

    def getChipsInTray(self,tray_number):
        df_ = self.getCurrentLocations()
        return df_[df_.current_tray==tray_number]

    def rejectChip(self, chip_id, start_tray, start_position, new_tray, new_position, comments="", timestamp=None):        
        sql_cmd_insert = '''INSERT INTO locations (chip_id,entry_type,initial_tray,initial_position,current_tray,current_position,location,comments,time)
                            VALUES(?,?,?,?,?,?,?,?,?) '''

        if timestamp is None:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        data = (chip_id,'REJECTED',int(start_tray),int(start_position), int(new_tray),int(new_position),"WH14",comments,timestamp)
        self.cursor.execute(sql_cmd_insert,data)