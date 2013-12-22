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

graphics_update_mutex = QtCore.QMutex(QtCore.QMutex.Recursive)
frame_change_mutex = QtCore.QMutex(QtCore.QMutex.Recursive)

from optparse import OptionParser
def create_parser():

    """
                     steering_noise=0.01, sonar_noise = 0.1, distance_noise=0.001,
                 measurement_noise=0.2, time_limit = 50,
                 speed = 5.0,
                 turning_speed = 0.4*pi,
                 execution_cpu_time_limit = 10.0,
                 simulation_time_limit = 10.0,
                 simulation_dt = 0.001,
                 frame_dt = 0.1,
                 collision_threshold = 50,
                 iteration_write_frequency = 1000,
                 visualisation = True
                 """

    """ Configure options and return parser object """
    parser = OptionParser()
    parser.add_option("-c", "--command_line", dest="command_line", action="store_true", default=False,
                      help="If simulation will run without visualisation")
    parser.add_option("-m", "--map", dest="map", default="maps/3.map",
                      help="Map that will be run after hitting Start Simulation button, or if in "
                           "console mode after running the program")
    parser.add_option("-r", "--robot", dest="robot", default="examples/omit_collisions_example.py",
                      help="Robot that will be compiled and run")
    parser.add_option("--steering_noise", dest="steering_noise", default=0.01, type="float",
                      help="Sigma of gaussian noise applied to turning motion")
    parser.add_option("--sonar_noise", dest="sonar_noise", default=0.1,type="float",
                      help="Sigma of gaussian noise applied to sensed distance by sonar")
    parser.add_option("--gps_noise", dest="measurement_noise", default=0.1,type="float",
                      help="Sigma of gaussian noise applied to the sensed GPS position")

    parser.add_option("--gps_delay", dest="gps_delay", default=2.0,type="float",
                      help="Time consumption (in simulation time units) of GPS")

    parser.add_option("--distance_noise", dest="distance_noise", default=0.001,type="float",
                      help="Sigma of gaussian noise applied to forward motion")

    parser.add_option("--speed", dest="speed", default=5.0,type="float",
                      help="Speed of the robot (i.e. units/simulation second)")
    parser.add_option("--turning_speed", dest="turning_speed", default=1.0,type="float",
                      help="Turning speed of the robot (i.e. rad/simulation second)")


    parser.add_option("--execution_cpu_time_limit", dest="execution_cpu_time_limit", default=10.0,type="float",
                      help="Execution CPU time limit")
    parser.add_option("--simulation_time_limit", dest="simulation_time_limit", default=10000.0,type="float",
                      help="Simulation time limit (in virtual time units)")

    parser.add_option("--frame_dt", dest="frame_dt", default=0.1,type="float",
                      help="How often (in simulation time units) to produce a frame")

    parser.add_option("--iteration_write_frequency", dest="iteration_write_frequency", default=1000,type="int",
                      help="How often (number of ticks of simulator) to report simulation status")
    return parser


parser = create_parser()
(options, args) = parser.parse_args()
print options, args


simulator_params = {"visualisation": not options.command_line,
                    "speed": options.speed,
                    "distance_noise": options.distance_noise,
                    "steering_noise": options.steering_noise,
                    "sonar_noise": options.sonar_noise,
                    "measurement_noise": options.measurement_noise,
                    "turning_speed":options.turning_speed,
                    "execution_cpu_time_limit": options.execution_cpu_time_limit,
                    "simulation_time_limit":options.simulation_time_limit,
                    "frame_dt":options.frame_dt,
                    "iteration_write_frequency":options.iteration_write_frequency,
                    "gps_delay":options.gps_delay,
                    "robot_controller_class": compile_robot(options.robot)[0],
                    "map": options.map
}

class SimulationThread(QtCore.QThread):
    """KrakrobotSimulator threading"""

    def set_simulator(self, simulator):
        self.simulator = simulator

    def run(self):
        """Running KrakrobotSimulator simulation"""
        self.simulator.reset()
        self.simulator.run()
        self.exec_()


class KrakrobotBoardAnimation(QtGui.QGraphicsView):
    """KrakrobotSimulator board animation painting widget"""

    status_bar_message = QtCore.pyqtSignal(str)
    animation_speed = 5
    frame_template = ''
    frames = []
    current_frame = 0
    frame_count = 0
    simulator = None
    animation_started = False
    animation_paused = False
    refresh_rate = 10

    def __init__(self, parent):
        super(KrakrobotBoardAnimation, self).__init__(parent)
        self.init_ui()


    def init_ui(self):
        self.frames_timer = QtCore.QTimer(self)
        self.frames_timer.timeout.connect(self.frames_update)
        self.animation_timer = QtCore.QTimer(self)
        self.animation_timer.timeout.connect(self.animation_update)

        self.setScene(QtGui.QGraphicsScene(self))
        self.setTransformationAnchor(self.AnchorUnderMouse)
        self.setCacheMode(self.CacheBackground)
        self.setViewportUpdateMode(self.NoViewportUpdate)


    def clear_board(self):

        scene = self.scene()
        scene.clear()
        self.resetTransform()

        self.xml_stream_reader = QtCore.QXmlStreamReader()
        if self.frame_template:
            self.xml_stream_reader = QtCore.QXmlStreamReader(self.frame_template)

        self.svg_renderer = QtSvg.QSvgRenderer(self.xml_stream_reader)
        self.svg_item = QtSvg.QGraphicsSvgItem()#str(time.ctime()))
        self.svg_item.setSharedRenderer(self.svg_renderer)
        self.svg_item.setFlags(QtGui.QGraphicsItem.ItemClipsToShape)
        self.svg_item.setCacheMode(QtGui.QGraphicsItem.NoCache)
        self.svg_item.setZValue(0)

        scene.addItem(self.svg_item)

        scene.setSceneRect(self.svg_item.boundingRect().adjusted(-10, -10, 10, 10))



    def start(self, simulator):

        if self.animation_paused:
            return

        self.animation_started = True

        self.simulation_thread = SimulationThread()
        self.simulator = simulator
        self.clear_board()
        self.simulation_thread.set_simulator(simulator)
        self.simulation_thread.start()

        self.status_bar_message.emit('Simulation started...')

        self.frames_timer.start(1)
        self.animation_timer.start(self.refresh_rate)


    def pause_animation(self):

        if not self.animation_started:
            return

        self.animation_paused = not self.animation_paused

        if self.animation_paused:
            self.animation_timer.stop()
            self.status_bar_message.emit('Animation paused.')

        else:
            self.animation_timer.start(self.refresh_rate)
            self.status_bar_message.emit('Animation played...')


    def frames_update(self):

        if self.simulator.finished:
            self.frames_timer.stop()

        if self.simulator:

            try:
                sim_data = self.simulator.get_next_frame_nowait()
            except Exception:
                return
            fill_visualisation_descriptor(sim_data)

            if self.frame_template == '':
                self.frame_template = RenderFrameTemplate(sim_data)
                self.clear_board()

            svg_data = RenderAnimatedPart(sim_data)
            self.frames.append(svg_data)
            self.frame_count += 1

            # GUI update #
            main_window = self.parent().parent()
            main_window.update_frame_count(self.frame_count)


    def animation_update(self):

        if len(self.frames) > 0:
            if self.current_frame+1 > self.frame_count:
                return
            svg_data = PrepareFrame(self.frame_template,self.frames[self.current_frame])
            self.xml_stream_reader = QtCore.QXmlStreamReader(svg_data)
            self.svg_renderer.load(self.xml_stream_reader)

            scene = self.scene()
            self.svg_item.setSharedRenderer(self.svg_renderer)
            self.svg_item.setFlags(QtGui.QGraphicsItem.ItemClipsToShape)
            self.svg_item.setCacheMode(QtGui.QGraphicsItem.NoCache)
            self.svg_item.setZValue(0)
            scene.update()

            scene.setSceneRect(self.svg_item.boundingRect().adjusted(-10, -10, 10, 10))
            self.current_frame += self.animation_speed

            # GUI update #
            main_window = self.parent().parent()
            main_window.update_current_frame(self.current_frame)



class MainWindow(QtGui.QMainWindow):
    """Main window (all-in-one window)"""

    def __init__(self, simulator):
        super(MainWindow, self).__init__()
        self._init_ui(simulator)
        self.simulator = simulator
        self.update_slider = True
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
        self.board_animation = KrakrobotBoardAnimation(self)
        self.board_animation.status_bar_message[str].connect(
            self.status_bar_message
        )
        simulation_layout.addWidget(self.board_animation)

        playback_layout = QtGui.QHBoxLayout()
        #playback_layout.addStrut(1)
        playback_toolbar = QtGui.QToolBar()
        self.speed_box = QtGui.QSpinBox(self)
        self.speed_box.setRange(1, 1000)
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
        playback_layout_widget.setMaximumHeight(playback_layout_widget.sizeHint().height())
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
        self.save_code_action = code_toolbar.addAction(
            QtGui.QIcon.fromTheme('document-send'),
            # NOTE: or:
            #QtGui.QIcon.fromTheme('media-record'),
            'Save code'
        )
        self.save_code_action.triggered.connect(self._save_code)
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
        #self.menuBar().addMenu(robot_menu)

        widgets_menu = QtGui.QMenu('&Widgets', self)
        self.code_tool_action = widgets_menu.addAction(
            self.code_dock_widget.toggleViewAction()
        )
        #self.menuBar().addMenu(widgets_menu)

        #settings_menu = QtGui.QMenu('&Settings', self)
        #self.menuBar().addMenu(settings_menu)

        # Actions that we need to disable when simulating
        self.conflicting_with_sim = [
            self.start_sim_action
        ]


    def status_bar_message(self, message):
        self.statusBar().showMessage(message)


    def update_frame_count(self, frame_count):
        if self.update_slider:
            self.scroll_bar.setMaximum(frame_count)
            self.scroll_text.frame_count = str(frame_count)
            self._update_scroll_bar_text()


    def update_current_frame(self, current_frame):
        if self.update_slider:
            self.scroll_bar.setValue(current_frame)
            self.scroll_text.current_frame = str(current_frame)
            self._update_scroll_bar_text()


    def _update_scroll_bar_text(self):
            self.scroll_text.setText('frame '+str(
                self.scroll_text.current_frame
                )+'/'+str(
                self.scroll_text.frame_count
                )
            )
            self.scroll_text.setMaximumWidth(self.scroll_text.sizeHint().width())


    def load_map(self):

        file_name = QtGui.QFileDialog.getOpenFileName(
            self, 'Load map from file...', '.', 'Krakrobot maps (*.map)'
        )
        simulator_params['map'] = file_name


    def open_source(self):

        file_name = QtGui.QFileDialog.getOpenFileName(
            self, 'Open robot source code file...', '.',
            'Python code (*.py);;C++ (*.cpp, *.cc);;Java (*.java)'
        )
        data = self._read_file_data(file_name)
        self.code_text_edit.setText(data)
        self.code_text_edit.file_name = file_name
        self.code_dock_widget.show()


    def _speed_value_changed(self):
        self.board_animation.animation_speed = \
            self.speed_box.value()


    def _hold_slider_updates(self):
        self.update_slider = False


    def _continue_slider_updates(self):
        self.update_slider = True


    def _send_scroll_bar_value(self):
        """Send scroll bar value to simulation and render thread"""
        frame_change_mutex.lock()
        self.board_animation.current_frame = self.scroll_bar.value()
        frame_change_mutex.unlock()


    def _send_slider_value_and_continue_updates(self):
        print self.scroll_bar.value()
        self._send_scroll_bar_value()
        self._continue_slider_updates()


    def _play_progress_animation(self):
        """Play progress (replay record) animation"""
        if self.board_animation.animation_paused:
            self.board_animation.pause_animation()


    def _pause_progress_animation(self):
        self.board_animation.pause_animation()


    def _skip_forward(self):
        self.scroll_bar.setValue(self.scroll_bar.maximum())
        self._send_scroll_bar_value()


    def _skip_backward(self):
        self.scroll_bar.setValue(self.scroll_bar.minimum())
        self._send_scroll_bar_value()


    def _run_simulation(self):
        self.currently_simulating = True
        for action in self.conflicting_with_sim:
            action.setEnabled(False)
        self.board_animation.start(self.simulator)


    def _simulation_finished(self):
        self.status_bar_message(MSG_EMP+'Simulation has finished!')
        for action in self.conflicting_with_sim:
            action.setEnabled(True)


    def _save_code(self):
        data = self.code_text_edit.toPlainText()
        self._save_to_file(self.code_text_edit.file_name, data)


    def _save_to_file(self, file_name, data):
        output_file = open(file_name, 'w')
        with output_file:
            output_file.write(str(data))


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

import sys
def main():
    import imp
 
 
 
 
    #simulator_params["robot_controller_class"] =OmitCollisionsLocal
 
 
    if not options.command_line:
        simulator = KrakrobotSimulator(**simulator_params)
        gui = SimulatorGUI(sys.argv, simulator)
        gui.run()
    else:
        simulator = KrakrobotSimulator(simulation_dt=0.0, **simulator_params)
        print "Simulation has finished. Results: {0}".format(simulator.run())



if __name__ == '__main__':
    main()
