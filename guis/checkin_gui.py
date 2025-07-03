#!/usr/bin/env python3

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QComboBox, QPushButton, QLabel, QHBoxLayout, QSpinBox, QTableWidget, QTableWidgetItem
)

import sys
sys.path.append('.')
from LocationsDB import LocationsDatabase

class ChipSummaryWindow(QWidget):
    def __init__(self, _data):
        super().__init__()
        self.data = _data
        self.setWindowTitle("Chips To Check In")
        self.setGeometry(150, 150, 800, 20*len(_data))
        layout = QVBoxLayout()

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

        # Button
        self.button = QPushButton("Confirm Checkin?", self)
        self.button.clicked.connect(self.checkin)
        layout.addWidget(self.button)

        # Button
        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.clicked.connect(self.close)
        layout.addWidget(self.cancel_button)

        self.setLayout(layout)

    def checkin(self):
        for c in self.data:
            print(c)
        self.close()


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
        self.wafer_lot.addItems(["N61H30.00", "N61H52.00"])
        self.wafer_lot.currentIndexChanged.connect(self.validate_options) #validate the selections
        layout.addWidget(self.wafer_lot)

        layout.addWidget(QLabel('Location:'))
        self.location = QLineEdit(self)
        self.location.setText('WH14')
        layout.addWidget(self.location)

        layout.addWidget(QLabel('Locations Database File:'))
        self.db_file = QLineEdit(self)
        self.db_file.setText('')
        layout.addWidget(self.db_file)

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

    def commit_and_close(self):
        print('Committing and Closing')
        self.close()

    def validate_options(self):
        """Validate the barcode_text to contain 'ECON'"""
        pkg_date_valid = self.pkg_week.currentText() not in ["", "Select an option"]  # Check if a valid option is selected
        wafer_lot_valid = self.wafer_lot.currentText() not in ["", "Select an option"]  # Check if a valid option is selected
        barcode_valid =  ("ECONT-" in self.barcode_text.text() or "ECOND-" in self.barcode_text.text()) and len(self.barcode_text.text())==11

        if pkg_date_valid and wafer_lot_valid and barcode_valid:
            self.checkin_button.setEnabled(True)
        else:
            self.checkin_button.setEnabled(False)

    def start_checkin(self):
        _barcode = self.barcode_text.text()
        _pkg_week = int(self.pkg_week.currentText())
        _pkg_year = self.pkg_year.value()
        _pkg_date = f"{_pkg_week}/{_pkg_year}"
        _n_chips = self.n_chips.value()
        _wafer_lot = self.wafer_lot.currentText()
        _location = self.location.text()
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
        self.chip_summary_window = ChipSummaryWindow(full_tray_data)
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


