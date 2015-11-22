from misc import *
import datetime
import subprocess

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

    def terminate(self):
        pass

class CmdLineRobotController(RobotController):
    def __init__(self, cmd):
        self.p = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, \
                                  stdin=subprocess.PIPE)
        self.cmd = cmd

    def clone(self):
        return CmdLineRobotController(self.cmd)

    def init(self, *args):
        self.p.stdin.write(" ".join(map(str, args)) + "\n")

    def act(self):
        self.p.stdin.write("act\n")
        cmd = self.p.stdout.readline().split()
        print cmd
        if cmd[0] == "move" or cmd[0] == "turn":
            return cmd[0], int(cmd[1])
        else:
            return cmd

    def on_sense_field(self, *args):
        self.p.stdin.write("on_sense_field\n")
        self.p.stdin.write(" ".join(map(str, args)) + "\n")

    def on_sense_sonar(self, *args):
        self.p.stdin.write("on_sense_sonar\n")
        self.p.stdin.write(" ".join(map(str, args)) + "\n")

    def on_sense_gps(self, *args):
        self.p.stdin.write("on_sense_gps\n")
        self.p.stdin.write(" ".join(map(str, args)) + "\n")

    def terminate(self):
        self.p.communicate()

class PythonTimedRobotController(RobotController):
    """ Wrapper class to manage time consumption (also for other language packages) """
    def __init__(self, rc):
        self.rc = rc
        self.time_consumed = datetime.timedelta(0)

    def clone(self):
        return PythonTimedRobotController(self.rc)

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

    def terminate(self):
        self.tc.terminate()

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

def construct_cmd_robot(cmd):
    """ Compiles robot from given file and returns class object """
    return CmdLineRobotController(cmd=cmd)
