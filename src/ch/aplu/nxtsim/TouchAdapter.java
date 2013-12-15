// TouchAdapter.java

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
 * Class with empty callback methods for the touch sensor.
 */
public class TouchAdapter implements TouchListener
{
  /**
   * Empty method called when the touch sensor is pressed.
   * Override it to process the event.
   * @param port the port where the sensor is plugged in
   */
  public void pressed(SensorPort port)
  {}

  /**
   * Empty method called when the touch sensor is released.
   * Override it to process the event.
   * @param port the port where the sensor is plugged in
   */
  public void released(SensorPort port)
  {}

}
