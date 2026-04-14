import config as config

from src.utils import open_folder
from src.workers import ScriptWorker
from src.tools.barcode_tool import generate_barcodes, generate_barcode_image

from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

from io import BytesIO


class BarcodeGeneratorPage(QWidget):
    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        layout = QVBoxLayout(self)
        title = QLabel("Barcode Generator")
        title.setObjectName("title")
        layout.addWidget(title)

        # ----- Barcode Style -----
        bc_style_layout = QHBoxLayout()
        self.prefix = QLineEdit()
        self.prefix.setPlaceholderText("Prefix")
        self.start_number = QSpinBox()
        self.start_number.setPrefix("Starting # ")
        self.start_number.setRange(0, 999999)
        self.suffix = QLineEdit()
        self.suffix.setPlaceholderText("Suffix")
        self.min_digits = QSpinBox()
        self.min_digits.setPrefix("Min. ")
        self.min_digits.setSuffix(" Characters")
        self.min_digits.setRange(4, 20)
        self.min_digits.setValue(8)

        bc_style_layout.addWidget(self.prefix, 1)
        bc_style_layout.addWidget(self.start_number, 1)
        bc_style_layout.addWidget(self.suffix, 1)
        bc_style_layout.addWidget(self.min_digits, 1)

        layout.addLayout(bc_style_layout)

        # ----- Barcode Type -----
        type_layout = QHBoxLayout()

        self.barcode_type = QComboBox()
        self.barcode_type.addItems(["Code 128", "Code 39", "QR Code", "Data Matrix"])
        type_layout.addWidget(self.barcode_type)

        layout.addLayout(type_layout)

        # ----- Preview Barcode -----
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumHeight(100)

        layout.addWidget(self.preview_label)

        self.preview_text = QLabel()
        self.preview_text.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.preview_text)

        self.prefix.textChanged.connect(self.update_preview)
        self.suffix.textChanged.connect(self.update_preview)
        self.start_number.valueChanged.connect(self.update_preview)
        self.min_digits.valueChanged.connect(self.update_preview)
        self.barcode_type.currentTextChanged.connect(self.update_preview)

        # --- Etikettengröße ---
        def labeled_widget(label_text, widget):
            container = QHBoxLayout()
            container.setSpacing(2)
            label = QLabel(label_text)
            label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            container.addWidget(label)
            container.addWidget(widget)

            return container

        size_layout = QHBoxLayout()

        self.count = QSpinBox()
        self.count.setRange(1, 10000)
        self.count.setValue(10)

        self.label_w = QDoubleSpinBox()
        self.label_w.setRange(3, 300)
        self.label_w.setValue(50)
        self.label_w.setSuffix(" mm")

        self.label_h = QDoubleSpinBox()
        self.label_h.setRange(3, 300)
        self.label_h.setValue(10)
        self.label_h.setSuffix(" mm")

        self.crop_marks = QCheckBox("Cutting marks")
        self.crop_marks.setChecked(True)

        layout.addSpacing(100)
        size_layout.addLayout(labeled_widget("Number of Barcodes:", self.count))
        size_layout.addLayout(labeled_widget("Width:", self.label_w))
        size_layout.addLayout(labeled_widget("Height:", self.label_h))
        size_layout.addSpacing(25)
        size_layout.addWidget(self.crop_marks)
        layout.addLayout(size_layout)

        self.update_preview()

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

    def update_preview(self):
        prefix = self.prefix.text()
        suffix = self.suffix.text()
        min_digits = self.min_digits.value()
        min_number_len = max(0, min_digits - len(prefix) - len(suffix))
        number = str(self.start_number.value()).zfill(min_number_len)
        content = f"{prefix}{number}{suffix}"

        try:
            image_h = 50 if self.barcode_type.currentText() in ["QR Code", "Data Matrix"] else 10
            image_w = 50 if self.barcode_type.currentText() in ["QR Code", "Data Matrix"] else 50

            img = generate_barcode_image(
                self.barcode_type.currentText(),
                content,
                image_w,
                image_h
            )

            buffer = BytesIO()
            img.save(buffer, format="PNG")
            buffer.seek(0)

            preview_h = 200 if self.barcode_type.currentText() in ["QR Code", "Data Matrix"] else 80
            max_w = 200 if self.barcode_type.currentText() in ["QR Code", "Data Matrix"] else self.preview_label.width()

            pixmap = QPixmap()
            pixmap.loadFromData(buffer.getvalue())
            pixmap = pixmap.scaled(
                max_w,
                preview_h,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.preview_label.setMinimumHeight(preview_h)
            self.preview_label.setPixmap(pixmap)
            self.preview_text.setText(content)

        except Exception as e:
            self.preview_label.setText(f"Preview not possible: {e}")


    def _run_barcode(self):
        self.worker = ScriptWorker(generate_barcodes, (
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
