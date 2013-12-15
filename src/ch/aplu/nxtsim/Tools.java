// Tools.java

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
 * Some useful helper methods.
 */
public class Tools
{
   /**
   * Suspends execution of the current thread for the given amount of time (unless
   * the game grid window is disposed).
   * @param duration the duration (in ms)
   */
  public static void delay(int duration)
  {
    if (GameGrid.isDisposed())
      return;
    try
    {
      Thread.currentThread().sleep(duration);
    }
    catch (InterruptedException ex)
    {}
  }
}
