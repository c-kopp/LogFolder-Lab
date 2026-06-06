import logging
import threading
import traceback

from PyQt6.QtCore import (
    QThread,
    pyqtSignal,
)


class ScriptWorker(QThread):
    finished      = pyqtSignal()
    file_progress = pyqtSignal(int, int)

    def __init__(self, func, args):
        super().__init__()
        self.func       = func
        self.args       = args
        self.stop_event = threading.Event()

    def stop(self):
        self.stop_event.set()

    def reset_stop(self):
        self.stop_event.clear()

    def run(self):
        try:
            self.func(*self.args)
        except Exception:
            error_msg = traceback.format_exc()
            logging.getLogger("AppLogger").critical(error_msg)

        finally:
            self.finished.emit()
