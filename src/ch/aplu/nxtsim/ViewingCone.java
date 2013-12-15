// ViewingCone.java
// Code by Stefan Moser

package ch.aplu.nxtsim;

import java.util.LinkedList;
import java.util.List;

import ch.aplu.jgamegrid.*;
import java.awt.Color;
import java.awt.Point;

class ViewingCone extends Triangle
{
  private LinkedList<IObstacle> obstacles;
  private LineSegment[] viewBoarderLines;
  private GGVector baseCenter;
  private boolean infinite;
  private GGVector apex;
  private static double apexAngle = 0;
  private static GGVector oldApex = null;
  private static GGVector oldBaseCenter = null;
  private static GGCircle oldCircle = null;

  /**
   * This constructor is mainly for testing, for real use see the other constructor
   */
  public ViewingCone(GGVector standPoint, GGVector b, GGVector c)
  {
    super(standPoint, b, c);
    this.obstacles = new LinkedList<IObstacle>();
    this.viewBoarderLines = new LineSegment[2];
    this.viewBoarderLines[0] = new LineSegment(standPoint, vertices[1].sub(standPoint));
    this.viewBoarderLines[1] = new LineSegment(standPoint, vertices[2].sub(standPoint));
    this.infinite = false;
  }

  /**
   * Initializes static instance variables.
   */
  public static void init()
  {
    oldApex = null;
    oldBaseCenter = null;
    oldCircle = null;
    apexAngle = 0;
  }

  /**
   * Creates a viewing cone located at standPoint, looking into the direction of baseCenter,
   * baseCenter also being the farthest visible point. The cone extends to apexAngle/2
   * to the left and apexAngle/2 to the right of baseCenter.
   * </br>
   * Be aware that there may be problems with double precision when using this 
   * constructor. 
   * @param standPoint
   * @param baseCenter
   * @param apexAngle in radian
   * @param infinite Set to true if the farthest visible point lies in infinity
   */
  public ViewingCone(GGVector standPoint, GGVector lookAtPoint, double angle, boolean infinite)
  {
    this(standPoint,
      makeCorner(standPoint, lookAtPoint, angle / 2),
      makeCorner(standPoint, lookAtPoint, -angle / 2));
    this.baseCenter = lookAtPoint;
    this.apexAngle = angle;
    this.apex = standPoint;
    this.infinite = infinite;
    for (LineSegment ls : viewBoarderLines)
      ls.setInfinite(infinite);
  }

  private static GGVector makeCorner(GGVector standPoint, GGVector lookAtPoint,
    double angle)
  {
    GGVector corner = lookAtPoint.sub(standPoint);
    corner.rotate(angle);
    corner = corner.add(standPoint);
    return corner;
  }

  public void addObstacle(IObstacle o)
  {
    obstacles.add(o);
  }

  public void addObstacles(List<IObstacle> oList)
  {
    obstacles.addAll(oList);
  }

  /**
   * Returns closest point of any obstacles added to this Viewing cone. 
   * Returns null if there is no obstacle visible. 
   * @return
   */
  public GGVector getClosestObstacle()
  {
    GGVector best = null;
    for (IObstacle o : obstacles)
    {
      GGVector closest = o.closestPointTo(getStandPoint());
      if (liesInside(closest) && isCloser(closest, best))
        best = closest; //not possible that intersecting point is closer
      else
      {
        for (GGVector candidate : o.getIntersectionPointsWith(viewBoarderLines))
          if (isCloser(candidate, best))
            best = candidate;
      }
    }
    return best;
  }

  /**
   * Returns the distance to the closest obstacle or 0
   *  (Double.NaN??) if there is no obstacle in the viewing cone.
   * @return
   */
  public double getDistanceToClosestObstacle()
  {
    GGVector obstaclePoint = getClosestObstacle();
    if (obstaclePoint == null)
      return Double.NaN;
    GGVector fromSPtoOP = obstaclePoint.sub(getStandPoint());
    return fromSPtoOP.magnitude();
  }

  private boolean isCloser(GGVector candidate, GGVector best)
  {
    if (best == null)
      return true;
    return candidate.sub(getStandPoint()).magnitude2() < best.sub(getStandPoint()).magnitude2();
  }

  public boolean liesInside(GGVector p)
  {
    GGVector pNorm = toTriangleCoordinates(p);
    // don't use magnitude2() or you'll have (more) rounding errors!
    return pNorm.x >= 0 && pNorm.y >= 0 && (infinite || pNorm.magnitude() <= 1);
  }

  @Override
  public String toString()
  {
    String result = "ViewingCone around:";
    for (GGVector v : vertices)
      result += " " + v;
    return result;
  }

  public GGVector getStandPoint()
  {
    return vertices[0];
  }

  public void setStandPoint(GGVector standPoint)
  {
    vertices[0] = standPoint;
  }

  public GGVector getLookAtPoint()
  {
    return baseCenter;
  }

  public void setLookAtPoint(GGVector lookAtPoint)
  {
    this.baseCenter = lookAtPoint;
    vertices[1] = makeCorner(getStandPoint(), lookAtPoint, apexAngle / 2);
    vertices[2] = makeCorner(getStandPoint(), lookAtPoint, -apexAngle / 2);
  }

  public boolean removeObstacle(IObstacle t)
  {
    return obstacles.remove(t);
  }

  public void removeAllObstacles()
  {
    obstacles.clear();
  }

  private static void paintCone(GGBackground bg, GGVector a, GGVector b)
  {
    drawLine(bg, a, b);
    GGVector axe = b.sub(a);
    GGVector border1 = axe.clone();
    GGVector border2 = axe.clone();
    border1.rotate(apexAngle / 2);
    border2.rotate(-apexAngle / 2);
    drawLine(bg, a, a.add(border1));
    drawLine(bg, a, a.add(border2));
  }

  private static void paintCircle(GGBackground bg, Point center, int radius)
  {
    bg.drawCircle(center, radius);
  }

  public void drawProximityCircle(GGBackground bg, int radius, Color color)
  {
    Color oldPaintColor = bg.getPaintColor();
    bg.setXORMode(color);
    if (oldCircle != null)
    {
      paintCircle(bg, toPoint(oldCircle.center), (int)(oldCircle.radius));   // Erase old
      oldCircle = null;
    }
    if (radius > 0)
    {
      paintCircle(bg, toPoint(apex), radius);
      oldCircle = new GGCircle(apex, radius);
    }
    bg.setPaintMode();
    bg.setPaintColor(oldPaintColor);
  }

  public void drawCone(GGBackground bg, Color color)
  {
    Color oldPaintColor = bg.getPaintColor();
    bg.setXORMode(color);
    if (oldApex == null)
      paintCone(bg, apex, baseCenter);
    else
    {
      paintCone(bg, oldApex, oldBaseCenter);   // Erase old
      paintCone(bg, apex, baseCenter);
    }
    oldApex = apex;
    oldBaseCenter = baseCenter;
    bg.setPaintMode();
    bg.setPaintColor(oldPaintColor);
  }

  protected static void eraseCone(GGBackground bg)
  {
    paintCone(bg, oldApex, oldBaseCenter);
    oldApex = null;
  }

  protected static void eraseProximityCircle(GGBackground bg)
  {
    paintCircle(bg, toPoint(oldCircle.center), (int)oldCircle.radius);
    oldCircle = null;
  }

  private static void drawLine(GGBackground bg, GGVector v1, GGVector v2)
  {
    bg.drawLine(toPoint(v1), toPoint(v2));
  }

  private static Point toPoint(GGVector v)
  {
    return new Point((int)v.x, (int)v.y);
  }

}
