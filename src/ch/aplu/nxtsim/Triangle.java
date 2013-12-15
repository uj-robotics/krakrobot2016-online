// Triangle.java
// Code by Stefan Moser

package ch.aplu.nxtsim;

import java.util.Arrays;
import java.util.LinkedList;
import java.util.List;

import ch.aplu.jgamegrid.*;
import java.awt.Color;
import java.awt.Point;

class Triangle implements IObstacle
{
  protected GGVector[] vertices = new GGVector[3];

  public Triangle(GGVector a, GGVector b, GGVector c)
  {
    vertices[0] = a;
    vertices[1] = b;
    vertices[2] = c;
  }

  @Override
  public boolean liesInside(GGVector p)
  {
    GGVector pNorm = toTriangleCoordinates(p);
    return pNorm.x >= 0 && pNorm.y >= 0 && pNorm.x + pNorm.y <= 1;
  }

  /**
   * Maps the given Point to the standard coordinate system 
   * (defined by the triangle around (0,0), (0,1), (1,0))
   * with the triangle defining the original coordinate system.
   * 
   * @param p
   * @return
   */
  public GGVector toTriangleCoordinates(GGVector p)
  {
    GGVector edgeOne = vertices[1].sub(vertices[0]);
    GGVector edgeTwo = vertices[2].sub(vertices[0]);
    GGVector translatedP = p.sub(vertices[0]);
    GGMatrix m = new GGMatrix(edgeOne, edgeTwo);
    m.invert();

    return m.transform(translatedP);
  }

  /* (non-Javadoc)
   * @see models.IObstacle#closestPointTo(ch.aplu.jgamegrid.GGVector)
   */
  @Override
  public GGVector closestPointTo(GGVector p)
  {
    //TODO: make iterator for points?
    GGVector best = closestPointOfLineTo(vertices[0], vertices[nextVertexIndex(0)], p);
    for (int i = 1; i < vertices.length; i++)
    {
      GGVector candidate = closestPointOfLineTo(vertices[i], vertices[nextVertexIndex(i)], p);
      if (candidate.distanceTo(p) < best.distanceTo(p))
        best = candidate;
    }

    return best;
  }

  private GGVector closestPointOfLineTo(GGVector a, GGVector b, GGVector p)
  {
    GGVector ap = p.sub(a);
    GGVector ab = b.sub(a);
    double abMag = ab.magnitude2();

    //if a and b are at the exact same position, return a by default
    if (abMag == 0)
      return a;

    double apDotAb = ap.dot(ab);

    double t = apDotAb / abMag;
    //only points on the line are valid:
    if (t <= 0)
      return a;
    else if (t >= 1)
      return b;
    else
      return a.add(ab.mult(t));
  }

  protected int nextVertexIndex(int i)
  {
    return (i + 1) % 3;
  }

  public GGVector[] getVertices()
  {
    return vertices;
  }

  @Override
  public List<GGVector> getIntersectionPointsWith(
    LineSegment[] viewBoarderLines)
  {
    LinkedList<GGVector> intersectionPoints = new LinkedList<GGVector>();
    for (LineSegment l : viewBoarderLines)
    {
      for (int i = 0; i < 3; i++)
      {
        LineSegment tl = new LineSegment(vertices[i], vertices[nextVertexIndex(i)].sub(vertices[i]));
        GGVector p = l.getIntersectionPointWith(tl);
        if (p != null)
          intersectionPoints.add(p);
      }
    }
    return intersectionPoints;
  }

  @Override
  public String toString()
  {
    return "Triangle around: " + Arrays.toString(vertices);
  }

  /**
   * Small helper class to make coordinate transformation easier. 
   * Only supports 2x2 Matrices!
   */
  class GGMatrix
  {
    private double[] entries;

    public GGMatrix(GGVector col1, GGVector col2)
    {
      this(col1.x, col2.x, col1.y, col2.y);
    }

    /**
     * Entries are ordered as follows:
     * 
     * { m1, m2
     *   m3, m4 }
     * @param entries
     */
    public GGMatrix(double m1, double m2, double m3, double m4)
    {
      this.entries = new double[4];
      entries[0] = m1;
      entries[1] = m2;
      entries[2] = m3;
      entries[3] = m4;
    }

    /**
     * Returns a new GGVector and lets the GGVector given as argument untouched.
     * @param v
     * @return the given GGVector multiplied the matrix 
     */
    public GGVector transform(GGVector v)
    {
      double x = entries[0] * v.x + entries[1] * v.y;
      double y = entries[2] * v.x + entries[3] * v.y;
      return new GGVector(x, y);
    }

    /**
     * Inverts this instance of the matrix
     */
    public void invert()
    {
      double det = entries[0] * entries[3] - entries[1] * entries[2];
      if (det == 0)
        throw new IllegalArgumentException("Matrix is not invertable");
      else
      {
        double oneOverDet = 1 / det;
        double[] invertedEntries = new double[4];
        invertedEntries[0] = entries[3] * oneOverDet;
        invertedEntries[1] = -entries[1] * oneOverDet;
        invertedEntries[2] = -entries[2] * oneOverDet;
        invertedEntries[3] = entries[0] * oneOverDet;
        entries = invertedEntries;
      }
    }
  }

  public void drawTriangle(GGBackground bg, Color color)
  {
    Color oldPaintColor = bg.getPaintColor();
    bg.setPaintColor(color);
    bg.fillPolygon(toPoints(getVertices()));
    bg.setPaintColor(oldPaintColor);
  }

  private Point[] toPoints(GGVector[] v)
  {
	Point[] p = new Point[v.length]; 
	for (int i = 0; i < v.length; i++) {
		p[i] = new Point((int)Math.round(v[i].x), (int) Math.round(v[i].y));
	}
    return p;
  }
}
