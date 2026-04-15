import os
import platform
import subprocess

def open_folder(path):
    if platform.system() == "Windows":
        os.startfile(path)
    else:
        subprocess.Popen(["open", path])
