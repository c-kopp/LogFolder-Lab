diff --git a/ui/pages/settings_page.py b/ui/pages/settings_page.py
--- a/ui/pages/settings_page.py
+++ b/ui/pages/settings_page.py
@@ -12,7 +12,7 @@
 from PyQt6.QtWidgets import (
     QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
     QLineEdit, QCheckBox, QFileDialog,
-)


 class SettingsPage(QWidget):
+class SettingsPage(QWidget):

     settings_changed = pyqtSignal()

