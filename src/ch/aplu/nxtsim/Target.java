// Target.java

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
import java.awt.Point;
import java.awt.image.BufferedImage;

/**
 * Class to represent a target detectable by the ultrasonic sensor.
 */
public class Target extends Actor
{
  private Point[] mesh;
  private String imageName = null;
  private BufferedImage bi = null;
  
  /**
   * Creates a target from given image file using the given mesh points. 
   * The coordinate system for the mesh is centered in the middle of the image with
   * pixel coordinates x to the right and y to the bottom.
   * @param imageName the image to be used as target
   * @param mesh the mesh points (at least 2)
   */
  public Target(String imageName, Point[] mesh)
  {
    super(imageName);
    this.imageName = imageName;
    int size = mesh.length;
    this.mesh = new Point[size];
    for (int i = 0; i < size; i++)
      this.mesh[i] = new Point(mesh[i]);
  }
  
  /**
   * Creates a target from given buffered image.
   * The coordinate system for the mesh is centered in the middle of the image with
   * pixel coordinates x to the right and y to the bottom.
   * @param bi the image to be used as target
   * @param mesh the mesh points (at least 2)
   */
  public Target(BufferedImage bi, Point[] mesh)
  {
    super(bi);
    this.bi = bi;
    int size = mesh.length;
    this.mesh = new Point[size];
    for (int i = 0; i < size; i++)
      this.mesh[i] = new Point(mesh[i]);
  }
  
  protected String getImageName()
  {
    return imageName;
  }

  protected BufferedImage getBufferedImage()
  {
    return bi;
  }
  
  protected Point[] getMesh()
  {
    Point[] tmp = new Point[mesh.length];
    for (int i = 0; i < mesh.length; i++)
      tmp[i] = new Point(mesh[i]);
    return tmp;
  }
}
