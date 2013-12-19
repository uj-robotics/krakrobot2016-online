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


VERSION = '0.0.1a'
APP_NAME = 'Krakrobot Simulator'
APP_FULL_NAME = APP_NAME + ' ' + VERSION
MSG_EMP = '-> '

# TODO: add logger

from math import (
  pi, sqrt, hypot, sin, cos, tan, asin, acos, atan, atan2, radians, degrees,
  floor, ceil, exp
)
import numpy as np
import random
from utils import logger

from visualisation import RenderToSVG, Save
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
                 collision_threshold = 50
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
        #TODO: Move adequate actions from __init__() to reset()
        self.reset()
        self.limit_actions = limit_actions
        self.grid = grid
        self.N = len(self.grid)
        self.M = len(self.grid[0])
        for i in xrange(self.N):
            for j in xrange(self.M):
                if self.grid[i][j] == MAP_GOAL:
                    self.goal = (i,j)

    def create_visualisation_descriptor(self, robot):
        """
            @returns Descriptor that is sufficient to visualize current frame
        """
        data = {}
        data['GoalThreshold'] = self.goal_threshold
        data['Sparks'] = list(self.collisions)
        data['ActualPath'] = list(self.robot_path)
        data['ActualPosition'] = [robot.x, robot.y]
        data['ActualOrientation'] = robot.orientation
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
        self.finished = False

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
                self.frames.append(self.create_visualisation_descriptor(robot))

        except Exception, e:
            logger.error("Simulation failed with exception " +str(e)+ " after " +str(robot.num_steps)+ " steps")

        # Simulation process finished
        self.finished = True
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
import time
from threading import Thread, Lock
import datetime

from PyQt4 import QtGui, QtCore, QtSvg, QtOpenGL

class SimulationRenderThread(QtCore.QThread):

    def __init__(self, simulator, parent):
        super(SimulationRenderThread, self).__init__()
        self.simulator = simulator
        self.parent = parent


    def run_simulation(self):
        """Running KrakrobotSimulator simulation"""
        self.simulator.reset()
        self.simulator.run(OmitCollisions)
        self.exec_()


    def run(self):
        """SVG rendering"""
        self.simulation_process_thread = Thread(target=self.run_simulation)
        self.simulation_process_thread.start()

        i = 0
        rendered_frames = 0
        svg_data = None
        time_elapsed = datetime.timedelta(0)
        time_elapsed_update = datetime.timedelta(0)
        try:
            while True:
                while len(self.simulator.frames) <= rendered_frames:
                    if self.simulator.finished:
                        break
                    time.sleep(0.25)

                #time.sleep(0.01) #TODO: Parametrize

                self.sim_data = self.simulator.get_visualisation_descriptor(rendered_frames)
                fill_visualisation_descriptor(self.sim_data)

                print "Rendering SVG..."
                start = datetime.datetime.now()
                svg_data = RenderToSVG(self.sim_data)
                time_elapsed += datetime.datetime.now() - start

                start = datetime.datetime.now()

                print "update"
                if rendered_frames == 0:
                    self.parent.setup_scene(svg_data)
                else:
                    self.parent.update(svg_data)
                rendered_frames += 1

                time_elapsed_update += datetime.datetime.now() - start
                print "Rendered , time elapsed for RenderTOSVG", time_elapsed, " update ",time_elapsed_update


        except IndexError:
            print 'Done painting.'

        if svg_data:
            OutputFileName = 'output.svg'
            print 'Saving SVG to "' + OutputFileName + '"...'
            Save(svg_data.encode('utf_8'), OutputFileName)
            print 'Saved.'

        self.quit()


import copy
class SimulationGraphicsView(QtGui.QGraphicsView):
    """QGraphicsView viewing SVG rendered from QSvgRenderer with QXmlStreamReader"""

    def __init__(self, simulator, parent):
        super(SimulationGraphicsView, self).__init__(parent)
        self.parent = parent
        self.simulation_render_thread = SimulationRenderThread(simulator, self)
        self.simulation_render_thread.finished.connect(self._animation_finished)
        self._init_ui()


    def _init_ui(self):
        self._set_renderer('OpenGL')
        self.image = QtGui.QImage()
        self.svg_item = QtSvg.QGraphicsSvgItem()
        self.bg_item = QtGui.QGraphicsRectItem()
        self.outline_item = QtGui.QGraphicsRectItem()

        # Settings #
        self.setScene(QtGui.QGraphicsScene(self))
        self.setTransformationAnchor(self.AnchorUnderMouse)
        self.setDragMode(self.ScrollHandDrag)
        self.setCacheMode(self.CacheBackground)
        self.setViewportUpdateMode(self.BoundingRectViewportUpdate)


    def run_simulation(self):
        self.simulation_render_thread.start()


    def message(self, message):
        self.parent.status_bar_message(message)


    def setup_scene(self, svg_data):

        # Load new graphics
        self.xml_stream_reader = QtCore.QXmlStreamReader(svg_data)
        self.svg_renderer = QtSvg.QSvgRenderer(self.xml_stream_reader)
        self.svg_item = QtSvg.QGraphicsSvgItem()
        self.svg_item.setSharedRenderer(self.svg_renderer)
        self.svg_item.setFlags(QtGui.QGraphicsItem.ItemClipsToShape)
        self.svg_item.setCacheMode(QtGui.QGraphicsItem.DeviceCoordinateCache)
        self.svg_item.setZValue(0)

        scene = self.scene()
        scene.addItem(self.svg_item)

        scene.setSceneRect(self.svg_item.boundingRect().adjusted(-10, -10, 10, 10))
        print "setted up"


    def update(self, svg_data):

        # Load new graphics
        self.xml_stream_reader = QtCore.QXmlStreamReader(svg_data)
        self.svg_renderer = QtSvg.QSvgRenderer(self.xml_stream_reader)
        self.svg_item = QtSvg.QGraphicsSvgItem()
        self.svg_item.setSharedRenderer(self.svg_renderer)
        self.svg_item.setFlags(QtGui.QGraphicsItem.ItemClipsToShape)
        self.svg_item.setCacheMode(QtGui.QGraphicsItem.NoCache)
        self.svg_item.setZValue(0)

        scene = self.scene()
        print 'scene.items()[0].hide()'
        #scene.items()[0].hide()
        scene.addItem(self.svg_item)

        print 'items: ', len(scene.items())

        #scene.setSceneRect(self.svg_item.boundingRect().adjusted(-10, -10, 10, 10))
        #self.updateSceneRect(self.svg_item.boundingRect().adjusted(-10,-10,10,10))
        print "updated"


    def open_file(self, qfile):

        if not qfile.exists():
            return -1;

        scene = self.scene()

        # Clean graphics
        scene.clear()
        self.resetTransform()

        # Load new graphics
        self.svg_item = QtSvg.QGraphicsSvgItem(qfile.fileName())
        self.svg_item.setFlags(QtGui.QGraphicsItem.ItemClipsToShape)
        self.svg_item.setCacheMode(QtGui.QGraphicsItem.NoCache)
        self.svg_item.setZValue(0)

        scene.addItem(self.svg_item)

        scene.setSceneRect(self.svg_item.boundingRect().adjusted(-10, -10, 10, 10))
        print self.svg_item.maximumCacheSize()


    def paintEvent(self, event):

        if type(event != QtGui.QPaintEvent):
            pass

        if (self.renderer == 'Image'):
            if self.image.size() != self.viewport().size():
                self.image = QtGui.QImage(
                    self.viewport().size(),
                    QtGui.QImage.Format_ARGB32_Premultiplied
                )

            image_painter = QtGui.QPainter(self.image)
            QtGui.QGraphicsView.render(self, image_painter)
            image_painter.end()

            painter = QtGui.QPainter(self.viewport())
            painter.drawImage(0, 0, self.image)

        else:
            QtGui.QGraphicsView.paintEvent(self, event)


    def wheelEvent(self, event):
        factor = pow(1.2, event.delta()/240.0)
        self.scale(factor, factor)
        event.accept()


    def _animation_finished(self):
        self.message(MSG_EMP+'Animation has finished!')


    def _set_renderer(self, renderer):
        self.renderer = renderer

        if self.renderer == 'OpenGL' and not QT_NO_OPENGL:
            self.setViewport(
                QtOpenGL.QGLWidget(
                    QtOpenGL.QGLFormat(QtOpenGL.QGL.SampleBuffers)
                )
            )
        else:
            self.setViewport(QtGui.QWidget())


    def _set_high_quality_aa(self, value):
        if not QT_NO_OPENGL:
            self.setRenderHint(QtGui.QPainter.HighQualityAntialiasing, value)
        #else: # Handle?
        #QtCore.Q_UNUSED(value)



class MainWindow(QtGui.QMainWindow):
    """Main window (all-in-one window)"""

    def __init__(self, simulator):
        super(MainWindow, self).__init__()
        self._init_ui(simulator)


    def _init_ui(self, simulator):
        self.simulation_view = SimulationGraphicsView(simulator, self)

        file_menu = QtGui.QMenu('&File', self)
        self.open_action = file_menu.addAction('&Open SVG...')
        self.open_action.triggered.connect(self.open_svg)
        self.menuBar().addMenu(file_menu)

        renderer_menu = QtGui.QMenu('&Renderer', self)
        self.native_action = renderer_menu.addAction('&Native')
        self.native_action.setCheckable(True)
        self.native_action.setChecked(True)
        if not QT_NO_OPENGL:
            self.gl_action = renderer_menu.addAction('&OpenGL')
            self.gl_action.setCheckable(True)
            self.native_action.setChecked(False)
            self.gl_action.setChecked(True)
        self.image_action = renderer_menu.addAction('&Image')
        self.image_action.setCheckable(True)
        if not QT_NO_OPENGL:
            renderer_menu.addSeparator()
            self.hqaa_action = renderer_menu.addAction('&HQ Antialiasing')
            self.hqaa_action.setEnabled(True)
            self.hqaa_action.setCheckable(True)
            self.hqaa_action.setChecked(False)
            self.hqaa_action.toggled.connect(
                self.simulation_view._set_high_quality_aa
            )
        self.renderer_group = QtGui.QActionGroup(self)
        self.renderer_group.addAction(self.native_action)
        if not QT_NO_OPENGL:
            self.renderer_group.addAction(self.gl_action)
        self.renderer_group.addAction(self.image_action)
        self.renderer_group.triggered.connect(self._set_renderer)
        self.menuBar().addMenu(renderer_menu)

        main_toolbar = self.addToolBar('Krakrobot Simulator')
        start_sim_action = main_toolbar.addAction('Start Sim')
        start_sim_action.triggered.connect(self.run_simulation)

        self.setCentralWidget(self.simulation_view)
        self.setWindowTitle(APP_FULL_NAME)
        self.status_bar_message('Welcome to ' + APP_FULL_NAME + '!')


    def status_bar_message(self, message):
        self.statusBar().showMessage(message)


    def run_simulation(self):
        self.status_bar_message('Simulation process started...')
        self.simulation_view.run_simulation()


    def open_file(self):

        file_name = QtGui.QFileDialog.getOpenFileName(
            self, 'Open file', '.'
        )

        input_file = open(file_name, 'r')

        with input_file:
            data = input_file.read()


    def open_svg(self):

        file_name = QtGui.QFileDialog.getOpenFileName(
            self, 'Open file', '.'
        )

        self.simulation_view.open_file(QtCore.QFile(file_name))


    def _set_renderer(self, action):
        if not QT_NO_OPENGL:
            self.hqaa_action.setEnabled(False)

        if action == self.native_action:
            self.simulation_view._set_renderer('Native')
        elif (not QT_NO_OPENGL) and action == self.gl_action:
            self.hqaa_action.setEnabled(True)
            self.simulation_view._set_renderer('OpenGL')
        elif action == self.image_action:
            self.simulation_view._set_renderer('Image')


class SimulatorGUI(object):
    """GUI master class"""

    simulator = None
    application_thread = None
    qt_app = None

    def __init__(self, argv, simulator):
        """ Initialize GUI

        @param argv - program arguments values
        @param simulator - KrakrobotSimulator object

        """
        self.simulator = simulator
        self.qt_app = QtGui.QApplication(argv)


    def run(self):
        main_window = MainWindow(self.simulator)
        main_window.showMaximized()

        sys.exit(self.qt_app.exec_())


#NOTE: End of future extraction


import sys
def main():

    grid = [[1, 1, 1, 1, 1, 1],
            [1, 0, 0, 1, 1, 1],
            [1, 1, 0, 1, MAP_GOAL, 1],
            [1, 0, 0, 1, 0, 1],
            [1, 1, 1, 1, 1, 1]]
    simulator = KrakrobotSimulator(grid, (1, 1, 0))

    #simulator.run(OmitCollisions)

    gui = SimulatorGUI(sys.argv, simulator)
    gui.run()


if __name__ == '__main__':
    main()
