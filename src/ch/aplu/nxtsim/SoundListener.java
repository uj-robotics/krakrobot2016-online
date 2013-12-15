// SoundListener.java

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
 * Class with declaration of callback methods for the sound sensor.
 */
public interface SoundListener extends java.util.EventListener
{
  /**
   * Called when the sound becomes louder than the trigger level.
   * @param port the port where the sensor is plugged in
   * @param level the current sound level
   */
   public void loud(SensorPort port, int level);

  /**
   * Called when the sound becomes lower than the trigger level.
   * @param port the port where the sensor is plugged in
   * @param level the current sound level
   */
   public void quiet(SensorPort port, int level);
}
