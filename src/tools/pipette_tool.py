import os
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


def _pipettingSchemeBuilder(file, logger, transports, pipetting):
    filenamePipetting = os.path.join(OUTPUT_FOLDER, f'PTS_{os.path.basename(file).replace(" ", "_")}')

    mainFunctions = getMainFunctions()
    logicFunctions = getLogicFunctions()

    positionList = []
    with open(file, 'r', encoding="utf-8", errors="replace") as trace:
        with open(filenamePipetting, 'w', encoding="utf-8", errors="replace") as pipetting:
            for i, line in enumerate(trace, start=1):

                # Convert start and complete to BEGIN and END in LogicLayer Functions
                if any(item in line for item in logicFunctions) and not "WaitFor" in line and not line.split(":")[-1].strip().startswith("_"):
                    tmp = " ".join(line.split(" ")[2:])

                    if "start" in line:
                        print(f">> Line: {i} - {tmp.replace('start', 'BEGIN')}", file=pipetting, end='')
                    else:
                        print(f"<< Line: {i} - {tmp.replace('complete', 'END')}", file=pipetting, end='')

                #TODO: Check if it gets better
                if any(item in line for item in mainFunctions):
                    tmp = " ".join(line.split(" ")[2:])

                    if "complete with error;" in line:
                        print(f"<< Line: {i} - {tmp.replace('complete', 'TMP END')}", file=pipetting, end='')

                if "Microlab" in line and "complete" in line and not "error" in line:
                    if "Head" in line:
                        if "Aspirate" in line:
                            destination = "HEAD Source"
                        elif "Dispense" in line:
                            destination = "HEAD Target"
                        elif "Tip Pick Up" in line:
                            destination = "HEAD Pickup"
                        elif "Tip Eject" in line:
                            destination = "HEAD Eject"
                        else:
                            destination = line.split('- complete;')[0].split(':')[-1]
                            logger.debug(f"Unattended HEAD operation: {destination}")
                            continue

                        returnValue = line.split('complete;')[1].strip().split('>')
                        returnValue = list(x.strip() for x in returnValue)
                        returnValue = list(x for x in returnValue if len(x.strip()) > 0)

                        logger.debug(returnValue)

                        plate = ""
                        volumes = []

                        for entry, item in enumerate(returnValue):
                            channel = item.split(':')[0]
                            rest = list(x.strip() for x in item.split(':')[1].split(','))

                            if len(rest) == 3:
                                if rest[2].startswith('0'):
                                    destination = "LiquidLevel"

                            if destination in ['HEAD Pickup', 'HEAD Eject']:
                                if destination == "Eject":
                                    print(f"\t Line: {i} - {destination}: {rest[0]}\n", file=pipetting)
                                else:
                                    print(f"\n\t Line: {i} - {destination}: {rest[0]}", file=pipetting)

                                break
                            else:
                                if entry == 0:
                                    if destination == "HEAD Source":
                                        print(f"\n\t Line: {i} - {destination}: {rest[0]} - Volume: {rest[1]}", file=pipetting)
                                    else:
                                        print(f"\t Line: {i} - {destination}: {rest[0]} - Volume: {rest[1]}", file=pipetting)

                        continue

                    elif "Channel" in line:
                        if not "Move To Position" in line:
                            if "Aspirate" in line:
                                destination = "CHANNELS Source"
                            elif "Dispense" in line:
                                destination = "CHANNELS Target"
                            elif "Tip Pick Up" in line:
                                destination = "CHANNELS Pickup"
                            elif "Tip Eject" in line:
                                destination = "CHANNELS Eject"
                            elif "Get Plate" in line:
                                destination = "CHANNELS Transport From"
                            elif "Place Plate" in line:
                                destination = "CHANNELS Transport To"
                            else:
                                destination = line.split('- complete;')[0].split(':')[-1]
                                logger.debug(f"Unattended CHANNELS operation: {destination}")
                                continue


                            returnValue = line.split('complete;')[1].strip().split('>')
                            returnValue = list(x.strip() for x in returnValue)
                            returnValue = list(x for x in returnValue if len(x.strip()) > 0)

                            logger.debug(returnValue)

                            plate = ""

                            positions = []
                            positions2 = []
                            volumes = []

                            volumes2 = []
                            channels = []
                            channels2 = []

                            for entry, item in enumerate(returnValue):
                                channel = item.split(':')[0].split(' ')
                                rest = list(x.strip() for x in item.split(':')[1].split(','))

                                if len(channel) > 1:
                                    rest.append(channel[1])

                                if len(rest) == 4:
                                    if rest[2].startswith('0'):
                                        if destination == "CHANNELS Source":
                                            destination = "Liquid Level Check"
                                        else:
                                            destination = "Drain Tip"

                                if destination in ['CHANNELS Pickup', 'CHANNELS Eject']:
                                    usedChannels = [x.split(':')[0] for x in returnValue]
                                    usedPositions = [x.split(':')[1] for x in returnValue]

                                    tmp = list(set([x.split(',')[0].strip() for x in usedPositions]))

                                    if destination == "CHANNELS Eject":
                                        print(f"\tLine: {i} - {destination} {usedChannels} -> {tmp}", file=pipetting)
                                    else:
                                        print(f"\n\tLine: {i} - {destination} {usedChannels} -> {tmp}", file=pipetting)

                                    if not "Waste" in tmp[0]:
                                        usedPositions = [x.split(',')[1].strip() for x in usedPositions]

                                        dataFrame = buildTip(createNumericPlate(8, 12), usedPositions)

                                        print(tabulate(dataFrame, tablefmt='grid', headers=dataFrame.columns, stralign="center", numalign="center"), file=pipetting)
                                        print(f"\n", file=pipetting)
                                    break

                                elif destination in ['CHANNELS Transport From', 'CHANNELS Transport To']:
                                    print(f"Line: {i} - On Deck {destination}: \t{channel}", file=pipetting)

                                else:
                                    if entry == 0:
                                        plate = rest[0]
                                        rest = rest[1:]

                                        if destination == "CHANNELS Source":
                                            print(f"\n\n\tLine: {i} - {destination}: {plate}", file=pipetting)
                                        else:
                                            print(f"\tLine: {i} - {destination}: {plate}", file=pipetting)

                                        tmp = f"\tLine: {i} - {destination}: "

                                    else:
                                        if plate == rest[0]:
                                            rest = rest[1:]

                                    positions.append(rest[0])
                                    volumes.append(rest[1])
                                    if len(rest) >= 3:
                                        channels.append(rest[2])

                                if len(rest) == 4:
                                    plate2 = rest[0]
                                    rest2 = rest[1:]

                                    positions2.append(rest2[0])
                                    volumes2.append(rest2[1])
                                    if len(rest2) >= 3:
                                        channels.append(rest2[2])

                            plate_config = {
                                "384": (16, 24),
                                "96": (8, 12),
                                "32": (4, 8),
                                "24": (4, 6),
                                "12": (3, 4),
                                "6": (2, 3)
                            }

                            trigger = next((p for p in plate_config if p in plate), None)

                            if trigger:
                                if "Waste" not in plate and "rgt_cont" not in plate:
                                    rows, cols = plate_config[trigger]

                                    logger.debug(f"{plate} with ({rows}, {cols})")
                                    if len(positions2) > 0:
                                        logger.debug(f"{plate2} with ({rows}, {cols})")

                                    if positions[0].isdigit():
                                        dataFrame = buildTarget(createNumericPlate(rows, cols), positions, volumes, channels)
                                    else:
                                        dataFrame = buildTarget(createAlphanumericPlate(rows, cols), positions, volumes, channels)

                                    print(tabulate(dataFrame, tablefmt='grid', headers=dataFrame.columns, stralign="center", numalign="center"), file=pipetting)

                                    if len(positions2) > 0:
                                        print(f"{tmp}{plate2}", file=pipetting)
                                        if positions2[0].isdigit():
                                            dataFrame = buildTarget(createNumericPlate(rows, cols), positions2, volumes2, channels2)
                                        else:
                                            dataFrame = buildTarget(createAlphanumericPlate(rows, cols), positions2, volumes2, channels2)

                                        print(tabulate(dataFrame, tablefmt='grid', headers=dataFrame.columns, stralign="center", numalign="center"), file=pipetting)
                                else:
                                    dataFrame = formatChannels(channels + channels2, volumes + volumes2)
                                    print(tabulate(dataFrame, tablefmt='grid', stralign="center", numalign="center"), file=pipetting)


                        continue

                    elif "iSWAP" in line:

                        if "Get Plate" in line:
                            destination = "ISWAP Transport From"
                        elif "Place Plate" in line:
                            destination = "ISWAP Transport To"
                        else:
                            destination = line.split('- complete;')[0].split(':')[-1]
                            logger.debug(f"Unattended ISWAP operation: {destination}")
                            continue

                        print(f"Line: {i} - {destination}", file=pipetting)

                        continue

                elif "HAMILTONHMOTIONCONTROLLER : GetPlate - complete;" in line or "HAMILTONHMOTIONCONTROLLER : PlacePlate - complete;" in line:
                    labware = line.split("> ")[-1]

                    if len(positionList) > 0:
                        if len(positionList) == 2:
                            tmp = f"\t{positionList[0]} @ {positionList[1]}"
                        else:
                            tmp = f"\t{positionList[0]}: {positionList[2]} -> {positionList[1]}"

                        print(tmp, file=pipetting)

                    positionList = []

                    if "GetPlate" in line:
                        if len(labware) > 0:
                            print(f"Line: {i} - HMotion Get Plate: {labware}", file=pipetting)
                        else:
                            print(f"Line: {i} - HMotion Get Plate", file=pipetting)
                    else:
                        if len(labware) > 0:
                            print(f"Line: {i} - HMotion Place Plate: {labware}", file=pipetting)
                        else:
                            print(f"Line: {i} - HMotion Place Plate", file=pipetting)

                    continue

    mtime = os.path.getmtime(file)
    atime = os.path.getatime(filenamePipetting)

    os.utime(filenamePipetting, (atime, mtime))

    if os.path.getsize(filenamePipetting) == 0:
        os.remove(filenamePipetting)
        return False
    else:
        return True

