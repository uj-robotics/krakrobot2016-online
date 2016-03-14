#!/usr/bin/env python3

import sys
import random
from random import random as rand
import math
from math import pi

TURN = "TURN"
BEEP = "BEEP"
MOVE = "MOVE"
FINISH = "FINISH"

TICK_MOVE = 0.01
TICK_ROTATE = 0.002
COLOR_SENSOR_DIST = 0.5

FIELD_SIZE_CM = 22

def deg_to_rad(deg):
    return deg * pi / 180.0

def cm_to_ticks(cm):
    return int(cm /(FIELD_SIZE_CM * TICK_MOVE))

def deg_to_ticks(deg):
    return int(deg_to_rad(deg) / TICK_ROTATE)

class TemplateBot(object):
    """ Example robot controller moving randomly """

    def init(self, x, y, angle, steering_noise, distance_noise, forward_steering_drift,
        speed, turning_speed, execution_cpu_time_limit, N, M):
        self.x = x
        self.y = y
        self.angle = angle

        self.steering_noise = steering_noise
        self.distance_noise = distance_noise
        self.forward_steering_drift = forward_steering_drift

        self.speed = speed
        self.turning_speed = turning_speed

        self.execution_cpu_time_limit = execution_cpu_time_limit

        self.N = N
        self.M = M

        self.current_color = (None, None, None)

        self.elapsed_time = 0

    def act(self):
        action = ["MOVE", "TURN"][random.randint(0,1)]  # MOVE or TURN
        direction = 1 - random.randint(0,1)*2  # 1 or -1
        return [action, direction]

    def on_sense_color(self, r, g, b):
        assert 0 <= r <= 255
        assert 0 <= g <= 255
        assert 0 <= b <= 255

        self.current_color = (r, g, b)

    def on_time(self, time):
        self.elapsed_time = time

if __name__ == "__main__":
    robot = TemplateBot()
    robot_kwargs = {}
    for i in range(11): # 11 parameters expected
        w = sys.stdin.readline().strip()
        key, value = w.split(":")
        robot_kwargs[key] = float(value)
    robot.init(**robot_kwargs)

    running = True
    while  running:
        cmd = sys.stdin.readline().strip()
        if cmd == "act":
            response = robot.act()
            if response[0] == FINISH:
                running = False
            sys.stdout.write(" ".join(map(str, response)) + "\n")
            sys.stdout.flush()
        elif cmd == "color":
            r, g, b = map(int, input().split())
            robot.on_sense_color(r, g, b)
        elif cmd == "time":
            robot.on_time(float(input()))
        else:
            raise RuntimeError("Not recognized cmd \"" + cmd + "\"")