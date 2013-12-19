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



#TODO: add colliding robot
#TODO: add robot exceeding speed
#TODO: add robot DFSing
