// UltrasonicListener.java

/*
This software is part of the NxtJLib library.
It is Open Source Free Software, so you may
- run the code for any purpose
- study how the code works and adapt it to your needs
- integrate all or parts of the code in your own programs
- redistribute copies of the code
- improve the code and release your improvements to the public
However the use of the code is entirely your responsibility.
*/

package ch.aplu.nxtsim;


/**
 * Class with declarations of callback methods for the ultrasonic sensor.
 */
public interface UltrasonicListener 
{
   /**
    * Called when the distance exceeds the trigger level.
    * If no target is found in the beam area, a far event is triggered with
    * value -1.
    * @param port the port where the sensor is plugged in
    * @param value the current distance
    */
   public void far(SensorPort port, int value);

   /**
    * Called when the distance falls below the trigger level.
    * @param port the port where the sensor is plugged in
    * @param value the current distance
    */
   public void near(SensorPort port, int value);
   
}
