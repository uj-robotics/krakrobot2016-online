# -*- coding: utf-8 -*-

"""
    Krakrobot Python Simulator

    Simulator which runs the simulation and renders SVG frames.
"""

from Queue import Queue
import time
import datetime
from math import (
    pi
)
import traceback

from map import logger, load_map
from misc.defines import *
from robot import Robot
from robot_controller import PythonTimedRobotController

class KrakrobotSimulator(object):

    def __init__(self,
                 map,
                 robot_controller,
                 init_position=None,
                 steering_noise=0.01,
                 color_noise=10,
                 sonar_noise=0.1,
                 distance_noise=0.001,
                 measurement_noise=0.2,
                 speed=5.0,
                 turning_speed=0.4 * pi,
                 execution_cpu_time_limit=10.0,
                 simulation_time_limit=10.0,
                 simulation_dt=0.0,
                 frame_dt=0.1,
                 gps_delay=2.0,
                 collision_threshold=50,
                 iteration_write_frequency=1000,
                 command_line=True,
                 print_robot=True,
                 print_logger=False,
                 accepted_commands=[TURN, MOVE, BEEP, FINISH, SENSE_COLOR]
                 ):
        """
            Construct KrakrobotSimulator instancew

            :param steering_noise - variance of steering in move
            :param distance_noise - variance of distance in move
            :param measurement_noise - variance of measurement (GPS??)
            :param map - map for the robot simulator representing the maze or file to map
            :param init_position - starting position of the Robot (can be moved to map class) [x,y,heading]
            :param speed - distance travelled by one move action (cannot be bigger than 0.5, or he could traverse the walls)
            :param simulation_time_limit - limit in ms for whole robot execution (also with init)
            :param collision_threshold - maximum number of collisions after which robot is destroyed
            :param simulation_dt -  controlls simulation calculation intensivity
            :param frame_dt - save frame every dt
            :param robot - RobotController class that will be simulated in run procedure
        """

        if type(map) is str :
            self.map = load_map(map)
            self.map_title = self.map["title"]
            for row in self.map['board']:
                logger.info(row)
        else:
            self.map = map
            self.map_title = ""
            self.map_params = {}

        self.N = self.map['N']
        self.M = self.map['M']

        self.iteration_write_frequency = iteration_write_frequency

        self.collision_threshold = collision_threshold

        if init_position is not None:
            self.init_position = tuple(init_position)
        else:
            for i in xrange(self.N):
                for j in xrange(self.M):
                    if self.map['board'][i][j] == MAP_START_POSITION:
                        self.init_position = (i + 0.5, j + 0.5, 0)

        self.speed = speed
        self.turning_speed = turning_speed
        self.simulation_dt = simulation_dt
        self.frame_dt = frame_dt
        self.robot_controller = robot_controller
        self.print_robot = print_robot
        self.print_logger = print_logger
        self.accepted_commands = accepted_commands

        self.command_line = command_line

        self.sonar_time = SONAR_TIME
        self.gps_delay = gps_delay
        self.light_sensor_time = FIELD_TIME

        self.tick_move = TICK_MOVE
        self.tick_rotate = TICK_ROTATE

        self.simulation_time_limit = simulation_time_limit
        self.execution_cpu_time_limit = execution_cpu_time_limit

        self.goal_threshold = 0.5  # When to declare goal reach

        self.color_noise = color_noise
        self.sonar_noise = sonar_noise
        self.distance_noise = distance_noise
        self.measurement_noise = measurement_noise
        self.steering_noise = steering_noise
        self.reset()

        # TODO: Disable logger printing when needed
        if self.print_logger:
            logger.propagate = True
        else:
            logger.propagate = False

        for i in xrange(self.N):
            for j in xrange(self.M):
                if self.map['board'][i][j] == MAP_GOAL:
                    self.goal = (i, j)

    def get_next_frame(self):
        """
            @returns next frame of simulation data

            @note the queue is thread-safe and it works like consumer-producer
            those frames should be consumed by rendering thread
        """
        # if len(self.sim_frames) == 0: return None

        return self.sim_frames.get()

    def get_next_frame_nowait(self):
        """
            @returns next frame of simulation data

            @note Only get an item if one is immediately available. Otherwise
            raise the Empty exception.
        """
        return self.sim_frames.get_nowait()

    def reset(self):
        """ Reset state of the KrakrobotSimulator """
        self.robot_path = []
        self.collisions = []
        self.results = None

        self.goal_achieved = False
        self.robot_timer = 0.0
        self.sim_frames = Queue(100000)
        self.finished = False
        self.terminate_flag = False

        self.logs = []

    def run(self):
        """ Runs simulations by quering the robot """
        self.reset()

        # Initialize robot object
        robot = Robot(self.speed, self.turning_speed, self.gps_delay, self.sonar_time, self.tick_move, self.tick_rotate)
        robot.set(self.init_position[0], self.init_position[1], self.init_position[2])
        robot.set_noise(new_s_noise=self.steering_noise,
                        new_d_noise=self.distance_noise,
                        new_m_noise=self.measurement_noise,
                        new_sonar_noise=self.sonar_noise,
                        new_c_noise=self.color_noise)


        # Initialize robot controller object given by contestant
        robot_controller = PythonTimedRobotController(self.robot_controller.clone())
        robot_controller.init(x=self.init_position[0],
                              y=self.init_position[1],
                              angle=self.init_position[2],
                              steering_noise=robot.steering_noise,
                              distance_noise=robot.distance_noise,
                              sonar_noise=robot.sonar_noise,
                              color_noise=robot.color_noise,
                              measurement_noise=robot.measurement_noise,
                              speed=robot.speed,
                              turning_speed=robot.turning_speed,
                              color_sensor_displacement=robot.color_sensor_displacement,
                              gps_delay=self.gps_delay,
                              execution_cpu_time_limit=self.execution_cpu_time_limit,
                              N=self.map['N'],
                              M=self.map['M'])


        maximum_timedelta = datetime.timedelta(seconds=self.execution_cpu_time_limit)

        self.robot_path.append((robot.x, robot.y))
        collision_counter = 0  # We have maximum collision allowed

        frame_time_left = self.simulation_dt
        frame_count = 0
        current_command = None
        iteration = 0
        beeps = []
        communicated_finished = False
        try:
            while not communicated_finished \
                    and not robot.time_elapsed >= self.simulation_time_limit \
                    and not self.terminate_flag:
                # logger.info(robot_controller.time_consumed)


                if maximum_timedelta <= robot_controller.time_consumed:
                    raise KrakrobotException("Robot has exceeded CPU time limit")

                if iteration % self.iteration_write_frequency == 0:
                    logger.info("Iteration {0}, produced {1} frames".format(iteration,
                                                                            frame_count))
                    logger.info("Elapsed {0}".format(robot.time_elapsed))
                    logger.info(current_command)

                iteration += 1
                # TODO: why this sleep is here?
                time.sleep(self.simulation_dt)

                if frame_time_left > self.frame_dt and not self.command_line:
                    ### Save frame <=> last command took long ###
                    if len(self.robot_path) == 0 or \
                                    robot.x != self.robot_path[-1][0] or robot.y != self.robot_path[-1][1]:
                        self.robot_path.append((robot.x, robot.y))
                    self.sim_frames.put(self._create_sim_data(robot, beeps))

                    frame_count += 1
                    frame_time_left -= self.frame_dt

                if current_command is not None:
                    ### Process current command ###

                    if current_command[0] == TURN:

                        robot = robot.turn(1) if current_command[1] > 0 else robot.turn(-1)
                        if current_command[1] > 1:
                            current_command = [current_command[0], current_command[1] - 1]
                        elif current_command[1] < 1:
                            current_command = [current_command[0], current_command[1] + 1]
                        else:
                            current_command = None

                        frame_time_left += self.tick_rotate / self.turning_speed


                    elif current_command[0] == MOVE:
                        robot_proposed = robot.move(1)

                        if not robot_proposed.check_collision(self.map['board']):
                            collision_counter += 1
                            self.collisions.append((robot_proposed.x, robot_proposed.y))
                            logger.error("Collision")
                            if collision_counter >= COLLISION_THRESHOLD:
                                raise KrakrobotException \
                                    ("The robot has been destroyed by wall. Sorry! We miss WALLE already.")
                        else:
                            robot = robot_proposed

                        ### Register movement, just do not move the robot

                        if current_command[1] > 1:
                            current_command = [current_command[0], current_command[1] - 1]
                        else:
                            current_command = None

                        frame_time_left += self.tick_move / self.speed
                    else:
                        raise KrakrobotException("Robot hasn't supplied any command")

                else:
                    ### Get current command ###

                    command = None
                    try:
                        command = list(robot_controller.act())
                    except Exception, e:
                        logger.error("Robot controller failed with exception " + str(e))
                        break

                    # logger.info("Received command "+str(command))
                    # logger.info("Robot timer "+str(robot.time_elapsed))
                    if not command or len(command) == 0:
                        raise KrakrobotException("No command passed, or zero length command passed")

                    if command[0] not in self.accepted_commands:
                        raise KrakrobotException("Not allowed command " + str(command[0]))

                    # Dispatch command
                    if command[0] == SENSE_GPS:
                        robot_controller.on_sense_gps(*robot.sense_gps())
                        frame_time_left += self.gps_delay
                    elif command[0] == WRITE_CONSOLE:
                        new_line = "{'frame': " + str(frame_count) + \
                                   ", 'time': " + str(robot.time_elapsed) + \
                                   '}:\n' + command[1]
                        self.logs.append(new_line)
                        if self.print_robot:
                            print new_line
                    elif command[0] == SENSE_SONAR:
                        w = robot.sense_sonar(self.map['board'])
                        robot_controller.on_sense_sonar(w)
                        frame_time_left += self.sonar_time
                    elif command[0] == SENSE_COLOR:
                        r, g, b = robot.sense_color(self.map)
                        robot_controller.on_sense_color(r, g, b)
                        frame_time_left += self.light_sensor_time
                    elif command[0] == TURN:
                        if len(command) <= 1 or len(command) > 2:
                            raise KrakrobotException("Incorrect command length")
                        current_command = command
                        current_command[1] = int(current_command[1])
                        # Turn robot
                        # robot = robot.turn(command[1])

                    elif command[0] == MOVE:
                        if len(command) <= 1 or len(command) > 2:
                            raise KrakrobotException("Incorrect command length")

                        if command[1] < 0:
                            raise KrakrobotException("Not allowed negative distance")
                        # Move robot
                        current_command = command
                        current_command[1] = int(current_command[1])
                    elif command[0] == BEEP:
                        beeps.append((robot.x, robot.y))
                    elif command[0] == FINISH:
                        logger.info("Communicated finishing")
                        communicated_finished = True
                    else:
                        raise KrakrobotException("Not received command from act(), or command was incorrect")

        except Exception, e:
            logger.error("Simulation failed with exception " + str(e) + " after " + str(robot.time_elapsed) + " time")
            return {
                    "sim_time": robot.time_elapsed,
                    "cpu_time": robot_controller.time_consumed.total_seconds() * 1000,
                    "error": str(traceback.format_exc()),
                    "beeps": beeps,
                    "map": self.map_meta
                    }

        logger.info("Simulation ended after " + str(robot.time_elapsed) + " seconds, communicated_finish=" + str(
            communicated_finished))

        self.sim_frames.put(self._create_sim_data(robot, beeps))
        while frame_time_left >= self.frame_dt and not self.command_line and not self.terminate_flag:
            ### Save frame <=> last command took long ###
            self.sim_frames.put(self._create_sim_data(robot, beeps))
            frame_time_left -= self.frame_dt

        # Simulation process finished
        self.finished = True
        logger.info("Exiting")
        self.results = None
        try:
            # Return simulation results
            map_to_save = dict(self.map)
            del map_to_save['color_bitmap']
            self.results = {"sim_time": robot.time_elapsed,
                    "map": map_to_save,
                    "beeps": beeps,
                    "cpu_time": robot_controller.time_consumed.total_seconds() * 1000,
                    "error": False
                    }
            return self.results

        except Exception, e:
            self.results = None
            logger.error("Failed constructing result " + str(e))
            return {"error": str(e)}

    def get_results(self):
        return self.results

    def get_logs(self):
        return self.logs

    def _create_sim_data(self, robot, beeps):
        """
            @returns Descriptor that is sufficient to visualize current frame
        """
        data = {}
        # data['GoalThreshold'] = self.goal_threshold
        data['Sparks'] = list(beeps)  # ommiting errors list(self.collisions)
        data['ActualPath'] = list(self.robot_path)
        # data['Grid'] = {"DrawGrid": True,
        #
        #     'CanvasMinima': (0, 0),
        #     'CanvasMaxima': (20, 20),
        #     'RangeMinima': (0, 0),
        #     'RangeMaxima': (5, 5)
        #                 }
        data['ActualPosition'] = [robot.x, robot.y]
        data['ActualOrientation'] = robot.orientation
        data['Map'] = self.map
        data['StartPos'] = self.init_position
        # data['GoalAchieved'] = self.goal_achieved
        return data

    def terminate(self):
        self.terminate_flag = True
        self.robot_controller.terminate()
