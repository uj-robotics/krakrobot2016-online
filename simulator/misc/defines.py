# -*- coding: utf-8 -*-

__version__ = '0.9'
__authors__ = u'Konrad Talik, Stanisław Jastrzębski'
__copyright__ = 'Copyright 2013-2015,\
                    Jagiellonian University Robotics Interest Group'
__license__ = 'MIT'
__maintainer__ = 'Konrad Talik'
__email__ = 'konradtalik@gmail.com'
__about__ = """This simulator is being developed for Krakrobot \
robotics and artificial intelligence competition. \
Visit website for further information."""

__website__ = 'www.krakrobot.pl'


### act() constants ###
MOVE = "move" # (move, steer) -> OK
TURN = "turn"
SENSE_SONAR = "sense_sonar" # (sense_radar) -> ([alpha,dist],[alpha,dist]....)
SENSE_GPS = "sense_gps" # (sense_gps) -> (x,y)
FINISH = "finish"
SENSE_FIELD = "sense_field"
SENSE_LIGHT_SENSOR = "sense_light_sensor"  # (sense_light_sensor) -> (field_type)   #TODO: add or erase it ? everytime robot knows the field?
WRITE_CONSOLE = "write_console"


### Contest constants ###
TICK_MOVE = 0.01
TICK_ROTATE = 0.002
GPS_TIME = 1.0
SONAR_TIME = 0.1
FIELD_TIME = 0.1

### Map constants ###
MAP_GOAL = 4 # coding MAP_GOAL
MAP_START_POSITION = 3
SQUARE_SIDE = 1.0
MAP_WALL = 1 # coding MAP_WALL
MAP_WHITE = 0 # coding MAP_WHITE
MAP_SPECIAL_DIRECTION = 11 # coding [MAP_SPECIAL_DIRECTION, DIRECTION]

DEFAULT_ANIMATION_RATE = 100

DIRECTION_E = 2
DIRECTION_NE = 3
DIRECTION_N = 4
DIRECTION_NW = 5
DIRECTION_W = 6
DIRECTION_SW = 7
DIRECTION_S = 0
DIRECTION_SE = 1

MAP_SPECIAL_EUCLIDEAN_DISTANCE = 9 # coding [MAP_SPECIAL_EUCLIDEAN_DISTANCE, DISTANCE IN MAP UNITS]
MAP_SPECIAL_OPTIMAL = 10

CONSTANT_MAP = {"direction":MAP_SPECIAL_DIRECTION,
                "east": DIRECTION_E, "northeast": DIRECTION_NE, "north": DIRECTION_N,
                "northwest":DIRECTION_NW, "west": DIRECTION_W,
                "southwest": DIRECTION_SW, "south": DIRECTION_S, "southeast": DIRECTION_SE,
                "distance":MAP_SPECIAL_EUCLIDEAN_DISTANCE,
                "optimal_path":MAP_SPECIAL_OPTIMAL
                }
MAP_CODING = {"#":1, ".":0, "s":MAP_START_POSITION, "x":MAP_GOAL}
REV_MAP_CODING = {v:k for k,v in MAP_CODING.items()}
REV_CONSTANT_MAP = {v:k for k,v in CONSTANT_MAP.items()}


# GUI
QT_NO_OPENGL = False

class KrakrobotException(Exception):
    pass

