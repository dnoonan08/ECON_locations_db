#!/usr/bin/env python3

from PyQt6.QtWidgets import (
    QApplication, 
    QWidget, 
    QVBoxLayout, 
    QLineEdit, 
    QComboBox, 
    QPushButton, 
    QLabel, 
    QHBoxLayout, 
    QSpinBox, 
    QTableWidget, 
    QTableWidgetItem, 
    QFileDialog, 
    QListWidget, 
    QMessageBox,
    QFrame,
    QDialogButtonBox
)

import os
from collections import Counter

import sys
sys.path.append('.')
from LocationsDB import LocationsDatabase,ECOND_grade_map
from GradesDB import GradesDatabase

# Main window
class ShipmentWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ship Trays")
        self.setGeometry(150, 150, 400, 200)
        layout = QVBoxLayout()

        # Variables
        self.tray_list = set()
        self.locations_db = None
        self.grade_db = None

        # Data base initialization
        # Locations DB
        self.file_locations_db = QLineEdit(self)
        self.file_locations_db.setText('/asic/projects/E/ECON_PROD_TESTING/ECON_locations_db/database_files/ECON_Locations_DB.db')
        self.file_locations_db.textChanged.connect(self.validate_options)

        self.loc_button = QPushButton("Browse Files", self)
        self.loc_button.clicked.connect(self.open_loc_file_dialog)
        self.loc_button.setFixedWidth(100)

        self.locations_db_label = QLabel('Locations Database File:')
        layout.addWidget(self.locations_db_label)
        loc_layout = QHBoxLayout()
        loc_layout.addWidget(self.loc_button)
        loc_layout.addWidget(self.file_locations_db)
        layout.addLayout(loc_layout)

        # Grade DB
        self.file_grade_db = QLineEdit(self)
        self.file_grade_db.setText('/asic/projects/E/ECON_PROD_TESTING/ECON_locations_db/database_files/test_grade_database.db')
        self.file_grade_db.textChanged.connect(self.validate_options)

        self.grade_button = QPushButton("Browse Files", self)
        self.grade_button.clicked.connect(self.open_grade_file_dialog)
        self.grade_button.setFixedWidth(100)

        self.grade_db_label = QLabel('Grade Database File:')
        layout.addWidget(self.grade_db_label)
        grade_layout = QHBoxLayout()
        grade_layout.addWidget(self.grade_button)
        grade_layout.addWidget(self.file_grade_db)
        layout.addLayout(grade_layout)
        # Button
        self.load_button = QPushButton("Load Databases", self)
        self.load_button.clicked.connect(self.load_databases)
        self.load_button.setEnabled(False)
        layout.addWidget(self.load_button)

        # Separator line
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.Shape.HLine)
        separator1.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator1)

        # Tray list input
        layout.addWidget(QLabel('Tray Barcode:'))
        self.barcodes = QLineEdit(self)
        self.barcodes.textChanged.connect(self.validate_options) #validate the selections
        self.barcodes.setPlaceholderText("Enter barcode for trays, use comma to separate multiple barcodes.")
        layout.addWidget(self.barcodes)

        # Tray list display
        self.tray_list_widget = QListWidget()
        layout.addWidget(self.tray_list_widget)

        # Grade list display
        self.grade_list_widget = QListWidget()
        layout.addWidget(self.grade_list_widget)

        self.add_disable_reason_label = QLabel("")
        layout.addWidget(self.add_disable_reason_label)
        # Buttons
        button_layout = QHBoxLayout()
        # Add Button 
        self.add_button = QPushButton("Add", self)
        self.add_button.clicked.connect(self.append_barcode)
        button_layout.addWidget(self.add_button)

        # Remove Button
        self.remove_button = QPushButton("Remove", self)
        self.remove_button.clicked.connect(self.remove_barcode)
        button_layout.addWidget(self.remove_button)

        self.clear_button = QPushButton("Clear", self)
        self.clear_button.clicked.connect(self.clear_barcode)
        button_layout.addWidget(self.clear_button)

        layout.addLayout(button_layout)

        # Destination input
        layout.addWidget(QLabel("Destination:"))
        self.destination = QLineEdit()
        self.destination.setPlaceholderText("Enter destination.")
        self.destination.textChanged.connect(self.validate_options) #validate the selections
        layout.addWidget(self.destination)

        # Shipment number input
        layout.addWidget(QLabel("Shipment Number:"))
        self.shipment_number = QSpinBox()
        self.shipment_number.setMinimum(1)
        self.shipment_number.setValue(1)
        layout.addWidget(self.shipment_number)

        # Shipment note input
        layout.addWidget(QLabel("Shipment Note:"))
        self.shipnote = QLineEdit()
        self.shipnote.setPlaceholderText("Enter shipment note (optional).")
        layout.addWidget(self.shipnote)


        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.HLine)  # Horizontal line
        separator2.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator2)

        shipment_button_layout = QHBoxLayout()

        # Ship button
        self.ship_disable_reason_label = QLabel("")
        layout.addWidget(self.ship_disable_reason_label)
        self.ship_button = QPushButton("Ship", self)
        self.ship_button.clicked.connect(self.ship)
        shipment_button_layout.addWidget(self.ship_button)
        # Save & Exit button
        self.close_button = QPushButton("Save and Exit", self)
        self.close_button.clicked.connect(self.close)
        shipment_button_layout.addWidget(self.close_button)

        self.validate_options()

        layout.addLayout(shipment_button_layout)
        self.setLayout(layout)


    def update_tray_list(self):
        qualities = []
        self.tray_list_widget.clear()
        for tray in sorted(self.tray_list):
            self.tray_list_widget.addItem(tray)
            tray_number = int(tray.split('-')[-1])
            chips = self.locations_db.getChipsInTray(tray_number)
            qualities+=[self.grade_db.getChip(chip.chip_id).quality.iloc[-1] for chip in chips.itertuples()]
        counted_qualities = sorted(Counter(qualities).items(), reverse=True)
        self.grade_list_widget.clear()
        for q,c in counted_qualities:
            self.grade_list_widget.addItem(f"{ECOND_grade_map[q]}:\t{c}")
        self.validate_options()
        

    def append_barcode(self):
        ignore_different_grades=False
        skip_different_grades=False
        warning_dialog = ""
        
        for barcode in self.barcodes.text().split(','):
            barcode = barcode.strip()
            try:                
                ECON_type = barcode.split('-')[0]
                tray_number = int(barcode.split('-')[-1])
                tray_exists = ((ECON_type == 'ECOND' and tray_number >= 10000) or (ECON_type == 'ECONT' and tray_number < 10000)) and self.locations_db.checkTrayExists(tray_number)
                chips = self.locations_db.getChipsInTray(tray_number)
                qualities = [self.grade_db.getChip(chip.chip_id).quality.iloc[-1] for chip in chips.itertuples()]
                counted_qualities = sorted(Counter(qualities).items(), reverse=True)
            except Exception as e:
                error_dialog = QMessageBox.critical(self,
                "Error",
                f"Error when checking tray {barcode} in locations database:\n{e}")
                return
            if not ignore_different_grades and len(counted_qualities)>1:
                if skip_different_grades:
                    continue
                question=f'Tray:{barcode} cotains chip with different grades:\n'
                for q,c in counted_qualities:
                    question+=f"{ECOND_grade_map[q]}: {c}\n"
                question+='Do you want to add this tray anyway?'
                reply = QMessageBox.question(self,
                        'Confirmation',
                        question,
                        QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.YesToAll | QMessageBox.StandardButton.NoToAll)
                if reply == QMessageBox.StandardButton.No:
                    continue
                elif reply == QMessageBox.StandardButton.YesToAll:
                    ignore_different_grades=True
                elif reply == QMessageBox.StandardButton.NoToAll:                
                    skip_different_grades=True
                    continue
            if tray_exists:
                self.tray_list.add(barcode)
            else:
                warning_dialog += f"{barcode}, "
        if warning_dialog:
            warning_dialog = warning_dialog[:-2]  # Remove trailing comma and space
            QMessageBox.warning(self,
            "Tray(s) not Found",
            f"The following tray(s) do not exist in the locations database:\n{warning_dialog}")
        self.barcodes.clear()
        self.update_tray_list()

    def remove_barcode(self):
        for barcode in self.barcodes.text().split(','):
            barcode = barcode.strip()
            if barcode in self.tray_list:
                self.tray_list.remove(barcode)
        self.barcodes.clear()
        self.update_tray_list()

    def clear_barcode(self):
        self.tray_list.clear()
        self.update_tray_list()

    def ship(self):
        reply = QMessageBox.question(self,
                                     'Confirmation',
                                     f'The following tray(s) will be shipped:\n{",".join(sorted(self.tray_list))}\nTo: {self.destination.text()}\nShipment Number: {self.shipment_number.value()}\n{"Shipment Note: "+self.shipnote.text() if self.shipnote.text() else "with no shipment note"}\n\nDo you want to proceed?')
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.locations_db.shipTraysAndGenerateUploadCSV(
                    trays=list(int(barcode.split('-')[-1]) for barcode in self.tray_list),
                    # trays=list(self.tray_list),
                    destination=self.destination.text(),
                    grade_db = self.grade_db,
                    shipment_number = self.shipment_number.value(),
                    shipment_note =  self.shipnote.text()
                )
                self.barcodes.clear()
                self.destination.clear()
                self.shipment_number.setValue(self.shipment_number.value()+1)
                self.shipnote.clear()
                self.tray_list.clear()
                self.update_tray_list()
            except Exception as e:
                error_dialog = QMessageBox.critical(self,"Error",f"Error when updating shipment process in location database:\n{e}\nPlease check if the tray is tested and sorted")
        else:
            pass

    
    def open_loc_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "database_files/","Database file (*db)")
        if file_path:
            self.file_locations_db.setText(file_path)

    def open_grade_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "database_files/","Database file (*db)")
        if file_path:
            self.file_grade_db.setText(file_path)

    def validate_options(self):
        locations_db = self.file_locations_db.text()
        locations_db_valid = os.path.exists(locations_db)
        if not locations_db_valid:
            self.locations_db_label.setText("Locations Database Files: <font color='red'>File Path Does Not Exist</font>")
        else:
            self.locations_db_label.setText("Locations Database Files:")
        grade_db = self.file_grade_db.text()
        grade_db_valid = os.path.exists(grade_db)
        if not grade_db_valid:
            self.grade_db_label.setText("Grade Database Files: <font color='red'>File Path Does Not Exist</font>")
        else:
            self.grade_db_label.setText("Grade Database Files:")
        if grade_db_valid and locations_db_valid:
            self.load_button.setEnabled(True)
        else:
            self.load_button.setEnabled(False)
        
        databases_loaded = self.locations_db is not None and self.grade_db is not None
        add_remove_disable_reason = ""
        if not databases_loaded:
            add_remove_disable_reason+="Databases not loaded. "
        if self.barcodes.text()=="":
            add_remove_disable_reason+="No barcode entered. "
        if not add_remove_disable_reason:
            self.add_button.setEnabled(True)
            self.remove_button.setEnabled(True)
            self.add_disable_reason_label.setText("")

        else:
            self.add_button.setEnabled(False)
            self.remove_button.setEnabled(False)
            self.add_disable_reason_label.setText(f"<font color='red'>{add_remove_disable_reason}</font>")

        ship_disable_reason = ""
        if not self.tray_list:
            ship_disable_reason+="No trays to ship. "
        if not self.destination.text().strip():
            ship_disable_reason+="Destination is required. "
        if not ship_disable_reason:
            self.ship_disable_reason_label.setText("")
            self.ship_button.setEnabled(True)
        else:   
            self.ship_button.setEnabled(False)
            self.ship_disable_reason_label.setText(f"<font color='red'>{ship_disable_reason}</font>")
        
    def load_databases(self):
        try:
            self.locations_db = LocationsDatabase(self.file_locations_db.text())
            self.grade_db = grade_db = GradesDatabase(self.file_grade_db.text())
            self.validate_options()
        except Exception as e:
            error_dialog = QMessageBox.critical(self,"Database Load Error",f"Error loading databases:\n{e}")
            self.locations_db = None
            self.grade_db = None

    def close(self):
        self.locations_db.commitAndClose()
        super().close()
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ShipmentWindow()
    window.show()
    sys.exit(app.exec())
