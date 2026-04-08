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

        # ----- Log Folder -----
        layout.addWidget(QLabel("Log Folder"))
        log_layout = QHBoxLayout()
        self.log_folder = QLineEdit(config.get("log_folder"))
        browse_log = QPushButton("Browse")
        browse_log.clicked.connect(lambda: self._browse(self.log_folder))
        log_layout.addWidget(self.log_folder)
        log_layout.addWidget(browse_log)
        layout.addLayout(log_layout)
        hint = QLabel("Note: Log folder change takes effect after restart.")
        hint.setStyleSheet("color: gray; font-size: 11px;")
        layout.addWidget(hint)

        # ----- Buttons -----
        btn_layout = QHBoxLayout()

        self.btn_save = QPushButton("Save")
        self.btn_save.clicked.connect(self._save)

        self.btn_restore = QPushButton("Restore Defaults")
        self.btn_restore.setObjectName("btnSecondary")
        self.btn_restore.clicked.connect(self._restore)

        layout.addWidget(self.btn_restore)
        layout.addWidget(self.btn_save)
        layout.addStretch()

    def _browse(self, target_input):
        path = QFileDialog.getExistingDirectory(self)
        if path:
            target_input.setText(path)

    def _save(self):
        config.set("input_folder",  self.input_folder.text())
        config.set("output_folder", self.output_folder.text())
        config.set("log_folder",    self.log_folder.text())

        self.logger.info("Settings saved")
        self.settings_changed.emit()

    def _restore(self):
        self.input_folder.setText(config.DEFAULTS['input_folder'])
        self.output_folder.setText(config.DEFAULTS['output_folder'])
        self.log_folder.setText(config.DEFAULTS['log_folder'])

        #self._save()
        self.logger.info("Settings restored to defaults")
