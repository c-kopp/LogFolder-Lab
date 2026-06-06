import config as config

from ui.widgets import FolderPickerWidget, DateRangeWidget, ProgressWidget

from src.utils import open_folder
from src.workers import ScriptWorker
from src.tools.search_tool import search_logs

from PyQt6.QtCore import (
    Qt,
)
from PyQt6.QtWidgets import (
    QLabel,
    QWidget,
    QComboBox,
    QGroupBox,
    QCheckBox,
    QHBoxLayout,
    QLineEdit,
    QVBoxLayout,
    QPushButton,
)


class SearchToolPage(QWidget):
    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        layout = QVBoxLayout(self)
        title = QLabel("Search Tool")
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

        # ----- Search Options -----
        group = QGroupBox("Search Options")
        group_layout = QVBoxLayout(group)

        self.search_input = QLineEdit()
        self.mode = QComboBox()
        self.mode.addItems(["OR", "AND"])
        self.regex = QCheckBox("Regex")
        self.regex_help = QLabel("?")
        self.regex_help.setObjectName("help")
        self.regex_help.setFixedSize(20, 20)
        self.regex_help.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.regex_help.setCursor(Qt.CursorShape.PointingHandCursor)
        self.regex_help.setToolTip("""
            <html><body style='font-family: Arial; font-size: 11px;'>
            <b>Regex – Reguläre Ausdrücke</b><br><br>
            <b>Zeichen &amp; Platzhalter</b><br>
            <table cellspacing="3">
                <tr><td><code style='font-family: Courier New;'>.</code></td><td>Beliebiges Zeichen</td><td><code style='font-family: Courier New;'>Ch.nnel → Channel, Ch1nnel</code></td></tr>
                <tr><td><code style='font-family: Courier New;'>\\d</code></td><td>Ziffer (0–9)</td><td><code style='font-family: Courier New;'>\\d\\d:\\d\\d → 09:59</code></td></tr>
                <tr><td><code style='font-family: Courier New;'>\\w</code></td><td>Wortzeichen (a-z, A-Z, 0-9, _)</td><td><code style='font-family: Courier New;'>\\w+ → Aspirate</code></td></tr>
                <tr><td><code style='font-family: Courier New;'>\\s</code></td><td>Whitespace</td><td><code style='font-family: Courier New;'>Channel\\sAspirate</code></td></tr>
            </table><br>
            <b>Quantoren</b><br>
            <table cellspacing="3">
                <tr><td><code style='font-family: Courier New;'>*</code></td><td>0 oder mehr</td><td><code style='font-family: Courier New;'>Err.*found → Error: not found</code></td></tr>
                <tr><td><code style='font-family: Courier New;'>+</code></td><td>1 oder mehr</td><td><code style='font-family: Courier New;'>\\d+ → 1000, 42</code></td></tr>
                <tr><td><code style='font-family: Courier New;'>.*</code></td><td>Beliebig viele Zeichen</td><td><code style='font-family: Courier New;'>Channel.*Aspirate</code></td></tr>
            </table><br>
            <b>Gruppen &amp; Alternativen</b><br>
            <table cellspacing="3">
                <tr><td><code style='font-family: Courier New;'>[abc]</code></td><td>Eines der Zeichen</td><td><code style='font-family: Courier New;'>[Ee]rror → Error, error</code></td></tr>
                <tr><td><code style='font-family: Courier New;'>(abc)</code></td><td>Gruppe</td><td><code style='font-family: Courier New;'>(Error|Warning)</code></td></tr>
                <tr><td><code style='font-family: Courier New;'>a|b</code></td><td>a oder b</td><td><code style='font-family: Courier New;'>start|end</code></td></tr>
            </table>
            </body></html>
        """)

        group_layout.addWidget(QLabel('Search Terms <span style="font-size: 12px; font-weight: normal; color: gray;">- If not Regex, separate terms with a semicolon</span>'))
        group_layout.addWidget(self.search_input)

        regex_layout = QHBoxLayout()
        regex_layout.setSpacing(6)
        regex_layout.setContentsMargins(0, 0, 0, 0)
        regex_layout.addSpacing(20)
        regex_layout.addWidget(self.regex)
        regex_layout.addSpacing(4)
        regex_layout.addWidget(self.regex_help)
        regex_layout.addSpacing(60)

        self.filetype = QComboBox()
        self.filetype.addItems([".trc", ".log", ".txt"])

        opt_layout = QHBoxLayout()
        opt_layout.addWidget(self.mode)
        opt_layout.addLayout(regex_layout)
        opt_layout.addWidget(self.filetype)
        opt_layout.setStretch(0, 1)
        opt_layout.setStretch(1, 0)
        opt_layout.setStretch(2, 1)
        group_layout.addLayout(opt_layout)

        self.copy_files = QCheckBox("Copy files containing search term(s)")
        self.copy_files.setChecked(True)
        self.exclude_sim = QCheckBox("Exclude Simulated Files")

        copy_layout = QHBoxLayout()
        copy_layout.addStretch()
        copy_layout.addWidget(self.copy_files)
        copy_layout.addStretch()
        copy_layout.addWidget(self.exclude_sim)
        copy_layout.addStretch()
        group_layout.addLayout(copy_layout)

        layout.addWidget(group)

        # ----- Stretch -----
        layout.addStretch()

        # ----- Progress -----
        self.progress = ProgressWidget("Processing")
        layout.addWidget(self.progress)

        # ----- Buttons -----
        open_button = QPushButton("Open Output Folder")
        open_button.setObjectName("btnSecondary")
        open_button.clicked.connect(lambda: open_folder(config.get_output_folder("Search")))
        self.run_button = QPushButton("Search")
        self.run_button.clicked.connect(self._run_search)
        layout.addWidget(open_button)
        layout.addWidget(self.run_button)

    def _on_progress(self, cur: int, total: int):
         self.progress.update(cur, total)

    def _run_search(self):
        folder = self.folder_widget.get_folder()
        start_date, end_date = self.date_widget.get_dates()
        start_date = start_date.toPyDate()
        end_date   = end_date.toPyDate()
        all_files  = self.date_widget.all_files_checked()
        terms      = self.search_input.text()
        mode       = self.mode.currentText()
        file_type  = self.filetype.currentText()
        regex      = self.regex.isChecked()
        copy       = self.copy_files.isChecked()
        exclude_sim = self.exclude_sim.isChecked()

        self.logger.info("Search button pressed")
        def on_progress(cur, total):
            self.worker.file_progress.emit(cur, total)

        self.worker = ScriptWorker(
            search_logs,
            (
                folder,
                start_date,
                end_date,
                all_files,
                file_type,
                terms,
                mode,
                regex,
                copy,
                exclude_sim,
                self.logger,
                on_progress,
            )
        )
        self.run_button.setEnabled(False)
        self.progress.reset()

        busy_cb = getattr(self, "set_busy_callback", None)
        if callable(busy_cb):
            busy_cb(True)
            self.worker.finished.connect(lambda: busy_cb(False))

        self.worker.file_progress.connect(self._on_progress)
        self.worker.finished.connect(lambda: self.run_button.setEnabled(True))
        self.worker.finished.connect(lambda: self.progress.finish)
        self.worker.start()
