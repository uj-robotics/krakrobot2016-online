from defines import *
from utils import *
import random
class RobotController(object):
    """ You have to implement this class """
    def init(self, starting_position, steering_noise, distance_noise, speed, turning_speed,
             maximum_turn):
        """ @param starting_position - (x,y) tuple representing current_position """
        raise NotImplementedError()

    def act(self):
        """ Return next action """
        raise NotImplementedError()

    def on_sense_sonar(self, dist):
        """ React to sensory data """
        raise NotImplementedError()

    def on_sense_field(self, file_type, file_parameter):
        """ React to sensory data """
        raise NotImplementedError()

    def on_sense_gps(self, x, y):
        """ React to sensory data """
        raise NotImplementedError()

class ForwardTurningRobotController(RobotController):
    """ Exemplary robot controller """
    def init(self, starting_position, steering_noise, distance_noise, measurement_noise, speed, turning_speed):
        self.speed = speed

    def act(self):
        return MOVE, 0.0, self.speed


    def on_sense_sonar(self, dist):
        pass

    def on_sense_field(self, file_type, file_parameter):
        pass

    def on_sense_gps(self, x, y):
        pass

class OmitCollisions(RobotController):
    """ Exemplary robot controller omitting collisions """
    STATE_FORWARD = 0
    STATE_LOOK_FOR_SPACE = 1

    def init(self, starting_position, steering_noise, distance_noise, measurement_noise, speed, turning_speed):
        self.phase = OmitCollisions.STATE_LOOK_FOR_SPACE
        self.speed = speed
        self.turn_speed = turning_speed
        self.command_queue = []
        self.last_distance = 0.0

    def act(self):
        if len(self.command_queue) == 0:
            if self.phase == OmitCollisions.STATE_LOOK_FOR_SPACE:
                self.command_queue.append([TURN, random.randint(-1, 1)* 10])
                self.command_queue.append([SENSE_SONAR])
            else:
                self.command_queue.append([MOVE, 1])
                self.command_queue.append([SENSE_SONAR])

        return self.command_queue.pop(0)

    def on_sense_sonar(self, distance):
        self.last_distance = distance
        logger.info(str(self.last_distance) +" last_distance updated ")
        if distance < 0.04:
            self.phase = OmitCollisions.STATE_LOOK_FOR_SPACE
        else:
            self.phase = OmitCollisions.STATE_FORWARD


class OmitCollisionsCheckAccuracy(RobotController):
    """ Exemplary robot controller omitting collisions """
    STATE_FORWARD = 0
    STATE_LOOK_FOR_SPACE = 1

    def init(self, starting_position, steering_noise, distance_noise, measurement_noise, speed, turning_speed):
        self.phase = OmitCollisions.STATE_LOOK_FOR_SPACE
        self.speed = speed
        self.turn_speed = turning_speed
        self.command_queue = []
        self.last_distance = 0.0

    def act(self):
        if len(self.command_queue) == 0:
            if self.phase == OmitCollisions.STATE_LOOK_FOR_SPACE:
                self.command_queue.append([TURN, random.randint(-1, 1)* 50])
                self.command_queue.append([SENSE_SONAR])
            else:
                self.command_queue.append([MOVE, int(self.last_distance/0.01)])
                self.command_queue.append([SENSE_SONAR])

        return self.command_queue.pop(0)

    def on_sense_sonar(self, distance):
        self.last_distance = distance
        logger.info(str(self.last_distance) +" last_distance updated ")
        if distance < 0.04:
            self.phase = OmitCollisions.STATE_LOOK_FOR_SPACE
        else:
            self.phase = OmitCollisions.STATE_FORWARD

from collections import defaultdict

#class DFSBot(RobotController):
#    """ Exemplary robot controller doing DFS - just for internal tests """
#    STATE_FORWARD = 0
#    STATE_LOOK_FOR_RIGHT_WALL = 1
#
#
#
#    def init(self, starting_position, steering_noise, distance_noise, measurement_noise, maximum_speed = 0.1):
#        self.map = defaultdict()
#        self.phase = DFSBot.STATE_LOOK_FOR_RIGHT_WALL
#        self.phase_variables = {}
#        self.speed = maximum_speed
#        self.right_wall_distance = 0.01
#        self.command_queue = []
#
#    def act(self):
#        if len(self.command_queue) == 0:
#            if self.phase == DFSBot.STATE_LOOK_FOR_RIGHT_WALL:
#                self.command_queue.append([MOVE, 0.1, 0.0])
#                self.command_queue.append([SENSE_SONAR])
#                self.phase_variables = {} #Reset current state
#            else:
#                self.command_queue.append([MOVE, 0.0, self.speed/2.0])
#                self.command_queue.append([SENSE_SONAR])
#                self.phase_variables = {} #Reset current state
#
#        return self.command_queue.pop()
#
#    def on_sense(self, sensor, reading):
#        if reading < 0.2:
#            self.phase = OmitCollisions.STATE_LOOK_FOR_SPACE
#        else:
#            self.phase = OmitCollisions.STATE_FORWARD
#


#TODO: fill in this function
def load_python_controller(file):
    pass

#TODO: add timing
#TODO: add C++ and Java interfaces (piping)
class TimedRobotController(RobotController):
    """ Wrapper class to manage time consumption (also for other language packages) """
    def init(self, rc):
        self.rc = rc
        self.time_consumed = 0.0

    def act(self):
        """ Return next action """

        ret = self.rc.act()

    def on_sense_sonar(self, dist):
        self.rc.on_sense_sonar(dist)

    def on_sense_field(self, field_type, field_parameter):
        self.rc.on_sense_field(field_type, field_parameter)

    def on_sense_gps(self, x, y):
        self.rc.on_sense_gps(x,y)

