""" Utility functions """

import logging
import json
import scipy
from scipy import misc
import os
import numpy as np

from .defines import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
formatter = logging.Formatter('%(funcName)s - %(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.propagate = False

def get_color(bitmap, x, y, map_width, map_height):
    """
    :returns closest (calculated by round) pixel from bitmap as extrapolated using map_width and map_height
    """
    x = np.round(bitmap.shape[0] / float(map_height) * x)
    y = np.round(bitmap.shape[1] / float(map_width) * y)
    c = bitmap[x, y]
    return bitmap[x,y][0:3]

def load_map(file_path):
    """
    Loads map and encodes it as a grid

    :returns grid, bitmap and metadata, where map and bitmap are arrays of ints
    """
    lines = [l.strip('\n') for l in open(file_path, "r")]
    params = json.loads("{"+lines.pop(0)+"}") # Hack, terrible hack

    try:
        bitmap = misc.imread(open(os.path.join(os.path.dirname(file_path), params['color_file'])))
    except IOError, e:
        print "Not found color file, exiting"
        raise e

    if "title" not in params:
        params["title"] = ""

    # Read map
    grid = [[0]*params["M"] for _ in xrange(params["N"])]

    for x in xrange(params["N"]):
        if not len(lines):
            raise KrakrobotException("Not found line. Probably something is wrong with file format (N?)")

        row = lines.pop(0)
        for y in xrange(params["M"]):
            grid[x][y] = MAP_CODING[row[y]]

    # Read special fields
    for k in xrange(params["K"]):
        if not len(lines):
            raise KrakrobotException("Not found line. Probably something is wrong with file format (K?)")

        line = lines.pop(0)
        type, x, y, value = line.split(" ")
        type = CONSTANT_MAP[type]
        if type == MAP_SPECIAL_DIRECTION:
            grid[int(x)][int(y)] = [MAP_SPECIAL_DIRECTION, CONSTANT_MAP[value]]
        elif type == MAP_SPECIAL_EUCLIDEAN_DISTANCE:
            grid[int(x)][int(y)] = [MAP_SPECIAL_EUCLIDEAN_DISTANCE, float(value)]
        elif type == MAP_SPECIAL_OPTIMAL:
            grid[int(x)][int(y)] = [MAP_SPECIAL_OPTIMAL, CONSTANT_MAP[value]]
        else:
            raise KrakrobotException("Not defined special map type")

    if len(lines):
        raise KrakrobotException("Not parsed last lines. Probably something is wrong with file format")

    return grid, bitmap, params
