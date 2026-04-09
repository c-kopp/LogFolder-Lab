import os

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel

class QRGeneratorPage(QWidget):
    def __init__(self, logger):
        super().__init__()

        layout = QVBoxLayout(self)

        hint = QLabel("Note: This will come in Future Releases")
        layout.addWidget(hint)

        return

        run_button = QPushButton("Generate QR Code")
        layout.addWidget(run_button)
