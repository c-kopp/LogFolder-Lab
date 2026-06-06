import threading

import config as config

from ui.widgets import FolderPickerWidget, DateRangeWidget, ProgressWidget

from src.utils import open_folder
from src.workers import ScriptWorker
from src.tools.beautify_tool import create_byt

from PyQt6.QtWidgets import (
    QLabel,
    QWidget,
    QGroupBox,
    QVBoxLayout,
    QPushButton,
)


class BeautifyTracePage(QWidget):
    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        layout = QVBoxLayout(self)
        title = QLabel("Beautiful Trace")
        title.setObjectName("title")
        layout.addWidget(title)

        # ----- General -----
        general_group = QGroupBox("General")
        general_group_layout = QVBoxLayout(general_group)
        self.folder_widget = FolderPickerWidget(config.get("input_folder"))
        general_group_layout.addWidget(self.folder_widget)
        self.date_widget = DateRangeWidget()
        general_group_layout.addWidget(self.date_widget)
        layout.addWidget(general_group)

        # ----- Stretch -----
        layout.addStretch()

        # ----- Progress -----
        self.progress = ProgressWidget("Processing")
        layout.addWidget(self.progress)

        # ----- Buttons -----
        open_button = QPushButton("Open Output Folder")
        open_button.setObjectName("btnSecondary")
        open_button.clicked.connect(lambda: open_folder(config.get_output_folder("BYT")))
        self.run_button = QPushButton("Create BYT")
        self.run_button.clicked.connect(self._start_or_abort)
        layout.addWidget(open_button)
        layout.addWidget(self.run_button)

    def _start_or_abort(self):
        if self.run_button.text() == "Stop":
            self._abort()
        else:
            self._run_byt()

    def _abort(self):
        if hasattr(self, "worker") and self.worker.isRunning():
            self._stop_event.set()

        self.run_button.setText("Create BYT")
        self.run_button.setObjectName("")
        self.run_button.setStyle(self.run_button.style())

        busy_cb = getattr(self, "set_busy_callback", None)

        if callable(busy_cb):
            busy_cb(False)

        self.logger.warning("Stopped by user.")

    def _on_progress(self, cur: int, total: int):
        self.progress.update(cur, total)

    def _run_byt(self):
        folder = self.folder_widget.get_folder()
        start_date, end_date = self.date_widget.get_dates()
        start_date = start_date.toPyDate()
        end_date   = end_date.toPyDate()
        all_files  = self.date_widget.all_files_checked()

        self.logger.info("Create BYT button pressed")
        def on_progress(cur, total):
            self.worker.file_progress.emit(cur, total)

        self._stop_event = threading.Event()
        self.worker = ScriptWorker(
            create_byt,
            (
                folder,
                start_date,
                end_date,
                all_files,
                self.logger,
                on_progress,
                self._stop_event,
            )
        )
        self.run_button.setText("Stop")
        self.run_button.setObjectName("btnWarning")
        self.run_button.setStyle(self.run_button.style())
        self.progress.reset()

        busy_cb = getattr(self, "set_busy_callback", None)
        if callable(busy_cb):
            busy_cb(True)
            self.worker.finished.connect(lambda: busy_cb(False))

        self._stop_event.clear()
        self.worker.file_progress.connect(self._on_progress)
        self.worker.finished.connect(lambda: self.run_button.setText("Create BYT"))
        self.worker.finished.connect(lambda: self.run_button.setObjectName(""))
        self.worker.finished.connect(lambda: self.run_button.setStyle(self.run_button.style()))
        self.worker.finished.connect(self.progress.finish)
        self.worker.start()
