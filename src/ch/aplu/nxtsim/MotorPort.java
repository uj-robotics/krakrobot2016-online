// MotorPort.java

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
 * Useful declarations for motor port connections.
 */
public class MotorPort
{
  /**
   * A motor port for a motor connected to port A.
   */
  public static MotorPort A = new MotorPort(1);
  /**
   * A motor port for a motor connected to port B.
   */
  public static MotorPort B = new MotorPort(2);
  /**
   * A motor port for a motor connected to port C.
   */
  public static MotorPort C = new MotorPort(3);
  private int portNb;

  private MotorPort(int portNb)
  {
    this.portNb = portNb;
  }
}
