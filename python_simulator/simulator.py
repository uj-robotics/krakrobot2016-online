""" Simulator which runs the simulation and renders SVG frames """


from defines import *

from robot import Robot
from robot_controller import PythonTimedRobotController
from math import (
  pi, sqrt, hypot, sin, cos, tan, asin, acos, atan, atan2, radians, degrees,
  floor, ceil, exp
)

from utils import logger, load_map
from Queue import Queue
import time
import datetime

class KrakrobotSimulator(object):
    COLLISION_THRESHOLD = 50

    def __init__(self,  map, init_position = None, steering_noise=0.01, sonar_noise = 0.1, distance_noise=0.001,
                 measurement_noise=0.2, time_limit = 5000,
                 speed = 5.0,
                 turning_speed = 0.4*pi,
                 execution_cpu_time_limit = 10.0,
                 simulation_time_limit = 10.0,
                 simulation_dt = 0.001,
                 frame_dt = 0.1,
                 collision_threshold = 50
                 ):
        """
            Initialize KrakrobotSimulator object
            @param steering_noise - variance of steering in move
            @param distance_noise - variance of distance in move
            @param measurement_noise - variance of measurement (GPS??)
            @param map - map for the robot simulator representing the maze or file to map
            @param init_position - starting position of the Robot (can be moved to map class) [x,y,heading]

            @param speed - distance travelled by one move action (cannot be bigger than 0.5, or he could traverse the walls)
            @param simulation_time_limit - limit in ms for whole robot execution (also with init)
            @param collision_threshold - maximum number of collisions after which robot is destroyed

            @param frame_dt - save frame every dt


        """

        if type(map) is str:
            grid, metadata  = load_map(map)
            self.map_title = metadata["title"]
            self.grid = grid
        else:
            self.grid = map
            self.map_title = ""


        self.collision_threshold = collision_threshold

        if init_position is not None:
            self.init_position = tuple(init_position)
        else:
            for i in xrange(self.N):
                for j in xrange(self.M):
                    if self.grid[i][j] == MAP_START_POSITION:
                        self.init_position = (i,j,0)

        self.speed = speed
        self.turning_speed = turning_speed
        self.simulation_dt = simulation_dt
        self.frame_dt = frame_dt

        self.sonar_time = 0.01
        self.gps_time = 1.0
        self.light_sensor_time = 0.01

        self.tick_move = 0.01
        self.tick_rotate = 0.07

        self.simulation_time_limit = simulation_time_limit
        self.execution_cpu_time_limit = execution_cpu_time_limit

        self.goal_threshold = 0.5 # When to declare goal reach

        self.sonar_noise = sonar_noise
        self.distance_noise    = distance_noise
        self.measurement_noise = measurement_noise
        self.steering_noise   = steering_noise
        self.reset()

        self.time_limit = time_limit


        self.N = len(self.grid)
        self.M = len(self.grid[0])

        for i in xrange(self.N):
            for j in xrange(self.M):
                if self.grid[i][j] == MAP_GOAL:
                    self.goal = (i,j)





    def get_next_frame(self):
        """
            @returns next frame of simulation data

            @note the queue is thread-safe and it works like consumer-producer
            those frames should be consumed by rendering thread
        """
        #if len(self.sim_frames) == 0: return None

        return self.sim_frames.get()



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
        self.sim_frames = Queue(1000)
        self.finished = False



    def run(self, robot_controller_class):
        """ Runs simulations by quering the robot """
        self.reset()

        # Initialize robot object
        robot = Robot(self.speed, self.turning_speed, self.gps_time, self.sonar_time, self.tick_move, self.tick_rotate)
        robot.set(self.init_position[0], self.init_position[1], self.init_position[2])
        robot.set_noise(self.steering_noise,
                        self.distance_noise,
                        self.measurement_noise,
                        self.sonar_noise)

        # Initialize robot controller object given by contestant
        robot_controller = PythonTimedRobotController(robot_controller_class())
        robot_controller.init(self.init_position, robot.steering_noise
            ,robot.distance_noise, robot.measurement_noise, self.speed, self.turning_speed,
                              self.execution_cpu_time_limit
                              )


        maximum_timedelta = datetime.timedelta(seconds=self.execution_cpu_time_limit)

        self.robot_path.append((robot.x, robot.y))
        collision_counter = 0 # We have maximum collision allowed


        frame_time_left = self.simulation_dt
        frame_count = 0
        current_command = None
        try:
            while not self.check_goal(robot) and not robot.time_elapsed >= self.time_limit:
                #logger.info(robot_controller.time_consumed)

                time.sleep(self.simulation_dt)
                if frame_time_left > self.frame_dt:
                    ### Save frame <=> last command took long ###
                    if len(self.robot_path) == 0 or\
                    robot.x != self.robot_path[-1][0] or robot.y != self.robot_path[-1][1]:
                        self.robot_path.append((robot.x, robot.y))
                    self.sim_frames.put(self._create_sim_data(robot))



                    frame_time_left -= self.frame_dt

                elif current_command is not None:
                    ### Process current command ###

                    if current_command[0] == TURN:

                        robot = robot.turn(1) if current_command[1] > 0 else robot.turn(-1)
                        if current_command[1] > 1: current_command = [current_command[0], current_command[1] - 1]
                        elif current_command[1] < 1: current_command = [current_command[0], current_command[1] + 1]
                        else: current_command = None

                        frame_time_left += self.tick_rotate / self.turning_speed


                    elif current_command[0] == MOVE:
                        robot_proposed = robot.move(1)



                        if not robot_proposed.check_collision(self.grid):
                            collision_counter += 1
                            self.collisions.append((robot_proposed.x, robot_proposed.y))
                            logger.error("##Collision##")
                            if collision_counter >= KrakrobotSimulator.COLLISION_THRESHOLD:
                                raise KrakrobotException\
                                        ("The robot has been destroyed by wall. Sorry! We miss WALLE already..")
                        else:
                            robot = robot_proposed

                            if current_command[1] > 1: current_command = [current_command[0], current_command[1] - 1]
                            else: current_command = None
                            frame_time_left += self.tick_move / self.speed

                else:
                    ### Get current command ###

                    command = None
                    try:
                        command = list(robot_controller.act())
                    except Exception, e:
                        logger.error("Robot controller failed with exception " + str(e))
                        break
                    #logger.info("Received command "+str(command))
                    #logger.info("Robot timer "+str(robot.time_elapsed))
                    if not command or len(command) == 0:
                        raise KrakrobotException("No command passed, or zero length command passed")

                    # Dispatch command
                    if command[0] == SENSE_GPS:
                        robot_controller.on_sense_gps(robot.sense_gps())
                        frame_time_left += self.gps_time
                    elif command[0] == SENSE_SONAR:
                        w = robot.sense_sonar(self.grid)
                        robot_controller.on_sense_sonar(w)
                        frame_time_left += self.sonar_time
                    elif command[0] == SENSE_FIELD:
                        w = robot.sense_field(self.grid)
                        if type(w) is not list:
                            robot_controller.on_sense_field(w, 0)
                        else:
                            robot_controller.on_sense_field(w[0], w[1])

                        frame_time_left += self.light_sensor_time
                    elif command[0] == TURN:
                        if len(command) <= 1 or len(command) > 2:
                            raise KrakrobotException("Wrong command length")
                        current_command = command
                        # Turn robot
                        #robot = robot.turn(command[1])

                    elif command[0] == MOVE:
                        if len(command) <= 1 or len(command) > 2:
                            raise KrakrobotException("Wrong command length")

                        if command[1] < 0:
                            raise KrakrobotException("Not allowed negative distance")
                        # Move robot

                        current_command = command

                    if maximum_timedelta <= robot_controller.time_consumed:
                        raise KrakrobotException("Robot has exceeded CPU time limit")


        except Exception, e:
            logger.error("Simulation failed with exception " +str(e)+ " after " +str(robot.time_elapsed)+ " time")


        while frame_time_left > self.frame_dt:
            ### Save frame <=> last command took long ###
            self.frames.append(self.create_visualisation_descriptor(robot))
            self.frames_count += 1
            frame_time_left -= self.frame_dt

        # Simulation process finished
        self.finished = True
        logger.info("Simulation ended after "+str(robot.time_elapsed)+ " seconds with goal reached = "+str(self.check_goal(robot)))
        self.goal_achieved = self.check_goal(robot)

        # Return simulation results
        return {"time_elapsed": robot.time_elapsed, "goal_achieved": self.check_goal(robot),
                "time_consumed_robot": robot_controller.time_consumed
                }


    def _create_sim_data(self, robot):
        """
            @returns Descriptor that is sufficient to visualize current frame
        """
        data = {}
        data['GoalThreshold'] = self.goal_threshold
        data['Sparks'] = []# ommiting errors list(self.collisions)
        data['ActualPath'] = list(self.robot_path)
        data['ActualPosition'] = [robot.x, robot.y]
        data['ActualOrientation'] = robot.orientation
        data['Map'] = self.grid
        data['StartPos'] = self.init_position
        data['GoalPos'] = self.goal
        data['GoalAchieved'] = self.goal_achieved
        return data


