#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    Krakrobot Python Simulator

    Krakrobot 2015 Qualifications simulator.

    Many thanks to udacity.com:
    https://www.udacity.com/wiki/CS373%20Visualizing%20Maze%20Driving,
    we have reused visualisation code and the general idea while implementing
    this simulator.

"""

from optparse import OptionParser
from gui import SimulatorGUI
from simulator import KrakrobotSimulator
from robot_controller import compile_robot, construct_cmd_robot
import sys
import json
from os.path import join, dirname


def create_parser():
    """ Configure options and return parser object """
    parser = OptionParser()
    parser.add_option(
        "-c",
        "--command_line",
        dest="command_line",
        action="store_true",
        default=False,
        help="Run simulation without visualisation"
    )
    parser.add_option(
        "-m",
        "--map",
        dest="map",
        default=join(dirname(__file__), "maps/3.map"),
        help="Map that will be run after hitting Start Simulation button, "
             "or in command_line mode after running the program"
    )
    parser.add_option(
        "-r",
        "--robot",
        dest="robot",
        default="python2.7 examples/python/omit_collisions_example.py",
        help="Robot that will be compiled and run"
    )
    parser.add_option(
        "--steering_noise",
        dest="steering_noise",
        default=0.0004,
        type="float",
        help="Sigma of gaussian noise applied to turning motion"
    )
    parser.add_option(
        "--sonar_noise",
        dest="sonar_noise",
        default=0.0015,
        type="float",
        help="Sigma of gaussian noise applied to sensed distance by sonar"
    )
    parser.add_option(
        "--gps_noise",
        dest="measurement_noise",
        default=0.1,
        type="float",
        help="Sigma of gaussian noise applied to the sensed GPS position"
    )
    parser.add_option(
        "--gps_delay",
        dest="gps_delay",
        default=2.0,
        type="float",
        help="Time consumption (in simulation time units) of GPS"
    )
    parser.add_option(
        "--distance_noise",
        dest="distance_noise",
        default=0.001,
        type="float",
        help="Sigma of gaussian noise applied to forward motion"
    )
    parser.add_option(
        "--speed",
        dest="speed",
        default=5.0,
        type="float",
        help="Speed of the robot (i.e. units/simulation second)")
    parser.add_option(
        "--turning_speed",
        dest="turning_speed",
        default=1.0,
        type="float",
        help="Turning speed of the robot (i.e. rad/simulation second)"
    )
    parser.add_option(
        "--execution_cpu_time_limit",
        dest="execution_cpu_time_limit",
        default=100.0,
        type="float",
        help="Execution CPU time limit"
    )
    parser.add_option(
        "--simulation_time_limit",
        dest="simulation_time_limit",
        default=100000.0,
        type="float",
        help="Simulation time limit (in virtual time units)"
    )
    parser.add_option(
        "--frame_dt",
        dest="frame_dt",
        default=1,
        type="float",
        help="How often (in simulation time units) to produce a frame"
    )
    parser.add_option(
        "--iteration_write_frequency",
        dest="iteration_write_frequency",
        default=1000,
        type="int",
        help="How often (number of ticks of simulator) to report simulation"
             " status"
    )
    return parser


parser = create_parser()
(options, args) = parser.parse_args()
print options, args

simulator_params = {"visualisation": not options.command_line,
                    "speed": options.speed,
                    "distance_noise": options.distance_noise,
                    "steering_noise": options.steering_noise,
                    "sonar_noise": options.sonar_noise,
                    "measurement_noise": options.measurement_noise,
                    "turning_speed": options.turning_speed,
                    "execution_cpu_time_limit": options.execution_cpu_time_limit,
                    "simulation_time_limit": options.simulation_time_limit,
                    "frame_dt": options.frame_dt,
                    "iteration_write_frequency": options.iteration_write_frequency,
                    "gps_delay": options.gps_delay,
                    "robot_controller":  construct_cmd_robot(options.robot), #compile_robot(options.robot)[0],
                    "map": options.map
                    }


def main():
    if options.command_line:
        simulator = KrakrobotSimulator(simulation_dt=0.0, **simulator_params)
        print "Running simulator"
        results = simulator.run()
        print "Finished running simulator"
        print "Simulation has finished. Results:\n{0}".format(json.dumps(results))
    else:
        simulator = KrakrobotSimulator(**simulator_params)
        gui = SimulatorGUI(sys.argv, simulator, simulator_params)
        gui.run()


if __name__ == '__main__':
    main()
