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

#TODO: add Java/C++ RobotController classes with TCP server attached



from visualisation import PrepareFrame, RenderAnimatedPart, RenderFrameTemplate, \
    Save, fill_visualisation_descriptor
from defines import *

from simulator import KrakrobotSimulator
from robot_controller import OmitCollisions



#multithreading queue for rendering job
from Queue import Queue




#TODO: Extract this code to GUI module
import time
from threading import Thread
import datetime

from PyQt4 import QtGui, QtCore, QtSvg, QtOpenGL
from threading import Event


class SimulationRenderThread(QtCore.QThread):

    def __init__(self, simulator, parent):
        super(SimulationRenderThread, self).__init__()
        self.simulator = simulator
        self.parent = parent
        self.frames = [] # frame buffer
        self.renderer_stop = Event()
        self.frame_template = ""
        self.frame_count = 0


    def run_simulation(self):
        """Running KrakrobotSimulator simulation"""
        self.simulator.reset()
        self.simulator.run(OmitCollisions)
        self.exec_() #?


    def run_rendering(self):
        """ Job rendering frames to stack """
        while not self.renderer_stop.is_set():
            # note: will hang here
            sim_data = self.simulator.get_next_frame()
            fill_visualisation_descriptor(sim_data)

            if self.frame_template == "":
                print "Rendering frame template"
                self.frame_template = RenderFrameTemplate(sim_data)

            svg_data = PrepareFrame(self.frame_template, RenderAnimatedPart(sim_data))
            self.frames.append(svg_data)
            self.frame_count += 1
            time.sleep(0.1)

    def run_animation(self):
        """
        It manually triggers update. TODO: check if there is no better way of controlling update rate
        """
        while not self.renderer_stop.is_set():
            self.parent.update_mutex.lock()
            self.parent.scene().update()
            self.parent.update_mutex.unlock()
            time.sleep(0.001)

    def run(self):
        """SVG rendering"""
        self.simulation_process_thread = Thread(target=self.run_simulation)
        self.simulation_process_thread.start()

        self.simulation_rendering_thread = Thread(target=self.run_rendering)
        self.simulation_rendering_thread.start()

        time.sleep(0.5)

        self.animation_thread = Thread(target=self.run_animation)
        self.animation_thread.start()



        i = 0
        current_frame = 0
        svg_data = None
        time_elapsed = datetime.timedelta(0)
        time_elapsed_update = datetime.timedelta(0)


        while True:
            # Wait for current frame
            while current_frame+1 > self.frame_count:
                time.sleep(0.01)

            if current_frame == 0:
                self.parent.update_mutex.lock()
                self.parent.setup_scene(self.frames[current_frame])
                self.parent.update_mutex.unlock()
            else:
                self.parent.update_mutex.lock()
                #It is important that this code does not work at all, it only sets current frame!
                self.parent.update_data(self.frames[current_frame])
                self.parent.update_mutex.unlock()

            current_frame += 1
            time.sleep(self.simulator.frame_dt)


        #if svg_data:
        #    OutputFileName = 'output.svg'
        #    print 'Saving SVG to "' + OutputFileName + '"...'
        #    Save(svg_data.encode('utf_8'), OutputFileName)
        #    print 'Saved.'

        self.renderer_stop.set()
        self.quit()


import copy


class SimulationGraphicsView(QtGui.QGraphicsView):
    """QGraphicsView viewing SVG rendered from QSvgRenderer with QXmlStreamReader"""

    def __init__(self, simulator, parent):
        super(SimulationGraphicsView, self).__init__(parent)
        self.parent = parent
        self.simulation_render_thread = SimulationRenderThread(simulator, self)
        self.simulation_render_thread.finished.connect(self._animation_finished)
        self.update_mutex = QtCore.QMutex(QtCore.QMutex.Recursive)
        self.svg_data = None
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
        self.setViewportUpdateMode(self.NoViewportUpdate)


    def run_simulation(self):
        self.simulation_render_thread.start()


    def message(self, message):
        self.parent.status_bar_message(message)


    def setup_scene(self, svg_data):

        # Load new graphics
        self.xml_stream_reader = QtCore.QXmlStreamReader(svg_data)
        self.svg_renderer = QtSvg.QSvgRenderer(self.xml_stream_reader)
        self.svg_item = QtSvg.QGraphicsSvgItem(str(time.ctime()))
        self.svg_item.setSharedRenderer(self.svg_renderer)
        self.svg_item.setFlags(QtGui.QGraphicsItem.ItemClipsToShape)
        self.svg_item.setCacheMode(QtGui.QGraphicsItem.DeviceCoordinateCache)
        self.svg_item.setZValue(0)

        scene = self.scene()
        scene.addItem(self.svg_item)

        scene.setSceneRect(self.svg_item.boundingRect().adjusted(-10, -10, 10, 10))


    def update_data(self, svg_data):
        self.svg_data = svg_data


    #def update(self, svg_data):



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



        # Load new graphics
        if self.svg_data:
            self.xml_stream_reader = QtCore.QXmlStreamReader(self.svg_data)
            self.svg_renderer.load(self.xml_stream_reader)# = QtSvg.QSvgRenderer(self.xml_stream_reader)
            self.svg_item = QtSvg.QGraphicsSvgItem()




            scene = self.scene()
            #scene.removeItem(self.svg_item)
            self.svg_item.setSharedRenderer(self.svg_renderer)
            self.svg_item.setFlags(QtGui.QGraphicsItem.ItemClipsToShape)
            self.svg_item.setCacheMode(QtGui.QGraphicsItem.NoCache)
            self.svg_item.setZValue(0)
            scene.items()[0].hide()
            scene.addItem(self.svg_item)

            scene.setSceneRect(self.svg_item.boundingRect().adjusted(-10, -10, 10, 10))


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
    simulator = KrakrobotSimulator("maps/2.map", (1, 1, 0))

    #simulator.run(OmitCollisions)

    gui = SimulatorGUI(sys.argv, simulator)
    gui.run()


if __name__ == '__main__':
    main()
