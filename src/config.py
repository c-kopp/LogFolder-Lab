import os
import platform

from PyQt6.QtCore import QSettings

APP_ORG  = "Hamilton Bonaduz AG"
APP_NAME = "ISD-LogFolder-Lab"
APP_VERSION = "0.0.1"

def _default_log_folder():
    if platform.system() == "Windows":
        return os.path.join(os.environ.get("APPDATA", "./logs"), APP_NAME, "logs")

    return "./logs"

def _default_input_folder():
    if platform.system() == "Windows":
        return r"C:/Programm Files (x86)/Hamilton/Logfiles"

    return "./data"

def _default_output_folder():
    if platform.system() == "Windows":
        return r"C:/Programm Files (x86)/Hamilton/Logfiles/ISD_logs"

    return "./results"

DEFAULTS = {
    "input_folder":  _default_input_folder(),
    "output_folder": _default_output_folder(),
    "log_folder": _default_log_folder(),
    "icon_folder": "icons",
    "image_folder": "images",
}

def get_settings():
    return QSettings(APP_ORG, APP_NAME)

def get(key):
    s = get_settings()
    return s.value(key, DEFAULTS.get(key, ""))

def set(key, value):
    s = get_settings()
    s.setValue(key, value)
    s.sync()

