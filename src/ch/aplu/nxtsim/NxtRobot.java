// NxtRobot.java

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
import java.awt.*;
import java.util.*;
import javax.swing.JOptionPane;
import java.lang.reflect.*;
import java.io.*;

/**
 * Class that represents a simulated NXT robot brick. Parts (e.g. motors, sensors) may
 * be assembled into the robot to make it doing the desired job. Each instance
 * creates its own square playground (501 x 501 pixels). Some initial conditions may be modified by
 * calling static methods of the class NxtContext in a static block. A typical example
 * is:<br><br>
 * <code>
 <font color="#0000ff">import</font><font color="#000000">&nbsp;ch.aplu.nxtsim.</font><font color="#c00000">*</font><font color="#000000">;</font><br>
 <font color="#000000"></font><br>
 <font color="#0000ff">public</font><font color="#000000">&nbsp;</font><font color="#0000ff">class</font><font color="#000000">&nbsp;Example</font><br>
 <font color="#000000">{</font><br>
 <font color="#000000">&nbsp;&nbsp;</font><font color="#0000ff">static</font><br>
 <font color="#000000">&nbsp;&nbsp;</font><font color="#000000">{</font><br>
 <font color="#000000">&nbsp;&nbsp;&nbsp;&nbsp;NxtContext.</font><font color="#000000">setStartPosition</font><font color="#000000">(</font><font color="#000000">100</font><font color="#000000">,&nbsp;</font><font color="#000000">100</font><font color="#000000">)</font><font color="#000000">;</font><br>
 <font color="#000000">&nbsp;&nbsp;&nbsp;&nbsp;NxtContext.</font><font color="#000000">setStartDirection</font><font color="#000000">(</font><font color="#000000">45</font><font color="#000000">)</font><font color="#000000">;</font><br>
 <font color="#000000">&nbsp;&nbsp;</font><font color="#000000">}</font><br>
 <font color="#000000"></font><br>
 <font color="#000000">&nbsp;&nbsp;</font><font color="#0000ff">public</font><font color="#000000">&nbsp;</font><font color="#000000">Example</font><font color="#000000">()</font><br>
 <font color="#000000">&nbsp;&nbsp;</font><font color="#000000">{</font><br>
 <font color="#000000">&nbsp;&nbsp;&nbsp;&nbsp;NxtRobot&nbsp;robot&nbsp;</font><font color="#c00000">=</font><font color="#000000">&nbsp;</font><font color="#0000ff">new</font><font color="#000000">&nbsp;</font><font color="#000000">NxtRobot</font><font color="#000000">()</font><font color="#000000">;</font><br>
 <font color="#000000">&nbsp;&nbsp;&nbsp;&nbsp;Gear&nbsp;gear&nbsp;</font><font color="#c00000">=</font><font color="#000000">&nbsp;</font><font color="#0000ff">new</font><font color="#000000">&nbsp;</font><font color="#000000">Gear</font><font color="#000000">()</font><font color="#000000">;</font><br>
 <font color="#000000">&nbsp;&nbsp;&nbsp;&nbsp;robot.</font><font color="#000000">addPart</font><font color="#000000">(</font><font color="#000000">gear</font><font color="#000000">)</font><font color="#000000">;</font><br>
 <font color="#000000">&nbsp;&nbsp;&nbsp;&nbsp;gear.</font><font color="#000000">forward</font><font color="#000000">(</font><font color="#000000">5000</font><font color="#000000">)</font><font color="#000000">;</font><br>
 <font color="#000000">&nbsp;&nbsp;&nbsp;&nbsp;robot.</font><font color="#000000">exit</font><font color="#000000">()</font><font color="#000000">;</font><br>
 <font color="#000000">&nbsp;&nbsp;</font><font color="#000000">}</font><br>
 <font color="#000000"></font><br>
 <font color="#000000">&nbsp;&nbsp;</font><font color="#0000ff">public</font><font color="#000000">&nbsp;</font><font color="#0000ff">static</font><font color="#000000">&nbsp;</font><font color="#0000ff">void</font><font color="#000000">&nbsp;</font><font color="#000000">main</font><font color="#000000">(</font><font color="#00008b">String</font><font color="#000000">[]</font><font color="#000000">&nbsp;args</font><font color="#000000">)</font><br>
 <font color="#000000">&nbsp;&nbsp;</font><font color="#000000">{</font><br>
 <font color="#000000">&nbsp;&nbsp;&nbsp;&nbsp;</font><font color="#0000ff">new</font><font color="#000000">&nbsp;</font><font color="#000000">Example</font><font color="#000000">()</font><font color="#000000">;</font><br>
 <font color="#000000">&nbsp;&nbsp;</font><font color="#000000">}</font><br>
 <font color="#000000">}</font><br>
 * </code><br><br>
 * In principle you may remove the static header and use the program unmodified
 * for the real NXT robot using the NxtJLib or NxtJLibA library (see www.aplu.ch/nxt).<br><br>
 *
 * Because NxtRobot extends Actor all public methods of Actor are exposed. Some
 * of them are overridden and
 */
public class NxtRobot
{
  private class Nxt extends Actor
    implements GGActorCollisionListener, GGExitListener
  {
    private Nxt(Location startLocation, double startDirection)
    {
      super(true, "sprites/nxtrobot.gif");  // Rotatable
      gg.setSimulationPeriod(SharedConstants.simulationPeriod);
      if (NxtContext.xLoc > 0 && NxtContext.yLoc > 0)
        gg.setLocation(NxtContext.xLoc, NxtContext.yLoc);
      gg.setBgColor(Color.white);
      gg.setTitle(title);
      gg.removeAllActors();

      int nbObstacles = NxtContext.obstacles.size();
      for (int i = 0; i < nbObstacles; i++)
      {
        gg.addActorNoRefresh(NxtContext.obstacles.get(i),
          NxtContext.obstacleLocations.get(i));
      }
      int nbTargets = NxtContext.targets.size();
      for (int i = 0; i < nbTargets; i++)
      {
        gg.addActorNoRefresh(NxtContext.targets.get(i),
          NxtContext.targetLocations.get(i));
      }

      gg.addActorNoRefresh(this, startLocation, startDirection);
      pos = new GGVector(getLocation().x, getLocation().y); // Double coordinates
      
      wheelDistance = getHeight(0) - 10;
      addActorCollisionListener(this);
      setCollisionCircle(collisionCenter, collisionRadius);

      gg.addExitListener(this);
      gg.show();
      if (NxtContext.isRun)
        gg.doRun();
      Class appClass = null;
      try
      {
        appClass = Class.forName(new Throwable().getStackTrace()[3].getClassName());
        if (appClass.toString().indexOf("TurtleRobot") != -1)
          appClass = Class.forName(new Throwable().getStackTrace()[4].getClassName());
      }
      catch (Exception ex)
      {
      }
      if (appClass != null)
        exec(appClass, gg, "_init");
    }

    public int collide(Actor actor1, Actor actor2)
    {
      gg.setTitle("Robot-Obstacle Collision");
      isCollisionInfo = true;
      if (collisionListener != null && isCollisionTriggerEnabled)
      { 
        new Thread(new Runnable()
        {
          public void run()
          {
            isCollisionTriggerEnabled = false;
            collisionListener.collide();
            isCollisionTriggerEnabled = true;
          }
        }).start();
      }
      return 0;
    }
    
    public boolean notifyExit()
    {
      exit();
      switch (GameGrid.getClosingMode())
      {
        case TerminateOnClose:
          gg.stopGameThread();
          System.exit(0);
          break;
        case AskOnClose:
          if (JOptionPane.showConfirmDialog(gg.getFrame(),
            "Terminating program. Are you sure?",
            "Please confirm",
            JOptionPane.YES_NO_OPTION) == JOptionPane.YES_OPTION)
          {
            gg.stopGameThread();
            System.exit(0);
          }
          break;
        case DisposeOnClose:
          gg.dispose();
          break;
        case NothingOnClose:
          break;
      }
      return false;
    }

    private void exec(Class appClass, GameGrid gg, String methodName)
    {
      Method execMethod = null;

      Method methods[] = appClass.getDeclaredMethods();
      for (int i = 0; i < methods.length; ++i)
      {
        if (methodName.equals(methods[i].getName()))
        {
          execMethod = methods[i];
          break;
        }
      }
      if (execMethod == null)
        return;

      execMethod.setAccessible(true);
      try
      {
        execMethod.invoke(this, new Object[]
          {
            gg
          });
      }
      catch (IllegalAccessException ex)
      {
//        System.out.println("method not accessible");
      }
      catch (IllegalArgumentException ex)
      {
        //       System.out.println("wrong parameter signature");
      }
      catch (InvocationTargetException ex)
      {
        StringWriter sw = new StringWriter();
        PrintWriter pw = new PrintWriter(sw);
        ex.getTargetException().printStackTrace(pw);
        JOptionPane.showMessageDialog(null, sw.toString()
          + "\n\nApplication will terminate.", "Fatal Error",
          JOptionPane.ERROR_MESSAGE);
        System.exit(0);
      }
    }

    public void reset()
    {
      pos = new GGVector(getLocationStart().x, getLocationStart().y); // Double coordinates
    }

    public void act()
    {
      synchronized (NxtRobot.class)
      {
        if (!title.equals("") && isCollisionInfo)
        {
          gg.setTitle("");
        }
        // Add new obstacles as collision actor
        int nb = NxtContext.obstacles.size();
        if (nb > nbObstacles)
        {
          for (int i = nb - 1; i >= nbObstacles; i--)
            addCollisionActor(NxtContext.obstacles.get(i));
          nbObstacles = nb;
        }

        // ------------------ We notify light listeners -------------
        for (Part part : parts)
        {
          if (part instanceof LightSensor)
            ((LightSensor)part).notifyEvent();
        }

        // ------------------ We notify ultrasonic listeners -------------
        for (Part part : parts)
        {
          if (part instanceof UltrasonicSensor)
            ((UltrasonicSensor)part).notifyEvent();
        }

        Gear gear = (Gear)(gg.getOneActor(Gear.class));
        ArrayList<Actor> motors = gg.getActors(Motor.class);
        if (gear != null && !motors.isEmpty())
          fail("Error constructing NxtRobot" + "\nCannot add both Gear and Motor." + "\nApplication will terminate.");

        // ------------------ We have a gear --------------------
        if (gear != null)
        {
          int speed = gear.getSpeed();
          if (currentSpeed != speed)
            setCurrentSpeed(speed);
          if (speed == 0)
            return;
          Gear.GearState state = gear.getState();
          double radius = gear.getRadius();
          if (state != oldGearState || radius != oldRadius)  // State change
          {
            oldGearState = state;
            oldRadius = radius;
            if (state == state.LEFT)
            {
              initRot(-Math.abs(radius));
              dphi = -SharedConstants.gearRotIncFactor * speed / radius;
            }
            if (state == state.RIGHT)
            {
              initRot(Math.abs(radius));
              dphi = SharedConstants.gearRotIncFactor * speed / radius;
            }
          }
          switch (state)
          {
            case FORWARD:
              advance(SharedConstants.nbSteps);
              break;
            case BACKWARD:
              advance(-SharedConstants.nbSteps);
              break;
            case LEFT:
              if (gear.getRadius() == 0)
              {
                dphi = SharedConstants.gearTurnAngle * speed / 50;
                turn(-dphi);
              }
              else
              {
                pos = getRotatedPosition(pos, rotCenter, dphi);
                setLocation(new Location((int)(pos.x), (int)(pos.y)));
                dir += dphi;
                setDirection(dir);
              }
              break;
            case RIGHT:
              if (gear.getRadius() == 0)
              {
                dphi = SharedConstants.gearTurnAngle * speed / 50;
                turn(dphi);
              }
              else
              {
                pos = getRotatedPosition(pos, rotCenter, dphi);
                setLocation(new Location((int)(pos.x), (int)(pos.y)));
                dir += dphi;
                setDirection(dir);
              }
              break;
          }
        }

        // ------------------ We have a two motors --------------
        if (!motors.isEmpty() && motors.size() == 2)
        {
          Motor motorA = (Motor)motors.get(0);
          Motor motorB = (Motor)motors.get(1);
          int speedA = motorA.getSpeed();
          int speedB = motorB.getSpeed();
          if (speedA == 0 && speedB == 0)
            return;
          MotorState stateA = motorA.getState();
          MotorState stateB = motorB.getState();
          double radius;

          if (stateA != oldMotorStateA || stateB != oldMotorStateB || speedA != oldSpeedA || speedB != oldSpeedB)  // State change
          {
            oldMotorStateA = stateA;
            oldMotorStateB = stateB;
            oldSpeedA = speedA;
            oldSpeedB = speedB;
            setCurrentSpeed((speedA + speedB) / 2);
            isRotationInit = true;
          }

          if (stateA == MotorState.FORWARD && stateB == MotorState.FORWARD)
          {
            if (speedA == speedB)
              advance(SharedConstants.nbSteps);
            else
            {
              if (isRotationInit)
              {
                isRotationInit = false;
                sign = (speedA > speedB ? -1 : 1);
                radius = wheelDistance / 2.0 * (speedA + speedB) / Math.abs(speedB - speedA);
                initRot(sign * radius);
                rotInc = SharedConstants.motorRotIncFactor * (speedA + speedB) / radius;
              }
              double rot = sign * rotInc;
              pos = getRotatedPosition(pos, rotCenter, rot);
              setLocation(new Location((int)(pos.x), (int)(pos.y)));
              dir += rot;
              setDirection(dir);
            }
          }
          if (stateA == MotorState.BACKWARD && stateB == MotorState.BACKWARD)
          {
            if (speedA == speedB)
              advance(-SharedConstants.nbSteps);
            else
            {
              if (isRotationInit)
              {
                isRotationInit = false;
                sign = (speedA > speedB ? -1 : 1);
                radius = wheelDistance / 2.0 * (speedA + speedB) / Math.abs(speedA - speedB);
                initRot(sign * radius);
                rotInc = SharedConstants.motorRotIncFactor * (speedA + speedB) / radius;
              }
              double rot = -sign * rotInc;
              pos = getRotatedPosition(pos, rotCenter, rot);
              setLocation(new Location((int)(pos.x), (int)(pos.y)));
              dir += rot;
              setDirection(dir);
            }
          }
          if (stateA == MotorState.FORWARD && stateB == MotorState.BACKWARD)
          {
            if (speedA == speedB)
              turn(-(int)(speedA / 60.0 * SharedConstants.motTurnAngle));
            else
            {
              if (isRotationInit)
              {
                isRotationInit = false;
                sign = (speedA > speedB ? -1 : 1);
                radius = wheelDistance / 200.0 * Math.abs(speedA - speedB);
                initRot(sign * radius);
                rotInc = SharedConstants.motorRotIncFactor * Math.max(speedA, speedB) / (wheelDistance + radius);
              }
              double rot = -rotInc;
              pos = getRotatedPosition(pos, rotCenter, rot);
              setLocation(new Location((int)(pos.x), (int)(pos.y)));
              dir += rot;
              setDirection(dir);
            }
          }
          if (stateA == MotorState.BACKWARD && stateB == MotorState.FORWARD)
          {
            if (speedA == speedB)
              turn((int)(speedA / 60.0 * SharedConstants.motTurnAngle));
            else
            {
              if (isRotationInit)
              {
                isRotationInit = false;
                sign = (speedA > speedB ? -1 : 1);
                radius = wheelDistance / 200.0 * Math.abs(speedA - speedB);
                initRot(sign * radius);
                rotInc = SharedConstants.motorRotIncFactor * Math.max(speedA, speedB) / (wheelDistance - Math.abs(radius));
              }
              double rot = rotInc;
              pos = getRotatedPosition(pos, rotCenter, rot);
              setLocation(new Location((int)(pos.x), (int)(pos.y)));
              dir += rot;
              setDirection(dir);
            }
          }
          if (stateA == MotorState.FORWARD && stateB == MotorState.STOPPED)
          {
            if (isRotationInit)
            {
              isRotationInit = false;
              radius = wheelDistance / 2;
              initRot(-radius);
              rotInc = SharedConstants.motorRotIncFactor * speedA / radius;
            }
            double rot = -rotInc;
            pos = getRotatedPosition(pos, rotCenter, rot);
            setLocation(new Location((int)(pos.x), (int)(pos.y)));
            dir += rot;
            setDirection(dir);
          }
          if (stateA == MotorState.BACKWARD && stateB == MotorState.STOPPED)
          {
            if (isRotationInit)
            {
              isRotationInit = false;
              radius = wheelDistance / 2;
              initRot(-radius);
              rotInc = SharedConstants.motorRotIncFactor * speedA / radius;
            }
            double rot = rotInc;
            pos = getRotatedPosition(pos, rotCenter, rot);
            setLocation(new Location((int)(pos.x), (int)(pos.y)));
            dir += rot;
            setDirection(dir);
          }
          if (stateA == MotorState.STOPPED && stateB == MotorState.FORWARD)
          {
            if (isRotationInit)
            {
              isRotationInit = false;
              radius = wheelDistance / 2;
              initRot(radius);
              rotInc = SharedConstants.motorRotIncFactor * speedB / radius;
            }
            double rot = rotInc;
            pos = getRotatedPosition(pos, rotCenter, rot);
            setLocation(new Location((int)(pos.x), (int)(pos.y)));
            dir += rot;
            setDirection(dir);
          }
          if (stateA == MotorState.STOPPED && stateB == MotorState.BACKWARD)
          {
            if (isRotationInit)
            {
              isRotationInit = false;
              radius = wheelDistance / 2;
              initRot(radius);
              rotInc = SharedConstants.motorRotIncFactor * speedB / radius;
            }
            double rot = -rotInc;
            pos = getRotatedPosition(pos, rotCenter, rot);
            setLocation(new Location((int)(pos.x), (int)(pos.y)));
            dir += rot;
            setDirection(dir);
          }
        }
      }
    }

    private void advance(int nbSteps)
    {
      pos = pos.add(
        new GGVector(nbSteps * Math.cos(Math.toRadians(getDirection())),
        nbSteps * Math.sin(Math.toRadians(getDirection()))));
      setLocation(new Location((int)(pos.x + 0.5), (int)(pos.y + 0.5)));
    }

    private void initRot(double radius)
    {
      GGVector v = new GGVector(getLocation().x, getLocation().y);
      GGVector vDir = new GGVector(
        -Math.sin(Math.toRadians(getDirection())),
        +Math.cos(Math.toRadians(getDirection())));
      GGVector vCenter = v.add(vDir.mult(radius));
      rotCenter = new Point((int)vCenter.x, (int)vCenter.y);
      pos = new GGVector(getLocation().x, getLocation().y);
      dir = getDirection();
    }

    public void turn(double angle)
    {
      synchronized (NxtRobot.class)
      {
        super.turn(angle);
        for (Part p : parts)
        {
          p.turn(angle);
          p.setLocation(getPartLocation(p));
        }
      }
    }

    public void setLocation(Location loc)
    {
      synchronized (NxtRobot.class)
      {
        super.setLocation(loc);
        for (Part p : parts)
          p.setLocation(getPartLocation(p));
      }
    }

    public void setDirection(double dir)
    {
      synchronized (NxtRobot.class)
      {
        super.setDirection(dir);
        for (Part p : parts)
        {
          p.setLocation(getPartLocation(p));
          p.setDirection(dir);
        }
      }
    }

    public Location getPartLocation(Part part)
    {
      Location pos = part.getPosition();
      double r = Math.sqrt(pos.x * pos.x + pos.y * pos.y);
      double phi = Math.atan2(pos.y, pos.x);
      double dir = getDirection() * Math.PI / 180;
      Location loc = new Location(
        (int)(Math.round(getX() + r * Math.cos(dir + phi))),
        (int)(Math.round(getY() + r * Math.sin(dir + phi))));
      return loc;
    }

    private void setCurrentSpeed(int speed)
    {
      if (speed < 0)
      {
        speed = 0;
      }
      if (speed > 100)
        speed = 100;
      currentSpeed = speed;

      // period = m * speed + n;
      // speed values
      int a = 100;
      int b = 10;
      // corresponding period values
      int u = 30;
      int v = 150;

      double m = (v - u) / (double)(b - a);
      double n = (u * b - a * v) / ((double)(b - a));
      int period = (int)(m * speed + n);
      gameGrid.setSimulationPeriod(period);
//    System.out.println("new period: " + period);
    }

  }
  // ---------------------- End of class Nxt ---------------------

  // ---------------------- Class Interceptor --------------------
  private class Interceptor extends PrintStream
  {
    public Interceptor(OutputStream out)
    {
      super(out, true);
    }

    /**
     * Print a boolean value.
     */
    public void print(boolean b)
    {
      gg.setStatusText("" + b);
    }

    /**
     * Print a character.
     */
    public void print(char c)
    {
      gg.setStatusText("" + c);
    }

    /**
     * Print an array of characters.
     */
    public void print(char[] s)
    {
      StringBuffer sbuf = new StringBuffer();
      for (int i = 0; i < s.length; i++)
        sbuf.append(s[i]);
      gg.setStatusText(sbuf.toString());
    }

    /**
     * Print a double-precision floating-point number.
     */
    public void print(double d)
    {
      gg.setStatusText("" + d);
    }

    /**
     * Print a floating-point number.
     */
    public void print(float f)
    {
      gg.setStatusText("" + f);
    }

    /**
     * Print an integer.
     */
    public void print(int i)
    {
      gg.setStatusText("" + i);
    }

    /**
     * Print a long integer.
     */
    public void print(long l)
    {
      gg.setStatusText("" + l);
    }

    /**
     * Print an object.
     */
    public void print(Object obj)
    {
      gg.setStatusText(obj.toString());
    }

    /**
     * Print a string.
     */
    public void print(String s)
    {
      gg.setStatusText(s);
    }

    /**
     *  Terminate the current line by writing the line separator string.
     */
    public void println()
    {
      gg.setStatusText("\n");
    }

    /**
     * Print a boolean and then terminate the line.
     */
    public void println(boolean b)
    {
      gg.setStatusText(b + "\n");
    }

    /**
     * Print a character and then terminate the line.
     */
    public void println(char c)
    {
      gg.setStatusText(c + "\n");
    }

    /**
     * Print an array of characters and then terminate the line.
     */
    public void println(char[] s)
    {
      StringBuffer sbuf = new StringBuffer();
      for (int i = 0; i < s.length; i++)
        sbuf.append(s[i]);
      gg.setStatusText(sbuf.toString() + "\n");
    }

    /**
     * Print a double and then terminate the line.
     */
    public void println(double d)
    {
      gg.setStatusText(d + "\n");
    }

    /**
     * Print a float and then terminate the line.
     */
    public void println(float f)
    {
      gg.setStatusText(f + "\n");
    }

    /**
     * Print an integer and then terminate the line.
     */
    public void println(int i)
    {
      gg.setStatusText(i + "\n");
    }

    /**
     * Print a long and then terminate the line.
     */
    public void println(long l)
    {
      gg.setStatusText(l + "\n");
    }

    /**
     * Print an Object and then terminate the line.
     */
    public void println(Object obj)
    {
      gg.setStatusText(obj.toString() + "\n");
    }

    /**
     * Print a String and then terminate the line.
     */
    public void println(String s)
    {
      gg.setStatusText(s + "\n");
    }

    /**
     * Print a formatted string using the specified format string and varargs.
     * (See PrintStream.printf() for more information)
     * @return the PrintStream reference
     */
    public PrintStream printf(String format, Object... args)
    {
      gg.setStatusText(String.format(format, args));
      return this;
    }

    /**
     * Print a formatted string using the specified format string and varargs
     * and applying given locale during formatting.
     * (See PrintStream.printf() for more information)
     * @return the PrintStream reference
     */
    public PrintStream printf(Locale l, String format, Object... args)
    {
      gg.setStatusText(String.format(l, format, args));
      return this;
    }

  }
  // ---------------------- End of class Interceptor -------------

  /**
   * Center of a circle to detect robot-obstacle collisions
   * (pixel coordinates relative to center of robot image, default: (-13, 0)).
   */
  public static Point collisionCenter = new Point(-13, 0);
  /**
   * Radius of a circle to detect robot-obstacle collisions
   * (in pixels, default: 20).
   */
  public static int collisionRadius = 16;
  //
  private final int nbRotatableSprites = 360;
  private static GameGrid gg;
  private static Nxt nxt;
  private int nbObstacles = 0;
  private String title = "NxtSim V"
    + SharedConstants.VERSION.substring(0, SharedConstants.VERSION.indexOf(" "));
  private ArrayList<Part> parts = new ArrayList<Part>();
  private double rotInc;
  private int currentSpeed;
  private MotorState oldMotorStateA = MotorState.STOPPED;
  private MotorState oldMotorStateB = MotorState.STOPPED;
  private int oldSpeedA = -1;
  private int oldSpeedB = -1;
  private boolean isRotationInit = true;
  private int wheelDistance;
  private Gear.GearState oldGearState = Gear.GearState.STOPPED;
  private Point rotCenter;
  private GGVector pos;
  private double dir;
  private int sign;
  private double oldRadius;
  private double dphi;
  private boolean isCollisionInfo = false;
  private CollisionListener collisionListener = null;
  private boolean isCollisionTriggerEnabled = true;

  /**
   * Creates a robot with its playground using defaults from NxtContext.
   */
  public NxtRobot()
  {
    gg = new GameGrid(500, 500, 1, null,
      NxtContext.imageName, NxtContext.isNavigationBar, nbRotatableSprites);
    nxt = new Nxt(NxtContext.startLocation, NxtContext.startDirection);
    ViewingCone.init();
    if (NxtContext.isStatusBar)
    {
      gg.addStatusBar(NxtContext.statusBarHeight);
      PrintStream originOut = System.out;
      PrintStream interceptor = new Interceptor(originOut);
      System.setOut(interceptor);
    }
  }

  /**
   * Assembles the given part into the robot.
   * @param part the part to assemble
   */
  public void addPart(Part part)
  {
    synchronized (NxtRobot.class)
    {
      part.setRobot(this);
      parts.add(part);
      gg.addActorNoRefresh(part, nxt.getPartLocation(part), nxt.getDirection());
      gg.setPaintOrder(getClass(), part.getClass());  // On top of obstacles
      gg.setActOrder(getClass());  // First
    }
  }

  /**
   * Returns the instance reference of the GameGrid.
   * @return the reference of the GameGrid
   */
  public static GameGrid getGameGrid()
  {
    return gg;
  }

  /**
   * Returns the instance reference of the Nxt actor.
   * @return the reference of the Nxt
   */
  public static Actor getNxt()
  {
    return nxt;
  }

  /**
   * Stops any motion and performs a cleanup of all parts.
   */
  public void exit()
  {
    synchronized (NxtRobot.class)
    {
      for (Part p : parts)
      {
        p.cleanup();
      }
    }
    gg.doPause();
  }

  /**
   * Returns the current library version.
   * @return a string telling the current version
   */
  public static String getVersion()
  {
    return SharedConstants.VERSION;
  }

  protected static void fail(String message)
  {
    JOptionPane.showMessageDialog(null, message, "Fatal Error", JOptionPane.ERROR_MESSAGE);
    if (GameGrid.getClosingMode() == GameGrid.ClosingMode.TerminateOnClose
      || GameGrid.getClosingMode() == GameGrid.ClosingMode.AskOnClose)
      System.exit(0);
  }

  /**
   * Resets Nxt to start location/direction.
   */
  public void reset()
  {
    Actor nxt = getNxt();
    nxt.reset();
    nxt.setLocation(nxt.getLocationStart());
    nxt.setDirection(nxt.getDirectionStart());
  }

  /**
   * Adds the given target in the target list and shows it at the given 
   * location. If the target is already in the target list, it is first removed.
   * @param target the target to add
   * @param x the x location of the target center
   * @param y the y location of the target center
   */
  public void addTarget(Target target, int x, int y)
  {
    synchronized (NxtContext.targets)
    {
      if (NxtContext.targets.contains(target))
      {
        removeTarget(target);
      }
      gg.addActorNoRefresh(target, new Location(x, y));
      NxtContext.targets.add(target);
      // targetLocations not used
    }
  }

  /**
   * Removes the given target from the target list and hides it.
   * If the target is not part of the target list, nothing happens.
   * @param target the target to remove
   */
  public void removeTarget(Target target)
  {
    synchronized (NxtContext.targets)
    {
      Location l = target.getLocation();
      GGBackground bg = gg.getBg();
      ViewingCone.eraseCone(bg);
      ViewingCone.eraseProximityCircle(bg);
      Color oldPaintColor = bg.getPaintColor();
      bg.setPaintColor(bg.getBgColor());
      Point[] mesh = target.getMesh();
      Point[] clearMesh = new Point[mesh.length];
      for (int i = 0; i < mesh.length; i++)
      {
        clearMesh[i] = new Point(mesh[i].x + l.x, mesh[i].y + l.y);
      }
      bg.fillPolygon(clearMesh);
      bg.setPaintColor(oldPaintColor);
      gg.removeActor(target);
      NxtContext.targets.remove(target);
    }
  }

  /**
   * Adds the given obstacle in the obstacle list and shows it at the given 
   * location. If the obstacle is already in the obstacle list, it is first removed.
   * @param obstacle the obstacle to add
   * @param x the x location of the target center
   * @param y the y location of the target center
   */
  public void addObstacle(Obstacle obstacle, int x, int y)
  {
    synchronized (NxtContext.obstacles)
    {
      if (NxtContext.obstacles.contains(obstacle))
      {
        removeObstacle(obstacle);
      }
      gg.addActorNoRefresh(obstacle, new Location(x, y));
      NxtContext.obstacles.add(obstacle);
      // obstacleLocations not used
    }
  }

  /**
   * Removes the given obstacle from the obstacle list and hides it.
   * If the obstacle is not part of the obstacle list, nothing happens.
   * @param obstacle the obstacle to remove
   */
  public void removeObstacle(Obstacle obstacle)
  {
    synchronized (NxtContext.obstacles)
    {
      gg.removeActor(obstacle);
      NxtContext.obstacles.remove(obstacle);
    }
  }
  
  /**
   * Registers a robot-obtacle collision listener that fires
   * the collide callback when the circumcircle of the robot overlaps
   * with an obstacle.
   * @param listener the CollisionLister to register
   */
  public void addCollisionListener(CollisionListener listener)
  {
    collisionListener = listener;
  }

}
