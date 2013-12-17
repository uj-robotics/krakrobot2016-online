from defines import *

class RobotController(object):
    """ You have to implement this class """
    def init(self, starting_position, steering_noise, distance_noise, measurement_noise):
        """ @param starting_position - (x,y) tuple representing current_position """
        raise NotImplementedError()

    def act(self):
        """ Return next action """
        raise NotImplementedError()

    def on_sense(self, sensor, reading):
        """ React to sensory data """
        raise NotImplementedError()

class ForwardTurningRobotController(RobotController):
    """ Exemplary robot controller """
    def init(self, starting_position, steering_noise, distance_noise, measurement_noise):
        pass

    def act(self):
        return MOVE, 0.09


    def on_sense(self, sensor, reading):
        pass

class OmitCollisions(RobotController):
    """ Exemplary robot controller """
    STATE_FORWARD = 0
    STATE_LOOK_FOR_SPACE = 1

    def init(self, starting_position, steering_noise, distance_noise, measurement_noise):
        self.phase = OmitCollisions.STATE_FORWARD

    def act(self):
        return MOVE, 0.2


    def on_sense(self, sensor, reading):
        pass

class TimedRobotController(RobotController):
    """ Wrapper class to manage time consumption (also for other language packages) """
    def init(self, robot_controller):
        pass
