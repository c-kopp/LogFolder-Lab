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
        except Exception:
            import traceback
            error_msg = traceback.format_exc()
            try:
                self.logger.critical(error_msg)
            except:
                pass
        finally:
            self.finished.emit()
