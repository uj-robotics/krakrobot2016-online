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
    """ Exemplary robot controller omitting collisions """
    STATE_FORWARD = 0
    STATE_LOOK_FOR_SPACE = 1

    def init(self, starting_position, steering_noise, distance_noise, measurement_noise):
        self.phase = OmitCollisions.STATE_LOOK_FOR_SPACE
        self.speed = 0.1
        self.command_queue = []

    def act(self):
        if len(self.command_queue) == 0:
            if self.phase == OmitCollisions.STATE_LOOK_FOR_SPACE:
                self.command_queue.append([MOVE, 0.1, 0.0])
                self.command_queue.append([SENSE_SONAR])
            else:
                self.command_queue.append([MOVE, 0.0, 0.1])
                self.command_queue.append([SENSE_SONAR])

        return self.command_queue.pop()

    def on_sense(self, sensor, reading):
        if reading < 0.2:
            self.phase = OmitCollisions.STATE_LOOK_FOR_SPACE
        else:
            self.phase = OmitCollisions.STATE_FORWARD



class TimedRobotController(RobotController):
    """ Wrapper class to manage time consumption (also for other language packages) """
    def init(self, robot_controller):
        pass
