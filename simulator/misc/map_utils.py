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
    x = np.round(bitmap.shape[1] / float(map_width) * x)
    y = np.round(bitmap.shape[0] / float(map_height) * y)
    return bitmap[y,x][0:3]

def load_map(file_name):
    """
    Loads map and encodes it as a grid

    :returns grid, bitmap and metadata, where map and bitmap are arrays of ints
    """
    lines = [l.strip('\n') for l in open(file_name, "r")]
    meta = json.loads("{"+lines.pop(0)+"}") # Hack, terrible hack

    try:
        bitmap = misc.imread(open(os.path.join(os.path.dirname(file_name), meta['color_file'])))
    except IOError, e:
        print "Not found color file, exiting"
        raise e

    if "title" not in meta:
        meta["title"] = ""

    # Read map
    grid = [[0]*meta["M"] for _ in xrange(meta["N"])]

    for x in xrange(meta["N"]):
        if not len(lines):
            raise KrakrobotException("Not found line. Probably something is wrong with file format (N?)")

        row = lines.pop(0)
        for y in xrange(meta["M"]):
            grid[x][y] = MAP_CODING[row[y]]

    if len(lines):
        raise KrakrobotException("Not parsed last lines. Probably something is wrong with file format")

    meta['file_name'] = file_name

    return grid, bitmap, meta
