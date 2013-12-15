// UltrasonicSensor.java

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
import java.awt.Point;
import javax.swing.JOptionPane;

/**
 * Class that represents a ultrasonic sensor. The sensor detects targets
 * in a cone with the apex at the current NxtRobot location. The cone's axis 
 * orientation  may be selected using the port parameter (forward, 
 * left or backward  direction of the current NxtRobot direction). The beam
 * opening angle (beam width) is fixed to the value ultrasonicBeamWidth defined
 * in ShareConstants.java. Targets normally have a visible actor sprite image, but
 * the target detection algorithms does not use it. The detection is based on 
 * a mesh of triangles defined when the target is created.<br><br>
 * 
 * Targets may dynamically change (modification of their location, 
 * new targets added, existing targets removed) because the current target 
 * layout is used each time the getDistance() method is called.<br><br>
 * 
 * Only one ultrasonic sensor is supported.
 */
public class UltrasonicSensor extends Part
{
  private final double beamWidth =
    Math.toRadians(SharedConstants.ultrasonicBeamWidth);
  private static final Location pos = new Location(-18, -1);
  private UltrasonicListener ultrasonicListener = null;
  private SensorPort port;
  private int triggerLevel;
  private volatile boolean isFarNotified = false;
  private volatile boolean isNearNotified = false;
  private Color sectorColor = null;
  private Color meshTriangleColor = null;
  private Color proximityCircleColor = null;
 
  /**
   * The port selection determines the position of the sensor and
   * the direction of the beam axis.
   * S1: forward; S2: left, S3: backward.
   * Creates a sensor instance connected to the given port.
   * Only one sensor is allowed.
   * @param port the port where the sensor is plugged-in
   */
  public UltrasonicSensor(SensorPort port)
  {
    super("sprites/ultrasonicsensor" + (port == SensorPort.S1
      ? "1" : (port == SensorPort.S2 ? "2" : "3")) + ".gif", pos);
    this.port = port;
   }

  protected void cleanup()
  {
  }

  /**
   * Registers the given UltrasonicListener to detect crossing the given trigger triggerLevel.
   * @param listener the UltrasonicListener to register
   * @param triggerLevel the distance value used as trigger level
   */
  public void addUltrasonicListener(UltrasonicListener listener, int triggerLevel)
  {
    ultrasonicListener = listener;
    this.triggerLevel = triggerLevel;
  }

  /**
   * Registers the given UltrasonicListener with default trigger triggerLevel 100.
   * @param listener the UltrasonicListener to register
   */
  public void addUltrasonicListener(UltrasonicListener listener)
  {
    addUltrasonicListener(listener, 100);
  }

  /**
   * Sets a new trigger level and returns the previous one.
   * @param triggerLevel the new trigger level
   * @return the previous trigger level
   */
  public int setTriggerLevel(int triggerLevel)
  {
    int oldLevel = this.triggerLevel;
    this.triggerLevel = triggerLevel;
    return oldLevel;
  }

  /**
   * Returns the distance to the nearest target object. The distance must
   * be adapted to the real robot's environment (the real ultrasonic sensor
   * returns distances in cm in the range 0..255 (255 corresponds to no target 
   * detected).
   * @return the distance (in pixels of the 501x501 pixel window); 
   * -1 of no target in range or robot inside a target
   */
  public int getDistance()
  {
    checkPart();
    Tools.delay(1);
    synchronized (NxtContext.targets)
    {
      int value = -1;
      Location loc = getLocation();
      double direction = getDirection() + 
        (port == SensorPort.S1 ? 0 : (port == SensorPort.S2 ? -90 : 180));
      GGVector center = new GGVector(loc.x, loc.y);
      GGVector dir = new GGVector(1000 * Math.cos(Math.toRadians(direction)),
        1000 * Math.sin(Math.toRadians(direction)));
      dir = center.add(dir);
      ViewingCone cone = new ViewingCone(center, dir, beamWidth, true);
      if (sectorColor != null)
        cone.drawCone(gameGrid.getBg(), sectorColor);
      if (NxtContext.targets.size() == 0)  // No target
      {
        // Erase old proximityCircle when last target is removed
        if (proximityCircleColor != null)
          cone.drawProximityCircle(gameGrid.getBg(), value, proximityCircleColor);
      }
      else
      {
        for (Target target : NxtContext.targets)
        {
          // Triangles created dynamically, because target may change location
          Point[] mesh = target.getMesh();
          GGVector targetCenter = new GGVector(target.getX(), target.getY());
          int size = mesh.length;
          for (int i = 0; i < size - 1; i++)
          {
            Triangle t = new Triangle(
              targetCenter,
              targetCenter.add(new GGVector(mesh[i])),
              targetCenter.add(new GGVector(mesh[i + 1])));
            if (meshTriangleColor != null)
              t.drawTriangle(gameGrid.getBg(), meshTriangleColor);
            cone.addObstacle(t);
          }
          Triangle t = new Triangle(
            targetCenter,
            targetCenter.add(new GGVector(mesh[size - 1])),
            targetCenter.add(new GGVector(mesh[0])));
          if (meshTriangleColor != null)
            t.drawTriangle(gameGrid.getBg(), meshTriangleColor);
          cone.addObstacle(t);
          double measure = (int)cone.getDistanceToClosestObstacle();
          if (measure == 0)
            value = -1;
          else
            value = (int)(measure + 0.5);

          if (proximityCircleColor != null)
            cone.drawProximityCircle(gameGrid.getBg(), value, proximityCircleColor);
        }
      }
      return value;
    }
  }

  /**
   * Returns the port of the sensor.
   * @return the sensor port
   */
  public SensorPort getPort()
  {
    return port;
  }

  /**
   * Sets the color of the triangle mesh lines.
   * @param color the color of the mesh; if null, the mesh is not shown (default)
   */
  public void setMeshTriangleColor(Color color)
  {
    meshTriangleColor = color;
  }

  /**
   * Sets the color of the beam area (two sector border lines and axis).
   * @param color the color of the beam area; if null, the beam lines are not shown (default)
   */
  public void setBeamAreaColor(Color color)
  {
    sectorColor = color;
  }

  /**
   * Erases the beam area (if it is currently shown).
   */
  public void eraseBeamArea()
  {
    ViewingCone.eraseCone(gameGrid.getBg());
  }

  /**
   * Sets the color of the circle with center at sensor location and radius
   * equals to the current distance value. If value = 0, no circle is shown.
   * @param color the color of the circle; if null, the circle is not shown (default)
   */
  public void setProximityCircleColor(Color color)
  {
    proximityCircleColor = color;
  }

  protected void notifyEvent()
  {
    if (ultrasonicListener == null)
      return;
    int v = getDistance();
    final int value;
    if (v == -1)
      value = Integer.MAX_VALUE;
    else
      value = v;
    if (value < triggerLevel)
      isFarNotified = false;
    if (value >= triggerLevel)
      isNearNotified = false;
    if (value >= triggerLevel && !isFarNotified)
    {
      isFarNotified = true;
      new Thread()
      {
        public void run()
        {
          if (value == Integer.MAX_VALUE)
            ultrasonicListener.far(port, -1);
          else
            ultrasonicListener.far(port, value);
        }

      }.start();
    }
    if (value < triggerLevel && !isNearNotified)
    {
      isNearNotified = true;
      new Thread()
      {
        public void run()
        {
          ultrasonicListener.near(port, value);
        }

      }.start();
    }
  }

  private void checkPart()
  {
    if (robot == null)
    {
      JOptionPane.showMessageDialog(null,
        "UltrasonicSensor is not part of the NxtRobot.\n"
        + "Call addPath() to assemble it.",
        "Fatal Error", JOptionPane.ERROR_MESSAGE);
      System.exit(1);
    }
  }

}
