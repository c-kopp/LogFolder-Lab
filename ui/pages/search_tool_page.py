import os

import src.config as config

from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

from ui.widgets import FolderPicker, DateRangeWidget

from src.workers import ScriptWorker
from src.search_tool import search_logs

class SearchToolPage(QWidget):
    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        layout = QVBoxLayout(self)
        title = QLabel("Search Tool")
        title.setObjectName("title")
        layout.addWidget(title)

        # ----- Folder Search -----
        self.folder_input = QLineEdit(config.get("input_folder"))
        browse = QPushButton("Browse")
        browse.clicked.connect(self.select_folder)

        folder_layout = QHBoxLayout()
        folder_layout.addWidget(self.folder_input)
        folder_layout.addWidget(browse)

        layout.addLayout(folder_layout)

        # ----- Pick Date -----
        self.start_date = QDateEdit(QDate.currentDate().addDays(-5))
        self.end_date = QDateEdit(QDate.currentDate())
        self.start_date.setCalendarPopup(True)
        self.end_date.setCalendarPopup(True)
        self.end_date.setMinimumDate(self.start_date.date())
        self.start_date.dateChanged.connect(self.update_end_date_min)

        self.all_files = QCheckBox("All Files")

        date_layout = QHBoxLayout()
        date_layout.addWidget(self.start_date)
        date_layout.addWidget(self.end_date)
        date_layout.addWidget(self.all_files)

        layout.addLayout(date_layout)

        # ----- Search Terms -----
        self.search_input = QLineEdit()
        layout.addWidget(QLabel('Search Terms <span style="font-size: 12px; font-weight: normal; color: gray;">- If not Regex, separate terms with a semicolon</span>'))
        layout.addWidget(self.search_input)

        self.mode = QComboBox()
        self.mode.addItems(["OR", "AND"])
        self.regex = QCheckBox("Regex")
        self.regex_help = QLabel("?")
        self.regex_help.setStyleSheet("""
            QLabel {
                color: white;
                background-color: #555;
                border-radius: 8px;
                padding: 0px 5px;
                font-size: 11px;
                font-weight: bold;
            }
            QLabel:hover {
                background-color: #333;
            }
        """)
        self.regex_help.setCursor(Qt.CursorShape.PointingHandCursor)
        self.regex_help.setToolTip("""<html><body style='font-family: Arial; font-size: 11px;'>
            <b>Regex – Reguläre Ausdrücke</b><br><br>

            <b>Zeichen &amp; Platzhalter</b><br>
            <table cellspacing="3">
                <tr><td><code style='font-family: Courier New;'>.</code></td><td>Beliebiges Zeichen</td><td><code style='font-family: Courier New;'>Ch.nnel → Channel, Ch1nnel</code></td></tr>
                <tr><td><code style='font-family: Courier New;'>\\d</code></td><td>Ziffer (0–9)</td><td><code style='font-family: Courier New;'>\\d\\d:\\d\\d → 09:59</code></td></tr>
                <tr><td><code style='font-family: Courier New;'>\\D</code></td><td>Kein Ziffernzeichen</td><td><code style='font-family: Courier New;'>\\D+ → Error</code></td></tr>
                <tr><td><code style='font-family: Courier New;'>\\w</code></td><td>Wortzeichen (a-z, A-Z, 0-9, _)</td><td><code style='font-family: Courier New;'>\\w+ → Aspirate</code></td></tr>
                <tr><td><code style='font-family: Courier New;'>\\W</code></td><td>Kein Wortzeichen</td><td><code style='font-family: Courier New;'>Leerzeichen, Sonderzeichen</code></td></tr>
                <tr><td><code style='font-family: Courier New;'>\\s</code></td><td>Whitespace (Leerzeichen, Tab)</td><td><code style='font-family: Courier New;'>Channel\\sAspirate</code></td></tr>
                <tr><td><code style='font-family: Courier New;'>\\t</code></td><td>Tab</td><td><code style='font-family: Courier New;'>Spalten in Log-Zeilen</code></td></tr>
            </table><br>

            <b>Quantoren</b><br>
            <table cellspacing="3">
                <tr><td><code style='font-family: Courier New;'>*</code></td><td>0 oder mehr (vorheriges Zeichen)</td><td><code style='font-family: Courier New;'>Err.*found → Error: not found</code></td></tr>
                <tr><td><code style='font-family: Courier New;'>+</code></td><td>1 oder mehr</td><td><code style='font-family: Courier New;'>\\d+ → 1000, 42</code></td></tr>
                <tr><td><code style='font-family: Courier New;'>?</code></td><td>0 oder 1 (optional)</td><td><code style='font-family: Courier New;'>Errors? → Error, Errors</code></td></tr>
                <tr><td><code style='font-family: Courier New;'>{n}</code></td><td>Genau n mal</td><td><code style='font-family: Courier New;'>\\d{4} → 2026</code></td></tr>
                <tr><td><code style='font-family: Courier New;'>{n,m}</code></td><td>Zwischen n und m mal</td><td><code style='font-family: Courier New;'>\\d{2,4} → 25, 2026</code></td></tr>
                <tr><td><code style='font-family: Courier New;'>.*</code></td><td>Beliebig viele beliebige Zeichen</td><td><code style='font-family: Courier New;'>Channel.*Aspirate</code></td></tr>
            </table><br>

            <b>Anker &amp; Grenzen</b><br>
            <table cellspacing="3">
                <tr><td><code style='font-family: Courier New;'>^</code></td><td>Anfang der Zeile</td><td><code style='font-family: Courier New;'>^2026 → Zeile beginnt mit 2026</code></td></tr>
                <tr><td><code style='font-family: Courier New;'>$</code></td><td>Ende der Zeile</td><td><code style='font-family: Courier New;'>start;$ → Zeile endet mit start;</code></td></tr>
                <tr><td><code style='font-family: Courier New;'>\\b</code></td><td>Wortgrenze</td><td><code style='font-family: Courier New;'>\\bError\\b → Error, nicht Errors</code></td></tr>
            </table><br>

            <b>Gruppen &amp; Alternativen</b><br>
            <table cellspacing="3">
                <tr><td><code style='font-family: Courier New;'>[abc]</code></td><td>Eines der Zeichen a, b oder c</td><td><code style='font-family: Courier New;'>[Ee]rror → Error, error</code></td></tr>
                <tr><td><code style='font-family: Courier New;'>[^abc]</code></td><td>Keines dieser Zeichen</td><td><code style='font-family: Courier New;'>[^0-9] → kein Ziffernzeichen</code></td></tr>
                <tr><td><code style='font-family: Courier New;'>[a-z]</code></td><td>Zeichenbereich</td><td><code style='font-family: Courier New;'>[a-zA-Z]+ → nur Buchstaben</code></td></tr>
                <tr><td><code style='font-family: Courier New;'>(abc)</code></td><td>Gruppe</td><td><code style='font-family: Courier New;'>(Error|Warning) → beides</code></td></tr>
                <tr><td><code style='font-family: Courier New;'>a|b</code></td><td>a oder b</td><td><code style='font-family: Courier New;'>start|end → start oder end</code></td></tr>
            </table><br>

            <b>Praxisbeispiele</b><br>
            <table cellspacing="3">
                <tr><td>Datum + Uhrzeit</td><td><code style='font-family: Courier New;'>\\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}</code></td></tr>
                <tr><td>Zwei Wörter mit Lücke</td><td><code style='font-family: Courier New;'>Channel.*Aspirate</code></td></tr>
                <tr><td>Fehler oder Warnung</td><td><code style='font-family: Courier New;'>(Error|Warning|WARN)</code></td></tr>
                <tr><td>Zahl am Ende</td><td><code style='font-family: Courier New;'>\\d+$</code></td></tr>
                <tr><td>IP-Adresse</td><td><code style='font-family: Courier New;'>\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}</code></td></tr>
            </table>
            </body></html>""")

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

        layout.addLayout(opt_layout)

        # ----- Start Script -----
        self.btn_search = QPushButton("Search")
        self.copy_files = QCheckBox("Copy files containing search term(s)")
        self.copy_files.setChecked(True)
        self.btn_search.clicked.connect(self.run_search)

        search_layout = QHBoxLayout()
        search_layout.addWidget(self.copy_files, 2)
        search_layout.addWidget(self.btn_search, 3)

        layout.addLayout(search_layout)
        layout.addStretch()


    def update_end_date_min(self, date):
        self.end_date.setMinimumDate(date)

        if self.end_date.date() < date:
            self.end_date.setDate(date)

    def select_folder(self):
        path = QFileDialog.getExistingDirectory(self)
        if path:
            self.folder_input.setText(path)

    def run_search(self):
        folder = self.folder_input.text()
        start_date = self.start_date.date().toPyDate()
        end_date = self.end_date.date().toPyDate()
        all_files = self.all_files.isChecked()
        terms = self.search_input.text()
        mode = self.mode.currentText()
        file_type = self.filetype.currentText()
        regex = self.regex.isChecked()
        copy = self.copy_files.isChecked()
        self.logger.info("Search button pressed")
        self.worker = ScriptWorker(search_logs, (folder, start_date, end_date, all_files, file_type, terms, mode, regex, copy, self.logger))
        self.worker.start()
