from main import *


def test1():
    """ Should collide """
    grid = [[0, 1, 0, 0, 0, 0],
            [0, 1, 0, 1, 1, 0],
            [0, 1, 0, 1, 0, 0],
            [0, 0, 0, 1, 0, 1],
            [0, 1, 0, 1, 0, 0]]
    simulator = KrakrobotSimulator(grid, (0, 0, 0))
    forward_controller = ForwardTurningRobotController
    simulator.run(forward_controller)
