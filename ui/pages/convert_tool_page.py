import os

import src.config as config

from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

from ui.widgets import FolderPicker, DateRangeWidget

from src.workers import ScriptWorker
from src.convert_tool import create_pts, create_byt


class ConvertToolPage(QWidget):
    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        layout = QVBoxLayout(self)
        title = QLabel("Convert Tool")
        title.setObjectName("title")
        layout.addWidget(title)

        self.folder_input = QLineEdit(config.get("input_folder"))
        browse = QPushButton("Browse")
        browse.clicked.connect(self.select_folder)
        folder_layout = QHBoxLayout()
        folder_layout.addWidget(self.folder_input, 4)
        folder_layout.addWidget(browse, 1)
        layout.addLayout(folder_layout)

        self.start_date = QDateEdit(QDate.currentDate().addDays(-5))
        self.end_date = QDateEdit(QDate.currentDate())
        self.start_date.setCalendarPopup(True)
        self.end_date.setCalendarPopup(True)
        self.end_date.setMinimumDate(self.start_date.date())
        self.start_date.dateChanged.connect(self.update_end_date_min)

        self.all_files = QCheckBox("All Files")

        date_layout = QHBoxLayout()
        date_layout.addWidget(self.start_date, 2)
        date_layout.addWidget(self.end_date, 2)
        date_layout.addWidget(self.all_files, 1)

        layout.addLayout(date_layout)

        self.btn_pts = QPushButton("Create PTS")
        self.transports = QCheckBox("Transports")
        self.transports.setChecked(True)
        self.pipetting = QCheckBox("Pipetting")
        self.pipetting.setChecked(True)
        self.btn_pts.clicked.connect(self.run_pts)

        pts_layout = QHBoxLayout()
        pts_layout.addWidget(self.transports, 1)
        pts_layout.addWidget(self.pipetting, 1)
        pts_layout.addWidget(self.btn_pts, 3)

        self.btn_byt = QPushButton("Create BYT")
        self.btn_byt.clicked.connect(self.run_byt)

        layout.addLayout(pts_layout)
        layout.addWidget(self.btn_byt)
        layout.addStretch()

    def update_end_date_min(self, date):
        self.end_date.setMinimumDate(date)

        if self.end_date.date() < date:
            self.end_date.setDate(date)

    def select_folder(self):
        path = QFileDialog.getExistingDirectory(self)
        if path:
            self.folder_input.setText(path)

    def run_pts(self):
        folder = self.folder_input.text()
        self.logger.info("Create PTS button pressed")
        start_date = self.start_date.date().toPyDate()
        end_date = self.end_date.date().toPyDate()
        all_files = self.all_files.isChecked()
        pipetting = self.pipetting.isChecked()
        transports = self.transports.isChecked()
        self.worker = ScriptWorker(create_pts, (folder, start_date, end_date, all_files, transports, pipetting, self.logger))
        self.worker.start()

    def run_byt(self):
        folder = self.folder_input.text()
        self.logger.info("Create BYT button pressed")
        start_date = self.start_date.date().toPyDate()
        end_date = self.end_date.date().toPyDate()
        all_files = self.all_files.isChecked()
        self.worker = ScriptWorker(create_byt, (folder, start_date, end_date, all_files, self.logger))
        self.worker.start()

