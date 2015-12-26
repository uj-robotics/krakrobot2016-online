from math import (
    pi, sqrt, sin, cos
)
from copy import deepcopy

import numpy as np

from map import get_color
from misc.defines import *


class Robot:
    """ The main class representing robot that can sense and move """

    def __init__(self, speed, turning_speed, gps_time, sonar_time, tick_move, tick_rotate,
                 color_sensor_displacement=SQUARE_SIDE/3.0):
        """
        Initialize robot
        """
        self.speed = speed
        self.rng = np.random.RandomState(777)
        self.tick_move = tick_move
        self.tick_rotate = tick_rotate
        self.color_sensor_displacement = color_sensor_displacement
        self.turning_speed = turning_speed
        self.x = 0.0
        self.y = 0.0
        self.orientation = 0.0
        self.steering_noise = 0.0
        self.distance_noise = 0.0
        self.sonar_noise = 0.0
        self.color_noise = 0.0
        self.measurement_noise = 0.0
        self.time_elapsed = 0.0
        self.gps_time = gps_time
        self.sonar_time = sonar_time

    def set(self, new_x, new_y, new_orientation):
        """
        Set robot position
        :note Cannot be called by contestant
        """

        self.x = float(new_x)
        self.y = float(new_y)
        self.orientation = float(new_orientation) % (2.0 * pi)

    def set_noise(self, new_s_noise, new_d_noise, new_m_noise, new_sonar_noise, new_c_noise):
        """
        Set noise parameters
        """
        self.color_noise = float(new_c_noise)
        self.steering_noise = float(new_s_noise)
        self.distance_noise = float(new_d_noise)
        self.measurement_noise = float(new_m_noise)
        self.sonar_noise = float(new_sonar_noise)

    def check_collision(self, grid):
        """
        Checks for collisions with some slack
        :note Cannot be called by contestant
        :returns True if no collisions
        """

        x_disc, y_disc = int(self.x + 0.5), int(self.y + 0.5)

        dist_x_border = min(abs(self.x - x_disc), abs(self.x - (x_disc + 1)))
        dist_y_border = min(abs(self.y - y_disc), abs(self.y - (y_disc + 1)))

        if grid[x_disc][y_disc] == 1:
            return False

        return True

    def move(self, x):
        """
        Move the robot forward by x **Ticks**
        """

        if (abs(x) > 1): raise ("Illegal move")
        res = deepcopy(self)

        distance = max(0.0, self.rng.normal(int(x) * self.tick_move, self.distance_noise))

        res.x += distance * cos(res.orientation)
        res.y += distance * sin(res.orientation)
        res.time_elapsed += abs(distance / self.speed)  # speed is 1.0/time_unit

        return res

    def turn(self, x):
        """
        Turn robot by x **Ticks**
        """

        if abs(x) > 1:
            raise RuntimeError("Illegal turn")

        res = deepcopy(self)

        turn = self.rng.normal(int(x) * self.tick_rotate, self.steering_noise)
        res.orientation = (res.orientation + turn) % (2 * pi)
        res.time_elapsed += abs(turn / self.turning_speed)  # speed is pi/time_unit
        return res

    def sense_color(self, map):
        """
        Returns color encoded as 3 integers from 0 to 255.
        """
        # TODO: uncomment
        dcx = self.color_sensor_displacement * cos(self.orientation)
        dcy = self.color_sensor_displacement * sin(self.orientation)

        raw_color = get_color(map, self.x + dcx,
                         self.y + dcy)

        random_vector = self.rng.normal(0, 1.0, size=(3,))
        random_vector /= np.linalg.norm(random_vector)
        random_vector *= self.color_noise

        return np.clip((raw_color + random_vector), 0, 255).astype(np.int)


    def sense_gps(self):
        """ Returns estimation for position (GPS signal) """
        self.time_elapsed += self.gps_time
        ret = [self.rng.normal(self.x, self.measurement_noise),
               self.rng.normal(self.y, self.measurement_noise)]
        return ret

    def sense_sonar(self, grid):
        """
        Returns distance to wall using 128bit precision floats
        """
        tolerance_a = np.float64(1e-13)
        max_a = np.float64(1e10)
        found = False

        def is_hit(x, y):
            tolerance_xy = np.float64(1e-4)  # will check nearby
            exact_hit = grid[int(x)][int(y)] == 1
            hit_right = int(x) < (len(grid) - 1) and grid[int(x) + 1][int(y)] == 1 and (x - int(x)) > (
                SQUARE_SIDE - tolerance_xy)
            hit_left = int(x) > 0 and grid[int(x) - 1][int(y)] == 1 and (x - int(x)) < tolerance_xy
            hit_top = int(y) < (len(grid[0]) - 1) and grid[int(x)][int(y) + 1] == 1 and (y - int(y)) > (
                SQUARE_SIDE - tolerance_xy)
            hit_bottom = int(y) > 0 and grid[int(x)][int(y) - 1] == 1 and (y - int(y)) < tolerance_xy
            return exact_hit or hit_right or hit_left or hit_top or hit_bottom

        x_min_col, y_min_col = [np.float64(0), np.float64(0), np.float64(1e100)], [np.float64(0), np.float64(0),
                                                                                   np.float64(1e100)]

        x, y = np.float64(self.x + SQUARE_SIDE / 2.0), np.float64((self.y + SQUARE_SIDE / 2.0))
        # logger.info(("robot:",x," ",y," ",self.orientation))
        x_disc, y_disc = int(x), int(y)

        orient_x = np.float64(np.cos(np.float64(self.orientation)))
        orient_y = np.float64(np.sin(np.float64(self.orientation)))
        a = np.float64(np.tan(np.float64(self.orientation)))
        b = np.float64(y - a * x)

        for i in xrange(0, len(grid)):

            if a > max_a:
                cross_x, cross_y = np.float64(x), np.float64(float(i) + 1e-10)
            else:
                cross_x, cross_y = np.float64(float(i) + 1e-10), np.float64(a * (float(i) + 1e-10) + b)

            if cross_x < 0.0 or cross_x > len(grid) * SQUARE_SIDE or cross_y < 0.0 or cross_y > len(
                    grid[0]) * SQUARE_SIDE:
                continue

            diff_x, diff_y = np.float64(cross_x - x), np.float64(cross_y - y)

            if orient_x * diff_x + orient_y * diff_y > 0:
                # logger.info((cross_x, cross_y))
                if is_hit(cross_x, cross_y) and (diff_x ** 2 + diff_y ** 2) < x_min_col[2]:
                    x_min_col = [cross_x, cross_y, (diff_x ** 2 + diff_y ** 2)]
                    found = True

        # Find collisions with y walls
        for i in xrange(0, len(grid[0])):
            # Check if line is almost parallel to the axis
            if abs(a) > tolerance_a:

                cross_x, cross_y = np.float64((float(i) + np.float64(1e-10) - b) / a), \
                                   np.float64(float(i) + 1e-10)
            else:
                cross_x, cross_y = np.float64(float(i) + 1e-10), np.float64(y)

            if cross_x < 0.0 or cross_x > len(grid) * SQUARE_SIDE or cross_y < 0.0 or cross_y > len(
                    grid[0]) * SQUARE_SIDE:
                continue

            diff_x, diff_y = np.float64(cross_x - x), np.float64(cross_y - y)
            if orient_x * diff_x + orient_y * diff_y > 0:
                if is_hit(cross_x, cross_y) and (diff_x ** 2 + diff_y ** 2) < y_min_col[2]:
                    y_min_col = [cross_x, cross_y, (diff_x ** 2 + diff_y ** 2)]
                    found = True

        if not found:
            raise KrakrobotException(
                "Something went wrong with sonar - not found wall! Note: boundary should be walled")

        self.time_elapsed += self.sonar_time
        return self.rng.normal(float(sqrt(min(x_min_col[2], y_min_col[2]))), self.sonar_noise)

    def __repr__(self):
        # return '[x=%.5f y=%.5f orient=%.5f]'  % (self.x, self.y, self.orientation)
        return '[%.5f, %.5f]' % (self.x, self.y)
