
package krakroboteliminacje;
import ch.aplu.nxtsim.TouchSensor;
import ch.aplu.nxtsim.SensorPort;
import ch.aplu.nxtsim.NxtContext;
import ch.aplu.nxtsim.NxtRobot;
import ch.aplu.nxtsim.Gear;
import ch.aplu.nxtsim.*;

/*
 * 
 */
class KrakrobotNxtContext{
    
}

public class KrakrobotEliminacje
{
  static
  {
    NxtContext.showNavigationBar();
    NxtContext.useObstacle("sprites/bar0.gif", 250, 200);
    NxtContext.useObstacle("sprites/bar1.gif", 400, 250);
    NxtContext.useObstacle("sprites/bar2.gif", 250, 400);
    NxtContext.useObstacle("sprites/bar3.gif", 100, 250);
  }

  public KrakrobotEliminacje()
  {
    NxtRobot robot = new NxtRobot();
    Gear gear = new Gear();
    TouchSensor ts = new TouchSensor(SensorPort.S3);
    robot.addPart(gear);
    robot.addPart(ts);
    gear.setSpeed(30);
    gear.forward();
    while (true)
    {
      if (ts.isPressed())
      {
        gear.backward(1200);
        gear.left(750);
        gear.forward();
      }
    }
  }

  public static void main(String[] args)
  {
    new KrakrobotEliminacje();
  }
}