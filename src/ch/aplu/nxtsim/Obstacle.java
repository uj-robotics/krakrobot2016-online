// Obstacle.java

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
import java.awt.image.BufferedImage;

/**
 * Class to represent an obstacle detected by a touch sensor.
 * The touch is detected by a JGameGrid collision with a non-transparent
 * pixel of the obstacle sprite image.
 */
public class Obstacle extends Actor
{
  /**
   * Creates an obstacle from given image file.
   * @param imageName the image to be used as obstacle
   */
  public Obstacle(String imageName)
  {
    super(imageName);
    setCollisionImage();
  }
  
  /**
   * Creates an obstacle from given buffered image.
   * @param bi the image to be used as obstacle
   */
  public Obstacle(BufferedImage bi)
  {
    super(bi);
    setCollisionImage();
  }
}
