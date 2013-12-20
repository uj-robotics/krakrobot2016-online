"""
Standalone command tool for generating maze

@note: This file is confidential and cannot be seen by contestants
"""

from defines import *
from optparse import OptionParser



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


class MapMaze:
    """
        Maze class copied and modified for our needs from
        http://thelinuxchronicles.blogspot.com.es/2012/07/python-maze-generation-and-solution.html
    """

    def __init__(self, rows, cols):
        """

            Generates maze using DFS-maze-gen algorithm,
            and then sets goal in a random place thats
            (rows+cols)/2 distance in euclidean space from starting position

        """

        if rows % 2 == 1 or cols % 2 == 1:
            raise KrakrobotException("Please pass even numbers")

        self.rows = rows/2  # division by 2 because every pair gets 0/1 between meaning wall or not
        self.cols = cols/2
        self.maze = []

        self.maze = [[[True, True, False] for j in range(self.cols)] for i in range(self.rows)]



        # Set enter position
        self.startrow = random.randrange(self.rows)
        self.startcol = random.randrange(self.cols)



        currrow = self.startrow
        currcol = self.startcol

        # The searh can be quite deep
        if self.rows * self.cols > sys.getrecursionlimit():
            sys.setrecursionlimit(self.rows * self.cols + 10)

        # generate the maze with depth-first algorithm
        self._gen_maze(currrow, currcol)


        # Add boundary (right boundaries are added automatically)
        rows_grid = rows + 1
        cols_grid = cols + 1

        self.grid = [[0]*(cols_grid) for i in xrange(rows_grid)]



        for i in xrange(rows_grid):
            for j in xrange(cols_grid):

                if i == 0 or i == rows_grid-1 or j == 0:
                    self.grid[i][j] = 1
                else:
                    x, y = i -1, j - 1
                    if x % 2 == 0:
                        if y % 2 == 0:
                            self.grid[i][j] = 0
                        else:
                            self.grid[i][j] = int(self.maze[x/2][y/2][RIGHTWALL])
                    else:
                        if y % 2 == 0:
                            self.grid[i][j] = int(self.maze[x/2][y/2][BOTTOMWALL])
                        else:
                            self.grid[i][j] = 1
        # Pick goal position

        start_x, start_y  = self.startrow*2 + 1, self.startcol*2 + 1

        goal_x, goal_y = start_x, start_y
        while self.grid[goal_x][goal_y] != 0 or \
                                        (goal_x-start_x)**2 + (goal_y-start_y)**2 < \
                                ((rows_grid + cols_grid)/4.0)**2:
            goal_x, goal_y = random.randrange(rows_grid), random.randrange(cols_grid)




        self.goal = [goal_x, goal_y]
        self.start = [start_x, start_y]
        self.grid[goal_x][goal_y] = MAP_GOAL
        self.grid[start_x][start_y] = MAP_START_POSITION

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
def generate_map(map_maze, file_name, title = "", K = 0):
    """
        Generate map and save to file_name based on
        generated maze
    """
    lines = []
    grid = map_maze.grid
    params = {"N": len(grid), "M":len(grid[0]), "title":title, "K":K}

    print json.dumps(params)[1:-1]
    lines.append(json.dumps(params)[1:-1])

    for r in xrange(params["N"]):
        lines.append("".join([REV_MAP_CODING[grid[r][c]] for c in xrange(params["M"])]))

    goal_position = map_maze.goal
    start_position = map_maze.start


    f = open(file_name, "w")
    f.write("\n".join(lines))


if __name__ == "__main__":
    mm = MapMaze(10,10)
    print mm
    generate_map(mm, "maps/3.map", "", 0)