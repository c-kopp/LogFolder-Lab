import os

import config as config

from src.utils import open_folder
from src.workers import ScriptWorker
from src.tools.qr_generator import generate_qrcode, generate_preview_image

from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

from io import BytesIO

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

        # ----- 2D Barcode Type -----
        type_layout = QHBoxLayout()

        self.barcode_type = QComboBox()
        self.barcode_type.addItems(["QR Code", "Data Matrix"])
        type_layout.addWidget(self.barcode_type)

        layout.addLayout(type_layout)

        # ----- Preview 2D Barcode -----
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumHeight(150)

        layout.addWidget(self.preview_label)

        self.path_input.textChanged.connect(self.update_preview)
        self.barcode_type.currentTextChanged.connect(self.update_preview)

        # ----- Open Output Folder -----
        open_button = QPushButton("Open Output Folder")
        open_button.setObjectName("btnSecondary")
        open_button.clicked.connect(lambda: open_folder(config.get_output_folder("QRCode")))

        # ----- Start Script -----
        self.run_button = QPushButton("Generate QR Code")
        self.run_button.clicked.connect(self._run_qr)

        layout.addStretch()
        layout.addWidget(open_button)
        layout.addWidget(self.run_button)


    def _run_qr(self):
        self.logger.info("Generate QR Code button pressed")

        self.worker = ScriptWorker(generate_qrcode, (
            self.path_input.text(),
            self.barcode_type.currentText(),
            self.logger
        ))
        self.worker.start()

    def update_preview(self):
        content = self.path_input.text()
        if not content.strip():
            self.preview_label.clear()
            return

        try:
            img = generate_preview_image(content, self.barcode_type.currentText())
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            buffer.seek(0)

            pixmap = QPixmap()
            pixmap.loadFromData(buffer.getvalue())
            pixmap = pixmap.scaled(
                250, 250,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.preview_label.setPixmap(pixmap)

        except Exception as e:
            self.preview_label.setText(f"Preview not possible: {e}")
