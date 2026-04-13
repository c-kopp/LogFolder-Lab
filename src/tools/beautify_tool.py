import os
import glob
import datetime

import pandas as pd

from pathlib import Path
from tabulate import tabulate

import config as config

from src.file_search import getFiles
from src.create_tables import *
from src.function_search import *

OUTPUT_FOLDER =  os.path.join(config.get("output_folder"), "BYT")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def create_byt(folder, start_date, end_date, all_files, logger):
    logger.info(f"Create BYT started")

    logger.debug(f"Folder: {folder}")
    logger.debug(f"Date range: {start_date} - {end_date}")
    logger.debug(f"All files: {all_files}")

    files = getFiles(folder, start_date, end_date, all_files)

    if len(files) == 0:
        logger.warning(f"No .trc files found in {folder}")
    else:
        for file in files:
            logger.info(f"[{datetime.datetime.fromtimestamp(Path(file).stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}]\t{os.path.basename(file)}")
            output = _beautifullTraces(file, logger)
            if output == False:
                logger.warning(f"No changes to original file -> removed")

    logger.info("BYT creation finished")


def _beautifullTraces(file, logger):
    filenameOutput = os.path.join(OUTPUT_FOLDER, f'BYT_{os.path.basename(file).replace(" ", "_")}')

    mainFunctions = getMainFunctions()
    logicFunctions = getLogicFunctions()

    changes = False

    # BEGIN and END to TraceFile (BYT)
    with open(file, 'r', encoding="utf-8", errors="replace") as trace:
        with open(filenameOutput, 'w') as output:
            for i, line in enumerate(trace, start=1):
                if line.split(":")[-1].strip().startswith("_"):
                    exportedLogicFunction = False
                else:
                    exportedLogicFunction = True

                if any(item in line for item in logicFunctions) and not "WaitFor" in line and exportedLogicFunction:
                    changes = True
                    if "start" in line:
                        print(f"{line.replace('start', 'BEGIN')}", file=output, end='')
                    else:
                        print(f"{line.replace('complete', 'END')}", file=output, end='')

                elif any(item in line for item in mainFunctions):
                    if "complete with error;" in line:
                        tmp = line.replace('complete with error', 'TMP END')
                        print(f"{tmp}", file=output, end='')
                        print(f"{line}", file=output, end='')
                else:
                    print(f"{line}", file=output, end='')

    mtime = os.path.getmtime(file)
    atime = os.path.getatime(filenameOutput)

    os.utime(filenameOutput, (atime, mtime))

    if changes == False:
        os.remove(filenameOutput)

    return changes
