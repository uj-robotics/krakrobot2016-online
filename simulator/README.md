Simulator
---------------------------------
To complete this task it is vital to understand how the simulator works.
Please feel free to inspect the code on your own, it has been written to be very readable and self-explanatory.
We will be also happy to answer all questions.

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
The map is a discretized grid with several field types, i.e:

* Empty field (field_type = 0)
* Wall (field_type = 1)
* Goal (field_type = 4)
* Start position (field_type = 3)
* Direction hint (field_type = 11, field_value in 0...7 indicating directions S, SE, E, NE, N, NW, N, SW respectively)
* Optimal path direction hint (field_type = 10, field_value in 0....7 indicating directions as above, note
however that the only possible values are S(0), E(2), N(4), W(6) )
* Distance hint (field_type = 9, field_value is a floor of the actual distance to the goal)

We have bundled the map generator utility with the simulator.
 In order to use it, please refer to map_gen.py file  Generation of the maps can be highly parameterized, please refer
to the documentation in the code. Note however that the maps for the final evaluation might be
generated differently (that is using a different generator, or designed by hand).

Please note that map doesn't have to be a maze.

![Example map](pics/1.png)