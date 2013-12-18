#!/usr/bin/python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Visualising the Segmented-CTE maze-solving in CS373 Unit6-6
#
# Source : https://www.udacity.com/wiki/CS373%20Visualizing%20Maze%20Driving
#
# Custom modules:
#   vegesvgplot.py        http://pastebin.com/6Aek3Exm
#-------------------------------------------------------------------------------

# General idea: run simulation with fixed speed attribute. Accept solution only
# if number of collisions was zero, or no two consecutive collisions happened
#
#
# Links:
# http://forums.udacity.com/questions/1021963/particle-filter-challenge-implement-hallway-robot-with-sonar

# Problems : traversable walls
from sklearn.ensemble._gradient_boosting import np_bool

VERSION = "0.0.1a"

# TODO: add logger

from math import (
  pi, sqrt, hypot, sin, cos, tan, asin, acos, atan, atan2, radians, degrees,
  floor, ceil, exp
)
import numpy as np
import random
from visualisation import RenderToSVG, Save
from utils import logger
from defines import *
from robot_controller import *
from robot import Robot




class KrakrobotException(Exception):
    pass


#TODO: add Java/C++ RobotController classes with TCP server attached



class KrakrobotSimulator(object):
    COLLISION_THRESHOLD = 50

    def __init__(self,  grid, init_position, steering_noise=0.1, sonar_noise = 0.1, distance_noise=0.03,
                 measurement_noise=0.3, limit_actions = 100, speed = 0.4, execution_time_limit = 1.0,
                 collision_threshold = 50,
                 goal=None
                 ):
        """ 
            Initialize KrakrobotSimulator object 
            @param steering_noise - variance of steering in move 
            @param distance_noise - variance of distance in move
            @param measurement_noise - variance of measurement (GPS??) 
            @param grid - 0/1 matrix representing the maze
            @param init_position - starting position of the Robot (can be moved to map class) [x,y,heading]
            @param limit_actions - maximum number of actions contestant can make
            @param speed - distance travelled by one move action (cannot be bigger than 0.5, or he could traverse the walls)
            @param execution_time_limit - limit in ms for whole robot execution (also with init)
            @param collision_threshold - maximum number of collisions after which robot is destroyed
        """
        self.steering_noise    = steering_noise
        self.collision_threshold = collision_threshold
        self.sonar_noise = sonar_noise
        self.init_position = tuple(init_position)
        self.speed = speed
        self.execution_time_limit = execution_time_limit
        self.distance_noise    = distance_noise
        self.goal_threshold = 0.5 # When to declare goal reach
        self.measurement_noise = measurement_noise
        self.robot_path = []
        self.collisions = []
        self.limit_actions = limit_actions
        self.grid = grid
        self.goal_achieved = False
        self.frames = []
        self.robot_timer = 0.0
        self.N = len(self.grid)
        self.M = len(self.grid[0])
        if goal is None: self.goal = (self.N - 1, self.M - 1)
        else: self.goal = goal

    def create_visualisation_descriptor(self):
        """
            @returns Descriptor that is sufficient to visualize current frame
        """
        data = {}
        data['GoalThreshold'] = self.goal_threshold
        data['Sparks'] = list(self.collisions)
        data['ActualPath'] = list(self.robot_path)
        data['Map'] = self.grid
        data['StartPos'] = self.init_position
        data['GoalPos'] = self.goal
        data['GoalAchieved'] = self.goal_achieved
        return data


    def get_visualisation_descriptor(self, i):
        """
            @returns i-th frame descriptor
        """
        return self.frames[i]

    def check_goal(self, robot):
        """ Checks if goal is within threshold distance"""
        dist = sqrt((float(self.goal[0]) - robot.x) ** 2 + (float(self.goal[1]) - robot.y) ** 2)
        return dist < self.goal_threshold


    #TODO: test
    def reset(self):
        """ Reset state of the KrakrobotSimulator """
        self.robot_path = []
        self.collisions = []
        self.goal_achieved = False
        self.robot_timer = 0.0
        self.frames = []

    def run(self, robot_controller_class):
        """ Runs simulations by quering the robot """
        self.reset()

        # Initialize robot controller object given by contestant
        robot_controller = robot_controller_class()
        robot_controller.init(self.init_position, self.steering_noise, self.distance_noise, self.measurement_noise)

        # Initialize robot object
        robot = Robot()

        robot.set(self.init_position[0], self.init_position[1], self.init_position[2])
        robot.set_noise(self.steering_noise, self.distance_noise, self.measurement_noise, self.sonar_noise)
        self.robot_path.append((robot.x, robot.y))
        collision_counter = 0 # We have maximum collision allowed
        try:
            while not self.check_goal(robot) and not robot.num_steps >= self.limit_actions:
                # Get command
                command = None
                try:
                    command = list(robot_controller.act())
                except Exception, e:
                    logger.error("Robot controller failed with exception " + str(e))
                    break
                logger.info("Received command "+str(command))
                if not command or len(command) == 0:
                    raise KrakrobotException("No command passed, or zero length command passed")
ut
                # Dispatch command
                if command[0] == SENSE_GPS:
                    robot_controller.on_sense_gps(robot.sense_gps())
                elif command[0] == SENSE_SONAR:
                    w = robot.sense_sonar(self.grid)
                    logger.info("Sensed sonar : "+str(w))
                    robot_controller.on_sense_sonar(w)
                elif command[0] == SENSE_FIELD:
                    w = robot.sense_field(self.grid)
                    if w == MAP_WHITE or w == MAP_WALL: robot_controller.on_sense_field(w, 0)
                    else: robot_controller.on_sense_field(w[0], w[1])
                elif command[0] == MOVE:
                    if len(command) <= 1 or len(command) > 3:
                        raise KrakrobotException("Wrong command length")
                    if len(command) == 2:
                        command.append(self.speed)
                    if command[2] > self.speed:
                        raise KrakrobotException("Distance exceedes the maximum distance allowed")

                    # Move robot
                    robot_proposed = robot.move(command[1], command[2])


                    if not robot_proposed.check_collision(self.grid):
                        collision_counter += 1
                        self.collisions.append((robot_proposed.x, robot_proposed.y))
                        logger.error("##Collision##")
                        if collision_counter >= KrakrobotSimulator.COLLISION_THRESHOLD:
                            raise KrakrobotException\
                                    ("The robot has been destroyed by wall. Sorry! We miss WALLE already..")
                    else:
                        print robot_proposed.x, robot_proposed.y
                        robot = robot_proposed
                        self.robot_path.append((robot.x, robot.y))

                # Save simulation frame descriptor for visualisation
                self.frames.append(self.create_visualisation_descriptor())

        except Exception, e:
            logger.error("Simulation failed with exception " +str(e)+ " after " +str(robot.num_steps)+ " steps")
    
        logger.info("Simulation ended after "+str(robot.num_steps)+ " steps with goal reached = "+str(self.check_goal(robot)))
        self.goal_achieved = self.check_goal(robot)



#   grid = [[0, 1, 0, 0, 0, 0, 0, 0, 0 , 0 ,0 ,0],
#           [0, 1, 0, 1, 1, 0, 0, 0, 0 , 0 ,0, 0],
#           [0, 1, 0, 1, 0, 0, 0, 0 ,0,0,0,0],
#           [0, 0, 0, 1, 0, 1, 0 ,0, 0,0,0,0],
#           [0, 1, 0, 1, 0, 0,0,0,0,0,0,0]]



#TODO: move it from here
def fill_visualisation_descriptor(Data):
    Map = Data['Map']
    Data['Title'] = 'Krakrobot Eliminacje, przejazd..'
    Grid = {
    'CanvasMinima': (0.5, 1.5),
    'CanvasMaxima': (27.5, 18.5),
    'RangeMinima': (0, 0),
    'RangeMaxima': (len(Map), len(Map[0])),
    'YIsUp': False,
    'Transpose': True,
    'SquareAlignment': 'Centre',
    'DrawGrid': True,
    'DrawUnitAxes': False,
    'GridLineAttributes': {
      'stroke-width': '0.02', 'stroke': 'rgba(0, 192, 255, 0.5)'
    },
    'GeneralAttributes': {
      'stroke-width': '0.05', 'stroke': 'red'
    }
    }
    Paths = []
    Data['Grid'] = Grid
    Data['Paths'] = Paths
    Data['Map'] = Map


#TODO: Extract this code to GUI module
from PyQt4 import QtGui, QtCore, QtSvg

class SimulatorWindow(QtGui.QWidget):
    """Parent class for every window used in simulator"""

    def __init__(self):
        super(SimulatorWindow, self).__init__()
        self.init_clientwindow_ui()


    def init_clientwindow_ui(self):
        QtGui.QToolTip.setFont(QtGui.QFont('SansSerif', 10))



        ## Qt event triggered while exiting or closing the window
    def closeEvent(self, event):
        choice = QtGui.QMessageBox.question (
            self,
            "Quit Snkeaky Snake",
            "Do you want to quit?",
            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
            QtGui.QMessageBox.No
        )

        if choice == QtGui.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


class MainWindow(QtGui.QMainWindow):
    """Main window (currently everything-in-one)"""

    simulation_view = None

    def __init__(self, svg_bg):
        super(MainWindow, self).__init__()
        self.label = QtGui.QLabel(self)

        self._initUI()


    def initPainting(self):
        pass
        #self.graphics_view = QtGui.QGraphicsView(self.graphics_scene, self)


    def _initUI(self):
        self.simulation_view = SimulationView(self)
        self.setCentralWidget(self.simulation_view)
        #self._centerWindow()
        self.setWindowTitle("Krakrobot Simulator v" + str(VERSION) );


    def _centerWindow(self):
        frame = self.frameGeometry()
        foo = QtGui.QDesktopWidget().availableGeometry().center()
        frame.moveCenter(foo)
        self.move(frame.topLeft())


class SimulationView(QtGui.QGraphicsView):
    """Graphics view for simulation SVG"""

    graphics_scene = None
    svg_item = None
    bg_item = None
    outline_item = None

    def __init__(self, parent):
        super(SimulationView, self).__init__(parent)
        self.setScene(QtGui.QGraphicsScene(self))

    def openFile(self, qfile):

        if not qfile.exists():
            return -1;

        scene = self.scene()

        if self.bg_item:
            draw_bg = self.sbg_item.isVisible()
        else:
            draw_bg = False

        if self.outline_item:
            draw_outline = self.outline_item.isVisible()
        else:
            draw_outline = True

        # Clean graphics
        scene.clear()
        self.resetTransform()

        # Load new graphics
        self.svg_item = QtSvg.QGraphicsSvgItem(qfile.fileName())
        self.svg_item.setFlags(QtGui.QGraphicsItem.ItemClipsToShape);
        self.svg_item.setCacheMode(QtGui.QGraphicsItem.NoCache);
        self.svg_item.setZValue(0);

        self.bg_item = QtGui.QGraphicsRectItem(self.svg_item.boundingRect());
        self.bg_item.setBrush(QtCore.Qt.white);
        self.bg_item.setPen(QtGui.QPen(QtCore.Qt.NoPen));
        self.bg_item.setVisible(draw_bg);
        self.bg_item.setZValue(-1);

        self.outline_item = QtGui.QGraphicsRectItem(self.svg_item.boundingRect());
        outline = QtGui.QPen(QtCore.Qt.black, 2, QtCore.Qt.DashLine);
        outline.setCosmetic(True);
        self.outline_item.setPen(outline);
        self.outline_item.setBrush(QtGui.QBrush(QtCore.Qt.NoBrush));
        self.outline_item.setVisible(draw_outline);
        self.outline_item.setZValue(1);

        scene.addItem(self.bg_item);
        scene.addItem(self.svg_item);
        scene.addItem(self.outline_item);

        scene.setSceneRect(self.outline_item.boundingRect().adjusted(-10, -10, 10, 10));

        self.parent().resize(self.sizeHint() + QtCore.QSize(80, 80) )


def initGUI(argv, svg_descriptor):
    """ Initialize GUI
    @param argv - program arguments values
    """

    app = QtGui.QApplication(argv)

    main_window = MainWindow(svg_descriptor)
    main_window.initPainting()
    main_window.show()
    main_window.simulation_view.openFile(QtCore.QFile("output.svg"))

    sys.exit(app.exec_())


#NOTE: End of extraction


import sys
def main():

    OutputFileName = 'output.svg'

    print 'Driving a car through a maze...'
    grid = [[1, 1, 1, 1, 1, 1],
            [1, 0, 0, 1, 1, 1],
            [1, 1, 0, 1, 0, 1],
            [1, 0, 0, 1, 0, 1],
            [1, 1, 1, 1, 1, 1]]
    simulator = KrakrobotSimulator(grid, (1, 1, 0))
    simulator.run(OmitCollisions)

    Data = simulator.create_visualisation_descriptor()
    fill_visualisation_descriptor(Data)

    print 'Rendering SVG...'
    SVG = RenderToSVG(Data)
    print 'Done.'

    print 'Saving SVG to "' + OutputFileName + '"...'
    Save(SVG.encode('utf_8'), OutputFileName)
    print 'Done.'

    initGUI(sys.argv, Data)




if __name__ == '__main__':
    main()
