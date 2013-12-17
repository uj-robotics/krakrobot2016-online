#!/usr/bin/python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Visualising the Segmented-CTE maze-solving in CS373 Unit6-6
#
# Source : https://www.udacity.com/wiki/CS373%20Visualizing%20Maze%20Driving
#
# Custom modules:
#   vegesvgplot.py        http://pastebin.com/6Aek3Exm
#-------------------------------------------------------------------------------

# General idea: run simulation with fixed speed attribute. Accept solution only
# if number of collisions was zero, or no two consecutive collisions happened


'''Udacity CS373 Unit 6-6 robot car demo

Description:

  This Python script runs a simulation of a robot car performing
  A* search, path smoothing, PID control and naivigation with
  horribly imprecise simulated GPS data. The output is in the form
  of a Scalable Vector Graphic file named “output.svg”

Author(s):

  Daniel Neville (Blancmange), creamygoat@gmail.com
  Prof. Sebastian Thrun, udacity (original robot simulation)

Copyright, licence:

  Code by Daniel Neville: Public domain
  Code snarfed from udacity: See http://www.udacity.com/legal/

Platform:

  Python 2.5


INDEX


Fun stuff:

  RunUnitCode(Data) – Snarfed and modified robot code
  RenderToSVG(Data)
  DoFunStuff(Data)

Main:

  Main()

'''


#-------------------------------------------------------------------------------


import math

from math import (
  pi, sqrt, hypot, sin, cos, tan, asin, acos, atan, atan2, radians, degrees,
  floor, ceil, exp
)

import random

# The SVG Plotting for Vegetables module can be found at
# http://pastebin.com/6Aek3Exm

from vegesvgplot import (

  # Shape constants
  Pt_Break, Pt_Anchor, Pt_Control,
  PtCmdWithCoordsSet, PtCmdSet,

  # Indent tracker class
  tIndentTracker,

  # Affine matrix class
  tAffineMtx,

  # Affine matrix creation functions
  AffineMtxTS, AffineMtxTRS2D, Affine2DMatrices,

  # Utility functions
  ValidatedRange, MergedDictionary, Save,
  ArrayDimensions,  CopyArray, At, SetAt,

  # Basic vector functions
  VZeros, VOnes, VStdBasis, VDim, VAug, VMajorAxis,
  VNeg, VSum, VDiff, VSchur, VDot,
  VLengthSquared, VLength, VManhattan,
  VScaled, VNormalised,
  VPerp, VCrossProduct, VCrossProduct4D,
  VScalarTripleProduct, VVectorTripleProduct,
  VProjectionOnto,
  VTransposedMAV,
  VRectToPol, VPolToRect,
  VLerp,

  # Shape functions
  ShapeFromVertices, ShapePoints, ShapeSubpathRanges, ShapeCurveRanges,
  ShapeLength, LineToShapeIntersections, TransformedShape, PiecewiseArc,

  # Output formatting functions
  MaxDP, GFListStr, GFTupleStr, HTMLEscaped, AttrMarkup, ProgressColourStr,

  # SVG functions
  SVGStart, SVGEnd, SVGPathDataSegments, SVGPath, SVGText,
  SVGGroup, SVGGroupEnd, SVGGrid

)

def GreekCross(Centre, ArmLength):


    A = Pt_Anchor
    C = Pt_Control
    B = (Pt_Break, None)



    x, y = Centre
    s = ArmLength
    return [
      (A, (x - s, y)), (A, (x + s, y)), B,
      (A, (x, y - s)), (A, (x, y + s))
    ]


def SparkSymbolDef(IT, ID, NumPoints=8):

    A = Pt_Anchor
    C = Pt_Control
    B = (Pt_Break, None)


    #---------------------------------------------------------------------------

    def StarPoint(Ix):
      AngleStep = 2.0 * pi / (2 * NumPoints)
      Theta = AngleStep * float(Ix % (2 * NumPoints))
      Radius = [1.0, 0.3, 0.7, 0.3][Ix % 4]
      return VPolToRect((Radius, Theta))

    #---------------------------------------------------------------------------

    Result = ''

    S = []
    S.append(VLerp(StarPoint(-1), StarPoint(0), 0.5))
    for i in range(2 * NumPoints):
      S.append(StarPoint(i))
    S.append((S[0][0], S[0][1]))
    S = ShapeFromVertices(S, 1)

    Result += IT(
      '<symbol id="' + HTMLEscaped(ID) + '" ' + 'viewBox="-1 -1 2 2">'
    )
    IT.StepIn()
    Result += SVGPath(IT, S, {
      'fill': 'rgba(255, 248, 0, 0.25)',
      'stroke': '#f90',
      'stroke-width': '0.02',
      'stroke-linejoin': 'miter',
      'stroke-linecap': 'butt'
    })
    Result += SVGPath(IT, GreekCross((0, 0), 0.1), {
      'fill': 'none',
      'stroke': 'black',
      'stroke-width': '0.008'
    })
    IT.StepOut()
    Result += IT('</symbol>')

    return Result


def RunSimulation(Data):

  Data['Sparks'] = []
  Data['EstimatedPath'] = []
  Data['ActualPath'] = []

  steering_noise    = 0.1
  distance_noise    = 0.03
  measurement_noise = 0.3



  class Robot:
      """ The main class representing robot that can sense and move """

      def __init__(self, length = 0.5):
          """
            Initialize robot    
          """

          self.x = 0.0
          self.y = 0.0
          self.orientation = 0.0
          self.length = length
          self.steering_noise    = 0.0
          self.distance_noise    = 0.0
          self.measurement_noise = 0.0
          self.num_collisions    = 0
          self.num_steps         = 0

      
      #TODO: extract  
      def set(self, new_x, new_y, new_orientation):
          """
            Set robot position
            @note: Cannot be called by contestant
          """

          self.x = float(new_x)
          self.y = float(new_y)
          self.orientation = float(new_orientation) % (2.0 * pi)


      #TODO: extract from this class
      def set_noise(self, new_s_noise, new_d_noise, new_m_noise):
          """
            Set noise parameter
            @note: Cannot be called by contestant
          """
          # makes it possible to change the noise parameters
          # this is often useful in particle filters
          self.steering_noise     = float(new_s_noise)
          self.distance_noise    = float(new_d_noise)
          self.measurement_noise = float(new_m_noise)

      #TODO: extract from this class
      def check_collision(self, grid):
          """
            Checks for collisions
            @note: Cannot be called by contestant
          """

          for i in range(len(grid)):
              for j in range(len(grid[0])):
                  if grid[i][j] == 1:
                      dist = sqrt((self.x - float(i)) ** 2 +
                                  (self.y - float(j)) ** 2)
                      if dist < 0.5:
                          self.num_collisions += 1
                          return False
          return True


      #TODO: extract from this class 
      def check_goal(self, goal, threshold = 1.0):
          """ Checks if goal is within threshold distance"""

          Data['GoalThreshold'] = threshold #TODO: erase from here
          dist =  sqrt((float(goal[0]) - self.x) ** 2 + (float(goal[1]) - self.y) ** 2)
          return dist < threshold


      #TODO: collision resolution? by distance thresholding? probably a good idea. So let threshold = a/2.0 (a - thickness of maze wall)
      def move(self, grid, steering, distance, tolerance = 0.001, max_steering_angle = pi / 4.0):
          """ 
            Move the robot using bicycle model from Udacity class.
            @param steering front wheel steering angle
            @param distance distance to be driven
          """


          if steering > max_steering_angle:
              steering = max_steering_angle
          if steering < -max_steering_angle:
              steering = -max_steering_angle
          if distance < 0.0:
              distance = 0.0


          # make a new copy
          res = Robot()
          res.length            = self.length
          res.steering_noise    = self.steering_noise
          res.distance_noise    = self.distance_noise
          res.measurement_noise = self.measurement_noise
          res.num_collisions    = self.num_collisions
          res.num_steps         = self.num_steps + 1

          # apply noise
          steering2 = random.gauss(steering, self.steering_noise)
          distance2 = random.gauss(distance, self.distance_noise)


          # Execute motion
          turn = tan(steering2) * distance2 / res.length

          if abs(turn) < tolerance:

              # approximate by straight line motion

              res.x = self.x + (distance2 * cos(self.orientation))
              res.y = self.y + (distance2 * sin(self.orientation))
              res.orientation = (self.orientation + turn) % (2.0 * pi)

          else:
              # approximate bicycle model for motion
              radius = distance2 / turn
              cx = self.x - (sin(self.orientation) * radius)
              cy = self.y + (cos(self.orientation) * radius)
              res.orientation = (self.orientation + turn) % (2.0 * pi)
              res.x = cx + (sin(res.orientation) * radius)
              res.y = cy - (cos(res.orientation) * radius)

          # check for collision
          # res.check_collision(grid)

          return res


      #TODO: add sonar here 
      # http://pastebin.com/GwXCHtS3 ..
      def sense(self):
          """ Returns estimation for position (GPS signal) """
          return [random.gauss(self.x, self.measurement_noise),
                  random.gauss(self.y, self.measurement_noise)]



      def measurement_prob(self, measurement):
          # compute errors
          error_x = measurement[0] - self.x
          error_y = measurement[1] - self.y

          # calculate Gaussian
          error = exp(- (error_x ** 2) / (self.measurement_noise ** 2) / 2.0) \
              / sqrt(2.0 * pi * (self.measurement_noise ** 2))
          error *= exp(- (error_y ** 2) / (self.measurement_noise ** 2) / 2.0) \
              / sqrt(2.0 * pi * (self.measurement_noise ** 2))

          return error



      def __repr__(self):
          # return '[x=%.5f y=%.5f orient=%.5f]'  % (self.x, self.y, self.orientation)
          return '[%.5f, %.5f]'  % (self.x, self.y)






  #TODO: remove
  def run(grid, goal, printflag = False, timeout = 1000):
      myrobot = Robot()
      myrobot.set(0., 0., 0.)
      Data['ActualPath'].append((myrobot.x, myrobot.y))
      myrobot.set_noise(steering_noise, distance_noise, measurement_noise)
      N = 0
      while not myrobot.check_goal(goal) and N < timeout:
          steer = 0.001
          distance = 0.1
          myrobot = myrobot.move(grid, steer, distance)
          
          Data['ActualPath'].append((myrobot.x, myrobot.y))

          if not myrobot.check_collision(grid):
              Data['Sparks'].append((myrobot.x, myrobot.y))
              print '##### Collision ####'

          N += 1
          if printflag:
              print myrobot, cte, index, u

      return [myrobot.check_goal(goal), myrobot.num_collisions, myrobot.num_steps]

 
  #TODO: remove
  def main(grid, goal):
      return run(grid, goal)


  grid = [[0, 1, 0, 0, 0, 0],
          [0, 1, 0, 1, 1, 0],
          [0, 1, 0, 1, 0, 0],
          [0, 0, 0, 1, 0, 1],
          [0, 1, 0, 1, 0, 0]]

  grid = [[0, 1, 0, 0, 0, 0, 0, 0, 0 , 0 ,0 ,0],
          [0, 1, 0, 1, 1, 0, 0, 0, 0 , 0 ,0, 0],
          [0, 1, 0, 1, 0, 0, 0, 0 ,0,0,0,0],
          [0, 0, 0, 1, 0, 1, 0 ,0, 0,0,0,0],
          [0, 1, 0, 1, 0, 0,0,0,0,0,0,0]]



  init = [0, 0]
  goal = [len(grid)-1, len(grid[0])-1]

  steering_noise    = 0.1
  distance_noise    = 0.03
  measurement_noise = 0.3

  print main(grid, goal)



  Data['Map'] = grid
  Data['StartPos'] = init
  Data['GoalPos'] = goal


#-------------------------------------------------------------------------------


def RenderToSVG(Data):

  '''Return Data rendered to an SVG file in a string.

  Data is a dictionary with the keys:

    Title:
      This title is rendered and is embedded in the SVG header.
    Grid:
      See SVGGrid().
    Map:
      The map is a 2D array of integers for hazards (1) and clear spaces (0).
    StartPos:
      The car starts here. The coordinates are units of map squares and the
      origin is in the centre of Map[0][0].
    GoalPos:
      Hopefully the car ends within GoalThreshold of here.
    GoalThreshold:
      The radius of the goal zone is measured in grid units.
    Sparks:
      Each time a collision occurs, a coordinate pair is added to Sparks.
    Paths:
      For the puspose of visualising progressive path modifications, Paths
      is a list of Shapes to be rendered in red-to-indigo rainbow colours.

  '''

  #-----------------------------------------------------------------------------

  # Shorthand

  A = Pt_Anchor
  C = Pt_Control
  B = (Pt_Break, None)

  #-----------------------------------------------------------------------------

  def Field(Name, Default):
    return Data[Name] if Name in Data else Default

  #-----------------------------------------------------------------------------

 

  IT = tIndentTracker('  ')

  Result = ''
  SparkSymbol = ''
  Sparks = Field('Sparks', None)
  Title = Field('Title', '(Untitled)')

  Result += SVGStart(IT, Title, {
    'width': '28cm',
    'height': '19cm',
    'viewBox': '0 0 28 19'
  })

  Result += IT('<defs>')
  IT.StepIn()
  Result += IT(
    '<marker id="ArrowHead"',
    '    viewBox="0 0 10 10" refX="0" refY="5"',
    '    markerUnits="strokeWidth"',
    '    markerWidth="8" markerHeight="6"',
    '    orient="auto">'
    '  <path d="M 0,0  L 10,5  L 0,10  z"/>',
    '</marker>'
  )
  Result += SparkSymbolDef(IT, 'spark') if Sparks is not None else ''
  # More marker, symbol and gradient definitions can go here.
  IT.StepOut()
  Result += IT('</defs>')

  # Background

  Result += IT(
    '<!-- Background -->',
    '<rect x="0" y="0" width="28" height="19" stroke="none" fill="white"/>'
  )

  # Outer group

  Result += IT('<!-- Outer group -->')
  Result += SVGGroup(IT, {'stroke': 'black', 'stroke-width': '0.025'})

  # Plot with grid

  Result += IT('<!-- Grid -->')
  Result += SVGGrid(IT, Data['Grid'])

  # Maze

  Map = Field('Map', None)
  if Map is not None:

    Result += IT('<!-- Hazards -->')
    Result += SVGGroup(IT, {
      'fill': '#a40',
      'stroke': 'black',
      'stroke-width': '0.01',
      'stroke-linecap': 'butt',
    })

    for i in range(len(Map)):
      for j in range(len(Map[0])):
        if Map[i][j] != 0:
          Result += IT('<circle cx="%g" cy="%g" r="0.495"/>\n' % (i, j))

    Result += SVGGroupEnd(IT)

  # Iniial position

  StartPos = Field('StartPos', None)
  if StartPos is not None:

    S = [
      (A, (-1.0, -1.0)), (A, (-1.0, +1.0)),
      (A, (+1.0, +1.0)), (A, (+1.0, -1.0)), (A, (-1.0, -1.0))
    ]

    Result += IT('<!-- Initial position -->')
    Result += SVGPath(IT,
      TransformedShape(AffineMtxTS(StartPos, 0.3), S),
      {'stroke': '#09f', 'stroke-width': '0.1', 'stroke-linecap': 'square'}
    )

  # Goal position

  GoalPos = Field('GoalPos', None)
  if GoalPos is not None:

    GoalThreshold = Field('GoalThreshold', None)
    if GoalThreshold is not None:
      Result += IT('<!-- Goal threshold -->')
      Result += IT(
        '<circle cx="%g" cy="%g" r="%g"' %
          (GoalPos[0], GoalPos[1], GoalThreshold)
      )
      IT.StepIn(2)
      Result += IT(
        'fill="rgba(0, 255, 0, 0.1)" stroke="#0d0" stroke-width="0.02"/>'
      )
      IT.StepOut(2)

    S = (
      GreekCross(GoalPos, 0.4) + [B] +
      PiecewiseArc(GoalPos, 0.25, (0, 2.0 * pi), 8)
    )
    Result += IT('<!-- Goal position -->')
    Result += SVGPath(IT, S, {
      'stroke': '#0d0', 'stroke-width': '0.1', 'stroke-linecap': 'butt'
    })

  # Sparks

  if Sparks is not None and len(Sparks) > 0:
    Result += IT('<!-- Points of collision (sparks) -->')
    Result += SVGGroup(IT, {'transform': 'translate(-0.5, -0.5)'})
    for SparkPos in Sparks:
      Result += IT(
        ('<use x="%g" y="%g"' % (SparkPos[0], SparkPos[1])) +
        ' width="1" height="1" xlink:href="#spark"/>'
      )
    Result += SVGGroupEnd(IT)

  # Actual path

  ActualPath = Field('ActualPath', None)
  if ActualPath is not None:
    Result += IT('<!-- Actual path -->')
    Result += SVGPath(IT,
      ShapeFromVertices(ActualPath, 1),
      {'stroke': '#40f', 'stroke-width': '0.02'}
    )
  

  # ??
  # Paths in rainbow colours
  Paths = Field('Paths', None)
  if Paths is not None and len(Paths) > 0:

    NumPaths = len(Paths)

    Result += IT('<!-- Paths in rainbow colours -->')
    for PathIx, Path in enumerate(Paths):
      if NumPaths >= 2:
        Progress = float(PathIx) / float(NumPaths - 1)
      else:
        Progress = 1.0
      Opacity = 1.0 if Progress in [0.0, 1.0] else 0.60 + 0.00 * Progress
      ColourStr = ProgressColourStr(Progress, Opacity)
      Result += IT('<!-- Path %d, (%.1f%%) -->' % (PathIx, 100.0 * Progress))
      Result += SVGPath(IT, Path, {"stroke": ColourStr})

  # End of plot

  Result += SVGGroupEnd(IT)

  # Title and legend

  Result += IT('<!-- Title background -->')
  Result += IT(
    '<rect x="0" y="0" width="28" height="1.1" stroke="none" fill="white"/>'
  )

  Result += IT('<!-- Title group -->')
  Result += SVGGroup(IT, {
    'font-family': 'sans-serif',
    'font-size': '0.36',
    'font-weight': 'normal',
    'fill': 'black',
    'stroke': 'none'
  })

  Result += IT('<!-- Title -->')
  Result += SVGText(IT, (0.5, 0.82), Title, {
    'font-size': '0.72',
    'font-weight': 'bold'
  })

  Result += IT('<!-- Legend line labels-->')
  Result += SVGText(IT, (19.5, 0.82), 'Planned')
  Result += SVGText(IT, (22.6, 0.82), 'Estimated')
  Result += SVGText(IT, (26.0, 0.82), 'Actual')

  Result += IT('<!-- Legend lines -->')
  Result += SVGGroup(IT, {
    'fill': 'none',
    'stroke-width': '0.12',
    'stroke-linecap': 'round'
  })

  Result += SVGPath(IT,
    [(Pt_Anchor, (18.5, 0.7)), (Pt_Anchor, (19.3, 0.7))],
    {'stroke': '#0d0'}
  )
  Result += SVGPath(IT,
    [(Pt_Anchor, (21.6, 0.7)), (Pt_Anchor, (22.4, 0.7))],
    {'stroke': '#f09', 'stroke-dasharray': '0.075 0.15'}
  )

  Result += SVGPath(IT,
    [(Pt_Anchor, (25.0, 0.7)), (Pt_Anchor, (25.8, 0.7))],
    {'stroke': '#40f'}
  )

  Result += SVGGroupEnd(IT)

  # End of title group

  Result += SVGGroupEnd(IT)

  # End of outer group

  Result += SVGGroupEnd(IT)

  Result += SVGEnd(IT)

  return Result


#-------------------------------------------------------------------------------


def DoFunStuff(Data):

  '''Drive a robot car though a maze.

  The output is written to the Data (a Python dictionary) to keep the
  rendering details separate.

  '''

  #-----------------------------------------------------------------------------

  RunSimulation(Data)

  Map = Data['Map']

  #MMS = unichr(0x205F)
  #MMSEquals = MMS + '=' + MMS
  #AStr = u'α%s%g' % (MMSEquals, Alpha)
  #BStr = u'β%s%g' % (MMSEquals,  Beta)
  #MuStr = u'µ%s%g' % (MMSEquals, Tolerance)

  Data['Title'] = 'Krakrobot Eliminacje, przejazd..'

  Grid = {
    'CanvasMinima': (0.5, 1.5),
    'CanvasMaxima': (27.5, 18.5),
    'RangeMinima': (0, 0),
    'RangeMaxima': (len(Map), len(Map[0])),
    'YIsUp': False,
    'Transpose': True,
    'SquareAlignment': 'Centre',
    'DrawGrid': True,
    'DrawUnitAxes': False,
    'GridLineAttributes': {
      'stroke-width': '0.02', 'stroke': 'rgba(0, 192, 255, 0.5)'
    },
    'GeneralAttributes': {
      'stroke-width': '0.05', 'stroke': 'red'
    }
  }

  Paths = []
  #PathLog = []
  #Paths.append(ShapeFromVertices(PathLog, 1))

  Data['Grid'] = Grid
  Data['Paths'] = Paths
  Data['Map'] = Map


#-------------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------------


def Main():

  OutputFileName = 'output.svg'

  print 'Driving a car through a maze...'

  Data = {}
  DoFunStuff(Data)

  print 'Rendering SVG...'
  SVG = RenderToSVG(Data)
  print 'Done.'

  print 'Saving SVG to "' + OutputFileName + '"...'
  Save(SVG.encode('utf_8'), OutputFileName)
  print 'Done.'


#-------------------------------------------------------------------------------
# Command line trigger
#-------------------------------------------------------------------------------


if __name__ == '__main__':
  Main()


#-------------------------------------------------------------------------------
# End
#-------------------------------------------------------------------------------
