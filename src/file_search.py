import os
import sys
import glob
import datetime

def getFiles(folder, start_date=None, end_date=None, all_files=False, filetype=".trc"):
    filetype = f"*{filetype}"

    files = glob.glob(f"{os.path.join(folder, filetype)}", recursive=True)

    if not all_files:
        files = [
            f for f in files
            if start_date <= datetime.datetime.fromtimestamp(os.path.getmtime(f)).date() <= end_date
        ]

    validFiles = []
    for file in files:
        if "ComTrace" in os.path.basename(file):
            continue
        elif "HxTcpIp" in os.path.basename(file):
            continue
        else:
            validFiles.append(file)

    validFiles.sort(key=os.path.getmtime, reverse=False)

    return validFiles

