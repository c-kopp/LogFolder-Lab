import os

import src.config as config

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *

class SettingsPage(QWidget):
    settings_changed = pyqtSignal()

    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        layout = QVBoxLayout(self)

        title = QLabel("Settings")
        title.setObjectName("title")
        layout.addWidget(title)

        # ----- Input Folder -----
        layout.addWidget(QLabel("Default Input Folder"))
        input_layout = QHBoxLayout()
        self.input_folder = QLineEdit(config.get("input_folder"))
        browse_input = QPushButton("Browse")
        browse_input.clicked.connect(lambda: self._browse(self.input_folder))
        input_layout.addWidget(self.input_folder)
        input_layout.addWidget(browse_input)
        layout.addLayout(input_layout)

        # ----- Output Folder -----
        layout.addWidget(QLabel("Default Output Folder"))
        output_layout = QHBoxLayout()
        self.output_folder = QLineEdit(config.get("output_folder"))
        browse_output = QPushButton("Browse")
        browse_output.clicked.connect(lambda: self._browse(self.output_folder))
        output_layout.addWidget(self.output_folder)
        output_layout.addWidget(browse_output)
        layout.addLayout(output_layout)

        # ----- Save Button -----
        self.btn_save = QPushButton("Save")
        self.btn_save.clicked.connect(self._save)
        layout.addWidget(self.btn_save)
        layout.addStretch()

    def _browse(self, target_input):
        path = QFileDialog.getExistingDirectory(self)
        if path:
            target_input.setText(path)

    def _save(self):
        config.set("input_folder",  self.input_folder.text())
        config.set("output_folder", self.output_folder.text())
        self.logger.info("Settings saved")
        self.settings_changed.emit()
