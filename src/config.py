import os

from PyQt6.QtCore import QSettings

APP_ORG  = "Hamilton Bonaduz AG"
APP_NAME = "ISD-LogFolder-Lab"
APP_VERSION = "0.0.1"

DEFAULTS = {
    "input_folder":  r"C:/Program Files (x86)/Hamilton/Logfiles",
    "output_folder": "./results",
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

