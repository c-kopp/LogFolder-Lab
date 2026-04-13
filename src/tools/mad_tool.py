import os
import datetime

from pathlib import Path

from src.core.file_search import getFiles

def visualize_mad(folder, start_date, end_date, all_files, logger):
    logger.info("MAD visualization started")

    file_type = "MAD.mdb"

    logger.debug(f"Folder: {folder}")
    logger.debug(f"Date range: {start_date} - {end_date}")
    logger.debug(f"FileType: {file_type}")
    logger.debug(f"All files: {all_files}")

    files = getFiles(folder, start_date, end_date, all_files, file_type)

    if len(files) == 0:
        logger.warning(f"No {file_type} files found in {folder}")
    else:
        for file in files:
            logger.info(f"[{datetime.datetime.fromtimestamp(Path(file).stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}]\t{os.path.basename(file)}")

    logger.info("MAD visualization finished")
