Simulator
---------------------------------
To complete this task it is vital to understand how the simulator works.

### Running

There are two ways to run KrakRobotSimulator. As a command line tool, or in a windowed mode.
Using the GUI you can replay and run simulations of your robot. To run the GUI simply type

``python main.py``

To run the command line tool see running options for details.

 ``python main.py -h``


Both in command line and windowed mode you can control parameters such as
precision of the GPS, or turning speed.

Map
---------------------
The map is a discretized grid with several distinguished values:

* Empty field (field_type = 0)
* Wall (field_type = 1)
* Goal (field_type = 4)
* Start position (field_type = 3)

Any other field type can be represented as int

![Example map](pics/1.png)