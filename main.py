#!/usr/bin/env python3.13.9

#==============================================================================#
# KoppiRight (CK) by Hamilton Bonaduz AG, CH-7402 Bonaduz                      #
# All rights reserved                                                          #
# Description: Scheme Builder for Pipetting and Transport for reNEW            #
#                                                                              #
# 14.03.2026 - Christoph Kopp                                                  #
#                                                                              #
#==============================================================================#

import os
import sys
import getpass
import logging
import requests
import platform

from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

from workers import ScriptWorker
from logger_handler import LogEmitter, setup_logger

from src.search_tool import search_logs
from src.convert_tool import create_pts, create_byt
from src.mad_tool import visualize_mad

DEFAULT_FOLDER = r"C:/Program Files (x86)/Hamilton/Logfiles"
ICON_FOLDER = "icons"
APP_NAME = "Hamilton LogFolder-Lab"
APP_VERSION = "0.0.1"

# ---------------- Sidebar Button ----------------
class SidebarButton(QPushButton):
    def __init__(self, text, icon=None):
        super().__init__(text)
        self.full_text = text
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(42)
        self.setIconSize(QSize(18, 18))
        self.setStyleSheet("QPushButton{ text-align:left; padding-left:14px;}")
        if icon:
            self.setIcon(icon)

# ---------------- Pages ----------------
class SearchToolPage(QWidget):
    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        layout = QVBoxLayout(self)
        title = QLabel("Search Tool")
        title.setObjectName("title")
        layout.addWidget(title)

        # ----- Folder Search -----
        self.folder_input = QLineEdit(DEFAULT_FOLDER)
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
        layout.addWidget(QLabel("Search Terms"))
        layout.addWidget(self.search_input)

        self.mode = QComboBox()
        self.mode.addItems(["OR", "AND"])
        self.regex = QCheckBox("Regex")
        self.filetype = QComboBox()
        self.filetype.addItems([".trc", ".log", ".txt"])
        opt_layout = QHBoxLayout()
        opt_layout.addWidget(self.mode)
        opt_layout.addWidget(self.regex)
        opt_layout.addWidget(self.filetype)

        layout.addLayout(opt_layout)

        # ----- Start Script -----
        self.btn_search = QPushButton("Search")
        self.btn_search.clicked.connect(self.run_search)
        layout.addWidget(self.btn_search)
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
        self.logger.info("Search button pressed")
        self.worker = ScriptWorker(search_logs, (folder, start_date, end_date, all_files, file_type, terms, mode, regex, self.logger))
        self.worker.start()

# ---------------- Convert Tool ----------------
class ConvertToolPage(QWidget):
    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        layout = QVBoxLayout(self)
        title = QLabel("Convert Tool")
        title.setObjectName("title")
        layout.addWidget(title)

        self.folder_input = QLineEdit(DEFAULT_FOLDER)
        browse = QPushButton("Browse")
        browse.clicked.connect(self.select_folder)
        folder_layout = QHBoxLayout()
        folder_layout.addWidget(self.folder_input, 4)
        folder_layout.addWidget(browse, 1)
        layout.addLayout(folder_layout)

        self.start_date = QDateEdit(QDate.currentDate().addDays(-5))
        self.end_date = QDateEdit(QDate.currentDate())
        self.start_date.setCalendarPopup(True)
        self.end_date.setCalendarPopup(True)
        self.end_date.setMinimumDate(self.start_date.date())
        self.start_date.dateChanged.connect(self.update_end_date_min)

        self.all_files = QCheckBox("All Files")

        date_layout = QHBoxLayout()
        date_layout.addWidget(self.start_date, 2)
        date_layout.addWidget(self.end_date, 2)
        date_layout.addWidget(self.all_files, 1)

        layout.addLayout(date_layout)

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

        layout.addLayout(pts_layout)
        layout.addWidget(self.btn_byt)
        layout.addStretch()

    def update_end_date_min(self, date):
        self.end_date.setMinimumDate(date)

        if self.end_date.date() < date:
            self.end_date.setDate(date)

    def select_folder(self):
        path = QFileDialog.getExistingDirectory(self)
        if path:
            self.folder_input.setText(path)

    def run_pts(self):
        folder = self.folder_input.text()
        self.logger.info("Create PTS button pressed")
        start_date = self.start_date.date().toPyDate()
        end_date = self.end_date.date().toPyDate()
        all_files = self.all_files.isChecked()
        pipetting = self.pipetting.isChecked()
        transports = self.transports.isChecked()
        self.worker = ScriptWorker(create_pts, (folder, start_date, end_date, all_files, transports, pipetting, self.logger))
        self.worker.start()

    def run_byt(self):
        folder = self.folder_input.text()
        self.logger.info("Create BYT button pressed")
        start_date = self.start_date.date().toPyDate()
        end_date = self.end_date.date().toPyDate()
        all_files = self.all_files.isChecked()
        self.worker = ScriptWorker(create_byt, (folder, start_date, end_date, all_files, self.logger))
        self.worker.start()

# ---------------- MAD Tool ----------------
class MADToolPage(QWidget):
    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        layout = QVBoxLayout(self)
        title = QLabel("MAD Tool")
        title.setObjectName("title")
        layout.addWidget(title)

        self.folder_input = QLineEdit(DEFAULT_FOLDER)
        browse = QPushButton("Browse")
        browse.clicked.connect(self.select_folder)
        folder_layout = QHBoxLayout()
        folder_layout.addWidget(self.folder_input)
        folder_layout.addWidget(browse)
        layout.addLayout(folder_layout)

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

        self.btn_visualize = QPushButton("Visualize")
        self.btn_visualize.clicked.connect(self.run_mad)
        layout.addWidget(self.btn_visualize)
        layout.addStretch()

    def update_end_date_min(self, date):
        self.end_date.setMinimumDate(date)

        if self.end_date.date() < date:
            self.end_date.setDate(date)

    def select_folder(self):
        path = QFileDialog.getExistingDirectory(self)
        if path:
            self.folder_input.setText(path)

    def run_mad(self):
        folder = self.folder_input.text()
        start_date = self.start_date.date().toPyDate()
        end_date = self.end_date.date().toPyDate()
        all_files = self.all_files.isChecked()
        self.logger.info("MAD visualize button pressed")
        self.worker = ScriptWorker(visualize_mad, (folder, start_date, end_date, all_files, self.logger))
        self.worker.start()

# ---------------- Main Window ----------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ISD Trace & Log Tool")
        self.resize(1250, 780)
        root = QWidget()
        self.setCentralWidget(root)
        main_layout = QHBoxLayout(root)

        # Logger
        self.log_emitter = LogEmitter()
        self.log_emitter.log_signal.connect(self.append_log)
        self.logger = logging.getLogger("AppLogger")
        self.logger.setLevel(logging.INFO)

        self.log_emitter = LogEmitter()
        self.log_emitter.log_signal.connect(self.append_log)

        self.logger = setup_logger(self.log_emitter)

        # ---------------- Sidebar + Icons ----------------
        self.icon_cache = {}

        def get_icon(name):
            os.makedirs(ICON_FOLDER, exist_ok=True)
            path = f"{ICON_FOLDER}/{name}.svg"

            if os.path.exists(path):
                return QIcon(path)

            url = f"https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/icons/{name}.svg"

            try:
                r = requests.get(url)
                r.raise_for_status()

                with open(path, "wb") as f:
                    f.write(r.content)

                return QIcon(path)

            except:
                return QIcon()

        # Toggle Icons
        self.icon_expand = get_icon("chevron-right")
        self.icon_collapse = get_icon("chevron-left")

        self.sidebar_expanded = True
        self.sidebar = QVBoxLayout()
        self.sidebar_widget = QWidget()
        self.sidebar_widget.setLayout(self.sidebar)
        self.sidebar_widget.setFixedWidth(220)

        self.title_label = QLabel("ISD Tool")
        self.title_label.setObjectName("sidebarTitle")
        self.sidebar.addWidget(self.title_label)
        self.sidebar.addSpacing(15)

        self.btn_home = SidebarButton("Home", get_icon("house"))
        self.btn_search = SidebarButton("Search Tool", get_icon("search"))
        self.btn_convert = SidebarButton("Convert Tool", get_icon("file-earmark-text"))
        self.btn_mad = SidebarButton("MAD Tool", get_icon("graph-up"))

        for btn in [self.btn_home, self.btn_search, self.btn_convert, self.btn_mad]:
            self.sidebar.addWidget(btn)
        self.sidebar.addStretch()

        self.toggle_btn = QPushButton()
        self.toggle_btn.setFixedSize(36,36)
        self.toggle_btn.setIcon(self.icon_collapse)
        self.toggle_btn.clicked.connect(self.toggle_sidebar)
        self.sidebar.addWidget(self.toggle_btn)

        main_layout.addWidget(self.sidebar_widget)

        # ---------------- Pages ----------------
        self.pages = QStackedWidget()

        home = QWidget()
        home_layout = QVBoxLayout(home)
        home_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        home_layout.addStretch()

        def rounded_pixmap(path):
            pixmap = QPixmap(path)

            width = 600
            radius = 50
            height = int(pixmap.height() * (width / pixmap.width()))

            scaled = pixmap.scaled(
                width,
                height,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )

            rounded = QPixmap(width, height)
            rounded.fill(Qt.GlobalColor.transparent)

            painter = QPainter(rounded)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            path_clip = QPainterPath()
            path_clip.addRoundedRect(0, 0, width, height, radius, radius)

            painter.setClipPath(path_clip)
            painter.drawPixmap(0, 0, scaled)
            painter.end()

            return rounded

        image_label = QLabel()
        image_label.setObjectName("HomeLogo")
        image_label.setPixmap(rounded_pixmap("icons/customizedSolution.png"))
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        app_name_label = QLabel(f"{APP_NAME}")
        app_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_name_label.setObjectName("title")

        home_layout.addWidget(image_label)
        home_layout.addWidget(app_name_label)

        home_layout.addStretch()

        self.search_page = SearchToolPage(self.logger)
        self.convert_page = ConvertToolPage(self.logger)
        self.mad_page = MADToolPage(self.logger)
        self.pages.addWidget(home)
        self.pages.addWidget(self.search_page)
        self.pages.addWidget(self.convert_page)
        self.pages.addWidget(self.mad_page)

        # Log window
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setFixedHeight(220)
        content_layout = QVBoxLayout()
        content_layout.addWidget(self.pages)
        content_layout.addWidget(self.log_box)

        self.system_info_label = QLabel()
        self.system_info_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.system_info_label.setObjectName("systemInfo")

        user = getpass.getuser()
        os_info = f"{platform.system()} {platform.release()}"

        self.system_info_label.setText(
            f"v{APP_VERSION} | {user} | {os_info}"
        )
        content_layout.addWidget(self.system_info_label)

        content_widget = QWidget()
        content_widget.setLayout(content_layout)
        main_layout.addWidget(content_widget)

        # Navigation
        self.btn_home.clicked.connect(lambda: self.switch_page(0,"Home"))
        self.btn_search.clicked.connect(lambda: self.switch_page(1,"Search Tool"))
        self.btn_convert.clicked.connect(lambda: self.switch_page(2,"Convert Tool"))
        self.btn_mad.clicked.connect(lambda: self.switch_page(3,"MAD Tool"))

        user = getpass.getuser()
        os_info = f"{platform.system()} {platform.release()}"

        self.logger.info("Application started")
        self.logger.debug(f"Version: {APP_VERSION}")
        self.logger.debug(f"User: {user}")
        self.logger.debug(f"OS: {os_info}")

        # Load Stylesheet
        with open("styles.qss","r") as f:
            self.setStyleSheet(f.read())

    def switch_page(self,index,name):
        self.pages.setCurrentIndex(index)
        self.logger.info(f"Changed to {name}")

    def toggle_sidebar(self):
        if self.sidebar_expanded:
            self.sidebar_widget.setFixedWidth(70)

            for btn in [self.btn_home,self.btn_search,self.btn_convert,self.btn_mad]:
                btn.setText("")

            self.title_label.setText("ISD")
            self.title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.title_label.setContentsMargins(0, 0, 0, 0)

            self.toggle_btn.setIcon(self.icon_expand)
            self.sidebar_expanded = False
        else:
            self.sidebar_widget.setFixedWidth(220)

            for btn,text in zip([self.btn_home,self.btn_search,self.btn_convert,self.btn_mad],
                                ["Home","Search Tool","Convert Tool","MAD Tool"]):
                btn.setText(text)

            self.title_label.setText("ISD Tool")
            self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.title_label.setContentsMargins(5, 0, 0, 0)

            self.toggle_btn.setIcon(self.icon_collapse)
            self.sidebar_expanded = True

    def append_log(self,msg):
        color = "#00ff9c"
        if "ERROR" in msg:
            color = "#ff6b6b"
        elif "WARNING" in msg:
            color = "#ffd166"
        elif "DEBUG" in msg:
            color = "#8ab4ff"
        self.log_box.append(f'<span style="color:{color}">{msg}</span>')

# ---------------- Run ----------------
app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
