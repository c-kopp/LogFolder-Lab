import os
import sys
import glob

import src.config as config

def getLogicFunctions():
    logicFiles = glob.glob(f'{config.get("hamilton_folder")}/Library/**/*.smt', recursive=True)
    logicFunctions = [os.path.basename(x).split('.')[0].upper() for x in logicFiles if "LogicLayer" in x]

    return logicFunctions


def getMainFunctions():
    mainFiles = glob.glob(f'{config.get("hamilton_folder")}/Methods/**/*.med', recursive=True)
    mainFunctions = [os.path.basename(x).split('.')[0].upper() for x in mainFiles]

    return mainFunctions
