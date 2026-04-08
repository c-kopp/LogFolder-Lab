from PyQt6.QtCore import QThread, pyqtSignal


class ScriptWorker(QThread):
    finished = pyqtSignal()

    def __init__(self, func, args):
        super().__init__()
        self.func = func
        self.args = args

    def run(self):
        try:
            self.func(*self.args)
        finally:
            self.finished.emit()
