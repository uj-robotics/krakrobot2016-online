""" Standalone command tool for generating maze """

from defines import *
from optparse import OptionParser
def create_parser():
    """ Configure options and return parser object """
    parser = OptionParser()
    #parser.add_option("-r", "--random_board", default=1, type="int", dest="rand_board",help="If set to 0  expects only board size (K), else (K) and row-wise map cells")
    #parser.add_option("-v", "--verbose",default=True, type="int", dest="verbose", help="If set prints simulation steps")
    #parser.add_option( "--agent_1", type="string",default="UCTAgent", dest="agent1", help="""Set agent1 to "UCTAgent","UCTAgentTran", "UCTAgentTranCut", "RandomAgent", "GreedyAgent" """)
    #parser.add_option( "--agent_2", type="string", default="GreedyAgent", dest="agent2", help="""Set agent2 to "UCTAgent", "UCTAgentTran", "UCTAgentTranCut",  "RandomAgent", "GreedyAgent" """)
    #parser.add_option("-t", "--time_per_move",default=3, type="int", dest="time_per_move", help="Set time per move, default is 2s")
    #parser.add_option("-n", "--number_of_simulations", default=10, type="int", dest="num_sim", help="Sets number of simulations, default is 10")
    return parser


import json
def load_map(file_path):
    """ Loads map and encodes it as a grid (TODO: change class to map) """
    lines = [l.strip('\n') for l in open(file_path, "r")]
    params = json.loads("{"+lines.pop(0)+"}")
    if "title" not in params: params["title"] = ""
    # Read map
    grid = [[0]*params["M"] for i in xrange(params["N"])]

    found_goal = False

    for x in xrange(params["N"]):
        if not len(lines):
            raise KrakrobotException("Not found line. Probably something is wrong with file format (N?)")

        row = lines.pop(0)
        for y in xrange(params["M"]):
            grid[x][y] = int(row[y])
            if int(row[y]) == MAP_GOAL: found_goal = True

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
        else:
            raise KrakrobotException("Not defined special map type")

    if len(lines):
        raise KrakrobotException("Not parsed last lines. Probably something is wrong with file format")

    return grid, params

if __name__ == "__main__":
    (options, args) = create_parser().parse_args()
    grid, metadata = load_map("maps/1.map")
    print grid

    pass


