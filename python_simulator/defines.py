MOVE = "move" # (move, steer) -> OK
TURN = "turn"
SENSE_SONAR = "sense_sonar" # (sense_radar) -> ([alpha,dist],[alpha,dist]....)
SENSE_GPS = "sense_gps" # (sense_gps) -> (x,y)
SENSE_GPS_ACTIONS = 3


SENSE_FIELD = "sense_field"
SENSE_LIGHT_SENSOR = "sense_light_sensor"  # (sense_light_sensor) -> (field_type)   #TODO: add or erase it ? everytime robot knows the field?
SQUARE_SIDE = 1.0




MAP_GOAL = 4 # coding MAP_GOAL
MAP_WALL = 1 # coding MAP_WALL
MAP_WHITE = 0 # coding MAP_WHITE
MAP_SPECIAL_DIRECTION = 2 # coding [MAP_SPECIAL_DIRECTION, DIRECTION]
DIRECTION_E = 0
DIRECTION_NE = 1
DIRECTION_N = 2
DIRECTION_NW = 3
DIRECTION_W = 4
DIRECTION_SW = 5
DIRECTION_S = 6
DIRECTION_SE = 7
MAP_SPECIAL_EUCLIDEAN_DISTANCE = 3 # coding [MAP_SPECIAL_EUCLIDEAN_DISTANCE, DISTANCE IN MAP UNITS]
#What field next?
#Map coding:

CONSTANT_MAP = {"direction":MAP_SPECIAL_DIRECTION, "east": DIRECTION_E, "northeast": DIRECTION_NE, "north": DIRECTION_N,
                "northwest":DIRECTION_NW, "west": DIRECTION_W, "southwest": DIRECTION_SW, "south": DIRECTION_S, "southeast": DIRECTION_SE
                }

# GUI
QT_NO_OPENGL = False



class KrakrobotException(Exception):
    pass

