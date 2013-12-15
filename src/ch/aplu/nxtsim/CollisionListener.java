// CollisionListener.java

/*
This software is part of the NxtSim library.
It is Open Source Free Software, so you may
- run the code for any purpose
- study how the code works and adapt it to your needs
- integrate all or parts of the code in your own programs
- redistribute copies of the code
- improve the code and release your improvements to the public
However the use of the code is entirely your responsibility.

Author: Aegidius Pluess, www.aplu.ch
 */

package ch.aplu.nxtsim;

/**
 * Interface with declarations of a callback method to detect robot-obstacle collisions.
 */
public interface CollisionListener extends java.util.EventListener
{
  /**
   * Called in a new thread when the circumcircle of the robot overlaps
   * with an obstacle. Any further events are inhibited until collide() returns.
  */
  public void collide();

}