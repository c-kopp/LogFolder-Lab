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

from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

from workers import ScriptWorker
from logger_handler import LogEmitter, setup_logger

from ui.pages.mad_tool_page import MadToolPage
from ui.pages.search_tool_page import SearchToolPage
from ui.pages.convert_tool_page import ConvertToolPage

from src.search_tool import search_logs
from src.convert_tool import create_pts, create_byt
from src.mad_tool import visualize_mad


DEFAULT_FOLDER = r"C:/Program Files (x86)/Hamilton/Logfiles"
if not os.path.isdir(DEFAULT_FOLDER):
    DEFAULT_FOLDER = r"./data"

ICON_FOLDER = "icons"
IMAGE_FOLDER = "images"
APP_NAME = "Hamilton LogFolder-Lab"
APP_VERSION = "0.0.1"


class SidebarButton(QPushButton):
    def __init__(self, text, icon=None):
        super().__init__(text)
        self.full_text = text
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(42)
        self.setIconSize(QSize(18, 18))
        self.setStyleSheet("""
            QPushButton{
                text-align: left;
                padding-left: 14px;
            }
        """)
        if icon:
            self.setIcon(icon)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("ISD LogFolder-Lab")
        self.resize(1250, 780)

        # ---------- Root Layout ----------
        root = QWidget()
        self.setCentralWidget(root)
        main_layout = QHBoxLayout(root)

        # ---------- Logger ----------
        self.log_emitter = LogEmitter()
        self.log_emitter.log_signal.connect(self.append_log)

        self.logger = logging.getLogger("AppLogger")
        self.logger = setup_logger(self.log_emitter)

        # ---------- Icons for Sidebar ----------
        self.icon_cache = {}

        def is_frozen():
            return getattr(sys, 'frozen', False)

        def resource_path(relative_path):
            if is_frozen():
                return os.path.join(sys._MEIPASS, relative_path)
            return os.path.join(os.path.abspath("."), relative_path)

        def get_icon(name):
            filename = f"{name}.svg"

            # if script is converted into .exe
            bundled_path = resource_path(os.path.join(ICON_FOLDER, filename))
            if os.path.exists(bundled_path):
                return QIcon(bundled_path)

            # if icon already used once and script is NOT converted to .exe
            local_path = os.path.join(ICON_FOLDER, filename)
            if os.path.exists(local_path):
                return QIcon(local_path)

            if not is_frozen():
                url = f"https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/icons/{name}.svg"
                try:
                    os.makedirs(ICON_FOLDER, exist_ok=True)

                    r = request.get(url, timeout=3)
                    r.raise_for_status()

                    with open(local_path, "wb") as f:
                        f.write(r.content)

                    return QIcon(local_path)
                except Exception as e:
                    logger.error(f"Download failed for {name}: {e}")

            logger.error(f"Icon not found: {name}")
            return QIcon()

        # ---------- Sidebar ----------
        self.sidebar_expanded = True
        self.sidebar = QVBoxLayout()

        self.sidebar_widget = QWidget()
        self.sidebar_widget.setLayout(self.sidebar)
        self.sidebar_widget.setFixedWidth(220)

        self.title_label = QLabel("ISD Tools")
        self.title_label.setObjectName("sidebarTitle")

        self.btn_home = SidebarButton("Home", get_icon("house"))
        self.btn_search = SidebarButton("Search Tool", get_icon("search"))
        self.btn_convert = SidebarButton("Convert Tool", get_icon("file-earmark-text"))
        self.btn_mad = SidebarButton("MAD Tool", get_icon("graph-up"))

        self.icon_expand = get_icon("chevron-right")
        self.icon_collapse = get_icon("chevron-left")
        self.toggle_btn = QPushButton()
        self.toggle_btn.setFixedSize(36, 36)
        self.toggle_btn.setIcon(self.icon_collapse)
        self.toggle_btn.clicked.connect(self.toggle_sidebar)

        self.sidebar.addWidget(self.title_label)
        self.sidebar.addSpacing(15)
        for btn in [
            self.btn_home,
            self.btn_search,
            self.btn_convert,
            #self.btn_mad
        ]:
            self.sidebar.addWidget(btn)
        self.sidebar.addStretch
        self.sidebar.addWidget(self.toggle_btn)

        main_layout.addWidget(self.sidebar_widget)

        # ---------- Pages ----------

        self.search_page = SearchToolPage(self.logger)
        self.convert_page = ConvertToolPage(self.logger)
        #self.mad_page = MADToolPage(self.logger)


        self.pages = QStackedWidget()
        home = QWidget()
        home_layout = QVBoxLayout(home)
        home_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        home_layout.addStretch()

        def rounded_pixmap(path):
            full_path = resource_path(path)

            pixmap = QPixmap(full_path)

            if pixmap.isNull():
                pixmap = QPixmap(f":/{path}")

            if pixmap.isNull() or pixmap.width() == 0:
                print(f"Image not found: {path}")
                return QPixmap(600, 400)

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
        image_label.setPixmap(rounded_pixmap(os.path.join(IMAGE_FOLDER, "customizedSolution.png")))
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        app_name_label = QLabel(f"{APP_NAME}")
        app_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_name_label.setObjectName("title")

        home_layout.addWidget(image_label)
        home_layout.addWidget(app_name_label)

        home_layout.addStretch()
        self.pages.addWidget(home)
        self.pages.addWidget(self.search_page)
        self.pages.addWidget(self.convert_page)
        #self.pages.addWidget(self.mad_page)


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

            for btn, text in zip([self.btn_home,self.btn_search,self.btn_convert],
                                ["Home","Search Tool","Convert Tool"]):
                btn.setText(text)

            self.title_label.setText("ISD Tool")
            self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.title_label.setContentsMargins(5, 0, 0, 0)

            self.toggle_btn.setIcon(self.icon_collapse)
            self.sidebar_expanded = True

    def append_log(self, msg):
        color = "#00ff9c"
        if "ERROR" in msg:
            color = "#ff6b6b"
        elif "WARNING" in msg:
            color = "#ffd166"
        elif "DEBUG" in msg:
            color = "#8ab4ff"
        self.log_box.append(f'<span style="color:{color}">{msg}</span>')

if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
