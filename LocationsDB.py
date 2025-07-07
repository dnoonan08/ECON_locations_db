import os
import sqlite3
from datetime import datetime

import pandas as pd


production_lot_map = {'N61.H30.00':'A',
                      'N61.H52.00':'B',
                      'P1':'C',
                      'P1v2':'D',
}

ECOND_grade_map = {10:'B', #0.99
                   9:'D', #1.01
                   8:'F', #1.03
                   7:'H', #1.05
                   6:'K', #1.08
                   5:'Q', #1.14
                   4:'W', #1.20
                   3:'Y',
                   2:'Y',
                   1:'Y',
                   0:'X',
                  }

qualToVoltage = {10:0.99,
                 9:1.01,
                 8:1.03,
                 7:1.05,
                 6:1.08,
                 5:1.14,
                 4:1.20,
                 3:1.26,
                 2:1.32}

ECONT_grade_map = {1:'A',
                   0:'X'}

class LocationsDatabase:
    def __init__(self,filename):
        if os.path.exists(filename):
            self.conn = sqlite3.connect(filename)
            self.cursor = self.conn.cursor()
        else:
            print("File Does Not Exists")

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

        sql_cmd_insert = '''INSERT INTO status (chip_id,chip_type,pkg_date,pkg_batch,grade,comments,time,serial_number,shipment_note)
                            VALUES(?,?,?,?,?,?,?,?,?) '''
        data = (chip_id,chip_type,pkg_date,pkg_batch,"","",str(timestamp),"","")
        self.cursor.execute(sql_cmd_insert,data)

    def checkTrayExists(self,tray_number,tableName='locations'):
        """Does a chip with this id already exist in the database"""
        self.cursor.execute(f"SELECT 1 FROM {tableName} WHERE initial_tray = ?", (tray_number,))
        result = self.cursor.fetchone()
        return result is not None

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
        sql_cmd_insert = '''INSERT INTO status (chip_id,chip_type,pkg_date,pkg_batch,grade,comments,time,serial_number,shipment_note)
                            VALUES(?,?,?,?,?,?,?,?,?) '''

        if timestamp is None:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.cursor.execute("SELECT * FROM status WHERE chip_id = ?",(chip_id,))
        chip_info = list(self.cursor.fetchone())
        data = (chip_info[0],chip_info[1],chip_info[2],chip_info[3],grade,comments,str(timestamp),"","")
        self.cursor.execute(sql_cmd_insert,data)

    def setChipSerialNumber(self,chip_id,serial_number,shipment_note="",timestamp=None):
        sql_cmd_insert = '''INSERT INTO status (chip_id,chip_type,pkg_date,pkg_batch,grade,comments,time,serial_number,shipment_note)
                            VALUES(?,?,?,?,?,?,?,?,?) '''

        if timestamp is None:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.cursor.execute("SELECT * FROM status WHERE chip_id = ?",(chip_id,))
        chip_info = list(self.cursor.fetchall()[-1])
        data = chip_info[:6] + [str(timestamp),serial_number,shipment_note]
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

    def shipTraysAndGenerateUploadCSV(self, trays, destination, grade_db, shipment_number=0, shipment_note="", timestamp=None, is_preseries=False):
        sql_cmd_insert = '''INSERT INTO locations (chip_id,entry_type,initial_tray,initial_position,current_tray,current_position,location,comments,time)
                            VALUES(?,?,?,?,?,?,?,?,?) '''

        csvFileName = f'ECON_upload_{shipment_number:04d}.csv'
        _csvFile = open(csvFileName,'w')
        _csvFile.write('KIND_OF_PART,SERIAL_NUMBER,BATCH_NUMBER,BARCODE,NAME_LABEL,LOCATION,INSTITUTION,COMMENT_DESCRIPTION,MANUFACTURER,PRODUCTION_DATE\n')

        if timestamp is None:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        df = self.getCurrentStatus().set_index('chip_id')

        full_chip_list = []

        if type(trays) is int:
            trays = [trays]

        for _tray_number in trays:
            print(_tray_number)
            chips = self.getChipsInTray(_tray_number)
            isECOND = (self.getStatusForTray(_tray_number).chip_type=='ECOND').all()
            isECONT = (self.getStatusForTray(_tray_number).chip_type=='ECONT').all()

            for _chip in chips.itertuples():
                chip_id = _chip.chip_id
                if _chip.entry_type=='SHIPPED':
                    print(f'Chip {chip_id:07d} is already listed as having been shipped, skipping')
                    continue
                if isECOND:
                    if is_preseries:
                        _grade=''
                        _voltage_str=''
                        _voltage_comment=''
                    else:
                        _quality = grade_db.getChip(chip_id).quality.iloc[-1]
                        _grade = ECOND_grade_map[_quality]
                        _voltage_str = f'-{qualToVoltage[_quality]:.2f}'
                        _voltage_comment = f"; passing at {qualToVoltage[_quality]:.2f}V"
                else:
                    try:
                        _quality = grade_db.getChip(chip_id).quality.iloc[-1]
                        _grade = ECONT_grade_map[_quality]
                        _voltage_str = ''
                        _voltage_comment = ''
                    except:
                        _quality = 0
                        print(f'Chip {chip_id:07d} not found in grades db!!!!!')
                        _grade = ECONT_grade_map[_quality]
                        _voltage_str = ''
                        _voltage_comment = 'Possibly untested chip'

                #get wafer production log grade
                _lot = production_lot_map[df.loc[chip_id].pkg_batch]
                #get packaging date
                _pkg_date = df.loc[chip_id].pkg_date

                #start buiding serial number
                _serial = '320ICEC'
                _serial += df.loc[chip_id].chip_type[-1:]
                _serial += _grade
                _serial += _lot
                _serial

                #count how many chips already have a serial number with the same grade and lot labels, increment by 1
                N = df.serial_number.str.startswith(_serial).sum()+1
                _serial += f'{N:05d}'

                if is_preseries:
                    _serial = f'320ICEC{df.loc[chip_id].chip_type[-1:]}{chip_id:07d}'

                #put this chip serial number into the dataframe
                df.loc[chip_id,'serial_number'] = _serial
                full_chip_list.append(_serial)
                #update the locations database with the shipment
                data = (chip_id,
                        'SHIPPED',
                        _chip.current_tray,
                        _chip.current_position,
                        _chip.current_tray,
                        _chip.current_position,
                        destination,
                        _chip.comments,
                        timestamp)
                self.cursor.execute(sql_cmd_insert,data)

                self.setChipSerialNumber(chip_id,_serial,shipment_note,timestamp)

                #write data into csv file
                T_D = 'T' if isECONT else 'D'
                KIND_OF_PART = f'ECON-{T_D}'
                SERIAL_NUMBER = _serial
                BATCH_NUMBER = f'{shipment_number:04d}-{_tray_number:05d}'
                if is_preseries:
                    BATCH_NUMBER = f'{shipment_number:04d}-PS-{_tray_number:05d}'
                BARCODE = _serial
                NAME_LABEL = f'ECON-{T_D}{_voltage_str}-{chip_id:07d}'
                LOCATION = "FNAL"
                INSTITUTION = "Fermi National Accelerator Lab."
                COMMENT_DESCRIPTION = f"ECON-{T_D} chip; FNAL chip ID {chip_id:07d} {_voltage_comment} {shipment_note}"
                COMMENT_DESCRIPTION = COMMENT_DESCRIPTION.replace(',',';') #replace any accidental commas with semicolons to avoid issues with CSV
                MANUFACTURER = "TSMC"
                PRODUCTION_DATE = datetime.strptime(_pkg_date + '-1', "%Y/%W-%w").strftime("%Y-%m-%d") #converts package week to date
                _csvFile.write(f'{KIND_OF_PART},{SERIAL_NUMBER},{BATCH_NUMBER},{BARCODE},{NAME_LABEL},{LOCATION},{INSTITUTION},{COMMENT_DESCRIPTION},{MANUFACTURER},{PRODUCTION_DATE}\n')
        _csvFile.close()

        csvFileName = f'ECON_shippingTool_{shipment_number:04d}.csv'
        _csvFile = open(csvFileName,'w')
        for chip in full_chip_list:
            _csvFile.write(f'{chip}\n')
        _csvFile.close()
