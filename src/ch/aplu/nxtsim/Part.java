// Part.java
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

import ch.aplu.jgamegrid.*;

/**
 * Abstract class as ancestor of all parts.
 */
public abstract class Part extends Actor
{
  private Location pos;
  protected NxtRobot robot = null;

  protected Part(String imageName, Location pos)
  {
    this(imageName, pos, 1);
  }

  protected Part(String imageName, Location pos, int nbSprites)
  {
    super(true, imageName, nbSprites, 360);
    this.pos = pos;
  }
  
  protected void setRobot(NxtRobot robot)
  {
    this.robot = robot;
  }  

  protected void setPosition(Location pos)
  {
    this.pos = pos.clone();
  }

  protected Location getPosition()
  {
    return pos;
  }

  // Called to cleanup
  protected abstract void cleanup();
}
