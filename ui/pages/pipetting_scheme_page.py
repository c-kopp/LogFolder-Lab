import os

import config as config

from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

from ui.widgets import FolderPickerWidget, DateRangeWidget

from src.utils import open_folder
from src.workers import ScriptWorker
from src.tools.pipette_tool import create_pts


class PipettingSchemePage(QWidget):
    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        layout = QVBoxLayout(self)
        title = QLabel("Pipette and Transport Scheme")
        title.setObjectName("title")
        layout.addWidget(title)

        # ----- General -----
        general_group = QGroupBox("General")
        general_group_layout = QVBoxLayout(general_group)

        # Folder Search
        self.folder_widget = FolderPickerWidget(config.get("input_folder"))
        general_group_layout.addWidget(self.folder_widget)

        # Pick Date
        self.date_widget = DateRangeWidget()
        general_group_layout.addWidget(self.date_widget)

        layout.addWidget(general_group)
        layout.addSpacing(20)

        # ----- Local Options -----
        group = QGroupBox("Needed Informations")

        self.transports = QCheckBox("Transports")
        self.transports.setChecked(True)

        self.pipetting = QCheckBox("Pipetting")
        self.pipetting.setChecked(True)

        opt_layout = QHBoxLayout()
        opt_layout.addStretch()
        opt_layout.addWidget(self.transports)
        opt_layout.addStretch()
        opt_layout.addWidget(self.pipetting)
        opt_layout.addStretch()

        group.setLayout(opt_layout)
        layout.addWidget(group)

        # ----- Open Output Folder -----
        open_button = QPushButton("Open Output Folder")
        open_button.setObjectName("btnSecondary")
        open_button.clicked.connect(lambda: open_folder(config.get_output_folder("PTS")))

        # ----- Start Script -----
        self.run_button = QPushButton("Create PTS")
        self.run_button.clicked.connect(self._run_pts)

        layout.addStretch()

        layout.addWidget(open_button)
        layout.addWidget(self.run_button)

    def _run_pts(self):
        folder = self.folder_widget.get_folder()

        start_date, end_date = self.date_widget.get_dates()
        start_date = start_date.toPyDate()
        end_date = end_date.toPyDate()

        all_files = self.date_widget.all_files_checked()

        pipetting = self.pipetting.isChecked()
        transports = self.transports.isChecked()

        self.logger.info("Create PTS button pressed")
        self.worker = ScriptWorker(
            create_pts,
            (folder, start_date, end_date, all_files, transports, pipetting, self.logger)
        )
        self.worker.start()

