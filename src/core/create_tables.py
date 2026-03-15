import string
import pandas as pd


def createAlphanumericPlate(rows, cols):
    rows = string.ascii_uppercase[:rows]

    return [
        [f"{row}{col}" for col in range(1, cols + 1)]
        for row in rows
    ]


def createNumericPlate(rows, cols, order='col'):
    if order == 'row':
        return [
            [str((r - 1) * cols + c) for c in range(1, cols + 1)]
            for r in range(1, rows + 1)
        ]

    elif order == 'col':
        return [
            [str((c - 1) * rows + r) for c in range(1, cols + 1)]
            for r in range(1, rows + 1)
        ]

    else:
        raise ValueError("order muss 'row' oder 'col' sein")


def buildTarget(matrix, target, replace, channel):
    """
       Ist maximal ausgelegt für 384 Well Platten
    """
    df = pd.DataFrame(matrix)

    shape = df.shape
    header = [str(i).center(8) for i in range(1, 25)]
    index = [char.center(3) for char in string.ascii_uppercase[:16]]

    if len(target) == len(replace):
        for i, position in enumerate(target):
            for x, row in enumerate(matrix):
                for y, item in enumerate(row):
                    if item == position:
                        if len(replace) == len(channel):
                            df.at[x,y] = f"{replace[i]} ({channel[i]})"
                        else:
                            df.at[x,y] = replace[i]

    df.columns = header[:shape[1]]
    df.index = index[:shape[0]]

    return df


def buildTip(matrix, target):
    df = pd.DataFrame(matrix)

    shape = df.shape
    header = [str(i).center(3) for i in range(1, 25)]
    index = [char for char in string.ascii_uppercase[:16]]

    for i, position in enumerate(target):
        for x, row in enumerate(matrix):
            for y, item in enumerate(row):
                if item == position:
                    df.at[x,y] = "X"

    df[df != "X"] = " "
    df.columns = header[:shape[1]]
    df.index = index[:shape[0]]

    return df


