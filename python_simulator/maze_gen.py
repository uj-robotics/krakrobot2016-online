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
    print params
    # Read map
    grid = [[0]*params["M"] for i in xrange(params["N"])]
    for x in xrange(params["N"]):
        row = lines.pop(0)
        print row
        for y in xrange(params["M"]):
            grid[x][y] = int(row[y])
    print grid
    # Read special fields
    for k in xrange(params["K"]):
        pass


if __name__ == "__main__":
    (options, args) = create_parser().parse_args()
    load_map("maps/1.map")


    pass


