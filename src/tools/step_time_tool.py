import os
import datetime

import pandas as pd

from pathlib import Path

import config as config

from src.file_search import getFiles
from src.function_search import *

OUTPUT_FOLDER =  config.get_output_folder("Times")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def analyze_step_time(folder, start_date, end_date, all_files, logger):
    logger.info(f"Analyze Step Times started")

    logger.debug(f"Folder: {folder}")
    logger.debug(f"Date range: {start_date} - {end_date}")
    logger.debug(f"All files: {all_files}")

    files = getFiles(folder, start_date, end_date, all_files)

    if len(files) == 0:
        logger.warning(f"No .trc files found in {folder}")
    else:
        for file in files:
            logger.info(f"[{datetime.datetime.fromtimestamp(Path(file).stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}]\t{os.path.basename(file)}")
            output = _stepTimes(file, logger)
            if output == False:
                logger.warning(f"No Step Times found")

    logger.info("Analyze Step times finished")


def _extract_key(line):
    try:
        part = line[24:]
        key = part.split(" - ")[0].strip()

        return key
    except:
        return None


def _parse_timestamp(line):
    try:
        ts_str = line[:23]
        return datetime.datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S.%f")
    except ValueError:
        return None


def _write_results(results):
    timestamp = datetime.datetime.now().strftime('%Y%m%d')
    filenameOutput = os.path.join(OUTPUT_FOLDER, f'{timestamp}_StepTimes.csv')

    df = pd.DataFrame(results)
    write_header = not os.path.exists(filenameOutput)
    df.to_csv(filenameOutput, mode="a", index=False, header=write_header)

def _format_duration(time):
    total_seconds = int(time.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    return f"{hours:02}:{minutes:02}:{seconds:02}"


def _stepTimes(file, logger):

    mainFunctions = getMainFunctions()
    logicFunctions = getLogicFunctions()

    all_functions = mainFunctions + logicFunctions

    changes = False
    results = []

    active_timers = {}
    pause_start = None

    try:
        with open(file, 'r', encoding="utf-8", errors="replace") as trace:
            for line in trace:
                timestamp = _parse_timestamp(line)
                if timestamp == None:
                    continue

                if "Microlab" in line and "Pause" in line:
                    changes = True
                    if "start;" in line:
                        pause_start = timestamp
                    elif "complete;" in line and pause_start:
                        pause_duration = timestamp - pause_start
                        pause_start = None
                        for key in active_timers:
                            for timer in active_timers[key]:
                                timer["pause_total"] += pause_duration

                elif any(fn in line for fn in all_functions):
                    key = _extract_key(line)

                    if key.split(":")[-1].strip().startswith("_"):
                        continue
                    if not key:
                        continue

                    changes = True

                    if "start" in line:
                        if key not in active_timers:
                            active_timers[key] = []

                        active_timers[key].append({
                            "start":        timestamp,
                            "pause_total":  datetime.timedelta(0)
                        })

                    elif "complete" in line and active_timers.get(key):
                        timer = active_timers[key].pop(0)
                        raw_duration = timestamp - timer["start"]
                        net_duration = raw_duration - timer["pause_total"]
                        results.append({
                            "file":             os.path.basename(file),
                            "function":         key,
                            "start":            timer["start"],
                            "end":              timestamp,
                            "duration":         _format_duration(raw_duration),
                            "pause":            _format_duration(timer["pause_total"]),
                            "net_duration":     _format_duration(net_duration)
                        })

    except Exception as e:
        logger.error(f"Error reading file {file}: {e}")

    if results:
        _write_results(results)

    return changes

