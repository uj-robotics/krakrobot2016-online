// IObstacle.java
// Code by Stefan Moser

package ch.aplu.nxtsim;

import java.util.Collection;
import java.util.List;

import ch.aplu.jgamegrid.GGVector;

interface IObstacle {

	public GGVector closestPointTo(GGVector p);
	
	/**
	 * returns true if the given point lies inside (or on the
	 * edge) of the obstacle.
	 * @param p
	 * @return
	 */
	public boolean liesInside(GGVector p);

	public List<GGVector> getIntersectionPointsWith(
			LineSegment[] viewBoarderLines);

}