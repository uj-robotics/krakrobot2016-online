// Button.java

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

import ch.aplu.util.*;

/**
 * Class to simulate the Nxt 'Escape' button by a 'Quit' button in a non-modal dialog.
 */
public class Button
{
  /**
   * A reference to the escape button.
   */
  public static Button ESCAPE = new Button();

  /**
   * Returns true, if the button was pressed.
   * @return true, if the button was pressed; otherwise false
   */
  public boolean isPressed()
  {
    return QuitPane.quit();
  }

  /**
   * Returns true, if the button was pressed.
   * @return true, if the button was pressed; otherwise false
   */
  public boolean isDown()
  {
    return QuitPane.quit();
  }
}
