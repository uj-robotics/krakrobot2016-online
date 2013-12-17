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

VERSION = "0.0.1a"

# TODO: add logger

from math import (
  pi, sqrt, hypot, sin, cos, tan, asin, acos, atan, atan2, radians, degrees,
  floor, ceil, exp
)
import random
from visualisation import RenderToSVG, Save
from utils import logger
from defines import *
from robot_controller import *

class Robot:
    """ The main class representing robot that can sense and move """

    def __init__(self, length = 0.5):
        """
        Initialize robot    
        """

        self.x = 0.0
        self.y = 0.0
        self.orientation = 0.0
        self.length = length
        self.steering_noise    = 0.0
        self.distance_noise    = 0.0
        self.measurement_noise = 0.0
        self.num_collisions    = 0
        self.num_steps         = 0

    
    #TODO: extract  
    def set(self, new_x, new_y, new_orientation):
        """
        Set robot position
        @note: Cannot be called by contestant
        """

        self.x = float(new_x)
        self.y = float(new_y)
        self.orientation = float(new_orientation) % (2.0 * pi)


    #TODO: extract from this class
    def set_noise(self, new_s_noise, new_d_noise, new_m_noise):
        """
        Set noise parameter
        @note: Cannot be called by contestant
        """
        # makes it possible to change the noise parameters
        # this is often useful in particle filters
        self.steering_noise     = float(new_s_noise)
        self.distance_noise    = float(new_d_noise)
        self.measurement_noise = float(new_m_noise)

    #TODO: extract from this class
    def check_collision(self, grid):
        """
        Checks for collisions
        @note: Cannot be called by contestant
        @returns: True if no collisions
        """
        # Box based (sharp edges):
        for i in xrange(len(grid)):
            for j in xrange(len(grid[0])):
                # not sure about chained operators..
                if grid[i][j] == 1 \
                    and (float(i+1) - SQUARE_SIDE) > self.x > (float(i) - SQUARE_SIDE )\
                    and (float(j+1) - SQUARE_SIDE) > self.y > (float(j) - SQUARE_SIDE):

                    self.num_collisions += 1
                    return False

        return True


    #TODO: collision resolution? by distance thresholding? probably a good idea. So let threshold = a/2.0 (a - thickness of maze wall)
    def move(self,  steering, distance, tolerance = 0.001, max_steering_angle = pi / 4.0):
        """ 
        Move the robot using bicycle model from Udacity class.
        @param steering front wheel steering angle
        @param distance distance to be driven
        """


        if steering > max_steering_angle:
            steering = max_steering_angle
        if steering < -max_steering_angle:
            steering = -max_steering_angle
        if distance < 0.0:
            distance = 0.0


        # make a new copy
        res = Robot()
        # TODO: not add new variables
        res.length            = self.length
        res.steering_noise    = self.steering_noise
        res.distance_noise    = self.distance_noise
        res.measurement_noise = self.measurement_noise
        res.num_collisions    = self.num_collisions
        res.num_steps         = self.num_steps + 1

        # apply noise
        steering2 = random.gauss(steering, self.steering_noise)
        distance2 = random.gauss(distance, self.distance_noise) if distance > 0 else 0.0


        # Execute motion
        turn = tan(steering2) * distance2 / res.length

        if abs(turn) < tolerance:

            # approximate by straight line motion

            res.x = self.x + (distance2 * cos(self.orientation))
            res.y = self.y + (distance2 * sin(self.orientation))
            res.orientation = (self.orientation + turn) % (2.0 * pi)

        else:
            # approximate bicycle model for motion
            radius = distance2 / turn
            cx = self.x - (sin(self.orientation) * radius)
            cy = self.y + (cos(self.orientation) * radius)
            res.orientation = (self.orientation + turn) % (2.0 * pi)
            res.x = cx + (sin(res.orientation) * radius)
            res.y = cy - (cos(res.orientation) * radius)

        # check for collision
        # res.check_collision(grid)

        return res


    #TODO: add sonar here
    # http://pastebin.com/GwXCHtS3 ..
    # Or allow for 2 collisions ? discuss ?
    def sense_gps(self):
        """ Returns estimation for position (GPS signal) """
        self.num_steps += KrakrobotSimulator.SENSE_GPS

        return [random.gauss(self.x, self.measurement_noise),
                random.gauss(self.y, self.measurement_noise)]



    def measurement_prob(self, measurement):
        # compute errors
        error_x = measurement[0] - self.x
        error_y = measurement[1] - self.y

        # calculate Gaussian
        error = exp(- (error_x ** 2) / (self.measurement_noise ** 2) / 2.0) \
            / sqrt(2.0 * pi * (self.measurement_noise ** 2))
        error *= exp(- (error_y ** 2) / (self.measurement_noise ** 2) / 2.0) \
            / sqrt(2.0 * pi * (self.measurement_noise ** 2))

        return error



    def __repr__(self):
        # return '[x=%.5f y=%.5f orient=%.5f]'  % (self.x, self.y, self.orientation)
        return '[%.5f, %.5f]'  % (self.x, self.y)




class KrakrobotException(Exception):
    pass


#TODO: add Java/C++ RobotController classes with TCP server attached



class KrakrobotSimulator(object):
    COLLISION_THRESHOLD = 50

    def __init__(self,  grid, init_position, steering_noise=0.1, distance_noise=0.03,
                 measurement_noise=0.3, limit_actions = 100, speed = 0.4, goal=None
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
        """
        self.steering_noise    = steering_noise
        self.init_position = tuple(init_position)
        self.speed = speed
        self.distance_noise    = distance_noise
        self.goal_threshold = 0.5 # When to declare goal reach
        self.measurement_noise = measurement_noise
        self.robot_path = []
        self.collisions = []
        self.limit_actions = limit_actions
        self.grid = grid
        self.goal_achieved = False
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



    def run(self, robot_controller_class):
        """ Runs simulations by quering the robot """
        self.reset()

        # Initialize robot controller object given by contestant
        robot_controller = robot_controller_class()
        robot_controller.init(self.init_position, self.steering_noise, self.distance_noise, self.measurement_noise)

        # Initialize robot object
        robot = Robot()

#           if not myrobot.check_collision(grid):
#               Data['Sparks'].append((myrobot.x, myrobot.y))
#               print '##### Collision ####'
# 

        robot.set(self.init_position[0], self.init_position[1], self.init_position[2])
        robot.set_noise(self.steering_noise, self.distance_noise, self.measurement_noise)
        self.robot_path.append((robot.x, robot.y))
        collision_counter = 0 # We have maximum collision allowed
        try:
            while not self.check_goal(robot) and not robot.num_steps >= self.limit_actions:
                #print robot.x, robot.y, robot.orientation

                command = None
                try:
                    command = list(robot_controller.act())
                except Exception, e:
                    logger.error("Robot controller failed with exception " + str(e))
                    break

                if not command or len(command) == 0:
                    raise KrakrobotException("No command passed, or zero length command passed")

                if command[0] == SENSE_GPS:
                    robot_controller.on_sense(SENSE_GPS, robot.sense_gps())
                elif command[0] == SENSE_SONAR:
                    robot_controller.on_sense(SENSE_SONAR, 0.0)
                elif command[0] == MOVE:
                    # Parse move command
                    if len(command) <= 1 or len(command) > 3:
                        raise KrakrobotException("Wrong command length")
                    if len(command) == 2:
                        command.append(self.speed)
                    if command[2] > self.speed:
                        raise KrakrobotException("Distance exceedes the maximum distance allowed")

                    # Move robot
                    robot_proposed = robot.move(command[1], self.speed)


                    if not robot_proposed.check_collision(self.grid):
                        print "##Collision##"
                        collision_counter += 1
                        self.collisions.append((robot_proposed.x, robot_proposed.y))
                        if collision_counter >= KrakrobotSimulator.COLLISION_THRESHOLD:
                            raise KrakrobotException\
                                    ("The robot has been destroyed by wall. Sorry! We miss WALLE already..")
                    else:
                        print robot_proposed.x, robot_proposed.y
                        robot = robot_proposed
                        self.robot_path.append((robot.x, robot.y))

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
from threading import Thread

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


def startGUI(argv, simulator):
    """ Initialize GUI
    @param argv - program arguments values
    """
    #NOTE: This part should be placed in non-graphic application aswell
    simulator_thread = Thread(target=simulator.run, args=(OmitCollisions,))
    simulator_thread.start()

    sim_data = simulator.create_visualisation_descriptor()
    fill_visualisation_descriptor(sim_data)

    print 'Rendering SVG...'
    SVG = RenderToSVG(sim_data)
    print 'Done.'

    OutputFileName = 'output.svg'
    print 'Saving SVG to "' + OutputFileName + '"...'
    Save(SVG.encode('utf_8'), OutputFileName)
    print 'Done.'
    #NOTE: end


    app = QtGui.QApplication(argv)

    main_window = MainWindow(sim_data)
    main_window.initPainting()
    main_window.show()
    main_window.simulation_view.openFile(QtCore.QFile("output.svg"))

    sys.exit(app.exec_())


#NOTE: End of future extraction


import sys
def main():

    print 'Driving a car through a maze...'
    grid = [[1, 1, 1, 1, 1, 1],
            [1, 0, 0, 1, 1, 1],
            [1, 1, 0, 1, 0, 1],
            [1, 0, 0, 1, 0, 1],
            [1, 1, 1, 1, 1, 1]]
    simulator = KrakrobotSimulator(grid, (1, 1, 0))

    #simulator.run(OmitCollisions)


    startGUI(sys.argv, simulator)




if __name__ == '__main__':
    main()
