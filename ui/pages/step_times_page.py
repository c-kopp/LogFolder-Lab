from ui.widgets import FolderPicker, DateRangeWidget

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel

class StepTimesPage(QWidget):

    def __init__(self, logger):
        super().__init__()

        layout = QVBoxLayout(self)

        hint = QLabel("Note: This will come in Future Releases")
        layout.addWidget(hint)

        return

        self.folder_picker = FolderPicker()
        layout.addWidget(self.folder_picker)

        self.date_range = DateRangeWidget()
        layout.addWidget(self.date_range)

        run_button = QPushButton("Get Step Times")
        layout.addWidget(run_button)
