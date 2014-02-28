from defines import *

from math import (
  pi, sqrt, hypot, sin, cos, tan, asin, acos, atan, atan2, radians, degrees,
  floor, ceil, exp
)
import numpy as np
import random
from utils import *
from copy import deepcopy

class Robot:
    """ The main class representing robot that can sense and move """

    def __init__(self,  speed, speed_turn, gps_time, sonar_time, tick_move, tick_rotate):
        """
        Initialize robot
        """
        self.speed = speed

        self.tick_move = tick_move
        self.tick_rotate = tick_rotate

        self.speed_turn = speed_turn
        self.x = 0.0
        self.y = 0.0
        self.orientation = 0.0
        self.steering_noise    = 0.0
        self.distance_noise    = 0.0
        self.sonar_noise = 0.0
        self.measurement_noise = 0.0
        self.time_elapsed = 0.0
        self.gps_time = gps_time
        self.sonar_time = sonar_time

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
    def set_noise(self, new_s_noise, new_d_noise, new_m_noise, new_sonar_noise):
        """
        Set noise parameter
        @note: Cannot be called by contestant
        """
        # makes it possible to change the noise parameters
        # this is often useful in particle filters
        self.steering_noise     = float(new_s_noise)
        self.distance_noise    = float(new_d_noise)
        self.measurement_noise = float(new_m_noise)
        self.sonar_noise = float(new_sonar_noise)


    def check_collision(self, grid):
        """
        Checks for collisions with some slack
        @note: Cannot be called by contestant
        @returns: True if no collisions
        """

        x_disc, y_disc = int(self.x +0.5), int(self.y + 0.5)

        dist_x_border = min(abs(self.x - x_disc), abs(self.x - (x_disc+1)))
        dist_y_border = min(abs(self.y - y_disc), abs(self.y - (y_disc+1)))
        dist_border = min(dist_x_border, dist_y_border)

        if grid[x_disc][y_disc] == 1:
            return False

        #
        ## Box based (sharp edges):
        ## TODO: add slack here !!
        #for i in xrange(len(grid)):
        #    for j in xrange(len(grid[0])):
        #        # not sure about chained operators..
        #        if grid[i][j] == 1 \
        #            and (float(i+1) - SQUARE_SIDE/2.0) > self.x > (float(i) - SQUARE_SIDE/2.0)\
        #            and (float(j+1) - SQUARE_SIDE/2.0) > self.y > (float(j) - SQUARE_SIDE/2.0):
        #            return False

        return True



    def move(self,  x):
        """
        Move the robot forward by x **Ticks**
        """

        if(abs(x) > 1): raise("Illegal move")

        # make a new copy (TODO: use deepcopy)
        res = deepcopy(self)

        distance = max(0.0,random.gauss(int(x)*self.tick_move, self.distance_noise))


        res.x += distance * cos(res.orientation)
        res.y += distance * sin(res.orientation)
        res.time_elapsed += distance/self.speed # speed is 1.0/time_unit

        return res

    def turn(self,  x):
        """
        Turn robot by x **Ticks**
        """

        if(abs(x) > 1): raise("Illegal turn")

        # make a new copy (TODO: use deepcopy)
        res = deepcopy(self)

        turn = random.gauss(int(x)*self.tick_rotate, self.steering_noise)
        res.orientation = (res.orientation+turn)%(2*pi)
        res.time_elapsed += turn/self.speed_turn # speed is pi/time_unit
        return res


    def sense_field(self, grid):
        disc_x, disc_y = int(self.x + SQUARE_SIDE/2.0), int(self.y + SQUARE_SIDE/2.0)
        return grid[disc_x][disc_y]

    def sense_gps(self):
        """ Returns estimation for position (GPS signal) """
        self.time_elapsed += self.gps_time
        ret =  [random.gauss(self.x, self.measurement_noise),
                random.gauss(self.y, self.measurement_noise)]
        return ret


    def sense_sonar(self, grid):
        """
        Returns distance to wall using 128bit precision floats
        """
        tolerance_a = np.float64(1e-13)
        max_a = np.float64(1e10)
        found = False

        def is_hit(x, y):
            tolerance_xy = np.float64(1e-4) # will check nearby
            exact_hit = grid[int(x)][int(y)] == 1
            hit_right = int(x) < (len(grid)-1) and grid[int(x)+1][int(y)] == 1 and (x - int(x)) > (SQUARE_SIDE-tolerance_xy)
            hit_left = int(x) > 0 and grid[int(x)-1][int(y)] == 1 and (x - int(x)) < tolerance_xy
            hit_top = int(y) < (len(grid[0])-1) and grid[int(x)][int(y)+1] == 1 and (y - int(y)) > (SQUARE_SIDE-tolerance_xy)
            hit_bottom = int(y) > 0 and grid[int(x)][int(y)-1] == 1 and (y - int(y)) < tolerance_xy
            return exact_hit or hit_right or hit_left or hit_top or hit_bottom


        x_min_col, y_min_col = [np.float64(0), np.float64(0), np.float64(1e100)], [np.float64(0), np.float64(0),
                                                                                      np.float64(1e100)]

        x, y = np.float64(self.x + SQUARE_SIDE/2.0), np.float64((self.y + SQUARE_SIDE/2.0))
        #logger.info(("robot:",x," ",y," ",self.orientation))
        x_disc, y_disc = int(x), int(y)

        orient_x = np.float64(np.cos(np.float64(self.orientation)))
        orient_y = np.float64(np.sin(np.float64(self.orientation)))
        a = np.float64(np.tan(np.float64(self.orientation)))
        b = np.float64(y - a*x)

        for i in xrange(0, len(grid)):

            if a > max_a:
                cross_x, cross_y = np.float64(x), np.float64(float(i)+1e-10)
            else:
                cross_x, cross_y = np.float64(float(i)+1e-10), np.float64(a*(float(i)+1e-10) + b)

            if cross_x < 0.0 or cross_x > len(grid)*SQUARE_SIDE or cross_y < 0.0 or cross_y > len(grid[0])*SQUARE_SIDE:
                continue

            diff_x, diff_y = np.float64(cross_x - x), np.float64(cross_y-y)

            if orient_x*diff_x + orient_y*diff_y > 0:
                #logger.info((cross_x, cross_y))
                if is_hit(cross_x, cross_y) and (diff_x**2 + diff_y**2) < x_min_col[2]:
                    x_min_col = [cross_x, cross_y, (diff_x**2 + diff_y**2)]
                    found = True

        # Find collisions with y walls
        for i in xrange(0, len(grid[0])):
            # Check if line is almost parallel to the axis
            if abs(a) > tolerance_a:

                cross_x, cross_y = np.float64((float(i)+np.float64(1e-10) - b)/a), \
                                   np.float64(float(i)+1e-10)
            else:
                cross_x, cross_y = np.float64(float(i)+1e-10),np.float64(y)


            if cross_x < 0.0 or cross_x > len(grid)*SQUARE_SIDE or cross_y < 0.0 or cross_y > len(grid[0])*SQUARE_SIDE:
                continue


            diff_x, diff_y = np.float64(cross_x - x), np.float64(cross_y - y)
            if orient_x*diff_x + orient_y*diff_y > 0:
                if is_hit(cross_x, cross_y) and (diff_x**2 + diff_y**2) < y_min_col[2]:
                    y_min_col = [cross_x, cross_y, (diff_x**2 + diff_y**2)]
                    found = True

        if not found:
            raise KrakrobotException("Something went wrong with sonar - not found wall! Note: boundary should be walled")


        self.time_elapsed += self.sonar_time
        return random.gauss(float(sqrt(min(x_min_col[2], y_min_col[2]))), self.sonar_noise)



    def __repr__(self):
        # return '[x=%.5f y=%.5f orient=%.5f]'  % (self.x, self.y, self.orientation)
        return '[%.5f, %.5f]'  % (self.x, self.y)
