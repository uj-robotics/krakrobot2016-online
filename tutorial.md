# Tutorial for qualifications task

## Installation and options

The first step is to download .zip uploaded to our website and unpack it. To run
the code you will need python 2.7 and PyQt python package (see task description
document for more specific installation guide).

In the root directory
you will see many files, but the most important one is ``main.py``. It is both GUI interface
for you, but also it can be used to test quickly execution result. For full list of options run:

``python main.py -h``

For instance to run exemplary bot, without GUI on exemplary map 4 you can run

``python main.py -c -m maps/4.map -r examples/omit_collisions_example.py``

To run GUI with preloaded map and robot remove the "-c" argument.


## Turner bot ##

Our goal will be to write bot that is doing 90 degrees turns and is picking fields
that he has visited the least amount of times

### Basics

Our bot will work using state variable and command queue. That is we will check if we have queued
actions, if yes we will fire it. If not we will plan next actions accordingly to present state,
and change state if we want to take different actions next time the command queue is empty. To 
see more informations on simillar approach look up "Hybrid Automaton", which is quite commonly
used model in robotics.

The first step will be writing bot rotating 90 degrees alternatively clokwise and counterclockwise.

For general outline for robot class see forward_example.py in examples/ directory and try to write 
yourself the rotating robot taking into consideration our state variable and command queue design.

For solution please see rotator.py in examples/ directory.

Here is our act() function:


      def act(self):
        if len(self.command_queue) == 0:
            if self.state == Rotator.STATE_ROTATE:
                self.command_queue.append([TURN, \
		self.state_helper * int((0.5*pi)/ TICK_ROTATE )]) # Rotate by 90 deegres
                self.state_helper *= -1
        return self.command_queue.pop(0)

To run your solution on 1.map run and press Run Simulation button.

``python main.py -m maps/1.map -r <your_file_path>``

However note that we cannot see many details, as the animation is too fast. We can force the simulator to render more frames by
passing argument frame_dt . Note that you can also alter simulation speed.

``python main.py -m maps/1.map -r <your_file_path> --frame_dt=0.01``

It is crucial to handle noise in this task. Please try changing steering noise (In the GUI panel, or by passing parameter).
As you can see the rotation movement is getting worse and less accurate. In your submissions you have to find
a robust way of dealing with noise.

### Turner

In this section we will try to design a bot that will be search the map by going to the field it wasn't before.

Solution for this section can be found in examples/turner.py

First we need to define states that our robot will be in. In our tutorial we have picked four states, that is:

  * STATE_FINDING_POSITION : Robot is using GPS to find its position

  * STATE_DECIDE_NEXT : Robot is deciding where to go next, and runs turning and moving commands

  * STATE_FOUND_GOAL : Robot is on the goal field

  * STATE_SCANNING : Robot is scanning for walls.

We will need also to keep track of how many times we have been to a field. We are keeping this
knowledge in the map_visited dictionary.

We will follow the same idea as in rotator example, that is we will keep queue of current commands and
if the queue is empty we will try to generate new commands on the current state. One modification is
adding new command *STATE_CHANGE* that will be handled by our bot, that will change states without executing
any command.

The first step in writing turner is writing scanner handler. Try to write code that will scan all the
directions for walls and write the result to map_visited dictionary.

Here is our proposition:

     if self.state == Turner.STATE_SCANNING:
        x_disc, y_disc = int(self.x + 0.5), int(self.y + 0.5) 
	# +0.5 because axis origin is in the middle of a field

        print "Scanning on ",x_disc, " ",y_disc

        import math
        # Determine vector in which direction we are scanning
        vector = (math.cos((self.angle - 90.0)/180.0 * pi), \
	math.sin((self.angle - 90.0)/180.0 * pi))

        scanned = (x_disc-round(vector[1]), y_disc + round(vector[0]))

        # Check if scanned field is not *discovered* yet
        if (x_disc-round(vector[1]+0.01), y_disc + \
	round(vector[0]+0.01)) not in self.map_visited:
            if self.last_distance < 0.9:
                # Strange indexing because x runs vertically 
	       # and y runs horizontally
                # Set big number so that it won't be visited
                self.map_visited[(x_disc-round(vector[1]+0.01),\
		 y_disc + round(vector[0]+0.01))] = 1000
            else:
                self.map_visited[(x_disc-round(vector[1]+0.01), \
		y_disc + round(vector[0]+0.01))] = 0

        # Keep track of scanned fields
        self.state_helper += 1


        # It means that we have reached the last rotation
        if self.state_helper == 4:
            self.command_queue.append(["STATE_CHANGE", Turner.STATE_DECIDE_NEXT])
        else:
            self.command_queue.append([TURN, int(0.5*pi / TICK_ROTATE)])
            self.angle = (self.angle + 90.0) % 360
            self.command_queue.append([SENSE_SONAR])

**State transitions rules**

Having done this, the rest is quite straightforward. We need to carefully design the state transition rules (for instance
from STATE_SCANNING to STATE_DECIDE_NEXT). Here are our propositions. The code is simillar to the one provided for scanning.

   * *STATE_DECIDE_NEXT* : we check if we have scanned all the fields touching our field. If no change state to STATE_SCANNING
if yes *enqueue* commands that will move us to this field (that is rotation and movement) and change state to STATE_FINDING_POSITION

   * *STATE_FINDING_POSITION* : this is the easiest state. We will run 4 times GPS scan and then average everything and switch to STATE_DECIDE_NEXT

   * *STATE_SCANNING* : was described before

   * *STATE_FOUND_GOAL* : end execution and fire command FINISH

The code following this logic is accessible at examples/turner.py. Note that it doesn't work well when noise (for steering, movement or
measurement) is high. However it is able to find goal in average sized maps, when noise is very low. Try executing turner.py on
different maps to see the effect.


