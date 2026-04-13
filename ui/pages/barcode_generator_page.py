import os

import config as config

from src.utils import open_folder
from src.workers import ScriptWorker
from src.tools.qr_generator import create_qr_code

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit

class BarcodeGeneratorPage(QWidget):
    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        layout = QVBoxLayout(self)
        title = QLabel("Barcode Generator")
        title.setObjectName("title")
        layout.addWidget(title)

        layout.addWidget(QLabel("Link"))
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("www.hamiltoncompany.com")
        layout.addWidget(self.path_input)

        # ----- Open Output Folder -----
        open_button = QPushButton("Open Output Folder")
        open_button.setObjectName("btnSecondary")
        open_button.clicked.connect(lambda: open_folder(config.get_output_folder("Barcode")))

        # ----- Start Script -----
        self.run_button = QPushButton("Generate Barcode")
        self.run_button.clicked.connect(self._run_qr)

        layout.addStretch()
        layout.addWidget(open_button)
        layout.addWidget(self.run_button)

    def _run_qr(self):
        path = self.path_input.text()
        self.logger.info("Generate Barcode button pressed")

        self.worker = ScriptWorker(create_qr_code, (path, self.logger))
        self.worker.start()
