import os
import logging

import config as config

from datetime import datetime
from PyQt6.QtCore import QObject, pyqtSignal

LOG_NAME = "LogFolder-Lab"

class LogEmitter(QObject):
    log_signal = pyqtSignal(str)


class QTextEditLogger(logging.Handler):
    def __init__(self, emitter):
        super().__init__()
        self.emitter = emitter

    def emit(self, record):
        msg = self.format(record)
        self.emitter.log_signal.emit(msg)


def setup_logger(emitter):
    log_folder = config.get("log_folder")
    print(log_folder)
    #os.makedirs(log_folder, exist_ok=True)

    today =  datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(log_folder, f"{today}_{LOG_NAME}.log")

    logger = logging.getLogger("AppLogger")
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    )

    gui_handler = QTextEditLogger(emitter)
    gui_handler.setFormatter(formatter)
    gui_handler.setLevel(logging.INFO)

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    logger.addHandler(gui_handler)
    logger.addHandler(file_handler)

    return logger
