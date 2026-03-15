from PyQt6.QtWidgets import (
    QWidget,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
    QFileDialog,
    QDateEdit,
    QCheckBox
)
from PyQt6.QtCore import QDate


class FolderPicker(QWidget):
    def __init__(self, default_folder=""):
        super().__init__()

        self.folder_input = QLineEdit(default_folder)
        browse = QPushButton("Browse")

        browse.clicked.connect(self.select_folder)

        layout = QHBoxLayout(self)
        layout.addWidget(self.folder_input)
        layout.addWidget(browse)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")

        if folder:
            self.folder_input.setText(folder)

    def get_folder(self):
        return self.folder_input.text()


class DateRangeWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.start_date = QDateEdit(QDate.currentDate().addDays(-5))
        self.end_date = QDateEdit(QDate.currentDate())

        self.start_date.setCalendarPopup(True)
        self.end_date.setCalendarPopup(True)

        self.end_date.setMinimumDate(self.start_date.date())

        self.start_date.dateChanged.connect(self.update_end_date_min)

        self.all_files = QCheckBox("All Files")

        layout = QHBoxLayout(self)
        layout.addWidget(self.start_date)
        layout.addWidget(self.end_date)
        layout.addWidget(self.all_files)

    def update_end_date_min(self, date):
        self.end_date.setMinimumDate(date)

        if self.end_date.date() < date:
            self.end_date.setDate(date)

    def get_dates(self):
        return self.start_date.date(), self.end_date.date()

    def all_files_checked(self):
        return self.all_files.isChecked()
