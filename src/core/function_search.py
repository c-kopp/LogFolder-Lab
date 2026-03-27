import os
import sys
import glob

def getLogicFunctions():
    logicFiles = glob.glob('C:/Program Files (x86)/Hamilton/Library/**/*.smt', recursive=True)
    logicFunctions = [os.path.basename(x).split('.')[0].upper() for x in logicFiles if "LogicLayer" in x]

    return logicFunctions


def getMainFunctions():
    mainFiles = glob.glob('C:/Program Files (x86)/Hamilton/Methods/**/*.med', recursive=True)
    mainFunctions = [os.path.basename(x).split('.')[0].upper() for x in mainFiles]

    return mainFunctions
