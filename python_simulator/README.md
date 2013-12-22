Krakrobot2014 Lost in the Cracows' alleys
===========================

Welcome to the rules and technical specification for Krakrobot2014 online qualifications problem.

The qualification round consists of one task,
called “Lost in the Cracows' alleys”. Your task will be to write the robot's AI allowing
it to figure out the way through complex maze of alleys as quick as possible.

In this package you will find the simulator, exemplary maps in maps directory and exemplary robots in examples directory.


General rules
-----------------------

1. Contestants have to be students, enrolled at Bachelor, Masters or PhD level programme in any field.
2. KrakRobot is a team competition – each team has to consist of 2 or 3 people, working together.
3. Task is simulation based – the appropriate code bundled
 with exemplary maps and robots is available https://github.com/uj-robotics/Krakrobot2014Qualifications
4. Each team write their own implementation of the robot's AI (one per team), some sample implementations are also avaliable in
the package
5. Robot moves around a rectangular map of dimensions M x N (unknown to the robot)
6. Robot is executed by simulator. Robot can choose from given set of actions (for instance move, or turn)
7. Each action performed (both sensing and acting) costs some time. The robot's total simulation time is the summarized cost of all performed actions
 from the simulation start to the moment of reaching the goal state
 (which is checked automatically by the simulation engine,
 and is defined as being located over the field and communicating it).
 The goal is to minimize total simulation time to finding the goal.
8. Each map can have upper bound on simulation time, after which all robots will be considered as having infinite total simulation time.
9. One round of simulations consists of running al contestants AI's on one, randomly generated map (the same for each robot).
In each round the constants (for instance accuracy of the GPS sensor) can change.
After each round, the ranking, obtained by sorting the total times in descending order, is created.
10. Whole qualification will consist of multiple rounds, and the final position of each robot will be its median position in all the rankings.
The best teams (number of advancing teams will be disclosed in January) will advance to the finals, which will take place at 12 april 2014 at Cracow.
11. Each simulation has limited CPU time, which will be passed to Robot at the initialization step. Besides that we set 1024 MB RAM limit.
12. Any modifications to the simulation code, attempts to hack the engine in order to achieve better score (either by reading the map or by any other type of cheating) will result in the disqualification.
13. Jury has indisputable right to disqualify any team if violations of this regulations are detected.
14. Jury has right to change the rules of this qualifications task at any time, however each modification will be sent to all
registered contestants and annouced on the official page www.krakrobot.pl


Installation
---------------------
<TODO:fill in>

Map
---------------------
Map is a discretized maze with several field types, i.e:

* Empty field (field_type = 0)
* Wall (field_type = 1)
* Goal (field_type = 4)
* Start position (field_type = 3)
* Hint direction (field_type = 11, field_value in 0...7 indicating in sequence direction S, SE, E, NE, N, NW, N, SW)
* Hint optimal path direction (field_type = 10, field_value in 0....7 indicating in sequence directions as above, however
note that the only possible values are S(0), E(2), N(4), W(6) )
* Hint distance (field_type = 9, field_value is a floor of actual distance to the goal)

(TODO: add picture)

Simulator
---------------------------------
To complete this task it is vital to understand how the simulator works.

### Running

There are two ways to run KrakrobotSimulat. As a command tool, or in a windowed mode.
Using GUI you can replay and run simulations of your robot. To run GUI simply type

``python main.py``

To run command tool see running options for details.

 ``python main.py -h``


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
* Communicate finishing

If by moving Robot collides with wall it doesn't move (but time for movement is consumed).
Robot can issue commands with multiple ticks, for instance [MOVE, 10], but such a move will be
discretized into 10 separate 1-tick moves.

On start of the simulation Simulator calls **init** on provided RobotController instance and
provides RobotController with constants for this run (i.e. moving speed, turning speed,
noise of move, noise of turn, noise of GPS, noise of sonar, CPU execution time limit,
sonar speed, GPS speed
).
All constants lie within bounds specified in the Constants Bounds section.

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

You task is to implement RobotController interface. The code should
be written in Python.

To see RobotController class and exemplary implementations please see *robot_controller.py* file.

The RobotController class should implement

* **init(starting_position, steering_noise, distance_noise, measurement_noise, speed, turning_speed,
execution_cpu_time_limit) - initialization function. Specifications of the arguments:
	* starting_position : tuple [x,y,angle], where x and y are accurate positions of the robot (we assume
upper-left corner is (0,0) and x runs vertically, whereas y runs horizontally) and angle which is an angle in radians
with respect to X axis (TODO: add picture)
	* steering_noise : variance 

* **act()** - this is the basic function. It is called always after executing last command.
In act you should return a list. For constants see *defines.py*

	*  Moving : ["move", number_of_ticks]
	*  Turning : ["turn", number_of_ticks]
	*  Sense GPS: ["sense_gps"]
	*  Sense sonar: ["sense_sonar"]
	*  Sense field: ["sense_field"]
	*  Communicate finish: ["finish"]

* **on_sense_gps(x,y)** - reponds to (x,y) measurement (no return)

* **on_sense_sonar(distance)** - responds to (distance) measurement (no return)

* **on_sense_field(field_type, field_value)** - responds to (field_type, field_value) measurement (no return)


Constants bounds
--------------------


Hints and resources
-------------------------
This section is very important. We strongly encourage you to get familiar with the
resources that we link in here, as they are tremendously helpful in solving this task.

We are aware that you might be not familliar with python, however we believe that this
is a great tool for robotics and it is worth learning.



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







