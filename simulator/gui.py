#TODO: add forward steering noise GUI element

import os
import sys
import pprint

from PyQt4 import QtGui, QtCore, QtSvg
from PyQt4.QtGui import QPixmap, QApplication
from simulator import KrakrobotSimulator
from robot_controller import construct_cmd_robot
from misc.visualisation import PrepareFrame, RenderAnimatedPart, \
    RenderFrameTemplate, fill_visualisation_descriptor
from misc.defines import __version__, __about__, __authors__, __license__
from misc.defines import *

graphicsmutex = QtCore.QMutex(QtCore.QMutex.Recursive)
frame_change_mutex = QtCore.QMutex(QtCore.QMutex.Recursive)

APP_NAME = 'Krakrobot Simulator'
APP_FULL_NAME = APP_NAME + ' ' + __version__
MSG_EMP = '-> '

DEFAULT_ANIMATION_RATE = 10


class SimulationThread(QtCore.QThread):
    """KrakrobotSimulator threading"""

    simulator = None

    def set_simulator(self, simulator):
        self.simulator = simulator

    def run(self):
        """Running KrakrobotSimulator simulation"""
        print "Simulation has finished. Results:\n{0}".format(pprint.pformat(self.simulator.run(), indent=1))


class KrakrobotBoardAnimation(QtGui.QGraphicsView):
    """KrakrobotSimulator board animation painting widget"""

    status_bar_message = QtCore.pyqtSignal(str)
    simulation_thread = None
    # Interval (ms) of every animation_update timer
    refresh_rate = 1000 / DEFAULT_ANIMATION_RATE
    # Number of frames skipped in animation_update timer
    # NOTE: Ths value is being incremented when when refresh_rate is too small
    animation_speed = 1
    frame_template = ''
    frames = []
    current_frame = 0
    frame_count = 0
    simulator = None
    animation_started = False
    animation_paused = False

    def __init__(self, simulator, parent):
        super(KrakrobotBoardAnimation, self).__init__(parent)
        self.init_ui()
        self.simulator = simulator

    def init_ui(self):
        self.frames_timer = QtCore.QTimer(self)
        self.frames_timer.timeout.connect(self.frames_update)
        self.animation_timer = QtCore.QTimer(self)
        self.animation_timer.timeout.connect(self.animation_update)

        self.setScene(QtGui.QGraphicsScene(self))
        self.setTransformationAnchor(self.AnchorUnderMouse)
        self.setDragMode(self.ScrollHandDrag)
        self.setCacheMode(self.CacheBackground)
        self.setViewportUpdateMode(self.NoViewportUpdate)

    def clear_board(self):
        """Clear and prepare board for animation"""

        scene = self.scene()
        scene.clear()
        self.resetTransform()

        self.xml_stream_reader = QtCore.QXmlStreamReader()
        if self.frame_template:
            self.xml_stream_reader = QtCore.QXmlStreamReader(self.frame_template)

        self.svg_renderer = QtSvg.QSvgRenderer(self.xml_stream_reader)
        self.svg_item = QtSvg.QGraphicsSvgItem()
        self.svg_item.setSharedRenderer(self.svg_renderer)
        self.svg_item.setFlags(QtGui.QGraphicsItem.ItemClipsToShape)
        self.svg_item.setCacheMode(QtGui.QGraphicsItem.NoCache)
        self.svg_item.setZValue(0)

        scene.addItem(self.svg_item)

        scene.setSceneRect(self.svg_item.boundingRect().adjusted(-10, -10, 10, 10))

    def start(self):
        """Start simulation process"""

        if self.animation_paused:
            return

        self.animation_started = True
        self.frame_template = ''
        self.frames = []
        self.current_frame = 0
        self.frame_count = 0
        self.animation_started = True
        self.animation_paused = False

        self.simulation_thread = SimulationThread()
        self.simulation_thread.finished.connect(self.parent().parent().simulation_finished)
        self.clear_board()
        self.simulation_thread.set_simulator(self.simulator)
        self.simulation_thread.start()

        self.status_bar_message.emit('Simulation started...')

        self.frames_timer.start(0)
        self.animation_timer.start(self.refresh_rate)

    def pause_animation(self):
        """Pause animation process"""

        if not self.animation_started:
            return

        self.animation_paused = not self.animation_paused

        if self.animation_paused:
            self.animation_timer.stop()
            self.status_bar_message.emit('Animation paused.')

        else:
            self.animation_timer.start(self.refresh_rate)
            self.status_bar_message.emit('Animation played...')

    def terminate_simulation(self):
        self.simulation_thread.terminate()
        self.simulator.terminate()
        self.frames_timer.stop()

    def frames_update(self):
        """Update collection and GUI with current simulator frames data

        This method is an event of self.frames_timer timeout

        """

        if self.simulator:

            try:
                sim_data = self.simulator.get_next_frame_nowait()
            except Exception:
                if self.simulator.finished:
                    self.frames_timer.stop()
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
        """Update GUI with current animation frame

        This method is an event of self.animation_timer timeout

        """

        if len(self.frames) > 0:
            if self.current_frame + 1 > self.frame_count:
                return
            svg_data = PrepareFrame(self.frame_template, self.frames[self.current_frame])
            self.xml_stream_reader.clear()
            self.xml_stream_reader.addData(svg_data)
            self.svg_renderer.load(self.xml_stream_reader)

            scene = self.scene()
            self.svg_item.setSharedRenderer(self.svg_renderer)
            self.svg_item.setFlags(QtGui.QGraphicsItem.ItemClipsToShape)
            self.svg_item.setCacheMode(QtGui.QGraphicsItem.NoCache)
            self.svg_item.setZValue(0)
            scene.update()

            scene.setSceneRect(self.svg_item.boundingRect().adjusted(-10, -10, 10, 10))

            if not self.animation_paused:
                previous_frame = self.current_frame
                self.current_frame += self.animation_speed

            # GUI update #
            main_window = self.parent().parent()
            main_window.update_current_frame(self.current_frame)
            # Animation output update - we must calculate frames we have skipped
            for frame in range(previous_frame, self.current_frame + 1):
                main_window.check_and_update_animation_console(frame)

            if self.refresh_rate >= 10:
                self.animation_timer.setInterval(self.refresh_rate)
            else:
                self.animation_speed = 10 / self.refresh_rate

    def new_simulator(self, simulator):
        self.simulator = simulator

    def wheelEvent(self, event):
        factor = pow(1.2, event.delta() / 240.0)
        self.scale(factor, factor)
        event.accept()


class MainWindow(QtGui.QMainWindow):
    """Main window (all-in-one window)"""

    text_edit_width = 80
    text_edit_height = 30

    def __init__(self, simulator, simulator_params):
        super(MainWindow, self).__init__()
        self.simulator = simulator
        self.simulator_params = simulator_params
        self.update_slider = True
        self.currently_simulating = False
        self.console_dict = {}
        self.console_timer = QtCore.QTimer(self)
        self.console_timer.timeout.connect(self._update_console_log)
        self._init_ui()

    def _init_ui(self):

        self.window_icon = QtGui.QIcon('./simulator/media/iiujrobotics.svg')
        self.setWindowIcon(self.window_icon)

        ### Toolbar ###
        main_toolbar = self.addToolBar('Krakrobot Simulator')
        self.setWindowTitle(APP_FULL_NAME)
        self.status_bar_message('Welcome to ' + APP_FULL_NAME + '!')

        main_toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.start_sim_action = main_toolbar.addAction(
            QtGui.QIcon.fromTheme('system-run'),
            'Start Simulation'
        )
        self.start_sim_action.triggered.connect(self._run_simulation)

        self.terminate_sim_action = main_toolbar.addAction(
            QtGui.QIcon.fromTheme('process-stop'),
            'Terminate'
        )
        self.terminate_sim_action.triggered.connect(self._terminate_simulation)

        # TODO: maximum lines for QPlainTextEdit = 1

        params_toolbar = self.addToolBar('Simulator parameters')

        frame_dt_label = QtGui.QLabel('frame_dt: ')
        params_toolbar.addWidget(frame_dt_label)
        self.frame_dt_edit = QtGui.QLineEdit(str(self.simulator_params['frame_dt']))
        params_toolbar.addWidget(self.frame_dt_edit)
        self.frame_dt_edit.textChanged.connect(self._update_frame_dt)

        steering_noise_label = QtGui.QLabel('steering_noise: ')
        params_toolbar.addWidget(steering_noise_label)
        self.steering_noise_edit = QtGui.QLineEdit(str(self.simulator_params['steering_noise']))
        params_toolbar.addWidget(self.steering_noise_edit)
        self.steering_noise_edit.textChanged.connect(self._update_steering_noise)

        fsteering_noise_label = QtGui.QLabel('forward_steering_drift: ')
        params_toolbar.addWidget(fsteering_noise_label)
        self.fsteering_noise_edit = QtGui.QLineEdit(str(self.simulator_params['forward_steering_drift']))
        params_toolbar.addWidget(self.fsteering_noise_edit)
        self.fsteering_noise_edit.textChanged.connect(self._update_fsteering_noise)

        distance_noise_label = QtGui.QLabel('distance_noise: ')
        params_toolbar.addWidget(distance_noise_label)
        self.distance_noise_edit = QtGui.QLineEdit(str(self.simulator_params['distance_noise']))
        params_toolbar.addWidget(self.distance_noise_edit)
        self.distance_noise_edit.textChanged.connect(self._update_distance_noise)

        speed_label = QtGui.QLabel('speed: ')
        params_toolbar.addWidget(speed_label)
        self.speed_edit = QtGui.QLineEdit(str(self.simulator_params['speed']))
        params_toolbar.addWidget(self.speed_edit)
        self.speed_edit.textChanged.connect(self._update_speed)

        turning_speed_label = QtGui.QLabel('turning_speed: ')
        params_toolbar.addWidget(turning_speed_label)
        self.turning_speed_edit = QtGui.QLineEdit(str(self.simulator_params['turning_speed']))
        params_toolbar.addWidget(self.turning_speed_edit)
        self.turning_speed_edit.textChanged.connect(self._update_turning_speed)

        execution_cpu_time_limit_label = QtGui.QLabel('execution_cpu_time_limit: ')
        params_toolbar.addWidget(execution_cpu_time_limit_label)
        self.execution_cpu_time_limit_edit = QtGui.QLineEdit(
            str(self.simulator_params['execution_cpu_time_limit']))
        params_toolbar.addWidget(self.execution_cpu_time_limit_edit)
        self.execution_cpu_time_limit_edit.textChanged.connect(self._update_execution_cpu_time_limit)

        simulation_time_limit_label = QtGui.QLabel('simulation_time_limit: ')
        params_toolbar.addWidget(simulation_time_limit_label)
        self.simulation_time_limit_edit = QtGui.QLineEdit(str(self.simulator_params['simulation_time_limit']))
        params_toolbar.addWidget(self.simulation_time_limit_edit)
        self.simulation_time_limit_edit.textChanged.connect(self._update_simulation_time_limit)

        simulation_layout = QtGui.QVBoxLayout()
        self.board_animation = KrakrobotBoardAnimation(self.simulator, self)
        self.board_animation.status_bar_message[str].connect(
            self.status_bar_message
        )
        simulation_layout.addWidget(self.board_animation)

        ### Playbock Layout ###
        playback_layout = QtGui.QHBoxLayout()
        playback_toolbar = QtGui.QToolBar()

        speed_label = QtGui.QLabel('Anim. rate: ')
        playback_toolbar.addWidget(speed_label)

        self.speed_box = QtGui.QSpinBox(self)
        self.speed_box.setRange(1, 1000)
        self.speed_box.setValue(DEFAULT_ANIMATION_RATE)
        self.speed_box.setToolTip('Change animation rate')
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
        self.scroll_text.current_frame = '-'
        self.scroll_text.frame_count = '-'
        self.scroll_text.setMaximumWidth(self.scroll_text.sizeHint().width())
        playback_layout.addWidget(self.scroll_text)

        playback_layout_widget = QtGui.QWidget()
        playback_layout_widget.setLayout(playback_layout)
        playback_layout_widget.setMaximumHeight(
            playback_layout_widget.sizeHint().height()
        )
        simulation_layout.addWidget(playback_layout_widget)

        self.simulation_layout_widget = QtGui.QWidget()
        self.simulation_layout_widget.setLayout(simulation_layout)
        self.setCentralWidget(self.simulation_layout_widget)

        ### Widgets (as named in this application) ###
        self.console_font = QtGui.QFont('Monospace', 10)

        self.output_console = QtGui.QTextBrowser()
        self.output_console.setFont(self.console_font)
        self.console_dock_widget = QtGui.QDockWidget(
            '  &Simulation output console  ',
            self
        )
        self.console_dock_widget.setWidget(self.output_console)
        self.addDockWidget(
            QtCore.Qt.BottomDockWidgetArea,
            self.console_dock_widget
        )

        self.animation_console = QtGui.QTextBrowser()
        self.animation_console.setFont(self.console_font)
        self.animation_console_dock_widget = QtGui.QDockWidget(
            '  &Animation output console  ',
            self
        )
        self.animation_console_dock_widget.setWidget(self.animation_console)
        self.addDockWidget(
            QtCore.Qt.BottomDockWidgetArea,
            self.animation_console_dock_widget
        )

        ### Menu ###
        map_menu = QtGui.QMenu('&Map', self)
        self.load_map_action = map_menu.addAction('&Load from file...')
        self.load_map_action.triggered.connect(self.load_map)
        self.menuBar().addMenu(map_menu)

        robot_menu = QtGui.QMenu('&Robot', self)
        self.open_source_action = robot_menu.addAction('&Load source code file...')
        self.open_source_action.triggered.connect(self.open_source)
        self.menuBar().addMenu(robot_menu)

        widgets_menu = QtGui.QMenu('&Widgets', self)
        self.console_action = widgets_menu.addAction(
            self.console_dock_widget.toggleViewAction()
        )
        self.animation_console_action = widgets_menu.addAction(
            self.animation_console_dock_widget.toggleViewAction()
        )
        self.menuBar().addMenu(widgets_menu)

        help_menu = QtGui.QMenu('&Help', self)
        self.about_action = help_menu.addAction(
            QtGui.QIcon.fromTheme('help-about'),
            '&About...'
        )
        self.about_action.triggered.connect(self.about_window)
        self.menuBar().addMenu(help_menu)

        # Actions that we need to disable when simulating
        self.conflicting_with_sim = [
            self.start_sim_action,
            self.steering_noise_edit,
            self.distance_noise_edit,
            self.fsteering_noise_edit,
            self.speed_edit,
            self.turning_speed_edit,
            self.execution_cpu_time_limit_edit,
            self.simulation_time_limit_edit,
            self.frame_dt_edit,
        ]

    def status_bar_message(self, message):
        print 'Status bar message: ', message
        self.statusBar().showMessage(message)

    def update_frame_count(self, frame_count):
        if self.update_slider:
            self.scroll_bar.setMaximum(frame_count)
            self.scroll_text.frame_count = str(frame_count)
            self.scroll_bar_text()

    def update_current_frame(self, current_frame):
        # if self.update_slider:
        self.scroll_bar.setValue(current_frame)
        self.scroll_text.current_frame = str(current_frame)
        self.scroll_bar_text()

    def scroll_bar_text(self):
        self.scroll_text.setText('frame ' + str(
            self.scroll_text.current_frame
        ) + '/' + str(
            self.scroll_text.frame_count
        )
                                 )
        self.scroll_text.setMaximumWidth(self.scroll_text.sizeHint().width())

    def load_map(self):

        file_name = QtGui.QFileDialog.getOpenFileName(
            self, 'Load map from file...', '.', 'Krakrobot maps (*.map)'
        )
        if os.path.isfile(file_name):
            self.simulator_params['map'] = str(file_name)
            self.status_bar_message(
                'Map loaded from ' + str(file_name)
            )
        else:
            self.status_bar_message(
                'File does not exist: ' + str(file_name)
            )

    def open_source(self):

        file_name = QtGui.QFileDialog.getOpenFileName(
            self, 'Open robot source code file...', '.',
            'Python code (*.py)'
        )
        self.status_bar_message(
            'Loading source code from ' + str(file_name) + ' ...'
        )
        try:
            cmd_robot = construct_cmd_robot(str(file_name))
        except Exception as error:
            self.status_bar_message(
                MSG_EMP + 'Robot source code compiling error: ' + str(error)
            )
            return -1
        self.simulator_params['robot_controller'] = cmd_robot
        self.status_bar_message(
            'Robot source code loaded from ' + str(file_name)
        )

    def about_window(self):
        QtGui.QMessageBox.about(
            self,
            'About Krakrobot Python Simulator ' + __version__,
            QtCore.QString(__about__ + '\n') + \
            QtCore.QString('\n' + __website__ + '\n') + \
            QtCore.QString('\n' + __authors__ + '\n') + \
            QtCore.QString(
                'https://github.com/uj-robotics/Krakrobot2014Qualifications\n'
            ) + \
            QtCore.QString('\nLicense: ' + __license__ + '\n') + \
            QtCore.QString(
                """Copyright (c) 2013-2014 """
                """Jagiellonian University Robotics Interest Group,"""
                """http://www.robotics.ii.uj.edu.pl/"""
            )
        )

    def _speed_value_changed(self):
        self.board_animation.refresh_rate = \
            1000 / self.speed_box.value()

    def _hold_slider_updates(self):
        self.update_slider = False

    def _continue_slider_updates(self):
        self.update_slider = True

    def _send_scroll_bar_value(self):
        """Send scroll bar value to animation widget"""
        frame_change_mutex.lock()
        self.board_animation.current_frame = self.scroll_bar.value()
        current_frame = self.scroll_bar.value()
        self.board_animation.animation_update()
        frame_change_mutex.unlock()

    def _send_slider_value_and_continue_updates(self):
        self._send_scroll_bar_value()
        self._continue_slider_updates()

    def _play_progress_animation(self):
        """Play animation process"""
        if self.board_animation.animation_paused:
            self.board_animation.pause_animation()

    def _toggle_pause_progress_animation(self):
        self.board_animation.pause_animation()

    def _pause_progress_animation(self):
        if not self.board_animation.animation_paused:
            self.board_animation.pause_animation()

    def _skip_forward(self):
        offset = self.scroll_bar.maximum() / 10
        new_value = min(self.scroll_bar.value() + offset, self.scroll_bar.maximum() - 1)
        self.scroll_bar.setValue(new_value)
        self._send_scroll_bar_value()
        self._pause_progress_animation()

    def _skip_backward(self):
        offset = self.scroll_bar.maximum() / 10
        new_value = max(self.scroll_bar.value() - offset, self.scroll_bar.minimum())
        self.scroll_bar.setValue(new_value)
        self._send_scroll_bar_value()
        self._pause_progress_animation()

    def _run_simulation(self):
        self.currently_simulating = True
        self._play_progress_animation()
        for action in self.conflicting_with_sim:
            action.setEnabled(False)
        self._reconstruct_simulator()
        self.board_animation.start()
        self.console_timer.start(1)

    def _terminate_simulation(self):
        self.board_animation.terminate_simulation()
        self.currently_simulating = False
        self.simulation_finished()
        # Communicative purposes
        self._pause_progress_animation()

    def simulation_finished(self):
        self.status_bar_message(MSG_EMP + 'Simulation has finished!')
        self.console_timer.stop()
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

    def _reconstruct_simulator(self):
        self.simulator = KrakrobotSimulator(**self.simulator_params)
        self.board_animation.new_simulator(
            self.simulator
        )

    def _update_console_log(self):
        logsc = len(self.board_animation.simulator.get_logs())
        if logsc > 0:
            new_line = self.board_animation.simulator.get_logs()[logsc - 1]
            new_line_split = new_line.split(':\n')
            line_dict = eval(new_line_split[0])
            self.console_dict[line_dict['frame']] = new_line

            self.output_console.append(str(
                new_line
            )
            )

        self.output_console.verticalScrollBar().setSliderPosition(
            self.output_console.verticalScrollBar().maximum()
        )

    def check_and_update_animation_console(self, frame):
        if self.console_dict.has_key(frame):
            self.animation_console.append(
                self.console_dict[frame]
            )

    def closeEvent(self, event):
        self._terminate_simulation()

    def _update_steering_noise(self):
        self.simulator_params['steering_noise'] = \
            float(self.steering_noise_edit.text())

    def _update_fsteering_noise(self):
        self.simulator_params['forward_steering_drift'] = \
            float(self.fsteering_noise_edit.text())

    def _update_sonar_noise(self):
        self.simulator_params['sonar_noise'] = \
            float(self.sonar_noise_edit.text())

    def _update_distance_noise(self):
        self.simulator_params['distance_noise'] = \
            float(self.distance_noise_edit.text())

    def _update_measurement_noise(self):
        self.simulator_params['measurement_noise'] = \
            float(self.measurement_noise_edit.text())

    def _update_speed(self):
        self.simulator_params['speed'] = \
            float(self.speed_edit.text())

    def _update_turning_speed(self):
        self.simulator_params['turning_speed'] = \
            float(self._edit.text())

    def _update_execution_cpu_time_limit(self):
        self.simulator_params['execution_cpu_time_limit'] = \
            float(self.execution_cpu_time_limit_edit.text())

    def _update_simulation_time_limit(self):
        self.simulator_params['simulation_time_limit'] = \
            float(self.simulation_time_limit_edit.text())

    def _update_simulation_dt(self):
        self.simulator_params['simulation_dt'] = \
            float(self.simulation_dt_edit.text())

    def _update_frame_dt(self):
        self.simulator_params['frame_dt'] = \
            float(self.frame_dt_edit.text())

    def _update_gps_delay(self):
        self.simulator_params['gps_delay'] = \
            float(self.gps_delay_edit.text())

    def _update_iteration_write_frequency(self):
        self.simulator_params['iteration_write_frequency'] = \
            float(self.iteration_write_frequency_edit.text())


class SimulatorGUI(object):
    """GUI master class"""

    simulator = None
    application_thread = None
    qt_app = None

    def __init__(self, argv, simulator, simulator_params):
        """ Initialize GUI

        @param argv - program arguments values
        @param simulator - KrakrobotSimulator object

        """
        self.simulator = simulator
        # TODO(kudkudak): remove simulator_params
        self.simulator_params = simulator_params
        self.qt_app = QtGui.QApplication(argv)

    def run(self):
        main_window = MainWindow(self.simulator, self.simulator_params)
        main_window.showMaximized()
        main_window.raise_()

        sys.exit(self.qt_app.exec_())
