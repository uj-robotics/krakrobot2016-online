// ColorSensor.java

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
import java.awt.Color;
import javax.swing.JOptionPane;

/**
 * Class that represents a color sensor.
 */
public class ColorSensor extends Part
{
  private static final Location pos1 = new Location(8, 7);
  private static final Location pos2 = new Location(8, -7);
  private static final Location pos3 = new Location(8, 0);
  private static final Location pos4 = new Location(-35, 0);
  private SensorPort port;

  /**
   * Creates a sensor instance connected to the given port.
   * The port selection determines the position of the sensor:
   * S1: right; S2: left, S3: middle, S4: rear-middle.
   * @param port the port where the sensor is plugged-in
   */
  public ColorSensor(SensorPort port)
  {
    super("sprites/colorsensor"
      + (port == SensorPort.S1 ? ".gif"
      : (port == SensorPort.S2 ? ".gif"
      : (port == SensorPort.S3 ? ".gif" : "_rear.gif"))),
      port == SensorPort.S1 ? pos1
      : (port == SensorPort.S2 ? pos2
      : (port == SensorPort.S3 ? pos3 : pos4)));
    this.port = port;
  }

  /**
   * Creates a sensor instance connected to port S1.
   */
  public ColorSensor()
  {
    this(SensorPort.S1);
  }

  protected void cleanup()
  {
  }

  /**
   * Returns the brightness (scaled intensity in the HSB color model)
   * detected by the light sensor at the current location.
   * Calls Thread.sleep(1) to prevent CPU overload in close polling loops.
   * @return the brightness of the background color at the current location
   * (0..1000, 0: dark, 1000: bright).
   */
  public int getLightValue()
  {
    checkPart();
    Tools.delay(1);
    Color c = getBackground().getColor(getLocation());
    float[] hsb = new float[3];
    Color.RGBtoHSB(c.getRed(), c.getGreen(), c.getBlue(), hsb);
    return (int)(1000 * hsb[2]);
  }

  /**
   * Returns the color detected by the color sensor at the current location.
   * Calls Thread.sleep(1) to prevent CPU overload in close polling loops.
   * @return the background color at the current location
   */
  public Color getColor()
  {
    checkPart();
    Tools.delay(1);
    return getBackground().getColor(getLocation());
  }

  /**
   * Returns the port of the sensor.
   * @return the sensor port
   */
  public SensorPort getPort()
  {
    return port;
  }

  private void checkPart()
  {
    if (robot == null)
    {
      JOptionPane.showMessageDialog(null,
        "ColorSensor is not part of the NxtRobot.\n"
        + "Call addPart() to assemble it.",
        "Fatal Error", JOptionPane.ERROR_MESSAGE);
      System.exit(1);
    }
  }
}
