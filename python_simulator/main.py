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



#multithreading queue for rendering job
from Queue import Queue




#TODO: Extract this code to GUI module
import time
from threading import Thread
import datetime

from PyQt4 import QtGui, QtCore, QtSvg, QtOpenGL
from threading import Event
from robot_controller import compile_robot

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
        self.simulator.run()
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

            svg_data = RenderAnimatedPart(sim_data)
            self.frames.append(svg_data)
            self.frame_count += 1

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
                self.parent.setup_scene(PrepareFrame(self.frame_template,self.frames[current_frame]))
                self.parent.update_mutex.unlock()
            else:
                self.parent.update_mutex.lock()
                #It is important that this code does not work at all, it only sets current frame!
                self.parent.update_data(PrepareFrame(self.frame_template, self.frames[current_frame]))
                self.parent.update_mutex.unlock()

            current_frame += 1
            time.sleep(self.simulator.frame_dt/10.0) #10x time


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

            QtGui.QGraphicsView.paintEvent(self, event)


    def wheelEvent(self, event):
        factor = pow(1.2, event.delta()/240.0)
        self.scale(factor, factor)
        event.accept()


    def _animation_finished(self):
        self.message(MSG_EMP+'Animation has finished!')


class MainWindow(QtGui.QMainWindow):
    """Main window (all-in-one window)"""

    def __init__(self, simulator):
        super(MainWindow, self).__init__()
        self._init_ui(simulator)
        self.update_slider = True
        self.animation_paused = False
        self.currently_simulating = False


    def _init_ui(self, simulator):
        main_toolbar = self.addToolBar('Krakrobot Simulator')
        self.setWindowTitle(APP_FULL_NAME)
        self.status_bar_message('Welcome to ' + APP_FULL_NAME + '!')

        main_toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.start_sim_action = main_toolbar.addAction(
            QtGui.QIcon.fromTheme('system-run'),
            'Start Simulation'
        )
        self.start_sim_action.triggered.connect(self._run_simulation)

        simulation_layout = QtGui.QVBoxLayout()
        self.simulation_view = SimulationGraphicsView(simulator, self)
        simulation_layout.addWidget(self.simulation_view)

        playback_layout = QtGui.QHBoxLayout()
        playback_layout.addStrut(1)
        playback_toolbar = QtGui.QToolBar()
        self.speed_box = QtGui.QDoubleSpinBox(self)
        self.speed_box.setRange(2,100)
        self.speed_box.setValue(10)
        self.speed_box.setToolTip('Change animation speed')
        self.speed_box.valueChanged.connect(self._speed_value_changed)
        playback_toolbar.addWidget(self.speed_box)
        play_progress_action = playback_toolbar.addAction(
            QtGui.QIcon.fromTheme('media-playback-start'),
            'Play progress animation'
        )
        play_progress_action.triggered.connect(self._play_progress_animation)
        pause_progress_action = playback_toolbar.addAction(
            QtGui.QIcon.fromTheme('media-playback-pause'),
            'Pause progress animation'
        )
        pause_progress_action.triggered.connect(self._pause_progress_animation)
        skip_backward_action = playback_toolbar.addAction(
            QtGui.QIcon.fromTheme('media-skip-backward'),
            'Skip to the beginning'
        )
        skip_backward_action.triggered.connect(self._skip_backward)
        skip_forward_action = playback_toolbar.addAction(
            QtGui.QIcon.fromTheme('media-skip-forward'),
            'Skip to the end'
        )
        skip_forward_action.triggered.connect(self._skip_forward)
        playback_toolbar.setMaximumWidth(playback_toolbar.sizeHint().width())
        playback_layout.addWidget(playback_toolbar)

        self.scroll_bar = QtGui.QScrollBar(QtCore.Qt.Horizontal)
        self.scroll_bar.sliderPressed.connect(self._hold_slider_updates)
        self.scroll_bar.sliderReleased.connect(
            self._send_slider_value_and_continue_updates
        )
        playback_layout.addWidget(self.scroll_bar)

        self.scroll_text = QtGui.QLabel('-/-', self)
        self.scroll_text.setMaximumWidth(self.scroll_text.sizeHint().width())
        playback_layout.addWidget(self.scroll_text)

        playback_layout_widget = QtGui.QWidget()
        playback_layout_widget.setLayout(playback_layout)
        simulation_layout.addWidget(playback_layout_widget)

        self.simulation_layout_widget = QtGui.QWidget()
        self.simulation_layout_widget.setLayout(simulation_layout)
        self.setCentralWidget(self.simulation_layout_widget)

        ### Tools ###
        self.code_text_edit = QtGui.QTextEdit(self)
        self.code_text_edit.setFont(QtGui.QFont('Monospace', 10))

        self.code_dock_widget = QtGui.QDockWidget('  Coding console', self)
        code_toolbar = QtGui.QToolBar(self.code_dock_widget)
        code_toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.send_to_robot_action = code_toolbar.addAction(
            QtGui.QIcon.fromTheme('document-send'),
            # NOTE: or:
            #QtGui.QIcon.fromTheme('media-record'),
            'Send to robot'
        )
        self.send_to_robot_action.triggered.connect(self._send_to_robot)
        code_layout = QtGui.QVBoxLayout()
        code_layout.addWidget(code_toolbar)
        code_layout.addWidget(self.code_text_edit)
        code_layout_widget = QtGui.QWidget()
        code_layout_widget.setLayout(code_layout)
        self.code_dock_widget.setWidget(code_layout_widget)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.code_dock_widget)
        self.code_dock_widget.hide()

        ### Menu ###
        map_menu = QtGui.QMenu('&Map', self)
        self.load_map_action = map_menu.addAction('&Load from file...')
        self.load_map_action.triggered.connect(self.load_map)
        self.menuBar().addMenu(map_menu)

        robot_menu = QtGui.QMenu('&Robot', self)
        self.open_source_action = robot_menu.addAction('&Open source code file...')
        self.open_source_action.triggered.connect(self.open_source)
        self.menuBar().addMenu(robot_menu)

        widgets_menu = QtGui.QMenu('&Widgets', self)
        self.code_tool_action = widgets_menu.addAction(
            self.code_dock_widget.toggleViewAction()
        )
        self.menuBar().addMenu(widgets_menu)

        #settings_menu = QtGui.QMenu('&Settings', self)
        #self.menuBar().addMenu(settings_menu)

        # Actions that we need to disable when simulating
        self.conflicting_with_sim = [
            self.start_sim_action,
            self.send_to_robot_action
        ]


    def status_bar_message(self, message):
        self.statusBar().showMessage(message)


    def update_data(self, current_frame, frame_count):
        if self.update_slider:
            self.scroll_bar.setMaximum(frame_count)
            self.scroll_bar.setValue(current_frame)
            self.scroll_text.setText('frame '+str(current_frame)+'/'+str(frame_count))
            self.scroll_text.setMaximumWidth(self.scroll_text.sizeHint().width())


    def load_map(self):

        file_name = QtGui.QFileDialog.getOpenFileName(
            self, 'Load map from file...', '.', 'Krakrobot maps (*.map)'
        )
        data = self._read_file_data(file_name)


    def open_source(self):

        file_name = QtGui.QFileDialog.getOpenFileName(
            self, 'Open robot source code file...', '.',
            'Python code (*.py);;C++ (*.cpp, *.cc);;Java (*.java)'
        )
        data = self._read_file_data(file_name)
        self.code_text_edit.setText(data)


    def _speed_value_changed(self):
        self.simulation_view.simulation_render_thread.frame_rate = \
            self.speed_box.value()


    def _hold_slider_updates(self):
        self.update_slider = False


    def _continue_slider_updates(self):
        self.update_slider = True


    def _send_scroll_bar_value(self):
        """Send scroll bar value to simulation and render threads"""
        self.simulation_view.simulation_render_thread.current_frame = \
            self.scroll_bar.value()


    def _send_slider_value_and_continue_updates(self):
        print self.scroll_bar.value()
        self._send_scroll_bar_value()
        self._continue_slider_updates()


    def _play_progress_animation(self):
        """Play progress (replay record) animation"""
        self.simulation_view.simulation_render_thread.paused = False
        self.animation_paused = False


    def _pause_progress_animation(self):
        self.simulation_view.simulation_render_thread.paused = True
        self.animation_paused = True


    def _skip_forward(self):
        self.scroll_bar.setValue(self.scroll_bar.maximum())
        self._send_scroll_bar_value()


    def _skip_backward(self):
        self.scroll_bar.setValue(0)
        self._send_scroll_bar_value()


    def _run_simulation(self):
        self.status_bar_message('Simulation process started...')
        self.currently_simulating = True
        for action in self.conflicting_with_sim:
            action.setEnabled(False)
        self.simulation_view.run_simulation()


    def _simulation_finished(self):
        self.status_bar_message(MSG_EMP+'Simulation has finished!')
        for action in self.conflicting_with_sim:
            action.setEnabled(True)


    def _send_to_robot(self):
        data = self.code_text_edit.text()
        print data


    def _read_file_data(self, file_name):
        input_file = open(file_name, 'r')
        with input_file:
            return input_file.read()



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


# Command Tool

from optparse import OptionParser
def create_parser():
    """ Configure options and return parser object """
    parser = OptionParser()
    parser.add_option("-c", "--command_line", dest="command_line", action="store_true", default=False,
                      help="If simulation will run without visualisation")
    parser.add_option("-m", "--map", dest="map", default="maps/5.map",
                      help="Map that will be run after hitting Start Simulation button, or if in "
                           "console mode after running the program")
    parser.add_option("-r", "--robot", dest="robot", default="examples/omit_collisions_example.py",
                      help="Robot that will be compiled and run")

    #parser.add_option("-v", "--verbose",default=True, type="int", dest="verbose", help="If set prints simulation steps")
    #parser.add_option( "--agent_1", type="string",default="UCTAgent", dest="agent1", help="""Set agent1 to "UCTAgent","UCTAgentTran", "UCTAgentTranCut", "RandomAgent", "GreedyAgent" """)
    #parser.add_option( "--agent_2", type="string", default="GreedyAgent", dest="agent2", help="""Set agent2 to "UCTAgent", "UCTAgentTran", "UCTAgentTranCut",  "RandomAgent", "GreedyAgent" """)
    #parser.add_option("-t", "--time_per_move",default=3, type="int", dest="time_per_move", help="Set time per move, default is 2s")
    #parser.add_option("-n", "--number_of_simulations", default=10, type="int", dest="num_sim", help="Sets number of simulations, default is 10")
    return parser


import sys
def main():
    parser = create_parser()
    (options, args) = parser.parse_args()
    print options, args

    import imp
 
 
    simulator_params = {"visualisation": not options.command_line
        ,"robot_controller_class": compile_robot(options.robot)[0]
    }
 
 
    #simulator_params["robot_controller_class"] =OmitCollisionsLocal
 
 
    if not options.command_line:
        simulator = KrakrobotSimulator(options.map, **simulator_params)
        gui = SimulatorGUI(sys.argv, simulator)
        gui.run()
    else:
        simulator = KrakrobotSimulator(options.map, simulation_dt=0.0, **simulator_params)
        print "Simulation has finished. Results: {0}".format(simulator.run())



if __name__ == '__main__':
    main()
