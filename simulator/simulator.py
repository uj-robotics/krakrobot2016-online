# -*- coding: utf-8 -*-

"""
    Krakrobot Python Simulator

    Simulator which runs the simulation and renders SVG frames.
"""

# TODO: restart fix

from Queue import Queue
import time
import datetime
from math import (
    pi
)

import traceback
from misc.map_utils import logger, load_map
from misc.defines import *
from robot import Robot
from robot_controller import PythonTimedRobotController

__author__ = u'Stanisław Jastrzębski'
__copyright__ = 'Copyright 2013-2014,\
                    Jagiellonian University Robotics Interest Group'

__license__ = 'MIT'
__version__ = '0.0.1a'
__maintainer__ = u'Stanisław Jastrzębski'
__email__ = 'grimghil@gmail.com'


class KrakrobotSimulator(object):
    COLLISION_THRESHOLD = 50

    def __init__(self, map, robot_controller, init_position=None,
                 steering_noise=0.01, sonar_noise=0.1, distance_noise=0.001,
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
                 visualisation=True,
                 print_robot=True,
                 print_logger=False,
                 ):
        """
            Initialize KrakrobotSimulator object

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

        if type(map) is str:
            grid, bitmap, metadata = load_map(map)
            self.map_title = metadata["title"]
            self.grid = grid
            self.bitmap = bitmap
            for row in grid:
                logger.info(row)
        else:
            self.grid = map
            self.map_title = ""

        self.N = len(self.grid)
        self.M = len(self.grid[0])

        self.iteration_write_frequency = iteration_write_frequency

        self.collision_threshold = collision_threshold

        if init_position is not None:
            self.init_position = tuple(init_position)
        else:
            for i in xrange(self.N):
                for j in xrange(self.M):
                    if self.grid[i][j] == MAP_START_POSITION:
                        self.init_position = (i, j, 0)

        self.speed = speed
        self.turning_speed = turning_speed
        self.simulation_dt = simulation_dt
        self.frame_dt = frame_dt
        self.robot_controller = robot_controller
        self.print_robot = print_robot
        self.print_logger = print_logger

        self.visualisation = visualisation

        self.sonar_time = SONAR_TIME
        self.gps_delay = gps_delay
        self.light_sensor_time = FIELD_TIME

        self.tick_move = TICK_MOVE
        self.tick_rotate = TICK_ROTATE

        self.simulation_time_limit = simulation_time_limit
        self.execution_cpu_time_limit = execution_cpu_time_limit

        self.goal_threshold = 0.5  # When to declare goal reach

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
                if self.grid[i][j] == MAP_GOAL:
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
        robot.set_noise(self.steering_noise,
                        self.distance_noise,
                        self.measurement_noise,
                        self.sonar_noise)


        # Initialize robot controller object given by contestant
        robot_controller = PythonTimedRobotController(self.robot_controller.clone())
        robot_controller.init(self.init_position[0], self.init_position[1], self.init_position[2],
                              robot.steering_noise
                              , robot.distance_noise, robot.sonar_noise, robot.measurement_noise, self.speed,
                              self.turning_speed, self.gps_delay,
                              self.execution_cpu_time_limit
                              )

        maximum_timedelta = datetime.timedelta(seconds=self.execution_cpu_time_limit)

        self.robot_path.append((robot.x, robot.y))
        collision_counter = 0  # We have maximum collision allowed

        frame_time_left = self.simulation_dt
        frame_count = 0
        current_command = None
        iteration = 0
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

                time.sleep(self.simulation_dt)
                if frame_time_left > self.frame_dt and self.visualisation:
                    ### Save frame <=> last command took long ###
                    if len(self.robot_path) == 0 or \
                                    robot.x != self.robot_path[-1][0] or robot.y != self.robot_path[-1][1]:
                        self.robot_path.append((robot.x, robot.y))
                    self.sim_frames.put(self._create_sim_data(robot))

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

                        if not robot_proposed.check_collision(self.grid):
                            collision_counter += 1
                            self.collisions.append((robot_proposed.x, robot_proposed.y))
                            logger.error("##Collision##")
                            if collision_counter >= KrakrobotSimulator.COLLISION_THRESHOLD:
                                raise KrakrobotException \
                                    ("The robot has been destroyed by wall. Sorry! We miss WALLE already..")
                        else:
                            robot = robot_proposed

                        ### Register movement, just do not move the robot

                        if current_command[1] > 1:
                            current_command = [current_command[0], current_command[1] - 1]
                        else:
                            current_command = None
                        frame_time_left += self.tick_move / self.speed

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
                        w = robot.sense_sonar(self.grid)
                        robot_controller.on_sense_sonar(w)
                        frame_time_left += self.sonar_time
                    elif command[0] == SENSE_COLOR:
                        r, g, b = robot.sense_color(self.grid, self.bitmap)
                        robot_controller.on_sense_color(r, g, b)
                        frame_time_left += self.light_sensor_time
                    elif command[0] == TURN:
                        if len(command) <= 1 or len(command) > 2:
                            raise KrakrobotException("Wrong command length")
                        current_command = command
                        current_command[1] = int(current_command[1])
                        # Turn robot
                        # robot = robot.turn(command[1])

                    elif command[0] == MOVE:
                        if len(command) <= 1 or len(command) > 2:
                            raise KrakrobotException("Wrong command length")

                        if command[1] < 0:
                            raise KrakrobotException("Not allowed negative distance")
                        # Move robot
                        current_command = command
                        current_command[1] = int(current_command[1])
                    elif command[0] == BEEP:
                        continue # TODO: add registering
                    elif command[0] == FINISH:
                        logger.info("Communicated finishing")
                        communicated_finished = True

                    else:
                        raise KrakrobotException("Not received command from act(), or command was incorrect :(")



        except Exception, e:
            logger.error("Simulation failed with exception " + str(e) + " after " + str(robot.time_elapsed) + " time")
            return {"time_elapsed": robot.time_elapsed, "goal_achieved": False,
                    "time_consumed_robot": robot_controller.time_consumed.total_seconds() * 1000,
                    "error": str(traceback.format_exc())
                    }

        logger.info("Simulation ended after " + str(robot.time_elapsed) + " seconds with goal reached = " + str(
            communicated_finished))

        self.sim_frames.put(self._create_sim_data(robot))
        while frame_time_left >= self.frame_dt and self.visualisation and not self.terminate_flag:
            ### Save frame <=> last command took long ###
            self.sim_frames.put(self._create_sim_data(robot))
            frame_time_left -= self.frame_dt

        # Simulation process finished
        self.finished = True
        logger.info("Exiting")

        try:
            # Return simulation results
            return {"time_elapsed": robot.time_elapsed,
                    # TODO: fix - add beep information
                    # "goal_achieved": communicated_finished and self.check_goal(robot),
                    "time_consumed_robot": robot_controller.time_consumed.total_seconds() * 1000,
                    "error": False
                    }

        except Exception, e:
            logger.error("Failed constructing result " + str(e))
            return {"error": str(e)}

    def get_logs(self):
        return self.logs

    def _create_sim_data(self, robot):
        """
            @returns Descriptor that is sufficient to visualize current frame
        """
        data = {}
        # data['GoalThreshold'] = self.goal_threshold
        data['Sparks'] = []  # ommiting errors list(self.collisions)
        data['ActualPath'] = list(self.robot_path)
        data['ActualPosition'] = [robot.x, robot.y]
        data['ActualOrientation'] = robot.orientation
        data['Map'] = self.grid
        data['StartPos'] = self.init_position
        # data['GoalPos'] = self.goal
        # data['GoalAchieved'] = self.goal_achieved
        return data

    def terminate(self):
        self.terminate_flag = True
        self.robot_controller.terminate()
