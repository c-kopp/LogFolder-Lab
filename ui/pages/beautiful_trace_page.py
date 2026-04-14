import os

import config as config

from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

from ui.widgets import FolderPickerWidget, DateRangeWidget

from src.utils import open_folder
from src.workers import ScriptWorker
from src.tools.beautify_tool import create_byt


class BeautifyTracePage(QWidget):
    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        layout = QVBoxLayout(self)
        title = QLabel("Beautiful Trace")
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

        # ----- Open Output Folder -----
        open_button = QPushButton("Open Output Folder")
        open_button.setObjectName("btnSecondary")
        open_button.clicked.connect(lambda: open_folder(config.get_output_folder("BYT")))

        # ----- Start Script -----
        self.run_button = QPushButton("Create Beautiful Traces")
        self.run_button.clicked.connect(self._run_byt)

        layout.addStretch()

        layout.addWidget(open_button)
        layout.addWidget(self.run_button)

    def _run_byt(self):
        folder = self.folder_widget.get_folder()

        start_date, end_date = self.date_widget.get_dates()
        start_date = start_date.toPyDate()
        end_date = end_date.toPyDate()

        all_files = self.date_widget.all_files_checked()

        self.logger.info("Create BYT button pressed")
        self.worker = ScriptWorker(
            create_byt,
            (folder, start_date, end_date, all_files, self.logger)
        )
        self.worker.start()

