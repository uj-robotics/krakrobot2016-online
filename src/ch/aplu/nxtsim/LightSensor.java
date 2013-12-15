// LightSensor.java

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
 * Class that represents a light sensor.
 */
public class LightSensor extends Part
{
  private static final Location pos1 = new Location(8, 7);
  private static final Location pos2 = new Location(8, -7);
  private static final Location pos3 = new Location(8, 0);
  private static final Location pos4 = new Location(-35, 0);
  private volatile boolean isBrightNotified = false;
  private volatile boolean isDarkNotified = false;
  private LightListener lightListener = null;
  private SensorPort port;
  private int triggerLevel;

  /**
   * Creates a sensor instance connected to the given port.
   * The port selection determines the position of the sensor:
   * S1: right; S2: left, S3: middle, S4: rear-middle.
   * @param port the port where the sensor is plugged-in
   */
  public LightSensor(SensorPort port)
  {
    super("sprites/lightsensor"
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
  public LightSensor()
  {
    this(SensorPort.S1);
  }

  protected void cleanup()
  {
  }

  /**
   * Registers the given LightListener to detect crossing the given trigger triggerLevel.
   * @param listener the LightListener to register
   * @param triggerLevel the light value used as trigger level
   */
  public void addLightListener(LightListener listener, int triggerLevel)
  {
    lightListener = listener;
    this.triggerLevel = triggerLevel;
  }

  /**
   * Registers the given LightListener with default trigger triggerLevel 500.
   * @param lightListener the LightListener to register
   */
  public void addLightListener(LightListener lightListener)
  {
    addLightListener(lightListener, 500);
  }

  /**
   * Sets a new trigger triggerLevel and returns the previous one.
   * @param triggerLevel the new trigger triggerLevel
   * @return the previous trigger triggerLevel
   */
  public int setTriggerLevel(int triggerLevel)
  {
    int oldLevel = this.triggerLevel;
    this.triggerLevel = triggerLevel;
    return oldLevel;
  }

  /**
   * Returns the brightness (scaled intensity in the HSB color model)
   * detected by the light sensor at the current location.
   * Calls Thread.sleep(1) to prevent CPU overload in close polling loops.
   * @return the brightness of the background color at the current location
   * (0..1000, 0: dark, 1000: bright).
   */
  public int getValue()
  {
    checkPart();
    Tools.delay(1);
    Color c = getBackground().getColor(getLocation());
    float[] hsb = new float[3];
    Color.RGBtoHSB(c.getRed(), c.getGreen(), c.getBlue(), hsb);
    return (int)(1000 * hsb[2]);
  }

  /**
   * Turns on/off the LED used for reflecting light back into the sensor.
   * Empty method in simulation mode.
   * @param enable if true, turn the LED on, otherwise turn it off
   */
  public void activate(boolean enable)
  {
  }

  /**
   * Returns the port of the sensor.
   * @return the sensor port
   */
  public SensorPort getPort()
  {
    return port;
  }

  protected void notifyEvent()
  {
    if (lightListener == null)
      return;
    final int value = getValue();
    if (value < triggerLevel)
      isBrightNotified = false;
    if (value >= triggerLevel)
      isDarkNotified = false;
    if (value >= triggerLevel && !isBrightNotified)
    {
      isBrightNotified = true;
      new Thread()
      {
        public void run()
        {
          lightListener.bright(port, value);
        }
      }.start();
    }
    if (value < triggerLevel && !isDarkNotified)
    {
      isDarkNotified = true;
      new Thread()
      {
        public void run()
        {
          lightListener.dark(port, value);
        }
      }.start();
    }
  }

  private void checkPart()
  {
    if (robot == null)
    {
      JOptionPane.showMessageDialog(null,
        "LightSensor is not part of the NxtRobot.\n"
        + "Call addPart() to assemble it.",
        "Fatal Error", JOptionPane.ERROR_MESSAGE);
      System.exit(1);
    }
  }
}
