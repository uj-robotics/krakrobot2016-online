#!/usr/bin/python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Visualising the Segmented-CTE maze-solving in CS373 Unit6-6
#
# unit0606_segmented_cte_svg.py
# http://pastebin.com/Jfyyyhxk
#
# Custom modules:
#   vegesvgplot.py        http://pastebin.com/6Aek3Exm
#
#-------------------------------------------------------------------------------


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


#-------------------------------------------------------------------------------
# Fun stuff
#-------------------------------------------------------------------------------


def RunUnitCode(Data):

  Data['Sparks'] = []
  Data['EstimatedPath'] = []
  Data['ActualPath'] = []

  #-----------------------------------------------------------------------------
  # Code snarfed from udacity and modified
  #-----------------------------------------------------------------------------

  # don't change the noise paameters

  steering_noise    = 0.1
  distance_noise    = 0.03
  measurement_noise = 0.3


  class plan:

      # --------
      # init:
      #    creates an empty plan
      #

      def __init__(self, grid, init, goal, cost = 1):
          self.cost = cost
          self.grid = grid
          self.init = init
          self.goal = goal
          self.make_heuristic(grid, goal, self.cost)
          self.path = []
          self.spath = []

      # --------
      #
      # make heuristic function for a grid

      def make_heuristic(self, grid, goal, cost):
          self.heuristic = [[0 for row in range(len(grid[0]))]
                            for col in range(len(grid))]
          for i in range(len(self.grid)):
              for j in range(len(self.grid[0])):
                  self.heuristic[i][j] = abs(i - self.goal[0]) + \
                      abs(j - self.goal[1])



      # ------------------------------------------------
      #
      # A* for searching a path to the goal
      #
      #

      def astar(self):


          if self.heuristic == []:
              raise ValueError, "Heuristic must be defined to run A*"

          # internal motion parameters
          delta = [[-1,  0], # go up
                   [ 0,  -1], # go left
                   [ 1,  0], # go down
                   [ 0,  1]] # do right


          # open list elements are of the type: [f, g, h, x, y]

          closed = [[0 for row in range(len(self.grid[0]))]
                    for col in range(len(self.grid))]
          action = [[0 for row in range(len(self.grid[0]))]
                    for col in range(len(self.grid))]

          closed[self.init[0]][self.init[1]] = 1


          x = self.init[0]
          y = self.init[1]
          h = self.heuristic[x][y]
          g = 0
          f = g + h

          open = [[f, g, h, x, y]]

          found  = False # flag that is set when search complete
          resign = False # flag set if we can't find expand
          count  = 0


          while not found and not resign:

              # check if we still have elements on the open list
              if len(open) == 0:
                  resign = True
                  print '###### Search terminated without success'

              else:
                  # remove node from list
                  open.sort()
                  open.reverse()
                  next = open.pop()
                  x = next[3]
                  y = next[4]
                  g = next[1]

              # check if we are done

              if x == goal[0] and y == goal[1]:
                  found = True
                  # print '###### A* search successful'

              else:
                  # expand winning element and add to new open list
                  for i in range(len(delta)):
                      x2 = x + delta[i][0]
                      y2 = y + delta[i][1]
                      if x2 >= 0 and x2 < len(self.grid) and y2 >= 0 \
                              and y2 < len(self.grid[0]):
                          if closed[x2][y2] == 0 and self.grid[x2][y2] == 0:
                              g2 = g + self.cost
                              h2 = self.heuristic[x2][y2]
                              f2 = g2 + h2
                              open.append([f2, g2, h2, x2, y2])
                              closed[x2][y2] = 1
                              action[x2][y2] = i

              count += 1

          # extract the path



          invpath = []
          x = self.goal[0]
          y = self.goal[1]
          invpath.append([x, y])
          while x != self.init[0] or y != self.init[1]:
              x2 = x - delta[action[x][y]][0]
              y2 = y - delta[action[x][y]][1]
              x = x2
              y = y2
              invpath.append([x, y])

          self.path = []
          for i in range(len(invpath)):
              self.path.append(invpath[len(invpath) - 1 - i])




      # ------------------------------------------------
      #
      # this is the smoothing function
      #




      def smooth(self, weight_data = 0.1, weight_smooth = 0.1,
                 tolerance = 0.000001):

          if self.path == []:
              raise ValueError, "Run A* first before smoothing path"

          self.spath = [[0 for row in range(len(self.path[0]))] \
                             for col in range(len(self.path))]
          for i in range(len(self.path)):
              for j in range(len(self.path[0])):
                  self.spath[i][j] = self.path[i][j]

          change = tolerance
          while change >= tolerance:
              change = 0.0
              for i in range(1, len(self.path)-1):
                  for j in range(len(self.path[0])):
                      aux = self.spath[i][j]

                      self.spath[i][j] += weight_data * \
                          (self.path[i][j] - self.spath[i][j])

                      self.spath[i][j] += weight_smooth * \
                          (self.spath[i-1][j] + self.spath[i+1][j]
                           - (2.0 * self.spath[i][j]))
                      if i >= 2:
                          self.spath[i][j] += 0.5 * weight_smooth * \
                              (2.0 * self.spath[i-1][j] - self.spath[i-2][j]
                               - self.spath[i][j])
                      if i <= len(self.path) - 3:
                          self.spath[i][j] += 0.5 * weight_smooth * \
                              (2.0 * self.spath[i+1][j] - self.spath[i+2][j]
                               - self.spath[i][j])

              change += abs(aux - self.spath[i][j])







  # ------------------------------------------------
  #
  # this is the robot class
  #

  class robot:

      # --------
      # init:
      #	creates robot and initializes location/orientation to 0, 0, 0
      #

      def __init__(self, length = 0.5):
          self.x = 0.0
          self.y = 0.0
          self.orientation = 0.0
          self.length = length
          self.steering_noise    = 0.0
          self.distance_noise    = 0.0
          self.measurement_noise = 0.0
          self.num_collisions    = 0
          self.num_steps         = 0

      # --------
      # set:
      #	sets a robot coordinate
      #

      def set(self, new_x, new_y, new_orientation):

          self.x = float(new_x)
          self.y = float(new_y)
          self.orientation = float(new_orientation) % (2.0 * pi)


      # --------
      # set_noise:
      #	sets the noise parameters
      #

      def set_noise(self, new_s_noise, new_d_noise, new_m_noise):
          # makes it possible to change the noise parameters
          # this is often useful in particle filters
          self.steering_noise     = float(new_s_noise)
          self.distance_noise    = float(new_d_noise)
          self.measurement_noise = float(new_m_noise)

      # --------
      # check:
      #    checks of the robot pose collides with an obstacle, or
      # is too far outside the plane

      def check_collision(self, grid):
          for i in range(len(grid)):
              for j in range(len(grid[0])):
                  if grid[i][j] == 1:
                      dist = sqrt((self.x - float(i)) ** 2 +
                                  (self.y - float(j)) ** 2)
                      if dist < 0.5:
                          self.num_collisions += 1
                          return False
          return True

      def check_goal(self, goal, threshold = 1.0):
          Data['GoalThreshold'] = threshold
          dist =  sqrt((float(goal[0]) - self.x) ** 2 + (float(goal[1]) - self.y) ** 2)
          return dist < threshold

      # --------
      # move:
      #    steering = front wheel steering angle, limited by max_steering_angle
      #    distance = total distance driven, most be non-negative

      def move(self, grid, steering, distance,
               tolerance = 0.001, max_steering_angle = pi / 4.0):

          if steering > max_steering_angle:
              steering = max_steering_angle
          if steering < -max_steering_angle:
              steering = -max_steering_angle
          if distance < 0.0:
              distance = 0.0


          # make a new copy
          res = robot()
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

      # --------
      # sense:
      #

      def sense(self):

          return [random.gauss(self.x, self.measurement_noise),
                  random.gauss(self.y, self.measurement_noise)]

      # --------
      # measurement_prob
      #    computes the probability of a measurement
      #

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






  # ------------------------------------------------
  #
  # this is the particle filter class
  #

  class particles:

      # --------
      # init:
      #	creates particle set with given initial position
      #

      def __init__(self, x, y, theta,
                   steering_noise, distance_noise, measurement_noise, N = 100):
          self.N = N
          self.steering_noise    = steering_noise
          self.distance_noise    = distance_noise
          self.measurement_noise = measurement_noise

          self.data = []
          for i in range(self.N):
              r = robot()
              r.set(x, y, theta)
              r.set_noise(steering_noise, distance_noise, measurement_noise)
              self.data.append(r)


      # --------
      #
      # extract position from a particle set
      #

      def get_position(self):
          x = 0.0
          y = 0.0
          orientation = 0.0

          for i in range(self.N):
              x += self.data[i].x
              y += self.data[i].y
              # orientation is tricky because it is cyclic. By normalizing
              # around the first particle we are somewhat more robust to
              # the 0=2pi problem
              orientation += (((self.data[i].orientation
                                - self.data[0].orientation + pi) % (2.0 * pi))
                              + self.data[0].orientation - pi)
          return [x / self.N, y / self.N, orientation / self.N]

      # --------
      #
      # motion of the particles
      #

      def move(self, grid, steer, speed):
          newdata = []

          for i in range(self.N):
              r = self.data[i].move(grid, steer, speed)
              newdata.append(r)
          self.data = newdata

      # --------
      #
      # sensing and resampling
      #

      def sense(self, Z):
          w = []
          for i in range(self.N):
              w.append(self.data[i].measurement_prob(Z))

          # resampling (careful, this is using shallow copy)
          p3 = []
          index = int(random.random() * self.N)
          beta = 0.0
          mw = max(w)

          for i in range(self.N):
              beta += random.random() * 2.0 * mw
              while beta > w[index]:
                  beta -= w[index]
                  index = (index + 1) % self.N
              p3.append(self.data[index])
          self.data = p3







  # --------
  #
  # run:  runs control program for the robot
  #


  def run(grid, goal, spath, params, printflag = False, speed = 0.1, timeout = 1000):

      myrobot = robot()
      myrobot.set(0., 0., 0.)
      Data['ActualPath'].append((myrobot.x, myrobot.y))
      myrobot.set_noise(steering_noise, distance_noise, measurement_noise)
      filter = particles(myrobot.x, myrobot.y, myrobot.orientation,
                         steering_noise, distance_noise, measurement_noise)

      cte  = 0.0
      err  = 0.0
      N    = 0

      index = 0 # index into the path

      while not myrobot.check_goal(goal) and N < timeout:

          diff_cte = - cte


          # ----------------------------------------
          # compute the CTE

          # start with the present robot estimate
          estimate = filter.get_position()
          Data['EstimatedPath'].append(tuple(estimate))

          #-----------------------------------------------------------------------

          def VDiff(A, B):
            return tuple(x - y for x, y in zip(A, B))

          def VDot(A, B):
            return sum(x * y for x, y in zip(A, B))

          def VLengthSquared(A):
            return sum(x * x for x in A)

          def VLength(A):
            return sqrt(VLengthSquared(A))

          def VScaled(A, Scale):
            return tuple(x * Scale for x in A)

          def VNormalised(A):
            return VScaled(A, 1.0 / VLength(A))

          def VPerp(A):
            return (-A[1], A[0])

          #-----------------------------------------------------------------------

          if 0 <= index < len(spath) - 2:

            Leg = (spath[index], spath[index + 1])
            # with the origin at the start of the leg,
            # L is the leg vector and K is the car's (estimated) position.
            L = VDiff(Leg[1], Leg[0])
            K = VDiff(estimate, Leg[0])
            LSinister = VPerp(VNormalised(L))
            cte = VDot(K, LSinister)
            u = VDot(K, L) / VLengthSquared(L)

            if u > 1.0:
              index += 1

          else:

            cte = 0.0

          # ----------------------------------------


          diff_cte += cte

          steer = - params[0] * cte - params[1] * diff_cte

          myrobot = myrobot.move(grid, steer, speed)
          Data['ActualPath'].append((myrobot.x, myrobot.y))
          filter.move(grid, steer, speed)

          Z = myrobot.sense()
          filter.sense(Z)

          if not myrobot.check_collision(grid):
              Data['Sparks'].append((myrobot.x, myrobot.y))
              print '##### Collision ####'

          err += (cte ** 2)
          N += 1

          if printflag:
              print myrobot, cte, index, u

      return [myrobot.check_goal(goal), myrobot.num_collisions, myrobot.num_steps]


  # ------------------------------------------------
  #
  # this is our main routine
  #

  def main(grid, init, goal, steering_noise, distance_noise, measurement_noise,
       weight_data, weight_smooth, p_gain, d_gain):

      path = plan(grid, init, goal)
      path.astar()
      path.smooth(weight_data, weight_smooth)
      Data['PlannedPath'] = path.spath
      return run(grid, goal, path.spath, [p_gain, d_gain])




  # ------------------------------------------------
  #
  # input data and parameters
  #


  # grid format:
  #   0 = navigable space
  #   1 = occupied space

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

  weight_data       = 0.1#0.1
  weight_smooth     = 0.1#0.2
  p_gain            = 2.0#2.0
  d_gain            = 7.5#6.0


  print main(grid, init, goal, steering_noise, distance_noise, measurement_noise,
             weight_data, weight_smooth, p_gain, d_gain)




  def twiddle(init_params):
      n_params   = len(init_params)
      dparams    = [1.0 for row in range(n_params)]
      params     = [0.0 for row in range(n_params)]
      K = 10

      for i in range(n_params):
          params[i] = init_params[i]


      best_error = 0.0;
      for k in range(K):
          ret = main(grid, init, goal,
                     steering_noise, distance_noise, measurement_noise,
                     params[0], params[1], params[2], params[3])
          if ret[0]:
              best_error += ret[1] * 100 + ret[2]
          else:
              best_error += 99999
      best_error = float(best_error) / float(k+1)
      print best_error

      n = 0
      while sum(dparams) > 0.0000001:
          for i in range(len(params)):
              params[i] += dparams[i]
              err = 0
              for k in range(K):
                  ret = main(grid, init, goal,
                             steering_noise, distance_noise, measurement_noise,
                             params[0], params[1], params[2], params[3], best_error)
                  if ret[0]:
                      err += ret[1] * 100 + ret[2]
                  else:
                      err += 99999
              print float(err) / float(k+1)
              if err < best_error:
                  best_error = float(err) / float(k+1)
                  dparams[i] *= 1.1
              else:
                  params[i] -= 2.0 * dparams[i]
                  err = 0
                  for k in range(K):
                      ret = main(grid, init, goal,
                                 steering_noise, distance_noise, measurement_noise,
                                 params[0], params[1], params[2], params[3], best_error)
                      if ret[0]:
                          err += ret[1] * 100 + ret[2]
                      else:
                          err += 99999
                  print float(err) / float(k+1)
                  if err < best_error:
                      best_error = float(err) / float(k+1)
                      dparams[i] *= 1.1
                  else:
                      params[i] += dparams[i]
                      dparams[i] *= 0.5
          n += 1
          print 'Twiddle #', n, params, ' -> ', best_error
      print ' '
      return params


  #twiddle([weight_data, weight_smooth, p_gain, d_gain])



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
    PlannedPath:
      Usually a polyline in Shape format, this is the (directed) path the
      car planned to follow as a result of smoothing the result of the A*
      route planner.
    EstimatedPath:
      Also in Shape format, a polylinr of the estimated positions of the
      car given by very noisy sensor measurements.
    Paths:
      For the puspose of visualising progressive path modifications, Paths
      is a list of Shapes to be rendered in red-to-indigo rainbow colours.
    BadPaths:
      Similar to Paths, BadPaths is a list of Shapes to be rendered in some
      muted colour, beneath any of those in Paths.

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

  def GreekCross(Centre, ArmLength):
    x, y = Centre
    s = ArmLength
    return [
      (A, (x - s, y)), (A, (x + s, y)), B,
      (A, (x, y - s)), (A, (x, y + s))
    ]

  #-----------------------------------------------------------------------------

  def SparkSymbolDef(IT, ID, NumPoints=8):

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

  # Planned path

  PlannedPath = Field('PlannedPath', None)
  if PlannedPath is not None:
    Result += IT('<!-- Planned path -->')
    Result += SVGPath(IT,
      ShapeFromVertices(PlannedPath, 1),
      {'stroke': '#0d0', 'stroke-width': '0.04'}
    )

  # Estimated path

  EstimatedPath = Field('EstimatedPath', None)
  if EstimatedPath is not None:
    Result += IT('<!-- Estimated path -->')
    Result += SVGPath(IT,
      ShapeFromVertices(EstimatedPath, 1),
      {
        'stroke': '#f09',
        'stroke-width': '0.04',
        'stroke-dasharray': '0.025 0.05'
      }
    )

  # Actual path

  ActualPath = Field('ActualPath', None)
  if ActualPath is not None:
    Result += IT('<!-- Actual path -->')
    Result += SVGPath(IT,
      ShapeFromVertices(ActualPath, 1),
      {'stroke': '#40f', 'stroke-width': '0.02'}
    )

  # Rejected paths

  BadPaths = Field('BadPaths', None)
  if BadPaths is not None and len(BadPaths) > 0:

    Result += IT('<!-- Rejected paths -->')
    Result += SVGGroup(IT, {
      'opacity': '0.10', 'stroke': '#ff0099'
    })

    NumBadPaths = len(BadPaths)

    for PathIx, Path in enumerate(BadPaths):
      Result += SVGPath(IT, Path)

    Result += SVGGroupEnd(IT)

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

  RunUnitCode(Data)

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
