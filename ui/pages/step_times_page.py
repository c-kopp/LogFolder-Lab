import config as config

from ui.widgets import FolderPickerWidget, DateRangeWidget, ProgressWidget

from src.utils import open_folder
from src.workers import ScriptWorker
from src.tools.step_time_tool import analyze_step_time

from PyQt6.QtWidgets import (
    QLabel,
    QWidget,
    QGroupBox,
    QCheckBox,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
)


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
        self.folder_widget = FolderPickerWidget(config.get("input_folder"))
        general_group_layout.addWidget(self.folder_widget)
        self.date_widget = DateRangeWidget()
        general_group_layout.addWidget(self.date_widget)
        layout.addWidget(general_group)
        layout.addSpacing(20)

        # ----- Options -----
        group = QGroupBox("Step Times Options")
        self.exclude_sim = QCheckBox("Exclude Simulated Files")
        self.exclude_sim.setChecked(True)
        opt_layout = QHBoxLayout()
        opt_layout.addStretch()
        opt_layout.addWidget(self.exclude_sim)
        opt_layout.addStretch()
        group.setLayout(opt_layout)
        layout.addWidget(group)

        # ----- Stretch -----
        layout.addStretch()

        # ----- Progress -----
        self.progress = ProgressWidget("Processing")
        layout.addWidget(self.progress)

        # ----- Buttons -----
        open_button = QPushButton("Open Output Folder")
        open_button.setObjectName("btnSecondary")
        open_button.clicked.connect(lambda: open_folder(config.get_output_folder("Times")))
        self.run_button = QPushButton("Analyze Step Times")
        self.run_button.clicked.connect(self._run_script)
        layout.addWidget(open_button)
        layout.addWidget(self.run_button)

    def _on_progress(self, cur: int, total: int):
         self.progress.update(cur, total)

    def _run_script(self):
        folder = self.folder_widget.get_folder()
        start_date, end_date = self.date_widget.get_dates()
        start_date  = start_date.toPyDate()
        end_date    = end_date.toPyDate()
        all_files   = self.date_widget.all_files_checked()
        exclude_sim = self.exclude_sim.isChecked()

        self.logger.info("Analyze Step Times button pressed")
        def on_progress(cur, total):
            self.worker.file_progress.emit(cur, total)

        self.worker = ScriptWorker(
            analyze_step_time,
            (
                folder,
                start_date,
                end_date,
                all_files,
                exclude_sim,
                self.logger,
                on_progress,
            )
        )

        busy_cb = getattr(self, "set_busy_callback", None)
        if callable(busy_cb):
            busy_cb(True)
            self.worker.finished.connect(lambda: busy_cb(False))

        self.worker.file_progress.connect(self._on_progress)
        self.worker.finished.connect(lambda: self.run_button.setEnabled(True))
        self.worker.finished.connect(lambda: self.progress.finish)
        self.worker.start()
