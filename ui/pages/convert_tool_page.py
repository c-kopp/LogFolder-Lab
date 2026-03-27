from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QCheckBox, QHBoxLayout

from ui.widgets import FolderPicker, DateRangeWidget

from src.convert_tool import create_pts


class ConvertToolPage(QWidget):
    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        layout = QVBoxLayout(self)
        title = QLabel("Convert Tool")
        title.setObjectName("title")
        layout.addWidget(title)


        self.folder_picker = FolderPicker()
        layout.addWidget(self.folder_picker)

        self.date_range = DateRangeWidget()
        layout.addWidget(self.date_range)


        self.btn_pts = QPushButton("Create PTS")
        self.transports = QCheckBox("Transports")
        self.transports.setChecked(True)
        self.pipetting = QCheckBox("Pipetting")
        self.pipetting.setChecked(True)
        self.btn_pts.clicked.connect(self.run_pts)
        pts_layout = QHBoxLayout()
        pts_layout.addWidget(self.transports, 1)
        pts_layout.addWidget(self.pipetting, 1)
        pts_layout.addWidget(self.btn_pts, 3)

        self.btn_byt = QPushButton("Create BYT")
        self.btn_byt.clicked.connect(self.run_byt)

    def run_pts(self):

        folder = self.folder_picker.get_folder()
        start, end = self.date_range.get_dates()

        create_pts(folder, start, end)

    def run_byt(self):
        pass
