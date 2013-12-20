""" Utility functions """

import logging
from defines import *
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
formatter = logging.Formatter('%(funcName)s - %(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.propagate = False

def load_map(file_path):
    """ Loads map and encodes it as a grid (TODO: change class to map) """
    lines = [l.strip('\n') for l in open(file_path, "r")]
    params = json.loads("{"+lines.pop(0)+"}")
    if "title" not in params: params["title"] = ""

    # TODO: load all defaults here



    # Read map
    grid = [[0]*params["M"] for i in xrange(params["N"])]

    found_goal = False

    for x in xrange(params["N"]):
        if not len(lines):
            raise KrakrobotException("Not found line. Probably something is wrong with file format (N?)")

        row = lines.pop(0)
        for y in xrange(params["M"]):
            grid[x][y] = MAP_CODING[row[y]]
            if MAP_CODING[row[y]] == MAP_GOAL: found_goal = True

    if not found_goal:
        raise KrakrobotException("Couldn't find goal cell")

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

    return grid, params
