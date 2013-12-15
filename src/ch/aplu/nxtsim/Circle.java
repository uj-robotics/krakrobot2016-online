// Circle.java
// Code by Stefan Moser

package ch.aplu.nxtsim;

import java.util.LinkedList;
import java.util.List;

import ch.aplu.jgamegrid.GGCircle;
import ch.aplu.jgamegrid.GGVector;

class Circle implements IObstacle {

	private GGVector center;
	private double radius;

	public Circle(GGVector centre, double radius) {
		this.center = centre;
		this.radius = radius;
	}
	
	public Circle(GGCircle circle) {
		this.center = circle.getCenter();
		this.radius = circle.getRadius();
	}

	@Override
	public GGVector closestPointTo(GGVector p) {
		GGVector between = p.sub(center);
		between.normalize();
		between = between.mult(radius);
		return center.add(between);
	}

	@Override
	public boolean liesInside(GGVector p) {
		GGVector v = p.sub(center);
		return v.magnitude() < radius;
	}

	@Override
	public List<GGVector> getIntersectionPointsWith(
		LineSegment[] viewBoarderLines) {
		LinkedList<GGVector> intersectionPoints = new LinkedList<GGVector>();
		for (LineSegment l: viewBoarderLines) {
			GGVector startCentered = l.start.sub(center);
			double a = l.direction.magnitude2();
			double b = 2*startCentered.dot(l.direction);
			double c = startCentered.magnitude2() - radius*radius;
			double discriminant = b*b - 4*a*c;
			if (discriminant < 0)
				continue; //only imaginary solutions
			else {
				int[] plusminus = {-1, 1};
				for (int i: plusminus) {
					double t = (-b + i*Math.sqrt(discriminant))/(2*a);
					if (t >= 0 && t <= 1)
						intersectionPoints.add(l.getPointOnLineSegment(t));
				}
			}
		}
		return intersectionPoints;
	}
	
	public String toString() {
		return "Circle around " + center + ", r=" + radius;
	}

	public GGVector getCenter() {
		return center;
	}

	public void setCenter(GGVector c) {
		this.center = c;
	}
}
