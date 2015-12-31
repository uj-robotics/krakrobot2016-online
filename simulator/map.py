""" Utility functions """

import logging
import json
import scipy
import os
import numpy as np
import copy

from misc.defines import *
from scipy.ndimage.io import imread

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
formatter = logging.Formatter('%(funcName)s - %(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.propagate = False

def get_color(map, x, y):
    """
    :returns closest (calculated by round) pixel from bitmap as extrapolated using map_width and map_height
    """
    # x = float(x/map['N']) * map['color_bitmap'].shape[0]
    # y = float(y/map['M']) * map['color_bitmap'].shape[1]
    #
    #
    y = np.round(map['color_bitmap'].shape[1] / float(map['M']) * y)
    x = np.round(map['color_bitmap'].shape[0] / float(map['N']) * x)
    return map['color_bitmap'][x, y][0:3]

def load_map(file_name):
    """
    Loads map and encodes it as a grid

    :returns map
    """
    map = json.loads(open(file_name, "r").read())

    try:
        map['color_bitmap'] = imread(os.path.join(os.path.dirname(file_name)))
    except IOError, e:
        print "Not found color file, exiting"
        raise e

    if "title" not in map:
        map["title"] = ""

    if "board" not in map:
        # Map is assumed to be always a simple box with 1-cell width wall around
        # and single start field.
        grid = [[1]*(map["M"])]
        grid += [[1] + [0]*(map["M"] - 2) + [1]]
        grid += [[1, 0] + [0]*(map["M"] - 4) + [0, 1] for _ in xrange(map["N"] - 4)]
        grid += [[1] + [0]*(map["M"] - 2) + [1]]
        grid += [[1]*(map["M"])]
        grid[map['start_field'][0]][map['start_field'][1]] = MAP_START_POSITION
        map['file_name'] = file_name
        map['board'] = grid

        map['color_board'] = copy.deepcopy(map['board'])
        for i in range(map['N']):
            for j in range(map['M']):
                map['color_board'][i][j] = [int(v) for v in get_color(map, i + 0.5, j + 0.5)]

    else:
        raise RuntimeError("Not supported custom board parsing")

    return map
