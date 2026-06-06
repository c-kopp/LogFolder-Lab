from PyQt6.QtCore import (
    Qt,
    QDate,
)
from PyQt6.QtWidgets import (
    QLabel,
    QProgressBar,
    QWidget,
    QDateEdit,
    QCheckBox,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QFileDialog,
    QPushButton,
    QProgressBar,
)

class FolderPickerWidget(QWidget):
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


class ProgressWidget(QWidget):
    def __init__(self, verb: str = "Processing"):
        super().__init__()
        self._verb = verb

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 0)
        layout.setSpacing(4)

        row = QHBoxLayout()

        self._count = QLabel(f"{verb} 0 of 0")
        self._count.setStyleSheet("font-size: 12px; font-weight: normal;")
        self._count.setFixedWidth(160)

        self._bar = QProgressBar()
        self._bar.setRange(0, 100)
        self._bar.setValue(0)
        self._bar.setTextVisible(False)
        self._bar.setFixedHeight(18)

        self._pct = QLabel("0 %")
        self._pct.setStyleSheet("font-size: 12px; font-weight: normal;")
        self._pct.setFixedWidth(36)
        self._pct.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        row.addWidget(self._count)
        row.addWidget(self._bar)
        row.addWidget(self._pct)

        layout.addLayout(row)

    def update(self, current: int, total: int):
        pct = int(current / total * 100) if total > 0 else 0
        self._bar.setValue(pct)
        self._pct.setText(f"{pct} %")
        self._count.setText(f"{self._verb} {current} of {total}")

    def finish(self):
        self._bar.setValue(100)
        self._pct.setText("100 %")

    def reset(self):
        self._bar.setValue(0)
        self._pct.setText("0 %")
        self._count.setText(f"{self._verb} 0 of 0")

