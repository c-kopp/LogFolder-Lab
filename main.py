import sys
import logging

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTabWidget,
    QWidget,
    QVBoxLayout,
    QTextEdit
)

from logger_handler import LogEmitter, setup_logger

from ui.pages.mad_tool_page import MadToolPage
from ui.pages.search_tool_page import SearchToolPage
from ui.pages.convert_tool_page import ConvertToolPage


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("ISD Trace & Log Tool")
        self.resize(1250, 780)

        # ---------- Logger ----------
        self.log_emitter = LogEmitter()
        self.log_emitter.log_signal.connect(self.append_log)

        self.logger = setup_logger(self.log_emitter)

        # ---------- Layout Container ----------
        container = QWidget()
        layout = QVBoxLayout(container)

        # ---------- Tabs ----------
        self.tabs = QTabWidget()

        self.tabs.addTab(MadToolPage(self.logger), "MAD Tool")
        self.tabs.addTab(SearchToolPage(self.logger), "Search Tool")
        self.tabs.addTab(ConvertToolPage(self.logger), "Convert Tool")

        layout.addWidget(self.tabs)

        # ---------- Log Window ----------
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setMaximumHeight(200)

        layout.addWidget(self.log_view)

        self.setCentralWidget(container)

    def append_log(self, message):
        self.log_view.append(message)


if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = MainWindow()   # ❗ kein logger hier
    window.show()

    sys.exit(app.exec())
