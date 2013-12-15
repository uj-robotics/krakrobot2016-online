// SensorPort.java

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
 * Useful declarations for sensor port connections.
 */
public class SensorPort
{
  /**
   * A sensor port for a sensor connected to port S1.
   */
  public static SensorPort S1 = new SensorPort(1);
  /**
   * A sensor port for a sensor connected to port S2.
   */
  public static SensorPort S2 = new SensorPort(2);
  /**
   * A sensor port for a sensor connected to port S3.
   */
  public static SensorPort S3 = new SensorPort(3);
  /**
   * A sensor port for a sensor connected to port S4.
   */
  public static SensorPort S4 = new SensorPort(4);
  private int portNb;

  private SensorPort(int portNb)
  {
    this.portNb = portNb;
  }

}
