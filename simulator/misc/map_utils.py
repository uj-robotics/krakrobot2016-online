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
    meta = json.loads(open(file_name, "r").read())

    try:
        bitmap = misc.imread(open(os.path.join(os.path.dirname(file_name), meta['bitmap'])))
    except IOError, e:
        print "Not found color file, exiting"
        raise e

    if "title" not in meta:
        meta["title"] = ""

    # Map is assumed to be always a simple box with 1-cell width wall around
    # and single start field.
    grid = [[1]*(meta["M"])]
    grid += [[1] + [0]*(meta["M"] - 2) + [1] for _ in xrange(meta["N"] - 2)]
    grid += [[1]*(meta["M"])]
    grid[meta['start_field'][0]][meta['start_field'][1]] = MAP_START_POSITION
    meta['file_name'] = file_name

    return grid, bitmap, meta
