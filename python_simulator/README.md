Krakrobot2014 Online Eliminations
===========================

Welcome to the technical specification for Krakrobot2014 online eliminations problem.
For description of the task please refer to the Problems page on the tournament's homepage www.krakrobot.pl


Installation
---------------------
<TODO:fill in>


Simulator
---------------------------------
To complete this task it is vital to understand how the simulator works.

### Running

There are two ways to run KrakrobotSimulat. As a command tool, or in a windowed mode.
Using GUI you can replay and run simulations of your robot. To run GUI simply type

    python main.py

To run command tool see running options for details.

    python main.py -h


Both in command and windowed mode you can control parameters such as
precision of the GPS, or turning speed.

### Simulator implementation

Simulator runs the robot until one of the following criteria is met:

*  Simulation time has exceeded provided maximum
*  Robot has exceeded CPU time limit
*  Robot has exceeded RAM limit (note: not controlled in your version)
*  Robot has reached the goal
*  Robot has thrown an exception
*  Robot has exceeded maximum number of collisions (dependent on the map, but always more than 100)

Every step of the simulation is an execution of one command (with appropriate
noise if applicable). In one step robot can

* Move by tick
* Turn by tick
* Use one of the three provided sensors

If by moving Robot collides with wall it doesn't move (but time for movement is consumed).
Robot can issue commands with multiple ticks, for instance [MOVE, 10], but such a move will be
discretized into 10 separate 1-tick moves.

On start of the simulation Simulator calls **init** on provided RobotController instance and
provides RobotController with constants for this run (i.e. moving speed, turning speed,
noise of move, noise of turn, noise of GPS, noise of sonar, CPU execution time limit,
sonar speed, GPS speed
).
All constants lie within bounds specified in the rules document.

Map is implemented as a discrete grid (of unknown to robot size), however move is executed continously

### Sensors

Robot is equipped with three sensors: GPS, sonar and field sensor.

When GPS is used RobotController on_sense_gps is called with measured absolute
x and y coordinates. 

When sonar is used Simulator calculates distance to the closest wall along ray casted
from the Robot center in the heading direction. (TODO: add picture)

Field sensor might be a little bit confusing. When called Simulator calculates on which
field the Robot is right now (i.e. floor(x), floor(y) ) and calls on_sense_field with 
field type and field value as arguments (for instance distance). Note that when Robot 
is close to the boundary of a field the results might be hard to predict. 


RobotController
---------------------------------

You task is to implement RobotController interface.


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







