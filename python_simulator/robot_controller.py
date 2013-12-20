from defines import *
from utils import *
import random
class RobotController(object):
    """ You have to implement this class """
    def init(self, starting_position, steering_noise, distance_noise, speed, turning_speed,
             maximum_turn, execution_cpu_time_limit):
        """ @param starting_position - (x,y) tuple representing current_position """
        raise NotImplementedError()

    def act(self):
        """ Return next action """
        raise NotImplementedError()

    def on_sense_sonar(self, dist):
        """ React to sensory data """
        raise NotImplementedError()

    def on_sense_field(self, field_type, field_parameter):
        """ React to sensory data """
        raise NotImplementedError()

    def on_sense_gps(self, x, y):
        """ React to sensory data """
        raise NotImplementedError()

class ForwardTurningRobotController(RobotController):
    """ Exemplary robot controller """
    def init(self, starting_position, steering_noise, distance_noise, measurement_noise, speed, turning_speed, execution_cpu_time_limit):
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

    def init(self, starting_position, steering_noise, distance_noise, measurement_noise, speed, turning_speed, execution_cpu_time_limit):
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
                self.command_queue.append([SENSE_FIELD])

        return self.command_queue.pop(0)

    def on_sense_sonar(self, distance):
        self.last_distance = distance
        if distance < 0.04:
            self.phase = OmitCollisions.STATE_LOOK_FOR_SPACE
        else:
            self.phase = OmitCollisions.STATE_FORWARD


    def on_sense_field(self, field_type, field_parameter):
        pass


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
                self.command_queue.append([SENSE_FIELD])

        return self.command_queue.pop(0)

    def on_sense_sonar(self, distance):
        self.last_distance = distance

        if distance < 0.04:
            self.phase = OmitCollisions.STATE_LOOK_FOR_SPACE
        else:
            self.phase = OmitCollisions.STATE_FORWARD


from collections import defaultdict



#TODO: fill in this function
def load_python_controller(file):
    pass

import datetime
#TODO: add timing
#TODO: add C++ and Java interfaces (piping)
class PythonTimedRobotController(RobotController):
    """ Wrapper class to manage time consumption (also for other language packages) """
    def __init__(self, rc):
        self.rc = rc
        self.time_consumed = datetime.timedelta(0)

    def init(self, starting_position, steering_noise, distance_noise, measurement_noise, speed, turning_speed, execution_cpu_time_limit):
        x = datetime.datetime.now()
        self.rc.init(starting_position, steering_noise, distance_noise, measurement_noise, speed, turning_speed, execution_cpu_time_limit)
        self.time_consumed += datetime.datetime.now() - x

    def act(self):
        """ Return next action """
        x = datetime.datetime.now()
        ret = self.rc.act()
        self.time_consumed += datetime.datetime.now() - x
        return ret

    def on_sense_sonar(self, dist):
        x = datetime.datetime.now()
        self.rc.on_sense_sonar(dist)
        self.time_consumed += datetime.datetime.now() - x

    def on_sense_field(self, field_type, field_parameter):
        x = datetime.datetime.now()
        self.rc.on_sense_field(field_type, field_parameter)
        self.time_consumed += datetime.datetime.now() - x
    def on_sense_gps(self, x, y):
        x = datetime.datetime.now()
        self.rc.on_sense_gps(x,y)
        self.time_consumed += datetime.datetime.now() - x

