#!/usr/bin/env python3

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QComboBox, QPushButton, QLabel, QHBoxLayout, QSpinBox, QTableWidget, QTableWidgetItem, QFileDialog
)

import os

import sys
sys.path.append('.')
from LocationsDB import LocationsDatabase

### second window, showing summary of chips that will be checked in
class ChipSummaryAndCheckinWindow(QWidget):
    def __init__(self, _data, _file_locations_db, _barcode):
        super().__init__()
        self.data = _data
        self.setWindowTitle("Chips To Check In")
        self.setGeometry(150, 150, 800, 20*len(_data))
        layout = QVBoxLayout()

        self.locations_db = LocationsDatabase(_file_locations_db)
        tray_exists = self.locations_db.checkTrayExists(self.data[0][2])

        table = QTableWidget()
        table.setRowCount(len(self.data))
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels([
            "Chip ID","Chip Type","Tray Number", "Tray Pos", "Location", "Pkg Date","Pkg Batch"
        ])
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        for i,c in enumerate(self.data):
            for j in range(7):
                table.setItem(i,j,QTableWidgetItem(str(c[j])))

        layout.addWidget(table)

        self.error_label=  QLabel('')
        self.error_label.setFixedHeight(0)
        layout.addWidget(self.error_label)
        # Button
        self.button = QPushButton("Confirm Checkin?", self)
        self.button.clicked.connect(self.checkin)
        layout.addWidget(self.button)
        if tray_exists:
            self.button.setEnabled(False)
            self.error_label.setText(f"<font color='red' size=6>Tray with barcode {_barcode} already exists in the locations database </font>")
            self.error_label.setFixedHeight(35)
        else:
            self.button.setEnabled(True)
        # Button
        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.clicked.connect(self.close)
        layout.addWidget(self.cancel_button)

        self.setLayout(layout)

    def checkin(self):
        for c in self.data:
            #example of what one chip's data looks like
            # [1050072, 'ECOND', 10500, 72, 'WH14', '3/2025', 'N61H52.00']
            c_id, c_type, c_tray, c_pos, c_loc, c_date, c_lot = c
            self.locations_db.checkin_chip(
                chip_id = c_id,
                chip_type = c_type,
                tray_number = c_tray,
                chip_position = c_pos,
                location = c_loc,
                pkg_date = c_date,
                pkg_batch = c_lot)
            print(c)
        self.close()
        self.locations_db.commitAndClose()

#primary gui window
class ECONCheckinWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ECON Tray Check In")
        self.setGeometry(100, 100, 600, 450)

        # Layout
        layout = QVBoxLayout()

        # Text input
        layout.addWidget(QLabel('Tray Barcode:'))
        self.barcode_text = QLineEdit(self)
        self.barcode_text.setPlaceholderText("Enter barcode...")
        self.barcode_text.textChanged.connect(self.validate_options)  # Connect textChanged to validation method
        layout.addWidget(self.barcode_text)



        layout.addWidget(QLabel('Number of Chips:'))
        self.n_chips = QSpinBox(self)
        self.n_chips.setRange(1, 90)  # Optional: set range
        self.n_chips.setValue(90)        # Default value
        layout.addWidget(self.n_chips)

        layout.addWidget(QLabel('Packaging Date:'))

        # Horizontal layout for dropdowns
        dropdown_pkg_date = QHBoxLayout()
        # First dropdown
        self.pkg_week = QComboBox(self)
        self.pkg_week.setPlaceholderText("Select Package Week")
        self.pkg_week.addItems([str(i) for i in range(1,53)])
        self.pkg_week.currentIndexChanged.connect(self.validate_options)  #validate the selections

        # self.pkg_week = QSpinBox(self)
        # self.pkg_week.setRange(1,52)
        dropdown_pkg_date.addWidget(self.pkg_week)
        backslash_label = QLabel("/", self)
        backslash_label.setStyleSheet("font-size: 14px;")
        backslash_label.setFixedWidth(10)
        dropdown_pkg_date.addWidget(backslash_label)

        # Second dropdown
        self.pkg_year = QSpinBox(self)
        self.pkg_year.setRange(2024,2026)
        self.pkg_year.setValue(2025)
        dropdown_pkg_date.addWidget(self.pkg_year)

        # Add the dropdown layout to the main layout
        layout.addLayout(dropdown_pkg_date)

        layout.addWidget(QLabel('Wafer Lot:'))
        self.wafer_lot = QComboBox(self)
        self.wafer_lot.setPlaceholderText("Select Wafer Lot")
        self.wafer_lot.addItems(["N61H30.00",
                                 "N61H52.00",
                                 "NCTA61 Wafs All",
                                 "N62A34 Wafs #2~3:5",
                                 "N62A34 Wafs #7~11",
                                 "N62A34 Wafs #13~14",
                                 "N62A34 Wafs #13~14",
                                 "N62A34 Wafs #16",
                                 "N62A34 Wafs #17~18",
                                 "N62A34 Wafs #19",
                                 "N62A34 Wafs #20",
                                 ])
        self.wafer_lot.currentIndexChanged.connect(self.validate_options) #validate the selections
        layout.addWidget(self.wafer_lot)

        layout.addWidget(QLabel('Location:'))
        self.location = QLineEdit(self)
        self.location.setText('WH14')
        layout.addWidget(self.location)

        # Button to open a file
        self.file_locations_db = QLineEdit(self)
        self.file_locations_db.setText('/asic/projects/E/ECON_PROD_TESTING/ECON_locations_db/database_files/ECON_Locations_DB.db')
        self.file_locations_db.textChanged.connect(self.validate_options) #validate the selections

        self.browse_button = QPushButton("Browse Files", self)
        self.browse_button.clicked.connect(self.open_file_dialog)
        self.browse_button.setFixedWidth(100)

        self.locations_db_label = QLabel('Locations Database File:')
        layout.addWidget(self.locations_db_label)
        db_layout = QHBoxLayout()
        db_layout.addWidget(self.browse_button)
        db_layout.addWidget(self.file_locations_db)
        layout.addLayout(db_layout)


        self.error_label=  QLabel('')
        self.error_label.setFixedHeight(0)
        layout.addWidget(self.error_label)

        # Button
        self.checkin_button = QPushButton("Check In", self)
        self.checkin_button.clicked.connect(self.start_checkin)
        self.checkin_button.setEnabled(False)
        layout.addWidget(self.checkin_button)

        # Button
        self.close_button = QPushButton("Close", self)
        self.close_button.clicked.connect(self.commit_and_close)
        layout.addWidget(self.close_button)

        # Set layout
        self.setLayout(layout)

    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "database_files/",
                                                   "Database file (*db)")
        if file_path:
            print(f"Selected file: {file_path}")
            self.file_locations_db.setText(file_path)

    def commit_and_close(self):
        print('Committing and Closing')
        self.close()


    # The checkin button will only appear if we have selected a value for the date and  wafer lot and have a valid barcode and locations database
    def validate_options(self):
        """Validate the barcode_text to contain 'ECON'"""
        pkg_date_valid = self.pkg_week.currentText() not in ["", "Select an option"]  # Check if a valid option is selected
        wafer_lot_valid = self.wafer_lot.currentText() not in ["", "Select an option"]  # Check if a valid option is selected
        barcode_valid =  ("ECONT-" in self.barcode_text.text() or "ECOND-" in self.barcode_text.text()) and len(self.barcode_text.text())==11
        locations_db = self.file_locations_db.text()
        locations_db_valid = os.path.exists(locations_db)
        if not locations_db_valid:
            self.locations_db_label.setText("Locations Database Files: <font color='red'>File Path Does Not Exist</font>")
        else:
            self.locations_db_label.setText("Locations Database Files:")

        #check that barcode matches wafer types
        barcode_wafer_match = True
        self.error_label.setText("")
        _barcode = self.barcode_text.text()
        if 'N62A34' in self.wafer_lot.currentText():
            try:
                barcode_number_group = int(self.barcode_text.text()[7:9])
                print(barcode_number_group)
                print(self.wafer_lot.currentText())
                if barcode_number_group==60 and self.wafer_lot.currentText()!="N62A34 Wafs #2~3:5": #Std wafers
                    self.error_label.setText(f"<font color='red' size=3>Tray barcode number {_barcode} does not match the selected wafer lot type {self.wafer_lot.currentText()}, expected to be 'N62A34 Wafs #2~3:5'</font>")
                    barcode_wafer_match = False
                elif barcode_number_group==61 and self.wafer_lot.currentText()!="N62A34 Wafs #7~11": #5% FF Corner
                    self.error_label.setText(f"<font color='red' size=3>Tray barcode number {_barcode} does not match the selected wafer lot type {self.wafer_lot.currentText()}, expected to be 'N62A34 Wafs #7~11'</font>")
                    barcode_wafer_match = False
                elif barcode_number_group==62 and self.wafer_lot.currentText()!="N62A34 Wafs #13~14": #10% FF Corner
                    self.error_label.setText(f"<font color='red' size=3>Tray barcode number {_barcode} does not match the selected wafer lot type {self.wafer_lot.currentText()}, expected to be 'N62A34 Wafs #13~14'</font>")
                    barcode_wafer_match = False
                elif barcode_number_group==63 and self.wafer_lot.currentText()!="N62A34 Wafs #16": #15% FF Corner
                    self.error_label.setText(f"<font color='red' size=3>Tray barcode number {_barcode} does not match the selected wafer lot type {self.wafer_lot.currentText()}, expected to be 'N62A34 Wafs #16'</font>")
                    barcode_wafer_match = False
                elif barcode_number_group==64 and self.wafer_lot.currentText()!="N62A34 Wafs #17~18": # Slow-Slow Corner
                    self.error_label.setText(f"<font color='red' size=3>Tray barcode number {_barcode} does not match the selected wafer lot type {self.wafer_lot.currentText()}, expected to be 'N62A34 Wafs #17~18'</font>")
                    barcode_wafer_match = False
                elif barcode_number_group==65 and self.wafer_lot.currentText()!="N62A34 Wafs #19": # FastP-SlowN Corner
                    self.error_label.setText(f"<font color='red' size=3>Tray barcode number {_barcode} does not match the selected wafer lot type {self.wafer_lot.currentText()}, expected to be 'N62A34 Wafs #19'</font>")
                    barcode_wafer_match = False
                elif barcode_number_group==66 and self.wafer_lot.currentText()!="N62A34 Wafs #20": # SlowP-FastN Corner
                    self.error_label.setText(f"<font color='red' size=3>Tray barcode number {_barcode} does not match the selected wafer lot type {self.wafer_lot.currentText()}, expected to be 'N62A34 Wafs #20'</font>")
                    barcode_wafer_match = False
                elif barcode_number_group<60 or barcode_number_group>66:
                    self.error_label.setText(f"<font color='red' size=3>Tray barcode number {_barcode} does not match the selected wafer lot type {self.wafer_lot.currentText()}, expected to be between 6000 and 6699</font>")
                    barcode_wafer_match = False
            except:
                #if no value in barcode, or it fails the integer casting
                barcode_wafer_match = False
        else:
            try:
                barcode_number_group = int(self.barcode_text.text()[7:9])
                if barcode_number_group>=60:
                    self.error_label.setText(f"<font color='red' size=3>Tray barcode number {_barcode} does not match the selected wafer lot type {self.wafer_lot.currentText()}, expected to be barcode less than 6000</font>")
                    barcode_wafer_match = False
            except:
                #if no value in barcode, or it fails the integer casting
                barcode_wafer_match = False

        if pkg_date_valid and wafer_lot_valid and barcode_valid and locations_db_valid and barcode_wafer_match:
            self.error_label.setFixedHeight(0)
            self.checkin_button.setEnabled(True)
        else:
            self.error_label.setFixedHeight(20)
            self.checkin_button.setEnabled(False)

    def start_checkin(self):
        _barcode = self.barcode_text.text()
        _pkg_week = int(self.pkg_week.currentText())
        _pkg_year = self.pkg_year.value()
        _pkg_date = f"{_pkg_week}/{_pkg_year}"
        _n_chips = self.n_chips.value()
        _wafer_lot = self.wafer_lot.currentText()
        _location = self.location.text()
        _file_locations_db = self.file_locations_db.text()
        print(f"Barcode: {_barcode}")
        print(f"Pkg Date: {_pkg_date}")
        print(f"Wafer Lot: {_wafer_lot}")

        _chip_type=_barcode[:5]
        if not _chip_type in ['ECONT','ECOND']:
            print('ERROR')
        _tray_number = int(_barcode.split('-')[-1])

        full_tray_data = []
        for _chip_pos in range(1,_n_chips + 1):
            _chip_id = _tray_number*100 + _chip_pos
            full_tray_data.append(
                [_chip_id, _chip_type, _tray_number, _chip_pos, _location, _pkg_date, _wafer_lot]
            )
        # Optional: Show it in the UI too
        self.chip_summary_window = ChipSummaryAndCheckinWindow(full_tray_data, _file_locations_db, _barcode)
        self.chip_summary_window.show()

        #reset values
        self.barcode_text.clear()
        self.n_chips.setValue(90)        # Default value
        self.checkin_button.setEnabled(False)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ECONCheckinWidget()
    window.show()
    sys.exit(app.exec())


