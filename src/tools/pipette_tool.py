import os
import re
import glob
import datetime

import pandas as pd
import config as config

from pathlib import Path
from tabulate import tabulate

from src.file_search import getFiles
from src.create_tables import *
from src.function_search import *

OUTPUT_FOLDER = config.get_output_folder("PTS")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

PLATE_CONFIG = {
    "384": (16, 24),
    "96":  ( 8, 12),
    "32":  ( 4,  8),
    "24":  ( 4,  6),
    "12":  ( 3,  4),
    "6":   ( 2,  3)
}

TABULATE_DEFAULTS = dict(tablefmt='grid', stralign='center', numalign='center')

def create_pts(folder, start_date, end_date, all_files, transports, pipetting, logger):
    logger.info(f"Create PTS started")

    logger.debug(f"Folder: {folder}")
    logger.debug(f"Date range: {start_date} - {end_date}")
    logger.debug(f"All files: {all_files}")

    files = getFiles(folder, start_date, end_date, all_files)

    if len(files) == 0:
        logger.warning(f"No .trc files found in {folder}")
    else:
        for file in files:
            logger.info(f"[{datetime.datetime.fromtimestamp(Path(file).stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}]\t{os.path.basename(file)}")
            output = _pipettingSchemeBuilder(file, logger, transports, pipetting)
            if output == False:
                logger.warning(f"No Transport and/or Pipetting information in file -> removed")

    logger.info("PTS creation finished")


def _parseReturnValue(item):
    channel, rest = item.split(':', 1)
    parts = [x.strip() for x in rest.split(',')]

    channel = re.sub('channel', '', channel, flags=re.IGNORECASE).strip()
    plate = parts[0]
    position = parts[1] if len(parts) > 1 else ""
    volume = parts[2] if len(parts) > 2 else ""

    return channel, plate, position, volume


def _groupByPlate(parsed):
    plateGroups = {}
    for channel, plate, position, volume in parsed:
        if plate not in plateGroups:
            plateGroups[plate] = {"channels": [], "positions": [], "volumes": []}
        plateGroups[plate]["channels"].append(channel)
        plateGroups[plate]["positions"].append(position)
        plateGroups[plate]["volumes"].append(volume)

    return plateGroups


def _handle_channels(lineNumber, systemPart, returnValue, destination, logger, outfile):
    logger.debug(f"{lineNumber}: {systemPart} - {destination}")
    logger.debug(f"->\t{returnValue}")

    if destination in ["Source", "Target"]:
        if len(returnValue) > 0:
            plateGroups = _groupByPlate([_parseReturnValue(x) for x in returnValue])

            for plate, data in plateGroups.items():
                print(f"Line: {lineNumber} - {systemPart}: {plate}", file=outfile)
                logger.debug(f'data: {data}')

                trigger = next((p for p in sorted(PLATE_CONFIG, key=len, reverse=True) if p in plate), None)
                logger.debug(f'Trigger: {trigger}')
                if trigger:
                    rows, cols = PLATE_CONFIG[trigger]
                    isNoPlate = any(x in plate for x in ["Waste", "rgt_cont"])

                    if isNoPlate:
                        noPlateTable = formatChannels(data["channels"], data["volumes"])
                        print(tabulate(noPlateTable, **TABULATE_DEFAULTS), file=outfile)
                    else:
                        plateLayout = createNumericPlate(rows, cols) if data["positions"][0].isdigit() else createAlphanumericPlate(rows, cols)
                        dataFrame = buildTarget(plateLayout, data["positions"], data["volumes"], data["channels"])
                        print(tabulate(dataFrame, headers=dataFrame.columns, **TABULATE_DEFAULTS), file=outfile)
                else:
                    noPlateTable = formatChannels(data["channels"], data["volumes"])
                    print(tabulate(noPlateTable, **TABULATE_DEFAULTS), file=outfile)
        else:
            logger.debug(f"Return Value empty!")

    elif destination in ["Pickup", "Eject "]:
        if len(returnValue) > 0:
            plateGroups = _groupByPlate([_parseReturnValue(x) for x in returnValue])

            for plate, data in plateGroups.items():
                print(f"Line: {lineNumber} - {systemPart}: {plate}", file=outfile)
                logger.debug(f'data: {data}')

                if "Waste" not in plate:
                    plateLayout = createNumericPlate(8, 12) if data["positions"][0].isdigit() else createAlphanumericPlate(8, 12)
                    dataFrame = buildTip(plateLayout, data["positions"])
                    print(tabulate(dataFrame, headers=dataFrame.columns, **TABULATE_DEFAULTS), file=outfile)

        else:
            logger.debug(f"Return Value empty!")

    elif destination in [" <--- ", " ---> "]:
        labware = [re.sub(f'[^\w\s()]', '', x) for x in returnValue]
        if len(returnValue) == 0:
            print(f"Line: {lineNumber} - {systemPart}: {labware[0]}", file=outfile)
        elif len(returnValue) > 1:
            print(f"Line: {lineNumber} - {systemPart}: {'; '.join(labware)}", file=outfile)
        else:
            print(f"Line: {lineNumber} - {systemPart}", file=outfile)
    else:
        logger.debug("Unattended Operation!")

def _handle_head(lineNumber, systemPart, returnValue, destination, logger, outfile):
    logger.debug(f"{lineNumber}: {systemPart} - {destination}")
    logger.debug(f"->\t{returnValue}")

    if destination in ["Source", "Target"]:
        if len(returnValue) > 0:
            parsed = [_parseReturnValue(x) for x in returnValue]
            plate = parsed[0][1]
            volumes = [p[2] for p in parsed]

            logger.debug(f'Volumes: {volumes}')

            print(f"Line: {lineNumber} - {systemPart}: {plate} -> {volumes[0]}", file=outfile)
        else:
            logger.debug(f"Return Value empty!")

    elif destination in ["Pickup", "Eject "]:
        if len(returnValue) > 0:
            parsed = [_parseReturnValue(x) for x in returnValue]
            plate = parsed[0][1]

            print(f"Line: {lineNumber} - {systemPart}: {plate}", file=outfile)
        else:
            logger.debug(f"Return Value empty!")
    else:
        logger.debug("Unattended Operation!")


def _handle_iswap(lineNumber, systemPart, returnValue, destination, logger, outfile):
    logger.debug(f"{lineNumber}: {systemPart} - {destination}")
    logger.debug(f"->\t{returnValue}")

    if destination in [" <--- ", " ---> "]:
        labware = [re.sub(f'[^\w\s()]', '', x) for x in returnValue]

        if len(returnValue) == 1:
            print(f"Line: {lineNumber} - {systemPart}: {labware[0]}", file=outfile)
        elif len(returnValue) > 1:
            print(f"Line: {lineNumber} - {systemPart}: {'; '.join(labware)}", file=outfile)
        else:
            print(f"Line: {lineNumber} - {systemPart}", file=outfile)
    else:
        logger.debug("Unattended Operation!")


def _handle_hmotion(lineNumber, systemPart, returnValue, destination, logger, outfile):
    logger.debug(f"{lineNumber}: {systemPart} - {destination}")
    logger.debug(f"->\t{returnValue}")

    if destination in [" <--- ", " ---> "]:
        labware = [re.sub(f'[^\w\s()]', '', x) for x in returnValue]
        if len(returnValue) == 1:
            print(f"Line: {lineNumber} - H-Motion {systemPart}: {labware[0]}", file=outfile)
        elif len(returnValue) > 1:
            print(f"Line: {lineNumber} - H-Motion {systemPart}: {'; '.join(labware)}", file=outfile)
        else:
            print(f"Line: {lineNumber} - H-Motion {systemPart}", file=outfile)
    else:
        logger.debug("Unattended Operation!")


def _pipettingSchemeBuilder(file, logger, transports, pipetting):
    filenamePipetting = os.path.join(OUTPUT_FOLDER, f'PTS_{os.path.basename(file).replace(" ", "_")}')

    mainFunctions = getMainFunctions()
    logicFunctions = getLogicFunctions()

    with open(file, 'r', encoding="utf-8", errors="replace") as trace:
        with open(filenamePipetting, 'w', encoding="utf-8", errors="replace") as outfile:
            for i, line in enumerate(trace, start=1):
                lineNumber = f"{i:>7}"

                if any(item in line for item in logicFunctions) and not "WaitFor" in line and not line.split(":")[-1].strip().startswith("_"):
                    tmp = " ".join(line.split(" ")[2:])

                    if "start" in line:
                        print(f">> Line: {lineNumber} - {tmp.replace('start', 'BEGIN')}", file=outfile, end='')
                    else:
                        print(f"<< Line: {lineNumber} - {tmp.replace('complete', 'END')}", file=outfile, end='')

                if any(item in line for item in mainFunctions):
                    tmp = " ".join(line.split(" ")[2:])

                    if "complete with error;" in line:
                        print(f"<< Line: {lineNumber} - {tmp.replace('complete', 'TMP END')}", file=outfile, end='')


                if "Microlab" in line and "complete;" in line and not "error" in line:
                    information = line.split('- complete;')
                    systemPart = information[0].split(":")[-1].lstrip().rstrip()
                    returnValue = [x.strip() for x in information[1].strip().split('>') if x.strip()]

                    if "Channel" in systemPart:
                        if "Aspirate" in systemPart:        destination = "Source"
                        elif "Dispense" in systemPart:      destination = "Target"
                        elif "Tip Pick Up" in systemPart:   destination = "Pickup"
                        elif "Tip Eject" in systemPart:     destination = "Eject "
                        elif "Get Plate" in systemPart:     destination = " <--- "
                        elif "Place Plate" in systemPart:   destination = " ---> "
                        else:
                            logger.debug(f"Unattended Operation: {systemPart}")
                            continue

                        _handle_channels(lineNumber, systemPart, returnValue, destination, logger, outfile)
                        continue

                    elif "Head" in systemPart:
                        if "Aspirate" in systemPart:        destination = "Source"
                        elif "Dispense" in systemPart:      destination = "Target"
                        elif "Tip Pick Up" in systemPart:   destination = "Pickup"
                        elif "Tip Eject" in systemPart:     destination = "Eject "
                        else:
                            logger.debug(f"Unattended Operation: {systemPart}")
                            continue

                        _handle_head(lineNumber, systemPart, returnValue, destination, logger, outfile)
                        continue

                    elif "iSWAP" in systemPart:
                        if "Get Plate" in systemPart:       destination = " <--- "
                        elif "Place Plate" in systemPart:   destination = " ---> "
                        else:
                            logger.debug(f"Unattended Operation: {systemPart}")
                            continue

                        _handle_iswap(lineNumber, systemPart, returnValue, destination, logger, outfile)
                        continue

                elif "HAMILTONHMOTIONCONTROLLER" in line and "complete;" in line:
                    information = line.split('- complete;')
                    systemPart = information[0].split(":")[-1].lstrip().rstrip()
                    returnValue = [x.strip() for x in information[1].strip().split('>') if x.strip()]

                    if "GetPlate" in systemPart:            destination = " <--- "
                    elif "PlacePlate" in systemPart:        destination = " ---> "
                    else:
                        if not systemPart.startswith("_"):
                            logger.debug(f"Unattended Operation: {systemPart}")

                        continue

                    _handle_hmotion(lineNumber, systemPart, returnValue, destination, logger, outfile)
                    continue

    mtime = os.path.getmtime(file)
    atime = os.path.getatime(filenamePipetting)

    os.utime(filenamePipetting, (atime, mtime))

    if os.path.getsize(filenamePipetting) == 0:
        os.remove(filenamePipetting)
        return False
    else:
        return True

