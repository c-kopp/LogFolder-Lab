import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import QSettings


# ──────────────────────────────────────────────────────────────────────────────
# Hamilton Brand Colors
# ──────────────────────────────────────────────────────────────────────────────

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
QSpinBox, QDoubleSpinBox {
    background: #0069aa;
    color: #ffffff;
    border: 1px solid #444;
    padding: 2px 4px;
    border-radius: 6px;
    selection-background-color: #00f091;
    selection-color: #000000;
}
QSpinBox::up-button, QDoubleSpinBox::up-button {
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 20px;
    height: 12px;
    background: #005a90;
    border-left: 1px solid #444;
    border-bottom: 1px solid #444;
    border-top-right-radius: 6px;
}
QSpinBox::down-button, QDoubleSpinBox::down-button {
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    width: 20px;
    height: 12px;
    background: #005a90;
    border-left: 1px solid #444;
    border-top: 1px solid #444;
    border-bottom-right-radius: 6px;
}
QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {
    background: #0080cc;
}
QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {
    width: 7px;
    height: 7px;
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-bottom: 5px solid #ffffff;
}
QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {
    width: 7px;
    height: 7px;
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #ffffff;
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
QTreeWidget {
    background: #0d1f3c;
    color: #ffffff;
    border: 1px solid #444;
    border-radius: 4px;
    alternate-background-color: #112244;
}
QTreeWidget::item {
    padding: 4px 2px;
    min-height: 26px;
    color: #ffffff;
}
QTreeWidget::item:selected {
    background: #00f091;
    color: #000000;
}
QTreeWidget::item:hover:!selected {
    background: rgba(0, 240, 145, 0.12);
}
QHeaderView::section {
    background: #1c2d57;
    color: #ffffff;
    padding: 4px 8px;
    border: none;
    border-bottom: 1px solid #444;
    font-weight: bold;
}
QComboBox {
    background: #0069aa;
    color: #ffffff;
    border: 1px solid #444;
    border-radius: 4px;
    padding: 2px 6px;
    min-height: 20px;
}
QComboBox::drop-down {
    border: none;
    width: 18px;
}
QComboBox QAbstractItemView {
    background: #0d1f3c;
    color: #ffffff;
    selection-background-color: #00f091;
    selection-color: #000000;
}

QRadioButton {
    color: #ffffff;
    spacing: 8px;
    font-size: 13px;
}
QRadioButton::indicator {
    width: 16px;
    height: 16px;
    border: 2px solid #4cc2ee;
    border-radius: 8px;
    background: #1c2d57;
}
QRadioButton::indicator:checked {
    background: #00f091;
    border-color: #00f091;
}
QRadioButton::indicator:hover {
    border-color: #00f091;
}

QTreeWidget {
    border: 1px solid #334466;
    border-radius: 6px;
    outline: none;
    font-size: 13px;
}
QTreeWidget::item {
    min-height: 28px;
    padding: 2px 4px;
}
QTreeWidget::item:hover {
    background: transparent;
}
QTreeWidget::indicator {
    width: 16px;
    height: 16px;
    border: 2px solid #4cc2ee;
    border-radius: 3px;
    background: transparent;
}
QTreeWidget::indicator:checked {
    background: #00f091;
    border-color: #00f091;
}
QTreeWidget::indicator:indeterminate {
    background: #4cc2ee;
    border-color: #4cc2ee;
}
QHeaderView::section {
    padding: 6px 8px;
    border: none;
    border-bottom: 2px solid #4cc2ee;
    font-weight: bold;
    font-size: 12px;
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
QSpinBox, QDoubleSpinBox {
    background: #ffffff;
    color: #1a2a4a;
    border: 1px solid #b0c4de;
    padding: 2px 4px;
    border-radius: 6px;
    selection-background-color: #00a066;
    selection-color: #ffffff;
}
QSpinBox::up-button, QDoubleSpinBox::up-button {
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 20px;
    height: 12px;
    background: #e8f0fb;
    border-left: 1px solid #b0c4de;
    border-bottom: 1px solid #b0c4de;
    border-top-right-radius: 6px;
}
QSpinBox::down-button, QDoubleSpinBox::down-button {
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    width: 20px;
    height: 12px;
    background: #e8f0fb;
    border-left: 1px solid #b0c4de;
    border-top: 1px solid #b0c4de;
    border-bottom-right-radius: 6px;
}
QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {
    background: #c0d0e8;
}
QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {
    width: 7px;
    height: 7px;
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-bottom: 5px solid #1a2a4a;
}
QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {
    width: 7px;
    height: 7px;
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #1a2a4a;
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
QTreeWidget {
    background: #ffffff;
    color: #1a2a4a;
    border: 1px solid #b0c4de;
    border-radius: 4px;
    alternate-background-color: #e4f6fc;
}
QTreeWidget::item {
    padding: 4px 2px;
    min-height: 26px;
    color: #1a2a4a;
}
QTreeWidget::item:selected {
    background: #00f091;
    color: #000000;
}
QTreeWidget::item:hover:!selected {
    background: rgba(0, 240, 145, 0.15);
}
QHeaderView::section {
    background: #c9edfa;
    color: #1c2d57;
    padding: 4px 8px;
    border: none;
    border-bottom: 1px solid #b0c4de;
    font-weight: bold;
}
QComboBox {
    background: #ffffff;
    color: #1a2a4a;
    border: 1px solid #b0c4de;
    border-radius: 4px;
    padding: 2px 6px;
    min-height: 20px;
}
QComboBox::drop-down {
    border: none;
    width: 18px;
}
QComboBox QAbstractItemView {
    background: #ffffff;
    color: #1a2a4a;
    selection-background-color: #00f091;
    selection-color: #000000;
}

QRadioButton {
    color: #000000;
    spacing: 8px;
    font-size: 13px;
}
QRadioButton::indicator {
    width: 16px;
    height: 16px;
    border: 2px solid #1c2d57;
    border-radius: 8px;
    background: #ffffff;
}
QRadioButton::indicator:checked {
    background: #00f091;
    border-color: #00f091;
}
QRadioButton::indicator:hover {
    border-color: #4cc2ee;
}

QTreeWidget {
    border: 1px solid #b0c4de;
    border-radius: 6px;
    outline: none;
    font-size: 13px;
}
QTreeWidget::item {
    min-height: 28px;
    padding: 2px 4px;
}
QTreeWidget::item:hover {
    background: transparent;
}
QTreeWidget::indicator {
    width: 16px;
    height: 16px;
    border: 2px solid #1c2d57;
    border-radius: 3px;
    background: transparent;
}
QTreeWidget::indicator:checked {
    background: #00f091;
    border-color: #00f091;
}
QTreeWidget::indicator:indeterminate {
    background: #4cc2ee;
    border-color: #4cc2ee;
}
QHeaderView::section {
    padding: 6px 8px;
    border: none;
    border-bottom: 2px solid #1c2d57;
    font-weight: bold;
    font-size: 12px;
}
"""


# ──────────────────────────────────────────────────────────────────────────────
# ThemeManager
# ──────────────────────────────────────────────────────────────────────────────

class ThemeManager:
    """
    Verwaltet Dark/Light-Mode für die gesamte App.

    Verwendung:
        tm = ThemeManager(app)
        tm.apply()        # beim Start (liest gespeicherte Präferenz)
        tm.toggle()       # manuell umschalten
        tm.is_dark        # True = Dark, False = Light
    """

    SETTINGS_KEY = "theme/dark_mode"

    def __init__(self, app: QApplication, window=None):
        self.app    = app
        self.window = window

        # Fusion-Style MUSS gesetzt sein, sonst überschreibt Windows den QSS
        self.app.setStyle("Fusion")

        self._dark: bool = self._load_preference()
        self.on_toggle_callback = None   # wird von MainWindow gesetzt

    # ── public ────────────────────────────────────────────────────────────────

    @property
    def is_dark(self) -> bool:
        return self._dark

    # Colors for custom-drawn widgets (e.g. FolderTreeWidget delegate)
    def color_text(self) -> str:
        return HamiltonWhite if self._dark else HamiltonBlack

    def color_line(self) -> str:
        return HamiltonTrustedBlue if self._dark else HamiltonDeepBlue

    def color_checked(self) -> str:
        return HamiltonEnablingGreen

    def color_bg(self) -> str:
        return HamiltonDeepBlue if self._dark else HamiltonTrustedBlue15

    def color_bg_alt(self) -> str:
        return "#112244" if self._dark else HamiltonBlack8

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
        if callable(self.on_toggle_callback):
            self.on_toggle_callback()

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
            palette.setColor(QPalette.ColorRole.Window,          QColor(HamiltonDeepBlue))
            palette.setColor(QPalette.ColorRole.WindowText,      QColor(HamiltonWhite))
            palette.setColor(QPalette.ColorRole.Base,            QColor("#0d1f3c"))
            palette.setColor(QPalette.ColorRole.AlternateBase,   QColor(HamiltonDeepBlue))
            palette.setColor(QPalette.ColorRole.Text,            QColor(HamiltonWhite))
            palette.setColor(QPalette.ColorRole.Button,          QColor(HamiltonDeepBlue))
            palette.setColor(QPalette.ColorRole.ButtonText,      QColor(HamiltonWhite))
            palette.setColor(QPalette.ColorRole.Highlight,       QColor(HamiltonEnablingGreen))
            palette.setColor(QPalette.ColorRole.HighlightedText, QColor(HamiltonBlack))
            palette.setColor(QPalette.ColorRole.ToolTipBase,     QColor("#0d1f3c"))
            palette.setColor(QPalette.ColorRole.ToolTipText,     QColor(HamiltonWhite))
            palette.setColor(QPalette.ColorRole.Link,            QColor(HamiltonTrustedBlue))
        else:
            palette.setColor(QPalette.ColorRole.Window,          QColor(HamiltonTrustedBlue15))
            palette.setColor(QPalette.ColorRole.WindowText,      QColor(HamiltonBlack))
            palette.setColor(QPalette.ColorRole.Base,            QColor(HamiltonWhite))
            palette.setColor(QPalette.ColorRole.AlternateBase,   QColor(HamiltonBlack8))
            palette.setColor(QPalette.ColorRole.Text,            QColor(HamiltonBlack))
            palette.setColor(QPalette.ColorRole.Button,          QColor(HamiltonTrustedBlue30))
            palette.setColor(QPalette.ColorRole.ButtonText,      QColor(HamiltonBlack))
            palette.setColor(QPalette.ColorRole.Highlight,       QColor(HamiltonEnablingGreen))
            palette.setColor(QPalette.ColorRole.HighlightedText, QColor(HamiltonBlack))
            palette.setColor(QPalette.ColorRole.ToolTipBase,     QColor(HamiltonWhite))
            palette.setColor(QPalette.ColorRole.ToolTipText,     QColor(HamiltonBlack))
            palette.setColor(QPalette.ColorRole.Link,            QColor(HamiltonTrustedBlue))

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
