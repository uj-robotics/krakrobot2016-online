""" Utility functions """

import logging
import json
import scipy
import os
import numpy as np
import copy

from misc.defines import *
from scipy.ndimage.io import imread

def get_color(map_, x, y):
    """
    :returns closest (calculated by round) pixel from bitmap as extrapolated using map_width and map_height
    """
    # x = float(x/map_['N']) * map_['color_bitmap'].shape[0]
    # y = float(y/map_['M']) * map_['color_bitmap'].shape[1]
    #
    #
    y = np.round(map_['color_bitmap'].shape[0] / float(map_['M']) * y)
    x = np.round(map_['color_bitmap'].shape[1] / float(map_['N']) * x)
    return map_['color_bitmap'][y, x][0:3]

def load_map(file_name, load_graphics=True):
    """
    Loads map and encodes it as a grid

    :returns map
    """
    map_ = json.loads(open(file_name, "r").read())

    color_names = ['red', 'green', 'blue']
    for color in color_names:
        if map_.has_key(color) and isinstance(map_[color], list) and len(map_[color]):
            # if the first element is also a list (list of fields notation)
            if isinstance(map_[color][0], list):
                map_[color] = map(tuple, map_[color])

            #if the first element is not a list (single field notation)
            else:
                map_[color] = [tuple(map_[color][0])]
        else:
            print "Warning: no coordinates provided or unsupported type for '{}' fields in the map file. Overwriting with empty list".format(color)
            map_[color] = []

    # convert beeps list to red, green and blue lists
    if map_.has_key('beeps'):
        beeps = map_['beeps']
        print "Warning: beeps is deprecated - use separate red, green and blue field lists in map file"
        assert len(beeps)==3, "The beeps list must have exactly 3 elements."
        for i, color in enumerate(color_names):
            map_[color].append(tuple(beeps[i]))

    fields = sum((map_[color] for color in color_names), [])
    # check for overlapping fields
    assert len(set(fields)) == len(fields), "There are some color fields with the same coordinates"


    if not os.path.isabs(map_['color_bitmap_file']):
        map_['color_bitmap_file'] = os.path.join(os.path.dirname(file_name), map_['color_bitmap_file'])

    try:
        if load_graphics:
            map_['color_bitmap'] = imread(map_['color_bitmap_file'])
    except IOError:
        print "Warning: Not found color file"

    if not os.path.isabs(map_['vector_graphics_file']):
        map_['vector_graphics_file'] = os.path.join(os.path.dirname(file_name), map_['vector_graphics_file'])

    if "title" not in map_:
        map_["title"] = ""

    if "board" not in map_:
        # Map is assumed to be always a simple box with 1-cell width wall around
        # and single start field.
        grid = [[1]*(map_["M"])]
        grid += [[1] + [0]*(map_["M"] - 2) + [1]]
        grid += [[1, 0] + [0]*(map_["M"] - 4) + [0, 1] for _ in xrange(map_["N"] - 4)]
        grid += [[1] + [0]*(map_["M"] - 2) + [1]]
        grid += [[1]*(map_["M"])]
        grid[map_['start_field'][0]][map_['start_field'][1]] = MAP_START_POSITION
        map_['file_name'] = file_name
        map_['board'] = grid
    else:
        raise RuntimeError("Not supported custom board parsing")

    return map_
