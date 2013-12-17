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

# TODO: add logger

from math import (
  pi, sqrt, hypot, sin, cos, tan, asin, acos, atan, atan2, radians, degrees,
  floor, ceil, exp
)
import random
from visualisation import RenderToSVG, Save
from utils import logger

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
        """

        for i in range(len(grid)):
            for j in range(len(grid[0])):
                if grid[i][j] == 1:
                    dist = sqrt((self.x - float(i)) ** 2 +
                                (self.y - float(j)) ** 2)
                    if dist < 0.5:
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
        res.length            = self.length
        res.steering_noise    = self.steering_noise
        res.distance_noise    = self.distance_noise
        res.measurement_noise = self.measurement_noise
        res.num_collisions    = self.num_collisions
        res.num_steps         = self.num_steps + 1

        # apply noise
        steering2 = random.gauss(steering, self.steering_noise)
        distance2 = random.gauss(distance, self.distance_noise)


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
    def sense(self):
        """ Returns estimation for position (GPS signal) """
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



class RobotController(object):
    """ You have to implement this class """
    def init(self, starting_position, steering_noise, distance_noise, measurement_noise):
        """ @param starting_position - (x,y) tuple representing current_position """
        raise NotImplementedError()
    def act(self):
        """ It should return move command """
        raise NotImplementedError()


class ForwardTurningRobotController(RobotController):
    """ Exemplary robot controller """
    def init(self, starting_position, steering_noise, distance_noise, measurement_noise):
        pass

    def act(self):
        return KrakrobotSimulator.MOVE, 0.2

class KrakrobotException(Exception):
    pass

class KrakrobotSimulator(object):
    MOVE = "move" # (move, steer) -> OK
    SENSE_RADAR = "sense_radar" # (sense_radar) -> ([alpha,dist],[alpha,dist]....)
    SENSE_GPS = "sense_gps" # (sense_gps) -> (x,y)
    SENSE_LIGHT_SENSOR = "sense_light_sensor"  # (sense_light_sensor) -> (field_type)   #TODO: add or erase it ? everytime robot knows the field?




    def __init__(self,  grid, init_position, steering_noise=0.1, distance_noise=0.03,
                 measurement_noise=0.3, limit_actions = 100, speed = 0.4, goal=None
                 ):
        """ 
            Initialize KrakrobotSimulator object 
            @param steering_noise - variance of steering in move 
            @param distance_noise - variance of distance in move
            @param measurement_noise - variance of measurement (GPS??) 
            @param grid - 0/1 matrix representing the maze
            @param init_position - starting position of the Robot (can be moved to map class)
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

        collision_counter = 0 # We have maximum collision allowed
        try:
            while not self.check_goal(robot) and not robot.num_steps >= self.limit_actions:
                command = None
                try:
                    command = list(robot_controller.act())
                except Exception, e:
                    print "Robot controller failed with exception ",e
                    break



                if command[0] == KrakrobotSimulator.MOVE:
                    # Parse move command
                    if len(command) <= 1 or len(command) > 3:
                        raise KrakrobotException("Wrong command length")
                    if len(command) == 2:
                        command.append(self.speed)
                    if command[2] > self.speed:
                        raise KrakrobotException("Distance exceedes the maximum distance allowed")

                    # Move robot
                    robot = robot.move(command[1], self.speed)
                    self.robot_path.append((robot.x, robot.y))

                if not robot.check_collision(self.grid):
                    collision_counter += 1
                    self.collisions.append((robot.x, robot.y))
                    if collision_counter >= 2:
                        raise KrakrobotException\
                                ("The robot has been destroyed by electric wall. Sorry! We miss WALLE already..")


                else:
                    collision_counter = 0

        except Exception, e:
            print "Simulation failed with exception ", e, " after ",robot.num_steps, " steps"
    
        logger.info("Simulation ended after "+str(robot.num_steps)+ " steps with goal reached = "+str(self.check_goal(robot)))




#   grid = [[0, 1, 0, 0, 0, 0, 0, 0, 0 , 0 ,0 ,0],
#           [0, 1, 0, 1, 1, 0, 0, 0, 0 , 0 ,0, 0],
#           [0, 1, 0, 1, 0, 0, 0, 0 ,0,0,0,0],
#           [0, 0, 0, 1, 0, 1, 0 ,0, 0,0,0,0],
#           [0, 1, 0, 1, 0, 0,0,0,0,0,0,0]]
# 



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



def main():

    OutputFileName = 'output.svg'

    print 'Driving a car through a maze...'
    grid = [[0, 1, 0, 0, 0, 0],
            [0, 1, 0, 1, 1, 0],
            [0, 1, 0, 1, 0, 0],
            [0, 0, 0, 1, 0, 1],
            [0, 1, 0, 1, 0, 0]]
    simulator = KrakrobotSimulator(grid, (0, 0))
    forward_controller = ForwardTurningRobotController
    simulator.run(forward_controller)


    Data = simulator.create_visualisation_descriptor()
    fill_visualisation_descriptor(Data)

    print 'Rendering SVG...'
    SVG = RenderToSVG(Data)
    print 'Done.'

    print 'Saving SVG to "' + OutputFileName + '"...'
    Save(SVG.encode('utf_8'), OutputFileName)
    print 'Done.'




if __name__ == '__main__':
    main()
