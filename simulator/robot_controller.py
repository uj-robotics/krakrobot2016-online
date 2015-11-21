from misc import *
import datetime

class RobotController(object):
    """ You have to implement this class """
    def init(starting_position, steering_noise, distance_noise, sonar_noise,
                     measurement_noise, speed, turning_speed, gps_delay, execution_cpu_time_limit):
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

class PythonTimedRobotController(RobotController):
    """ Wrapper class to manage time consumption (also for other language packages) """
    def __init__(self, rc):
        self.rc = rc
        self.time_consumed = datetime.timedelta(0)

    def init(self, *args, **dargs):
        x = datetime.datetime.now()
        self.rc.init(*args, **dargs)
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
        tmp = datetime.datetime.now()
        self.rc.on_sense_gps(x,y)
        self.time_consumed += datetime.datetime.now() - tmp

def importCode(file_name, name):
    import imp
    return imp.load_source(name, file_name)

counter_module = 0
def compile_robot(file_name, module_name = "contestant_module"):
    """ Compiles robot from given file and returns class object """
    global counter_module
    module_name += str(counter_module)
    counter_module += 1
    mod =  importCode(file_name, module_name)
    compiled_class = None
    for symbol in dir(mod):
        if hasattr(getattr(mod, symbol), "act") and getattr(mod, symbol).__name__ != "RobotController":
            compiled_class = getattr(mod, symbol)
    print compiled_class
    globals()[compiled_class.__name__] = compiled_class
    if compiled_class is None:
        raise KrakrobotException("Not found class with act() function named different than RobotController in provided .py")
    return compiled_class, mod
