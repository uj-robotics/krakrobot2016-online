// Rectangle.java
// Code by Stefan Moser

package ch.aplu.nxtsim;

import java.util.ArrayList;
import java.util.LinkedList;
import java.util.List;

import ch.aplu.jgamegrid.GGRectangle;
import ch.aplu.jgamegrid.GGVector;

class Rectangle implements IObstacle
{
  LinkedList<Triangle> triangles;
  /**
   * careful, this array does not provide any functionality. It is just for easier
   * retrieving all 4 vertices through getVertices.
   */
  GGVector vertices[];

  /**
   * Could also be more generalized
   * @param r
   */
  public Rectangle(GGRectangle r)
  {
    this.vertices = r.getVertexes();
    triangles = new LinkedList<Triangle>();
    triangles.add(new Triangle(vertices[0], vertices[1], vertices[3]));
    triangles.add(new Triangle(vertices[1], vertices[2], vertices[3]));
  }

  public void setVertices(GGRectangle r)
  {
    this.vertices = r.getVertexes();
    GGVector[] triangle1 = triangles.get(0).vertices;
    GGVector[] triangle2 = triangles.get(1).vertices;
    //quite stupid hardcoding:
    triangle1[0] = vertices[0];
    triangle1[1] = vertices[1];
    triangle1[2] = vertices[3];

    triangle2[0] = vertices[1];
    triangle2[1] = vertices[2];
    triangle2[2] = vertices[3];
  }

  public GGVector[] getVertices()
  {
    return vertices;
  }

  @Override
  public GGVector closestPointTo(GGVector p)
  {
    GGVector best = new GGVector(Double.MAX_VALUE, Double.MAX_VALUE);
    for (Triangle t : triangles)
    {
      GGVector candidate = t.closestPointTo(p);
      if (p.distanceTo(candidate) < p.distanceTo(best))
        best = candidate;
    }
    return best;
  }

  @Override
  public boolean liesInside(GGVector p)
  {
    for (Triangle t : triangles)
      if (t.liesInside(p))
        return true;
    return false;
  }

  @Override
  public List<GGVector> getIntersectionPointsWith(LineSegment[] viewBoarderLines)
  {
    LinkedList<GGVector> intersectionPoints = new LinkedList<GGVector>();
    for (Triangle t : triangles)
      intersectionPoints.addAll(t.getIntersectionPointsWith(viewBoarderLines));
    return intersectionPoints;
  }

}
