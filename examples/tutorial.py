#Note : work in progress

from defines import *
from robot_controller import RobotController
import random
from math import pi

from collections import Counter


class Turner(RobotController):
    """ Exemplary robot controller choosing to go where it wasn't before :) """



    STATE_FINDING_POSITION = 0 # Robot is localizing itself on GPS to update map_visited
    STATE_GOING_TO_NEW_POSITION = 1 # Robot is moving itself to the new position
    STATE_FOUND_GOAL = 2 # Robot found goal, yell finish!
    STATE_SCANNING = 3 # Robot doesnt know about fields nearby if there are walls or open, scanning

    def get_discrete_position(self):
        return round(self.x+0.5) , roud(self.y+0.5)

    def init(self, starting_position, steering_noise, distance_noise, sonar_noise,
             measurement_noise, speed, turning_speed, gps_delay, execution_cpu_time_limit):
        self.speed = speed
        self.turn_speed = turning_speed
        self.command_queue = []
        self.last_distance = 0.0

        self.state = Turner.STATE_FINDING_POSITION
        self.state_helper = 0

        self.x = starting_position[0]
        self.y = starting_position[1]
        self.angle = 0

        self.map_visited = {}
        self.map_visited[self.get_discrete_position()] = 1 # <=> Open and visited once

    def act(self):
        # Add state change command
        if len(self.command_queue) != 0 and self.command_queue[0][0] == "STATE_CHANGE":
            self.state = self.command_queue[0][1]
            self.command_queue.pop()


        # We need to plan actions if we are out of actions in out command_queue
        if len(self.command_queue) == 0:

            # Find next move
            if self.state == Turner.STATE_FINDING_POSITION:
                # Scanning for distance
                if self.state_helper == 0:
                    self.command_queue.append([SENSE_SONAR])
                elif self.state_helper == 1:
                    self.state_helper = 0
            # Finish
            elif self.state == Turner.STATE_FOUND_GOAL:
                self.command_queue.append([FINISH])

        return self.command_queue.pop(0)

    def on_sense_gps(self, x, y):
        self.x = x
        self.y = y

    def on_sense_sonar(self, distance):
        self.last_distance = distance

    def on_sense_field(self, field_type, field_parameter):
        if field_type == MAP_GOAL:
            self.state = Turner.STATE_FOUND_GOAL

