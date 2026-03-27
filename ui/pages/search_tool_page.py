from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton

from ui.widgets import FolderPicker, DateRangeWidget


class SearchToolPage(QWidget):

    def __init__(self, logger):
        super().__init__()

        layout = QVBoxLayout(self)

        self.folder_picker = FolderPicker()
        layout.addWidget(self.folder_picker)

        self.date_range = DateRangeWidget()
        layout.addWidget(self.date_range)

        run_button = QPushButton("Run Search")
        layout.addWidget(run_button)
