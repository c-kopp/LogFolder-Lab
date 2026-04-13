import os

from src.workers import ScriptWorker
from src.tools.qr_generator import create_qr_code

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit

class QRGeneratorPage(QWidget):
    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        layout = QVBoxLayout(self)
        title = QLabel("QR Code Generator")
        title.setObjectName("title")
        layout.addWidget(title)

        layout.addWidget(QLabel("Link"))
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("www.hamiltoncompany.com")
        layout.addWidget(self.path_input)

        self.run_button = QPushButton("Generate QR Code")
        self.run_button.clicked.connect(self._run_qr)

        layout.addStretch()
        layout.addWidget(self.run_button)


    def _run_qr(self):
        path = self.path_input.text()
        self.logger.info("Generate QR Code button pressed")

        self.worker = ScriptWorker(create_qr_code, (path, self.logger))
        self.worker.start()
