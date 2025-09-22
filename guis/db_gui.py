#!/usr/bin/env python3

from PyQt6.QtWidgets import (
    QTabWidget,
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
    QDialogButtonBox,
    QGridLayout,
    QSizePolicy,
    QDialog
)
from PyQt6.QtGui import QIntValidator
from PyQt6.QtCore import Qt
import os
import pandas as pd
from collections import Counter
from datetime import datetime
import sys
sys.path.append('.')
from LocationsDB import LocationsDatabase,ECOND_grade_map,ECONT_grade_map
from GradesDB import GradesDatabase

Palette_Quality={
    'A':    '#00ff00',
    'B':    '#00ff00', 
    'D':    '#041a00', 
    'F':    '#202e00', 
    'H':    '#4b6200', 
    'K':    '#808000',
    'Q':    '#b9d900',
    'W':    '#f0f800',
    'Y':    '#f87e00',
    'X':    '#ff0000',
    'Not Tested':   '#555555'
}

Palette_Entry={
    'CHECKIN': '#555555',
    'TESTED': '#008080',
    'SORTED': '#77dd77',
    'SHIPPED': '#00ff00',
    'REJECTED': '#ff0000',
}

Palette_PF={
    'Pass':  '#00ff00',
    'Fail':  '#ff0000',
    'Not Tested': '#555555',
}
# Main window
class DBWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Database Management")
        self.setGeometry(150, 150, 1500, 800)
        layout = QHBoxLayout()

        left_panel = QVBoxLayout()

        self.df = pd.DataFrame()
        self.df_picked = pd.DataFrame()
        self.parameters = []
        # Variables
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
        left_panel.addWidget(self.locations_db_label)
        loc_layout = QHBoxLayout()
        loc_layout.addWidget(self.file_locations_db)
        loc_layout.addWidget(self.loc_button)
        left_panel.addLayout(loc_layout)

        # Grade DB
        self.file_grade_db = QLineEdit(self)
        self.file_grade_db.setText('/asic/projects/E/ECON_PROD_TESTING/ECON_locations_db/database_files/test_grade_database.db')
        self.file_grade_db.textChanged.connect(self.validate_options)

        self.grade_button = QPushButton("Browse Files", self)
        self.grade_button.clicked.connect(self.open_grade_file_dialog)
        self.grade_button.setFixedWidth(100)

        self.grade_db_label = QLabel('Grade Database File:')
        left_panel.addWidget(self.grade_db_label)
        grade_layout = QHBoxLayout()
        
        grade_layout.addWidget(self.file_grade_db)
        grade_layout.addWidget(self.grade_button)
        left_panel.addLayout(grade_layout)
        # Load Button
        self.load_button = QPushButton("Load Databases", self)
        self.load_button.clicked.connect(self.load_databases)
        self.load_button.setEnabled(False)
        left_panel.addWidget(self.load_button)

        # Separator line
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.Shape.HLine)
        separator1.setFrameShadow(QFrame.Shadow.Sunken)
        left_panel.addWidget(separator1)

        # Tray list input
        self.barcode_label=QLabel('Tray Barcode:')
        left_panel.addWidget(self.barcode_label)
        self.barcode = QLineEdit(self)
        self.barcode.textChanged.connect(self.validate_options) #validate the selections
        self.barcode.setPlaceholderText("Enter barcode for the tray.")
        self.select_button = QPushButton("Select Tray", self)
        self.select_button.setFixedWidth(100)
        self.select_button.clicked.connect(self.select_tray)
        tray_layout = QHBoxLayout()
        tray_layout.addWidget(self.barcode)
        tray_layout.addWidget(self.select_button)
        left_panel.addLayout(tray_layout)
        
        tab_widget = QTabWidget()
        # Table for picked summary
        tab_picked_content = QWidget()
        tab_picked_layout = QVBoxLayout(tab_picked_content)
        self.picked_table = QTableWidget()
        tab_picked_layout.addWidget(self.picked_table)

        # Table for tray summary
        tab_tray_content = QWidget()
        tab_tray_layout = QVBoxLayout(tab_tray_content)
        self.tray_table = QTableWidget()
        tab_tray_layout.addWidget(self.tray_table)

        # Add tabs to the QTabWidget
        tab_widget.addTab(tab_picked_content,"Selected")
        tab_widget.addTab(tab_tray_content, "Tray")
        left_panel.addWidget(tab_widget)
        
        # Separator line
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.HLine)
        separator2.setFrameShadow(QFrame.Shadow.Sunken)
        left_panel.addWidget(separator2)

        # Operations
        operation_layout = QHBoxLayout()
        self.change_disable_label = QLabel(self)
        self.change_disable_label.setText("")
        left_panel.addWidget(self.change_disable_label)
        self.operations = QComboBox(self)
        self.operations.setPlaceholderText("Select Operation")
        self.operations.addItems(["Change Status","Change Grade","Change Location"])
        self.operations.setCurrentText("Change Status")
        self.operations.currentIndexChanged.connect(self.update_options)
        operation_layout.addWidget(self.operations)
        self.options = QComboBox(self)    
        self.options.setPlaceholderText("Select Option")
        self.options.addItems(["CHECKIN","TESTED","SORTED","SHIPPED","REJECTED"])
        self.options.setCurrentText("REJECTED")
        operation_layout.addWidget(self.options)
        left_panel.addLayout(operation_layout)
        # Buttons
        button_layout = QHBoxLayout()
        # change button 
        self.change_button = QPushButton("Change", self)
        self.change_button.clicked.connect(self.change)
        # close button
        self.close_button = QPushButton("Save and Exit", self)
        self.close_button.clicked.connect(self.close)
        button_layout.addWidget(self.change_button,stretch=1)
        button_layout.addWidget(self.close_button,stretch=1)
        left_panel.addLayout(button_layout)

        layout.addLayout(left_panel)
        Vseparator = QFrame()
        Vseparator.setFrameShape(QFrame.Shape.VLine)
        Vseparator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(Vseparator)

        # Chip panel
        chip_panel = QGridLayout()
        self.chip_bottons=[QPushButton(f"{i+1}\nNo Chip") for i in range(90)]
        for i in range(15):
            for j in range(6):
                self.chip_bottons[i*6+j].setCheckable(True)
                self.chip_bottons[i*6+j].toggled.connect(self.update_picked)
                self.chip_bottons[i*6+j].setFixedSize(50, 50)
                self.chip_bottons[i*6+j].setEnabled(False)
                chip_panel.addWidget(self.chip_bottons[i*6+j],i,j)
        layout.addLayout(chip_panel)

        # Right panel
        right_panel = QVBoxLayout()
        right_panel.setAlignment(Qt.AlignmentFlag.AlignTop)
        # Palette control panel
        palette_panel_control = QHBoxLayout()
        palette_panel_control.addWidget(QLabel('Color by:'))
        self.palette = QComboBox(self)
        self.palette.addItems(["Quality","Entry Type","Pass/Fail","No Color"])
        self.palette.setCurrentIndex(0)
        self.palette.currentIndexChanged.connect(self.update_pick_buttons)
        palette_panel_control.addWidget(self.palette)
        right_panel.addLayout(palette_panel_control)
        # Legend panel
        self.legend_panel = QVBoxLayout()
        right_panel.addLayout(self.legend_panel)
        # (Un)select all
        right_panel.addStretch()
        self.select_all_button = QPushButton("Select All")
        self.select_all_button.clicked.connect(self.select_all)
        right_panel.addWidget(self.select_all_button)
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear)
        right_panel.addWidget(self.clear_button)
        layout.addLayout(right_panel)
        self.validate_options()
        self.setLayout(layout)
        
    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clear_layout(item.layout())

    def select_tray(self):
        warning_dialog = ""
        barcode = self.barcode.text().strip()
        try:                
            ECON_type = barcode.split('-')[0]
            tray_number = int(barcode.split('-')[-1])
            tray_exists = ((ECON_type == 'ECOND' and tray_number >= 10000) or (ECON_type == 'ECONT' and tray_number < 10000)) and self.locations_db.checkTrayExists(tray_number)

        except Exception as e:
            error_dialog = QMessageBox.critical(self,
            "Error",
            f"Error when checking tray {barcode} in locations database:\n{e}")
            self.df = pd.DataFrame()
            self.update_table(self.tray_table,self.df)
            self.validate_options()
            return

        if tray_exists:
            df_tray = self.locations_db.getChipsInTray(tray_number)
            df_status = self.locations_db.getStatusForTray(tray_number)
            self.df = pd.merge(df_tray, df_status, on='chip_id', how='inner',suffixes=('_tray', '_status')).sort_values(by='current_position')
            qualities = []
            for chip_id,chip_type in zip(self.df['chip_id'],self.df['chip_type']):
                chip_grade = self.grade_db.getChip(chip_id)
                if chip_grade.empty:
                    qualities.append('Not Tested')
                elif chip_type == "ECOND":
                    qualities.append(ECOND_grade_map[chip_grade.quality.iloc[-1]])
                else:
                    qualities.append(ECONT_grade_map[chip_grade.quality.iloc[-1]])
            self.df['quality']=qualities
        else:
            warning_dialog = warning_dialog[:-2]  # Remove trailing comma and space
            QMessageBox.warning(self,
            "Tray(s) not Found",
            f"The following tray(s) do not exist in the locations database:\n{barcode}")
            self.df = pd.DataFrame()
        self.validate_options()
        self.update_table(self.tray_table,self.df)
        for button in self.chip_bottons:
            button.setChecked(False)
        self.update_pick_buttons()

    def update_picked(self):
        chip_positions=[]
        for i,button in enumerate(self.chip_bottons):
            if button.isChecked():
                chip_positions.append(i+1)
        self.df_picked=self.df[self.df['current_position'].isin(chip_positions)].copy()
        self.update_table(self.picked_table,self.df_picked)
        self.validate_options()

    def update_table(self,table,df):
        table.clear()
        # rows and columns
        table.setRowCount(df.shape[0])
        table.setColumnCount(df.shape[1])
        # title
        table.setHorizontalHeaderLabels(df.columns.tolist())
        # Populate the table widget
        for row_idx,(_, row_data) in enumerate(df.iterrows()):
            for col_idx, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                table.setItem(row_idx, col_idx, item)

    def update_pick_buttons(self):
        for i,button in enumerate(self.chip_bottons):
            button.setEnabled(False)
            button.setText(f"{i+1}\nNo Chip")
            button.setStyleSheet('background-color: None')
        for _, row in self.df.iterrows():
            i = row['current_position'] - 1 
            button = self.chip_bottons[i]
            button.setEnabled(True)
            button.setText(f"{row['current_position']}\n{row['chip_id']}\n{row['quality']}")
        # Coloring
        legend=dict()
        match self.palette.currentText():
            case "Quality": # Quality
                colors=Palette_Quality
                for _, row in self.df.iterrows():
                    i = row['current_position'] - 1 
                    button = self.chip_bottons[i]                
                    button.setStyleSheet(f'background-color: {Palette_Quality[row['quality']]}')
                    legend[row['quality']]=Palette_Quality[row['quality']]
            case "Entry Type":
                colors=Palette_Entry
                for _, row in self.df.iterrows():
                    i = row['current_position'] - 1 
                    button = self.chip_bottons[i]
                    button.setStyleSheet(f'background-color: {Palette_Entry[row['entry_type']]}')
                    legend[row['entry_type']]=Palette_Entry[row['entry_type']]
            case "Pass/Fail":
                colors=Palette_PF
                for _, row in self.df.iterrows():
                    i = row['current_position'] - 1 
                    button = self.chip_bottons[i]
                    if row['quality']=='Not Tested':
                        j = 'Not Tested'
                    elif  row['quality']=='X':
                        j = 'Fail'
                    else:
                        j = 'Pass'
                    button.setStyleSheet(f'background-color: {Palette_PF[j]}')
                    legend[j]=Palette_PF[j]        
        # legend            
        self.clear_layout(self.legend_panel)
        for key,color in colors.items():
            if key in legend:
                _ = QHBoxLayout()
                square = QPushButton()
                square.setFixedSize(50,50)
                square.setStyleSheet(f"background-color: {color}")
                _.addWidget(square)
                _.addWidget(QLabel(f"{key}"))
                self.legend_panel.addLayout(_)

    def open_loc_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "database_files/","Database file (*db)")
        if file_path:
            self.file_locations_db.setText(file_path)

    def open_grade_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "database_files/","Database file (*db)")
        if file_path:
            self.file_grade_db.setText(file_path)

    def validate_options(self):
        # load database part
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
        
        # select tray part
        databases_loaded = self.locations_db is not None and self.grade_db is not None
        add_disable_reason = ""
        if not databases_loaded:
            add_disable_reason+="Databases not loaded. "
        if self.barcode.text()=="":
            add_disable_reason+="No barcode entered. "
        if not add_disable_reason:
            self.select_button.setEnabled(True)
            self.barcode_label.setText("Tray Barcode:")
        else:
            self.select_button.setEnabled(False)
            self.barcode_label.setText(f"Tray Barcode: <font color='red'>{add_disable_reason}</font>")

        # Change button
        change_disable_reason = ""

        if self.df_picked.empty:
            change_disable_reason+="No chips to change. "
        if not change_disable_reason:
            self.change_button.setEnabled(True)
            self.change_disable_label.setText("")
        else:   
            self.change_button.setEnabled(False)
            self.change_disable_label.setText(f"<font color='red'>{change_disable_reason}</font>")

    def load_databases(self):
        try:
            self.locations_db = LocationsDatabase(self.file_locations_db.text())
            self.grade_db = grade_db = GradesDatabase(self.file_grade_db.text())
            tables_in_locations_db = ["locations","status"]
            tables_in_grade_db =["grades"]
            for table in tables_in_locations_db:
                query = f"""SELECT name FROM sqlite_master WHERE type='table' AND name='{table}';"""
                assert self.locations_db.cursor.execute(query).fetchone(),f"Table \"{table}\" not found in location database:\n{self.file_locations_db.text()}"

            for table in tables_in_grade_db:
                query = f"""SELECT name FROM sqlite_master WHERE type='table' AND name='{table}';"""
                assert self.grade_db.cursor.execute(query).fetchone(),f"Table \"{table}\" not found in grade database:\n{self.file_grade_db.text()}"

            self.validate_options()
        except Exception as e:
            error_dialog = QMessageBox.critical(self,"Database Load Error",f"Error loading databases:\n{e}")
            self.locations_db = None
            self.grade_db = None

    def update_options(self):
        self.options.clear()
        match self.operations.currentText():
            case "Change Status":
                self.options.addItems(['CHECKIN','TESTED','SORTED','SHIPPED','REJECTED'])
                self.options.setCurrentText('REJECTED')
            case "Change Grade":
                self.options.addItems(['A','B','D','F','H','K','Q','W','Y','X','NotTested'])
                self.options.setCurrentText('X')

    def change(self):
        match self.operations.currentText():
            case "Change Status":
                self.change_status()
            case "Change Grade":
                self.change_grade()
            case "Change Location":
                self.change_location()
    
    def change_status(self):
        match self.options.currentText():
            case "REJECTED":
                reject_diaglog = RejectSummaryAndConfirmDialog(self.df_picked,self.locations_db)
                if(reject_diaglog.exec()):
                    self.select_tray()
            case _:
                QMessageBox.warning(self,"Under Construction","Status except REJECTED is under construction")

    def change_grade(self):
        QMessageBox.warning(self,"Under Construction","Change Grade is under construction")

    def change_location(self):
        change_location_diaglog = ChangeLocationSummaryAndConfirmDialog(self.df_picked,self.locations_db)
        if(change_location_diaglog.exec()):
            self.select_tray()
    def select_all(self):
        for button in self.chip_bottons:
            if button.isEnabled():
                button.setChecked(True)

    def clear(self):
        for button in self.chip_bottons:
            if button.isEnabled():
                button.setChecked(False)

    def close(self):
        if(self.locations_db!=None):
            self.locations_db.commitAndClose()
        if(self.grade_db!=None):
            self.grade_db.commitAndClose()
        super().close()

## Dialog for chips to reject
class RejectSummaryAndConfirmDialog(QDialog):
    def __init__(self,df_picked_,locations_db_):
        super().__init__()
        self.df_picked = df_picked_
        self.locations_db=locations_db_
        self.setWindowTitle("Reject Chips")
        self.setGeometry(150, 150, 800, 20*len(df_picked_)+3)
        layout = QVBoxLayout()
        summary_label = QLabel(f"Summary of tray {self.df_picked['current_tray'].iloc[-1]}")
        summary_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(summary_label)
        chip_layout = QGridLayout()
        labels = ["Chip","Position","Entry","Quality","Destiniation Tray","Destiniation Position"]
        for i,label in enumerate(labels):
            chip_layout.addWidget(QLabel(label),0,i)

        self.destination_trays=[QLineEdit(self) for i in range(len(df_picked_))]
        self.destination_positions=[QLineEdit(self) for i in range(len(df_picked_))]

        tray_contraint = QIntValidator()
        tray_contraint.setRange(1, 99999)
        position_contraint = QIntValidator()
        position_contraint.setRange(1, 90)

        if len(self.df_picked) >= 2:
            self.destination_tray_all = QLineEdit(self)
            self.destination_tray_all.setValidator(tray_contraint)
            self.destination_tray_all.textChanged.connect(self.change_all_tray)
            chip_layout.addWidget(self.destination_tray_all,1,4)
            for i,(_, row) in enumerate(self.df_picked.iterrows()):
                chip_layout.addWidget(QLabel(f"{row['chip_id']}"),i+2,0)
                chip_layout.addWidget(QLabel(f"{row['current_position']}"),i+2,1)
                chip_layout.addWidget(QLabel(f"{row['entry_type']}"),i+2,2)
                chip_layout.addWidget(QLabel(f"{row['quality']}"),i+2,3)
                chip_layout.addWidget(self.destination_trays[i],i+2,4)
                chip_layout.addWidget(self.destination_positions[i],i+2,5)
                self.destination_trays[i].textChanged.connect(self.validate_options)
                self.destination_trays[i].setValidator(tray_contraint)
                self.destination_positions[i].setValidator(position_contraint)
                self.destination_positions[i].textChanged.connect(self.validate_options)


        else:
            for i,(_, row) in enumerate(self.df_picked.iterrows()):
                chip_layout.addWidget(QLabel(f"{row['chip_id']}"),i+1,0)
                chip_layout.addWidget(QLabel(f"{row['current_position']}"),i+1,1)
                chip_layout.addWidget(QLabel(f"{row['entry_type']}"),i+1,2)
                chip_layout.addWidget(QLabel(f"{row['quality']}"),i+1,3)
                chip_layout.addWidget(self.destination_trays[i],i+1,4)
                chip_layout.addWidget(self.destination_positions[i],i+1,5)
                self.destination_trays[i].setValidator(tray_contraint)
                self.destination_trays[i].textChanged.connect(self.validate_options)
                self.destination_positions[i].setValidator(position_contraint)
                self.destination_positions[i].textChanged.connect(self.validate_options)

        layout.addLayout(chip_layout)
        self.comment = QLineEdit(self)
        self.comment.setPlaceholderText("Comment")
        layout.addWidget(self.comment)
        self.accept_disable_label = QLabel("")
        layout.addWidget(self.accept_disable_label)
        self.button_box = QDialogButtonBox( QDialogButtonBox.StandardButton.Ok |  QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)
        self.validate_options()
        self.setLayout(layout)
    def validate_options(self):
        accept_disable_reason = ""
        tray_valid = all([tray.text().isdigit() and 1<=int(tray.text())<=99999 for tray in self.destination_trays])
        position_valid = all([pos.text().isdigit() and 1 <= int(pos.text()) <= 90 for pos in self.destination_positions])
        if not tray_valid:
            accept_disable_reason+="Tray number(s) invalid. "
        if not position_valid:
            accept_disable_reason+="Position number(s) invalid. "
        if accept_disable_reason:
            self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)
            self.accept_disable_label.setText(f"<font color='red'>{accept_disable_reason}</font>")
        else:
            self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(True)
            self.accept_disable_label.setText("")
        pass
    def change_all_tray(self):
        for tray in self.destination_trays:
            tray.setText(self.destination_tray_all.text())
    def accept(self):
        #override the accept
        question=f'The following chip(s) will be set to REJECT:\n'
        for i,(_, row) in enumerate(self.df_picked.iterrows()):
            question+=f'chip: {row['chip_id']:7},position: {row['current_position']:2},quality:{row['quality']} To tray: {self.destination_trays[i].text():5}, position: {self.destination_positions[i].text():2}\n'
        question+=f'{"comment: "+self.comment.text() if self.comment.text() else "with no comment"}\n\nDo you want to proceed?'
        reply = QMessageBox.question(self,
                'Confirmation',
                question,
                QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes)
        if reply == QMessageBox.StandardButton.Yes:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for i,(_, row) in enumerate(self.df_picked.iterrows()):
                self.locations_db.setChipGrade(
                    chip_id=row['chip_id'],
                    grade="Reject", 
                    comments=self.comment.text(),
                    timestamp=timestamp)
                self.locations_db.rejectChip(
                    chip_id=row['chip_id'],
                    start_tray=row['current_tray'],
                    start_position=row['current_position'],
                    new_tray=int(self.destination_trays[i].text()),
                    new_position=int(self.destination_positions[i].text()),
                    comments=self.comment.text(),
                    timestamp=timestamp)
                super().accept()

## Dialog for chips to change location
class ChangeLocationSummaryAndConfirmDialog(QDialog):
    def __init__(self,df_picked_,locations_db_):
        super().__init__()
        self.df_picked = df_picked_
        self.locations_db=locations_db_
        self.setWindowTitle("Change Locations of Chips")
        self.setGeometry(150, 150, 800, 20*len(df_picked_)+3)
        layout = QVBoxLayout()
        summary_label = QLabel(f"Summary of tray {self.df_picked['current_tray'].iloc[-1]}")
        summary_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(summary_label)
        chip_layout = QGridLayout()
        labels = ["Chip","Position","Entry","Quality","Destiniation Tray","Destiniation Position"]
        for i,label in enumerate(labels):
            chip_layout.addWidget(QLabel(label),0,i)

        self.destination_trays=[QLineEdit(self) for i in range(len(df_picked_))]
        self.destination_positions=[QLineEdit(self) for i in range(len(df_picked_))]

        tray_contraint = QIntValidator()
        tray_contraint.setRange(1, 99999)
        position_contraint = QIntValidator()
        position_contraint.setRange(1, 90)

        if len(self.df_picked) >= 2:
            self.destination_tray_all = QLineEdit(self)
            self.destination_tray_all.setValidator(tray_contraint)
            self.destination_tray_all.textChanged.connect(self.change_all_tray)
            chip_layout.addWidget(self.destination_tray_all,1,4)
            for i,(_, row) in enumerate(self.df_picked.iterrows()):
                chip_layout.addWidget(QLabel(f"{row['chip_id']}"),i+2,0)
                chip_layout.addWidget(QLabel(f"{row['current_position']}"),i+2,1)
                chip_layout.addWidget(QLabel(f"{row['entry_type']}"),i+2,2)
                chip_layout.addWidget(QLabel(f"{row['quality']}"),i+2,3)
                chip_layout.addWidget(self.destination_trays[i],i+2,4)
                chip_layout.addWidget(self.destination_positions[i],i+2,5)
                self.destination_trays[i].textChanged.connect(self.validate_options)
                self.destination_trays[i].setValidator(tray_contraint)
                self.destination_positions[i].setValidator(position_contraint)
                self.destination_positions[i].textChanged.connect(self.validate_options)
        else:
            for i,(_, row) in enumerate(self.df_picked.iterrows()):
                chip_layout.addWidget(QLabel(f"{row['chip_id']}"),i+1,0)
                chip_layout.addWidget(QLabel(f"{row['current_position']}"),i+1,1)
                chip_layout.addWidget(QLabel(f"{row['entry_type']}"),i+1,2)
                chip_layout.addWidget(QLabel(f"{row['quality']}"),i+1,3)
                chip_layout.addWidget(self.destination_trays[i],i+1,4)
                chip_layout.addWidget(self.destination_positions[i],i+1,5)
                self.destination_trays[i].setValidator(tray_contraint)
                self.destination_trays[i].textChanged.connect(self.validate_options)
                self.destination_positions[i].setValidator(position_contraint)
                self.destination_positions[i].textChanged.connect(self.validate_options)

        layout.addLayout(chip_layout)
        self.comment = QLineEdit(self)
        self.comment.setPlaceholderText("Comment")
        layout.addWidget(self.comment)
        self.accept_disable_label = QLabel("")
        layout.addWidget(self.accept_disable_label)
        self.button_box = QDialogButtonBox( QDialogButtonBox.StandardButton.Ok |  QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)
        self.validate_options()
        self.setLayout(layout)
    def validate_options(self):
        accept_disable_reason = ""
        tray_valid = all([tray.text().isdigit() and 1<=int(tray.text())<=99999 for tray in self.destination_trays])
        position_valid = all([pos.text().isdigit() and 1 <= int(pos.text()) <= 90 for pos in self.destination_positions])
        if not tray_valid:
            accept_disable_reason+="Tray number(s) invalid. "
        if not position_valid:
            accept_disable_reason+="Position number(s) invalid. "
        if accept_disable_reason:
            self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)
            self.accept_disable_label.setText(f"<font color='red'>{accept_disable_reason}</font>")
        else:
            self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(True)
            self.accept_disable_label.setText("")
        pass
    def change_all_tray(self):
        for tray in self.destination_trays:
            tray.setText(self.destination_tray_all.text())
    def accept(self):
        #override the accept
        question=f'The following chip(s) will be put into new location:\n'
        for i,(_, row) in enumerate(self.df_picked.iterrows()):
            question+=f'chip: {row['chip_id']:7},position: {row['current_position']:2},quality:{row['quality']} To tray: {self.destination_trays[i].text():5}, position: {self.destination_positions[i].text():2}\n'
        question+=f'{"comment: "+self.comment.text() if self.comment.text() else "with no comment"}\n\nDo you want to proceed?'
        reply = QMessageBox.question(self,
                'Confirmation',
                question,
                QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes)
        if reply == QMessageBox.StandardButton.Yes:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for i,(_, row) in enumerate(self.df_picked.iterrows()):
                self.locations_db.setChipLocation(
                    chip_id=row['chip_id'],
                    entry_type=row['entry_type'],
                    start_tray=row['current_tray'],
                    start_position=row['current_position'],
                    new_tray=int(self.destination_trays[i].text()),
                    new_position=int(self.destination_positions[i].text()),
                    comments=self.comment.text(),
                    timestamp=timestamp)
                super().accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DBWindow()
    window.show()

    sys.exit(app.exec())
