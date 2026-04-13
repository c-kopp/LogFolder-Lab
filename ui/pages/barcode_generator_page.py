import config as config

from src.utils import open_folder
from src.tools.barcode_tool import generate_barcodes
from src.workers import ScriptWorker

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *


class BarcodeGeneratorPage(QWidget):
    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        layout = QVBoxLayout(self)

        title = QLabel("Barcode Generator")
        title.setObjectName("title")
        layout.addWidget(title)

        # --- Barcode Typ ---
        self.barcode_type = QComboBox()
        self.barcode_type.addItems(["Code128", "Code 39", "QR Code"])
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Typ:"))
        type_layout.addWidget(self.barcode_type)
        layout.addLayout(type_layout)

        # --- Präfix / Suffix / Startnummer / Anzahl ---
        form = QFormLayout()
        self.prefix = QLineEdit()
        self.suffix = QLineEdit()
        self.start_number = QSpinBox()
        self.start_number.setRange(0, 999999)
        self.count = QSpinBox()
        self.count.setRange(1, 10000)
        self.count.setValue(10)
        self.min_digits = QSpinBox()
        self.min_digits.setRange(4, 20)
        self.min_digits.setValue(8)
        form.addRow("Mindestlänge Zahl:", self.min_digits)
        form.addRow("Präfix:", self.prefix)
        form.addRow("Suffix:", self.suffix)
        form.addRow("Startnummer:", self.start_number)
        form.addRow("Anzahl:", self.count)
        layout.addLayout(form)

        # --- Etikettengröße ---
        size_layout = QHBoxLayout()
        self.label_w = QDoubleSpinBox()
        self.label_w.setRange(10, 300)
        self.label_w.setValue(50)
        self.label_w.setSuffix(" mm")
        self.label_h = QDoubleSpinBox()
        self.label_h.setRange(10, 300)
        self.label_h.setValue(10)
        self.label_h.setSuffix(" mm")
        size_layout.addWidget(QLabel("Breite:"))
        size_layout.addWidget(self.label_w)
        size_layout.addWidget(QLabel("Höhe:"))
        size_layout.addWidget(self.label_h)
        layout.addLayout(size_layout)

        # --- Optionen ---
        self.crop_marks = QCheckBox("Schneidzeichen")
        self.crop_marks.setChecked(True)
        layout.addWidget(self.crop_marks)

        # ----- Open Output Folder -----
        open_button = QPushButton("Open Output Folder")
        open_button.setObjectName("btnSecondary")
        open_button.clicked.connect(lambda: open_folder(config.get_output_folder("Barcode")))

        # ----- Start Script -----
        self.run_button = QPushButton("Generate Barcodes")
        self.run_button.clicked.connect(self._run_barcode)

        layout.addStretch()

        layout.addWidget(open_button)
        layout.addWidget(self.run_button)

    def _run_barcode(self):
        self.worker = ScriptWorker(generate_barcodes, (
            config.get_output_folder("Barcode"),
            self.prefix.text(),
            self.suffix.text(),
            self.start_number.value(),
            self.count.value(),
            self.barcode_type.currentText(),
            self.label_w.value(),
            self.label_h.value(),
            self.min_digits.value(),
            self.crop_marks.isChecked(),
            self.logger
        ))
        self.worker.start()
