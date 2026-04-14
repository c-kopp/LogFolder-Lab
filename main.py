#==============================================================================#
# KoppiRight (CK) by Hamilton Bonaduz AG, CH-7402 Bonaduz                      #
# All rights reserved                                                          #
# Description: ISD LogFolder Lab Tool to search and convert log files          #
#      for better analysis of runs and statistics                              #
# 14.03.2026 - Christoph Kopp                                                  #
#                                                                              #
#==============================================================================#

import os
import sys
import getpass
import logging
import requests
import platform

import config as config

from config import APP_NAME, APP_VERSION

from src.workers import ScriptWorker
from src.logger_handler import LogEmitter, setup_logger

from ui.pages.mad_tool_page import MadToolPage
from ui.pages.settings_page import SettingsPage
from ui.pages.step_times_page import StepTimesPage
from ui.pages.search_tool_page import SearchToolPage
from ui.pages.qr_generator_page import QRGeneratorPage
from ui.pages.beautiful_trace_page import BeautifyTracePage
from ui.pages.pipetting_scheme_page import PipettingSchemePage
from ui.pages.barcode_generator_page import BarcodeGeneratorPage

from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *


class SidebarButton(QPushButton):
    def __init__(self, text, icon=None):
        super().__init__(text)
        self.full_text = text
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(42)
        self.setIconSize(QSize(18, 18))
        self.setStyleSheet("QPushButton { text-align: left; padding-left: 14px; }")
        if icon:
            self.setIcon(icon)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ISD LogFolder-Lab")
        self.resize(1250, 780)

        self._setup_logger()
        self._setup_ui()
        self._load_stylesheet()

        user    = getpass.getuser()
        os_info = f"{platform.system()} {platform.release()}"
        self.system_info_label.setText(f"v{APP_VERSION} | {user} | {os_info}")
        self.logger.info("Application started")
        self.logger.debug(f"Version: {APP_VERSION} | User: {user} | OS: {os_info}")

    # ------------------------------------------------------------------ #
    # Setup                                                              #
    # ------------------------------------------------------------------ #

    def _setup_logger(self):
        self.log_emitter = LogEmitter()
        self.log_emitter.log_signal.connect(self.append_log)
        self.logger = setup_logger(self.log_emitter)

    def _setup_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        main_layout = QHBoxLayout(root)
        main_layout.addWidget(self._build_sidebar())
        main_layout.addWidget(self._build_content())

    def _build_sidebar(self):
        self.icon_expand   = self.get_icon("chevron-right")
        self.icon_collapse = self.get_icon("chevron-left")

        self.btn_home       = SidebarButton("Home",                 self.get_icon("house"))
        self.btn_search     = SidebarButton("Search Tool",          self.get_icon("search"))
        self.btn_pipetting  = SidebarButton("Pipetting Scheme",     self.get_icon("grid-3x2-gap"))
        self.btn_beautiful  = SidebarButton("Beautify Trace",       self.get_icon("file-earmark-text"))
        self.btn_timings    = SidebarButton("Step Times",           self.get_icon("stopwatch"))
        self.btn_mad        = SidebarButton("MAD Tool",             self.get_icon("graph-up"))
        self.btn_qr         = SidebarButton("QR Generator",         self.get_icon("qr-code-scan"))
        self.btn_barcode    = SidebarButton("Barcode Generator",    self.get_icon("upc-scan"))
        self.btn_settings   = SidebarButton("Settings",             self.get_icon("gear"))

        self.btn_list  = [
            self.btn_home,
            self.btn_search,
            self.btn_pipetting,
            self.btn_beautiful,
            self.btn_timings,
            self.btn_mad,
            self.btn_qr,
            self.btn_barcode,
            self.btn_settings
        ]
        self.name_list = [
            "Home",
            "Search Tool",
            "Pipetting Scheme",
            "Beautify Trace",
            "Step Times",
            "MAD Tool",
            "QR Generator",
            "Barcode Generator",
            "Settings"
        ]

        self.toggle_btn = QPushButton()
        self.toggle_btn.setObjectName("btnSecondary")
        self.toggle_btn.setFixedSize(40, 40)
        self.toggle_btn.setIcon(self.icon_collapse)
        self.toggle_btn.clicked.connect(self.toggle_sidebar)


        sidebar_layout = QVBoxLayout()

        for btn in self.btn_list[:-1]:
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()
        sidebar_layout.addWidget(self.btn_settings)
        sidebar_layout.addWidget(self.toggle_btn)

        self.sidebar_expanded = True
        self.sidebar_widget = QWidget()
        self.sidebar_widget.setLayout(sidebar_layout)
        self.sidebar_widget.setFixedWidth(220)

        return self.sidebar_widget

    def _build_content(self):
        config.init_output_folders()

        self.settings_page = SettingsPage(self.logger)
        self.settings_page.settings_changed.connect(self._on_settings_changed)

        self.search_page = SearchToolPage(self.logger)
        self.pipette_page = PipettingSchemePage(self.logger)
        self.beautify_page = BeautifyTracePage(self.logger)
        self.times_page = StepTimesPage(self.logger)
        self.mad_page = MadToolPage(self.logger)
        self.qr_page = QRGeneratorPage(self.logger)
        self.barcode_page = BarcodeGeneratorPage(self.logger)

        self.pages = QStackedWidget()
        self.pages.addWidget(self._build_home())
        self.pages.addWidget(self.search_page)
        self.pages.addWidget(self.pipette_page)
        self.pages.addWidget(self.beautify_page)
        self.pages.addWidget(self.times_page)
        self.pages.addWidget(self.mad_page)
        self.pages.addWidget(self.qr_page)
        self.pages.addWidget(self.barcode_page)
        self.pages.addWidget(self.settings_page)

        for i, btn in enumerate(self.btn_list):
            btn.clicked.connect(lambda _, idx=i, name=self.name_list[i]: self.switch_page(idx, name))

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setFixedHeight(130)

        self.system_info_label = QLabel()
        self.system_info_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.system_info_label.setObjectName("systemInfo")

        content_layout = QVBoxLayout()
        content_layout.addWidget(self.pages)
        content_layout.addWidget(self.log_box)
        content_layout.addWidget(self.system_info_label)

        content_widget = QWidget()
        content_widget.setLayout(content_layout)

        wrap = config.get("log_word_wrap") == "true"
        self.log_box.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth if wrap else QTextEdit.LineWrapMode.NoWrap)
        return content_widget

    def _build_home(self):
        home = QWidget()
        layout = QVBoxLayout(home)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

        image_label = QLabel()
        image_label.setObjectName("HomeLogo")
        image_label.setPixmap(self._rounded_pixmap(
            os.path.join(config.get("image_folder"), "customizedSolution.png")))
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_label = QLabel(APP_NAME)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setObjectName("title")

        hint = QLabel('If you face any issue please reach out to me: <a href="mailto:ckopp@hamilton.ch">ckopp@hamilton.ch</a>')
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint.setStyleSheet("color: gray; font-size: 11px;")

        layout.addWidget(image_label)
        layout.addWidget(title_label)
        layout.addWidget(hint)
        layout.addStretch()
        return home

    def _load_stylesheet(self):
        path = self.resource_path("styles.qss")
        try:
            with open(path, "r") as f:
                self.setStyleSheet(f.read())
        except Exception:
            self.setStyleSheet("QMainWindow { background-color: #1e1e1e; } QLabel { color: white; }")

    # ------------------------------------------------------------------ #
    # Helpers                                                            #
    # ------------------------------------------------------------------ #

    def resource_path(self, relative_path):
        if getattr(sys, 'frozen', False):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)

    def get_icon(self, name):
        local_path    = os.path.join(config.get("icon_folder"), f"{name}.svg")
        bundled_path  = self.resource_path(local_path)

        for path in [bundled_path, local_path]:
            if os.path.exists(path):
                return QIcon(path)

        try:
            os.makedirs(config.get("icon_folder"), exist_ok=True)
            url = f"https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/icons/{name}.svg"
            r = requests.get(url, timeout=3)
            r.raise_for_status()
            with open(local_path, "wb") as f:
                f.write(r.content)
            return QIcon(local_path)
        except Exception as e:
            self.logger.error(f"Icon not found: {name} ({e})")
            return QIcon()

    def _rounded_pixmap(self, path, width=600, radius=50):
        pixmap = QPixmap(self.resource_path(path))
        if pixmap.isNull() or pixmap.width() == 0:
            return QPixmap(width, 400)

        height = int(pixmap.height() * (width / pixmap.width()))
        scaled = pixmap.scaled(width, height,
                               Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                               Qt.TransformationMode.SmoothTransformation)
        rounded = QPixmap(width, height)
        rounded.fill(Qt.GlobalColor.transparent)
        painter = QPainter(rounded)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        clip = QPainterPath()
        clip.addRoundedRect(0, 0, width, height, radius, radius)
        painter.setClipPath(clip)
        painter.drawPixmap(0, 0, scaled)
        painter.end()
        return rounded

    # ------------------------------------------------------------------ #
    # Slots                                                              #
    # ------------------------------------------------------------------ #

    def switch_page(self, index, name):
        self.pages.setCurrentIndex(index)
        self.logger.info(f"Changed to {name}")

    def toggle_sidebar(self):
        if self.sidebar_expanded:
            self.sidebar_widget.setFixedWidth(70)

            for btn in self.btn_list:
                btn.setText("")

            self.toggle_btn.setIcon(self.icon_expand)
            self.sidebar_expanded = False
        else:
            self.sidebar_widget.setFixedWidth(220)

            for btn, text in zip(self.btn_list, self.name_list):
                btn.setText(text)

            self.toggle_btn.setIcon(self.icon_collapse)
            self.sidebar_expanded = True

    def _on_settings_changed(self):
        self.search_page.folder_widget.folder_input.setText(config.get("input_folder"))
        self.pipette_page.folder_widget.folder_input.setText(config.get("input_folder"))
        self.beautify_page.folder_widget.folder_input.setText(config.get("input_folder"))
        wrap = config.get("log_word_wrap") == "true"
        self.log_box.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth if wrap else QTextEdit.LineWrapMode.NoWrap)
        self.logger.info("Settings applied")

    def append_log(self, msg):
        color = "#00ff9c"
        if "ERROR"     in msg: color = "#ff6b6b"
        elif "WARNING" in msg: color = "#ffd166"
        elif "DEBUG"   in msg: color = "#8ab4ff"
        self.log_box.append(f'<span style="color:{color}">{msg}</span>')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
