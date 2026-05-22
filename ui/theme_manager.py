import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import QSettings

# Standard Hamilton Colors:

HamiltonDeepBlue        = '#1c2d57'
HamiltonBlack           = '#000000'
HamiltonWhite           = '#ffffff'

HamiltonBlack8          = '#eff0f0'

HamiltonTrustedBlue     = '#4cc2ee'
HamiltonTrustedBlue30   = '#c9edfa'
HamiltonTrustedBlue15   = '#e4f6fc'

HamiltonEnablingGreen   = '#00f091'
HamiltonEnablingGreen30 = '#b2fade'
HamiltonEnablingGreen15 = '#d9fdef'


# ──────────────────────────────────────────────────────────────────────────────
# QSS Themes
# ──────────────────────────────────────────────────────────────────────────────

DARK_QSS = """
QMainWindow, QWidget {
    background: #1c2d57;
}
QLabel {
    color: #ffffff;
    font-size: 14px;
    font-weight: bold;
}
#title {
    font-size: 26px;
    font-weight: bold;
    color: #ffffff;
}
#HomeLogo {
    border: 4px solid #00f091;
    border-radius: 55px;
    max-width: 600px;
    margin: auto;
}
#sidebarTitle {
    font-size: 20px;
    font-weight: bold;
    padding: 10px;
    color: #ffffff;
}
#systemInfo {
    font-size: 11px;
    color: #bbbbbb;
    padding: 4px;
}
QPushButton {
    background: #00f091;
    color: #000000;
    border: none;
    padding: 8px;
    border-radius: 6px;
    font-weight: bold;
}
QPushButton:hover {
    background: #4cc2ee;
}
QPushButton[active="true"] {
    background: #4cc2ee;
    border-left: 4px solid #00f091;
}
QLineEdit, QDateEdit, QComboBox {
    background: #0069aa;
    color: white;
    border: 1px solid #444;
    padding: 6px 8px;
    border-radius: 6px;
}
QTextEdit {
    background: #0d1f3c;
    color: #00ff9c;
    font-family: Consolas, Ubuntu Mono, monospace;
    border-top: 1px solid #333;
}
QPushButton#btnSecondary {
    background-color: #556;
    color: #ffffff;
}
QPushButton#btnSecondary:hover {
    background-color: #778;
}
QPushButton#btnThemeToggle {
    background-color: #334;
    color: #ffffff;
    font-size: 16px;
    border-radius: 6px;
}
QPushButton#btnThemeToggle:hover {
    background-color: #556;
}
QLabel#help {
    color: white;
    background-color: #555;
    border-radius: 8px;
    padding: 0px 5px;
    font-size: 11px;
    font-weight: bold;
    border: none;
}
QLabel#help:hover {
    background-color: #333;
}
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    min-height: 24px;
    padding: 2px 4px;
}
QGroupBox::title {
    font-size: 24px;
    font-weight: bold;
    border: 1px dashed #555;
    border-radius: 4px;
    padding: 2px 6px;
    color: #ffffff;
}
QScrollBar:vertical {
    background: #1c2d57;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #4cc2ee;
    border-radius: 4px;
}
QCheckBox {
    color: #ffffff;
    spacing: 6px;
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 2px solid #4cc2ee;
    border-radius: 3px;
    background: #1c2d57;
}
QCheckBox::indicator:checked {
    background: #00f091;
    border-color: #00f091;
}
"""

LIGHT_QSS = """
QMainWindow, QWidget {
    background: #e4f6fc;
}
QLabel {
    color: #000000;
    font-size: 14px;
    font-weight: bold;
}
#title {
    font-size: 26px;
    font-weight: bold;
    color: #000000;
}
#HomeLogo {
    border: 4px solid #00f091;
    border-radius: 55px;
    max-width: 600px;
    margin: auto;
}
#sidebarTitle {
    font-size: 20px;
    font-weight: bold;
    padding: 10px;
    color: #000000;
}
#systemInfo {
    font-size: 11px;
    color: #666;
    padding: 4px;
}
QPushButton {
    background: #00f091;
    color: #000000;
    border: none;
    padding: 8px;
    border-radius: 6px;
    font-weight: bold;
}
QPushButton:hover {
    background: #4cc2ee;
    color: #000000;
}
QPushButton[active="true"] {
    background: #4cc2ee;
    border-left: 4px solid #00f091;
}
QLineEdit, QDateEdit, QComboBox {
    background: #ffffff;
    color: #1a2a4a;
    border: 1px solid #b0c4de;
    padding: 6px 8px;
    border-radius: 6px;
}
QTextEdit {
    background: #ffffff;
    color: #000000;
    font-family: Consolas, Ubuntu Mono, monospace;
    border-top: 1px solid #ccc;
}
QPushButton#btnSecondary {
    background-color: #ccd6e8;
    color: #1a2a4a;
}
QPushButton#btnSecondary:hover {
    background-color: #aabbcc;
}
QPushButton#btnThemeToggle {
    background-color: #dde8f5;
    color: #1a2a4a;
    font-size: 16px;
    border-radius: 6px;
}
QPushButton#btnThemeToggle:hover {
    background-color: #c0d0e8;
}
QLabel#help {
    color: #1a2a4a;
    background-color: #dde8f5;
    border-radius: 8px;
    padding: 0px 5px;
    font-size: 11px;
    font-weight: bold;
    border: none;
}
QLabel#help:hover {
    background-color: #aabbcc;
}
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    min-height: 24px;
    padding: 2px 4px;
}
QGroupBox::title {
    font-size: 24px;
    font-weight: bold;
    border: 1px dashed #aaa;
    border-radius: 4px;
    padding: 2px 6px;
    color: #1a2a4a;
}
QScrollBar:vertical {
    background: #e0eaf5;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #90aac8;
    border-radius: 4px;
}
QCheckBox {
    color: #1a2a4a;
    spacing: 6px;
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 2px solid #90aac8;
    border-radius: 3px;
    background: #ffffff;
}
QCheckBox::indicator:checked {
    background: #00f091;
    border-color: #00f091;
}
"""


# ──────────────────────────────────────────────────────────────────────────────
# ThemeManager
# ──────────────────────────────────────────────────────────────────────────────

class ThemeManager:
    """
    Verwaltet Dark/Light-Mode für die gesamte App.

    Verwendung:
        tm = ThemeManager(app, window)
        tm.apply()                  # beim Start (liest gespeicherte Präferenz)
        tm.toggle()                 # manuell umschalten
        current = tm.is_dark        # True = Dark, False = Light
    """

    SETTINGS_KEY = "theme/dark_mode"

    def __init__(self, app: QApplication, window=None):
        self.app    = app
        self.window = window

        # Fusion-Style MUSS gesetzt sein, sonst überschreibt Windows den QSS
        self.app.setStyle("Fusion")

        self._dark: bool = self._load_preference()

    # ── public ────────────────────────────────────────────────────────────────

    @property
    def is_dark(self) -> bool:
        return self._dark

    def apply(self):
        """Wendet das aktuelle Theme auf die App an."""
        qss = DARK_QSS if self._dark else LIGHT_QSS
        self.app.setStyleSheet(qss)
        self._apply_palette()
        self._save_preference()

    def toggle(self):
        """Schaltet zwischen Dark und Light um."""
        self._dark = not self._dark
        self.apply()

    def set_dark(self, dark: bool):
        """Setzt das Theme direkt."""
        self._dark = dark
        self.apply()

    # ── private ───────────────────────────────────────────────────────────────

    def _apply_palette(self):
        """
        Setzt die QPalette passend zum Theme.
        Notwendig für Widgets die QSS nicht vollständig respektieren
        (z.B. QMessageBox, QFileDialog, native Dialoge).
        """
        palette = QPalette()
        if self._dark:
            palette.setColor(QPalette.ColorRole.Window,          QColor("#1c2d57"))
            palette.setColor(QPalette.ColorRole.WindowText,      QColor("#ffffff"))
            palette.setColor(QPalette.ColorRole.Base,            QColor("#0d1f3c"))
            palette.setColor(QPalette.ColorRole.AlternateBase,   QColor("#1c2d57"))
            palette.setColor(QPalette.ColorRole.Text,            QColor("#ffffff"))
            palette.setColor(QPalette.ColorRole.Button,          QColor("#1c2d57"))
            palette.setColor(QPalette.ColorRole.ButtonText,      QColor("#ffffff"))
            palette.setColor(QPalette.ColorRole.Highlight,       QColor("#00f091"))
            palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#000000"))
            palette.setColor(QPalette.ColorRole.ToolTipBase,     QColor("#0d1f3c"))
            palette.setColor(QPalette.ColorRole.ToolTipText,     QColor("#ffffff"))
            palette.setColor(QPalette.ColorRole.Link,            QColor("#4cc2ee"))
        else:
            palette.setColor(QPalette.ColorRole.Window,          QColor("#f0f4fc"))
            palette.setColor(QPalette.ColorRole.WindowText,      QColor("#1a2a4a"))
            palette.setColor(QPalette.ColorRole.Base,            QColor("#ffffff"))
            palette.setColor(QPalette.ColorRole.AlternateBase,   QColor("#e8f0fb"))
            palette.setColor(QPalette.ColorRole.Text,            QColor("#1a2a4a"))
            palette.setColor(QPalette.ColorRole.Button,          QColor("#dde8f5"))
            palette.setColor(QPalette.ColorRole.ButtonText,      QColor("#1a2a4a"))
            palette.setColor(QPalette.ColorRole.Highlight,       QColor("#00a066"))
            palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
            palette.setColor(QPalette.ColorRole.ToolTipBase,     QColor("#ffffff"))
            palette.setColor(QPalette.ColorRole.ToolTipText,     QColor("#1a2a4a"))
            palette.setColor(QPalette.ColorRole.Link,            QColor("#0080cc"))

        self.app.setPalette(palette)

    def _detect_system_dark(self) -> bool:
        """Erkennt ob Windows/macOS im Dark Mode ist."""
        try:
            if sys.platform == "win32":
                import winreg
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
                )
                value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                winreg.CloseKey(key)
                return value == 0  # 0 = Dark Mode
            elif sys.platform == "darwin":
                import subprocess
                result = subprocess.run(
                    ["defaults", "read", "-g", "AppleInterfaceStyle"],
                    capture_output=True, text=True
                )
                return result.stdout.strip() == "Dark"
        except Exception:
            pass
        return True  # Fallback: Dark

    def _load_preference(self) -> bool:
        """Liest gespeicherte Präferenz; fällt auf System-Theme zurück."""
        settings = QSettings("ISD", "LogFolderLab")
        stored = settings.value(self.SETTINGS_KEY, None)
        if stored is None:
            return self._detect_system_dark()
        return stored == "true" or stored is True

    def _save_preference(self):
        settings = QSettings("ISD", "LogFolderLab")
        settings.setValue(self.SETTINGS_KEY, "true" if self._dark else "false")
