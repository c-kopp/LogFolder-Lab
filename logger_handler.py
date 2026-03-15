import os
import logging

from datetime import datetime
from PyQt6.QtCore import QObject, pyqtSignal

LOG_FOLDER = "logs"
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
    if not os.path.exists(LOG_FOLDER):
        os.makedirs(LOG_FOLDER)

    today =  datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(LOG_FOLDER, f"{today}_{LOG_NAME}.log")

    logger = logging.getLogger("AppLogger")
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    )

    gui_handler = QTextEditLogger(emitter)
    gui_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)

    logger.addHandler(gui_handler)
    logger.addHandler(file_handler)

    return logger
