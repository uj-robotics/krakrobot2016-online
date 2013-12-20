Krakrobot2014 Online Eliminations

#######################################

Welcome to the technical specification for Krakrobot2014 online eliminations problem.
For description of the task please refer to the Problems page on the tournament's homepage www.krakrobot.pl




Installation
---------------------
<TODO:fill in>


Simulator
---------------------------------

1. Running

To complete this task it is vital to understand how the simulator works.
There are two ways to run KrakrobotSimulat. As a command tool, or in a windowed mode.
Using GUI you can replay and run simulations of your robot. To run GUI simply type

    python main.py

To run command tool see running options for details.

    python main.py -h

Both in command and windowed mode you can control parameters such as
precision of the GPS, or turning speed.

2. Simulator implementation

Simulator runs the robot until one of the following criteria is met:
a) Simulation time has exceeded provided maximum
b) Robot has exceeded CPU time limit
c) Robot has exceeded RAM limit (note: not controlled in your version)
d) Robot has reached the goal
e) Robot has thrown an exception
f) Robot has exceeded maximum number of collisions (dependent on the map, but always more than 100)

Every step of the simulation is an execution of one command (with appropriate
noise if applicable). In one step robot can
a) Move by tick
b) Turn by tick
c) Use one of the three provided sensors

If by moving Robot collides with wall it doesn't move (but time for movement is consumed).
Robot can issue commands with multiple ticks, for instance [MOVE, 10], but such a move will be
discretized into 10 separate 1-tick moves.


RobotController
---------------------------------



1. Initialization



2.


Hints and resources
-------------------------
This section is very important. We strongly encourage you to get familiar with the
resources that we link in here, as they are tremendously helpful in solving this task



Rzeczy do uściślenia
* Okreslic przedzial predkosci obrotu i jazdy do przodu
* Okreslic przedzial dokladnosci GPS, sonaru, jazdy do przodu, obrotu (4 wariancje)
* Okreslic przedzial czasu ladowania GPS/sonaru (albo zrobić to stałe??)

Specyfikacja:
* Maksymalna ilosc kolizji ze scianami (to pomaga w ocenianiu, bo kolizja oznacza
bledy numeryczna. Mala ilosc kolizji, tj. wymuszona mala ilosc kolizji,
zapewni nam rozwiazania ktore nie jezdza beznadziejnie blisko scian) - czy to dobry pomysł?

Maksymalny czas wykonania zalezny od planszy


RobotController init:
init(starting_position, steering_noise, distance_noise, measurement_noise, speed, turning_speed,
execution_cpu_time_limit
)







