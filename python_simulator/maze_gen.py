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


import random
import sys


# constants and help for list access
BOTTOMWALL = 0
RIGHTWALL = 1
VISITED = 2
UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3


# maze class definition
class Maze:
    #object constructor
    def __init__(self, rows, cols):

        # set maze size, walls and visited values
        self.rows = rows
        self.cols = cols
        self.maze = [[[True, True, False] for j in range(cols)] for i in range(rows)]

        # set current position, start and end point
        # start and end points are used to solve the maze
        # currrow is used to generate the maze
        self.startrow = random.randrange(rows)
        self.startcol = random.randrange(cols)

        self.endrow = random.randrange(rows)
        self.endcol = random.randrange(cols)

        currrow = self.startrow
        currcol = self.startcol

        # The searh can be quite deep
        if rows * cols > sys.getrecursionlimit():
            sys.setrecursionlimit(rows * cols + 10)

        # generate the maze with depth-first algorithm
        self._gen_maze(currrow, currcol)

        # number matrix for solving
        self.numtable = [[-1 for j in range(cols)] for i in range(rows)]

        #solution path
        self.solutionpath = []

    #-----------------------------------------------------------------------------

    # returns the maze in ascii characters for printing on terminal
    def __str__(self):

        # the upper wall first
        outtable = '.' + self.cols * '_.' + '\n'

        for i in range(self.rows):
            outtable += '|'

            for j in range(self.cols):
                if self.maze[i][j][BOTTOMWALL]:
                    outtable += '_'
                else:
                    outtable += ' '
                if self.maze[i][j][RIGHTWALL]:
                    outtable += '|'
                else:
                    outtable += '.'

            outtable += '\n'

        outtable += 'Start Point   : (' + str(self.startrow) + ',' + str(self.startcol) + ')\n'
        outtable += 'End Point     : (' + str(self.endrow) + ',' + str(self.endcol) + ')\n'

        return outtable

    #------------------------------------------------------------------------------

    # get a list with posible directions from the current position
    def _get_dirs(self, r, c):
        dirlist = []

        # check limits
        if r - 1 >= 0: dirlist.append(UP)
        if r + 1 <= self.rows - 1: dirlist.append(DOWN)
        if c - 1 >= 0: dirlist.append(LEFT)
        if c + 1 <= self.cols - 1: dirlist.append(RIGHT)

        return dirlist

    #------------------------------------------------------------------------------

    # generates the maze with depth-first algorithm
    def _gen_maze(self, r, c, d=None):
        maze = self.maze

        # knock down the wall between actual and previous position
        maze[r][c][VISITED] = True
        if d == UP:
            maze[r][c][BOTTOMWALL] = False
        elif d == DOWN:
            maze[r - 1][c][BOTTOMWALL] = False
        elif d == RIGHT:
            maze[r][c - 1][RIGHTWALL] = False
        elif d == LEFT:
            maze[r][c][RIGHTWALL] = False

        # get the next no visited directions to move
        dirs = self._get_dirs(r, c)

        # random reorder directions
        for i in range(len(dirs)):
            j = random.randrange(len(dirs))
            dirs[i], dirs[j] = dirs[j], dirs[i]

        # make recursive call if the target cell is not visited
        for d in dirs:
            if d == UP:
                if not maze[r - 1][c][VISITED]:
                    self._gen_maze(r - 1, c, UP)
            elif d == DOWN:
                if not maze[r + 1][c][VISITED]:
                    self._gen_maze(r + 1, c, DOWN)
            elif d == RIGHT:
                if not maze[r][c + 1][VISITED]:
                    self._gen_maze(r, c + 1, RIGHT)
            elif d == LEFT:
                if not maze[r][c - 1][VISITED]:
                    self._gen_maze(r, c - 1, LEFT)

    #------------------------------------------------------------------------------

    # solve the maze by filling it with numbers(algorithm name?)
    def _solve_maze_aux(self, r, c, n):
        maze = self.maze
        numtable = self.numtable
        numtable[r][c] = n

        # check if the end has been reached
        if (r, c) != (self.endrow, self.endcol):
            directions = self._get_dirs(r, c)

            # recursive calls only if there is no wall between cells and
            # targel cell is not marked (=-1)
            for d in directions:
                if d == UP and not maze[r - 1][c][BOTTOMWALL] and numtable[r - 1][c] == -1:
                    self._solve_maze_aux(r - 1, c, n + 1)
                elif d == DOWN and not maze[r][c][BOTTOMWALL] and numtable[r + 1][c] == -1:
                    self._solve_maze_aux(r + 1, c, n + 1)
                elif d == RIGHT and not maze[r][c][RIGHTWALL] and numtable[r][c + 1] == -1:
                    self._solve_maze_aux(r, c + 1, n + 1)
                elif d == LEFT and not maze[r][c - 1][RIGHTWALL] and numtable[r][c - 1] == -1:
                    self._solve_maze_aux(r, c - 1, n + 1)

    #------------------------------------------------------------------------------

    # get the solution path
    def _get_solution_path(self):
        actrow = self.endrow
        actcol = self.endcol
        startrow = self.startrow
        startcol = self.startcol
        path = []
        numtable = self.numtable
        path = self.solutionpath

        while (actrow, actcol) != (startrow, startcol):
            path.append((actrow, actcol))
            directions = self._get_dirs(actrow, actcol)
            for d in directions:
                if d == UP:
                    if numtable[actrow][actcol] - 1 == numtable[actrow - 1][actcol]:
                        actrow -= 1
                        break
                elif d == DOWN:
                    if numtable[actrow][actcol] - 1 == numtable[actrow + 1][actcol]:
                        actrow += 1
                        break
                elif d == LEFT:
                    if numtable[actrow][actcol] - 1 == numtable[actrow][actcol - 1]:
                        actcol -= 1
                        break
                elif d == RIGHT:
                    if numtable[actrow][actcol] - 1 == numtable[actrow][actcol + 1]:
                        actcol += 1
                        break

        path.append((actrow, actcol))
        path.reverse()

    #------------------------------------------------------------------------------

    # solve the maze
    def solve_maze(self):
        self._solve_maze_aux(self.startrow, self.startcol, 0)
        self._get_solution_path()