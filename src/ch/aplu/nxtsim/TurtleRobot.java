// TurtleRobot.java

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
 * Implementation of the basic Logo turtle movements.
 */
public class TurtleRobot extends NxtRobot
{
  private Gear gear = new Gear();
  private final int turtleSpeed = 50;

  /**
   * Creates a turtle robot instance.
   */
  public TurtleRobot()
  {
    super();
    addPart(gear);
    gear.setSpeed(turtleSpeed);
  }

  /**
   * Sets the turtle speed to the given value.
   * @param speed 0..100
   * @return the object reference to allow method chaining
   */
  public TurtleRobot setTurtleSpeed(int speed)
  {
    gear.setSpeed(speed);
    return this;
  }

  /**
   * Returns the current turtle speed.
   * @return speed 0..100
   */
  public int getTurtleSpeed()
  {
    return gear.getSpeed();
  }

  /**
   * Starts moving forward and returns immediately.
   * @return the object reference to allow method chaining
   */
  public TurtleRobot forward()
  {
    gear.forward();
    return this;
  }

  /**
   * Moves the turtle forward the given number of steps.
   * The methods blocks until the turtle is at the final position (or the
   * game grid window is disposed).
   * @param steps the number of steps to go.
   * @return the object reference to allow method chaining
   */
  public TurtleRobot forward(int steps)
  {
    Location loc = getNxt().getLocation();
    gear.forward();
    double d = 0;
    while (d < steps)
    {
      Location newLoc = getNxt().getLocation();
      d = Math.sqrt((newLoc.x - loc.x) * (newLoc.x - loc.x)
        + (newLoc.y - loc.y) * (newLoc.y - loc.y));
      Tools.delay(1);
      if (GameGrid.isDisposed())
        break;
    }
    gear.stop();
    return this;
  }

  /**
   * Moves the turtle backward the given number of steps.
   * The methods blocks until the turtle is at the final position (or the
   * game grid window is disposed).
   * @param steps the number of steps to go.
   * @return the object reference to allow method chaining
   */
  public TurtleRobot backward(int steps)
  {
    Location loc = getNxt().getLocation();
    gear.backward();
    double d = 0;
    while (d < steps)
    {
      Location newLoc = getNxt().getLocation();
      d = Math.sqrt((newLoc.x - loc.x) * (newLoc.x - loc.x)
        + (newLoc.y - loc.y) * (newLoc.y - loc.y));
      Tools.delay(1);
      if (GameGrid.isDisposed())
        break;
    }
    gear.stop();
    return this;
  }

  /**
   * Starts moving backward and returns immediately.
   * @return the object reference to allow method chaining
   */
  public TurtleRobot backward()
  {
    gear.backward();
    return this;
  }

  /**
   * Turns the turtle to the right for the given angle.
   * The methods blocks until the turtle is at the final position (or the
   * game grid window is disposed).
   * @param angle the angle in degree to rotate.
   * @return the object reference to allow method chaining
   */
  public TurtleRobot right(double angle)
  {
    if (angle == 0)
      return this;
    if (angle < 0)
    {
      left(-angle);
      return this;
    }
    int oldSpeed = gear.getSpeed();
    gear.setSpeed(10);
    gear.right();
    double dir = getNxt().getDirection();
    double inc = 0;
    while (inc < angle)
    {
      double newDir = getNxt().getDirection();
      inc = newDir - dir;
      if (inc < 0)
        inc = 360 + inc;
      inc = inc % 360;
      Tools.delay(1);
      if (GameGrid.isDisposed())
        break;
    }
    gear.stop();
    gear.setSpeed(oldSpeed);
    return this;
  }

  /**
   * Starts turning right and returns immediately.
   * @return the object reference to allow method chaining
   */
  public TurtleRobot right()
  {
    gear.right();
    return this;
  }

  /**
   * Turns the left to the right for the given angle.
   * The methods blocks until the turtle is at the final position (or the
   * game grid window is disposed).
   * @param angle the angle in degree to rotate.
   * @return the object reference to allow method chaining
   */
  public TurtleRobot left(double angle)
  {
    if (angle == 0)
      return this;
    if (angle < 0)
    {
      right(-angle);
      return this;
    }
    int oldSpeed = gear.getSpeed();
    gear.setSpeed(10);
    gear.left();
    double dir = getNxt().getDirection();
    double inc = 0;
    while (inc < angle)
    {
      double newDir = getNxt().getDirection();
      inc = dir - newDir;
      if (inc < 0)
        inc = 360 + inc;
      inc = inc % 360;
      Tools.delay(1);
      if (GameGrid.isDisposed())
        break;
    }
    gear.setSpeed(oldSpeed);
    gear.stop();
    return this;
  }

  /**
   * Starts turning left and returns immediately.
   * @return the object reference to allow method chaining
   */
  public TurtleRobot left()
  {
    gear.left();
    return this;
  }

  /**
   * Returns the gear used for the turtle robot.
   * @return the gear reference
   */
  public Gear getGear()
  {
    return gear;
  }

}
