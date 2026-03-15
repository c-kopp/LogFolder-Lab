import os
import datetime

from pathlib import Path

from src.core.file_search import getFiles


OUTPUT_FOLDER = "results/searched"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def search_logs(folder, start_date, end_date, all_files, file_type, terms, mode, regex, logger):

    logger.info("Search started")

    logger.debug(f"Folder: {folder}")
    logger.debug(f"Date range: {start_date} - {end_date}")
    logger.debug(f"All Files: {all_files}")
    logger.debug(f"Terms: {terms}")
    logger.debug(f"Mode: {mode}")
    logger.debug(f"Filetype: {file_type}")
    logger.debug(f"Regex: {regex}")

    files = getFiles(folder, start_date, end_date, all_files, file_type)

    if len(files) == 0:
        logger.warning(f"No {file_type} files found in {folder}")
    else:
        for file in files:
            logger.info(f"[{datetime.datetime.fromtimestamp(Path(file).stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}]\t{os.path.basename(file)}")

            continue

            with open(filenameSearch, 'a') as searchfile:
                print(f"{os.path.basename(file)}\n", file=searchfile, end='')
                with open(file, 'r') as trace:
                    for i, line in enumerate(trace, start=1):
                        if "RENEWCELLMAINTENANCESCREENING : " in line:
                            print(f"\tLine {i}>\t{line}", file=searchfile, end='')

    logger.info("Search finished")
