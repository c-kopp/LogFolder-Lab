import config as config

from ui.widgets import FolderPickerWidget, DateRangeWidget

from src.utils import open_folder

from PyQt6.QtWidgets import *


class StepTimesPage(QWidget):
    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        layout = QVBoxLayout(self)
        title = QLabel("Step Times Tool")
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

        layout.addStretch()

        hint = QLabel("Note: This will come in Future Releases")
        layout.addWidget(hint)

        return

        self.folder_picker = FolderPicker()
        layout.addWidget(self.folder_picker)

        self.date_range = DateRangeWidget()
        layout.addWidget(self.date_range)

        run_button = QPushButton("Get Step Times")
        layout.addWidget(run_button)
