Krakrobot2014 Online Eliminations
#######################################

Welcome to the technical specification for Krakrobot2014 online eliminations problem.
For description of the task please refer to the Problems page on the tournament's homepage www.krakrobot.pl




Installation
---------------------
<TODO:fill in>


Simulator
---------------------------------
To complete this task it is vital to understand how the simulator works.
To see running options of the simulator type

    python main.py -h


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







