#!/usr/bin/python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# vegesvgplot.py
# http://pastebin.com/6Aek3Exm
#-------------------------------------------------------------------------------


u'''VegeSVGPlot, a Python SVG plotting and maths module for vegetables

Description:
  The VegeSVGPlot module is a collection of simple mathematics, geometry
  and SVG output functions. The module makes it easy to write simple Python
  scripts to produce 2D graphical output such as function plots.

Author:
  Daniel Neville (Blancmange), creamygoat@gmail.com

Copyright:
  None

Licence:
  Public domain


INDEX


Imports

Shape constants:

  Pt_Break
  Pt_Anchor
  Pt_Control

  PtCmdWithCoordsSet
  PtCmdSet

Legendre–Gauss quadrature tables:

  LGQWeights25
  LGQAbscissae25

Exceptions:

  Error

tIndentTracker:

  __init__([IndentUnitStr], [StartingLevel], [LineTerminator])
  __call__(*StringArgs)
  Clone()
  StepIn([LevelIncrement])
  StepOut([LevelDecrement])
  LineTerminator
  IndentUnitStr
  Level
  LIStr

tAffineMtx:

  __init__(Origin, BasisVectors)
  __repr__()
  MultV(Vector)
  MultVectors(Vectors)
  MultAM(AM)
  B
  T

Affine matrix creation functions:

  AffineMtxTS(Translation, Scale)
  AffineMtxTRS2D(Translation, Angle, Scale)
  Affine2DMatrices(Origin, X)

Utility functions:

  ValidatedRange(ARange, Length)
  MergedDictionary(Original, Patch)
  Save(Data, FileName)

Array access functions:

  ArrayDimensions(MDArray)
  NewArray(Dimensions, Value)
  CopyArray(Source, [CopyDepth])
  At(MDArray, Indices)
  SetAt(MDArray, Indices, Value)
  EnumerateArray(MDArray, [Depth])

Basic vector functions:

  VZeros(n)
  VOnes(n)
  VStdBasis(Dimensions, Index, [Scale])
  VDim(A, n)
  VAug(A, x)
  VMajorAxis(A)
  VNeg(A)
  VSum(A, B...)
  VDiff(A, B)
  VSchur(A, B...)
  VDot(A, B)
  VLengthSquared(A)
  VLength(A)
  VManhattan(A)
  VScaled(A, scale)
  VNormalised(A)
  VPerp(A)
  VRevPerp(A)
  VCrossProduct(A, B)
  VCrossProduct4D(A, B, C)
  VScalarTripleProduct(A, B, C)
  VVectorTripleProduct(A, B, C)
  VProjectionOnto(Axis, Vector)
  VDiagonalMAV(Diagonals)
  VTransposedMAV(BasisVectors)
  VRectToPol(A)
  VPolToRect(DistanceAngle)
  VLerp(A, B, Progress)

Mathematical functions:

  BinomialCoefficient(n, k)
  BinomialRow(n)
  NextBinomialRow(Row)
  ApproxSaggita(ArcLength, ChordLength)
  LGQIntegral25(Interval, Fn, InitalParams, FinalParams)
  IntegralFunctionOfPLF(Vertices, C=0.0)
  EvaluatePQF(PQF, x)
  EvaluateInvPQF(PQF, y)

Linear intersection functions:

  LineParameter(Point, Line)
  XInterceptOfLine(Line)
  UnitXToLineIntersection(Line2)
  LineToLineIntersectionPoint(Line1, Line2)
  LineToLineIntersection(Line1, Line2)

Bézier functions:

  CubicBezierArcHandleLength(AngleSweep)
  BezierPoint(Curve, t)
  BezierPAT(Curve, t)
  SplitBezier(Curve, t)
  BezierDerivative(Curve)
  ManhattanBezierDeviance(Curve)
  BezierLength(Curve, [Interval])

Bézier intersection functions:

  UnitXToBezierIntersections(Curve, [Tolerance])
  LineToBezierIntersections(Line, Curve, [Tolerance])

Shape functions:

  ShapeDim(Shape, n)
  ShapeFromVertices(Vertices, Order)
  ShapePoints(Shape, [Range])
  ShapeSubpathRanges(Shape)
  ShapeCurveRanges(Shape, [Range])
  ShapeLength(Shape)
  LineToShapeIntersections(Line, Shape, [Tolerance])
  TransformedShape(AM, Shape)
  PiecewiseArc(Centre, Radius, AngleRange, NumPieces)

Output formatting functions:

  MaxDP(x, n)
  GFListStr(L)
  GFTupleStr(T)
  HTMLEscaped(Text)
  AttrMarkup(Attributes, PrependSpace)
  ProgressColourStr(Progress, [Opacity])

SVG functions:

  SVGStart(IT, Title, [SVGAttributes])
  SVGEnd(IT)
  SVGPathDataSegments(ShapePoints)
  SVGPath(IT, ShapePoints, [Attributes])
  SVGText(IT, Position, Text, [Attributes])
  SVGGroup(IT, [Attributes])
  SVGGroupEnd(IT)
  SVGGrid(IT, Grid)

'''


#-------------------------------------------------------------------------------
# Imports
#-------------------------------------------------------------------------------


import math

from math import (
  pi, sqrt, hypot, sin, cos, tan, asin, acos, atan, atan2, radians, degrees,
  floor, ceil
)


#-------------------------------------------------------------------------------
# Shape constants
#
# A “Shape” is a list of (PointType, Point) pairs intended to represent paths
# in the matter of Postscript or SVG but in a way which allows a path segment
# to be very easily reversed.
#
#-------------------------------------------------------------------------------


Pt_Break = 0
Pt_Anchor = 1
Pt_Control = 2

PtCmdWithCoordsSet = set([Pt_Anchor, Pt_Control])
PtCmdSet = set([Pt_Break, Pt_Anchor, Pt_Control])


#-------------------------------------------------------------------------------
# Legendre–Gauss quadrature tables
#
# The following tables were adapted from Mike "Pomax" Kamermans’s tables,
# which were computed to 295 decimal places and given for orders up to 64.
#
#-------------------------------------------------------------------------------


# Legendre–Gauss quadrature weights for
# the 25th order Legendre polynomial

LGQWeights25 = [
  0.1222424429903100416889595189458515058351, # −12
  0.1222424429903100416889595189458515058351, # +12
  0.1194557635357847722281781265129010473902, # −11
  0.1194557635357847722281781265129010473902, # +11
  0.1148582591457116483393255458695558086409, # −10
  0.1148582591457116483393255458695558086409, # +10
  0.1085196244742636531160939570501166193401, #  −9
  0.1085196244742636531160939570501166193401, #  +9
  0.1005359490670506442022068903926858269885, #  −8
  0.1005359490670506442022068903926858269885, #  +8
  0.0910282619829636498114972207028916533810, #  −7
  0.0910282619829636498114972207028916533810, #  +7
  0.0801407003350010180132349596691113022902, #  −6
  0.0801407003350010180132349596691113022902, #  +6
  0.0680383338123569172071871856567079685547, #  −5
  0.0680383338123569172071871856567079685547, #  +5
  0.0549046959758351919259368915404733241601, #  −4
  0.0549046959758351919259368915404733241601, #  +4
  0.0409391567013063126556234877116459536608, #  −3
  0.0409391567013063126556234877116459536608, #  +3
  0.0263549866150321372619018152952991449360, #  −2
  0.0263549866150321372619018152952991449360, #  +2
  0.0113937985010262879479029641132347736033, #  −1
  0.0113937985010262879479029641132347736033, #  +1
  0.1231760537267154512039028730790501424382  #   0
]

# Legendre–Gauss quadrature abscissae (x-values)
# for the 25th order Legendre polynomial

LGQAbscissae25 = [
 -0.1228646926107103963873598188080368055322, # −12
  0.1228646926107103963873598188080368055322, # +12
 -0.2438668837209884320451903627974515864056, # −11
  0.2438668837209884320451903627974515864056, # +11
 -0.3611723058093878377358217301276406674221, # −10
  0.3611723058093878377358217301276406674221, # +10
 -0.4730027314457149605221821150091920413318, #  −9
  0.4730027314457149605221821150091920413318, #  +9
 -0.5776629302412229677236898416126540673957, #  −8
  0.5776629302412229677236898416126540673957, #  +8
 -0.6735663684734683644851206332476221758834, #  −7
  0.6735663684734683644851206332476221758834, #  +7
 -0.7592592630373576305772828652043609763875, #  −6
  0.7592592630373576305772828652043609763875, #  +6
 -0.8334426287608340014210211086935695694610, #  −5
  0.8334426287608340014210211086935695694610, #  +5
 -0.8949919978782753688510420067828049541746, #  −4
  0.8949919978782753688510420067828049541746, #  +4
 -0.9429745712289743394140111696584705319052, #  −3
  0.9429745712289743394140111696584705319052, #  +3
 -0.9766639214595175114983153864795940677454, #  −2
  0.9766639214595175114983153864795940677454, #  +2
 -0.9955569697904980979087849468939016172576, #  −1
  0.9955569697904980979087849468939016172576, #  +1
  0                                           #   0
]


#-------------------------------------------------------------------------------
# Exceptions
#-------------------------------------------------------------------------------


class Error (Exception):
  pass;


#-------------------------------------------------------------------------------
# tIndentTracker
#-------------------------------------------------------------------------------


class tIndentTracker (object):

  u'''Keeper of current indentation levels for text output

  Functions which output strings of nicely indented markup can be made
  especially easy to use when an object like this keeps track of the
  current indenting level and the caller’s preference for the character
  or string used for indenting.

  The default method returns indented and line-terminated text given one
  or more string arguments, one argument per line of text. (Use the “*”
  list or tuple unpacking operator to work with lists or tuples.)

  For convenience when writing custom markup, the LIStr field may
  be used to begin each line of output.

  Functions which produce markup which imply a change in indentation
  level should update both the Level and LIStr fields.

  Methods:

    __init__([IndentUnitStr], [StartingLevel], [LineTerminator])
    __call__(*StringArgs)
    Clone()
    StepIn([LevelIncrement])
    StepOut([LevelDecrement])

  Fields:

    IndentUnitStr
    LineTerminator
    Level
    LIStr

  '''

  #-----------------------------------------------------------------------------

  def __init__(self, IndentUnitStr='  ', StartingLevel=0, LineTerminator='\n'):

    u'''Construct a keeper for the current indentation level for text output.

    All three arguments are optional.

    IndentUnitStr is the string used for each level of indentation.
    This string is typically two spaces (to emulate the em-square of
    typography), four spaces or a tab control character.

    StartingLevel, which defaults to zero, sets the current indentation
    level.

    LineTerminator is the character or string appended to each string
    argument supplied to the default method, a function which returns
    indented and line-terminated text.

    '''

    self.IndentUnitStr = IndentUnitStr
    self.LineTerminator = LineTerminator
    self.Level = StartingLevel
    self.LIStr = IndentUnitStr * StartingLevel

  #-----------------------------------------------------------------------------

  def __call__(self, *StringArgs):

    u'''Return a block of text with lines indented and terminated.

    Each argument is taken to be a line of text which is to be indented
    at the current level and terminated with LineTerminator. If a list
    or tuple of strings is to be processed, use the list or tuple unpacking
    operator “*”.

    '''

    IndentedLines = []
    for Line in StringArgs:
      ILine = Line.rstrip()
      if len(Line) > 0:
        ILine = self.LIStr + ILine
      IndentedLines.append(ILine)

    Result = self.LineTerminator.join(IndentedLines) + self.LineTerminator

    return Result

  #-----------------------------------------------------------------------------

  def Clone(self):

    u'''Create a clone of this tIndentTracker instance.

    A clone is handy for temporarily going into deeper nesting levels when
    the supplied tIndentTracker instance must be treated as immutable.

    '''

    Result = tIndentTracker()

    # Return an exact copy, even if it is internally inconsistent.
    # The user probably knows what they’re doing.

    Result.IndentUnitStr = self.IndentUnitStr
    Result.LineTerminator = self.LineTerminator
    Result.Level = self.StartingLevel
    Result.LIStr = self.LIStr

    return Result

  #-----------------------------------------------------------------------------

  def StepIn(self, LevelIncrement=1):

    u'''Increase the indentation level.

    The fields Level and the convenience string LIStr are updated.

    '''

    self.Level += LevelIncrement
    self.LIStr = self.IndentUnitStr * max(0, self.Level)

  #-----------------------------------------------------------------------------

  def StepOut(self, LevelDecrement=1):

    u'''Decrease the indentation level.

    The fields Level and the convenience string LIStr are updated.

    '''

    self.Level -= LevelDecrement
    self.LIStr = self.IndentUnitStr * max(0, self.Level)

  #-----------------------------------------------------------------------------

#-------------------------------------------------------------------------------
# tAffineMtx
#-------------------------------------------------------------------------------


class tAffineMtx (object):

  u'''Affine matrix for transforming non-homogeneous vectors

  An affine matrix is the usual square transformation matrix augmented
  with a translation vector. Thus uniform and non-uniform scaling,
  shearing, rotation and translation transformations can be combined
  in any order. Using the convention that vectors are written as columns,
  an affine matrix is like a homogeneous matrix without the bottom row and
  is used to transform non-homogeneous vectors or other affine matrices.

  Methods:

    __init__(Origin, BasisVectors)
    __repr__()
    MultV(Vector)
    MultVectors(Vectors)
    MultAM(AM)

  Fields:

    B - Basis vectors (rotation, scaling, skewing)
    T - Translation (Local origin)

  '''

  #-----------------------------------------------------------------------------

  def __init__(self, Origin, BasisVectors):

    u'''Construct an affine matrix.

    The origin is loaded into the translation part and is measured in terms
    of the reference frame outside the local frame constructed by the basis
    vectors and the origin.

    '''

    self.B = tuple(tuple(Bi) for Bi in BasisVectors)
    self.T = tuple(Origin)

  #-----------------------------------------------------------------------------

  def __repr__(self):

    u'''Return a Python code string representation of this affine matrix.'''

    Name = self.__class__.__name__
    return Name + '(' + repr(self.T) + ', ' + repr(self.B) + ')'

  #-----------------------------------------------------------------------------

  def MultV(self, Vector):

    u'''Return a vector transformed by this matrix.

    The vector is permitted to have a number of dimensions that differ to
    the number of basis vectors represented in the affine matrix. Excess
    basis vectors or excess vector components are ignored.

    If the vector is None or has a length of zero, the vector is returned
    untransformed. This behaviour is convenient for processing Shapes, which
    may include items like (Pt_Break, None).

    '''

    if (Vector is not None) and (len(Vector) > 0):

      Result = self.T

      for i, Basis in enumerate(self.B):
        if i < len(Vector):
          Result = VSum(Result, VScaled(Basis, Vector[i]))

    else:

      Result = Vector

    return Result

  #-----------------------------------------------------------------------------

  def MultVectors(self, Vectors):

    u'''Return a tuple of vectors transformed by this affine matrix.

    The vectors are each permitted to have a number of dimensions
    different to the number of basis vectors represented in the
    affine matrix. Excess basis vectors or excess vector components
    are ignored.

    Any vector that is None or has a length of zero is appears in
    the result untransformed.

    '''

    Result = []

    for V in Vectors:

      if (V is not None) and (len(V) > 0):

        VPrime = self.T

        for i, Basis in enumerate(self.B):
          if i < len(V):
            VPrime = VSum(VPrime, VScaled(Basis, V[i]))

      else:

        VPrime = V

      Result.append(VPrime)

    Result = tuple(Result)

    return Result

  #-----------------------------------------------------------------------------

  def MultAM(self, AM):

    u'''Return the product of this and a second affine matrix.

    When the resulting affine matrix is applied to vertices, the effect is as
    if the second matrix was applied first and the first matrix applied last.
    From the point of view of nested transformed reference frames in the manner
    of SVG and OpenGL, the transformations are nested in left-to-right order.

    Considering the vectors to be transformed as column vectors, the nesting of
    reference frames is performed by postmultiplying the current affine matrix
    with successive (affine) transformation matrices. The composite matrix is
    then premultiplied to each vector to be transformed.

    '''

    d = len(self.T)
    dr = range(d)

    B1t = VTransposedMAV(self.B)
    T1 = self.T
    B2 = AM.B
    T2 = AM.T

    BasisVectors = tuple(tuple(VDot(B1t[j], B2[i]) for j in dr) for i in dr)
    Traslation = tuple(VDot(B1t[j], T2) + T1[j] for j in DimRange)

    return tAffineMtx(Translation, BasisVectors)

  #-----------------------------------------------------------------------------


#-------------------------------------------------------------------------------
# Affine matrix creation functions
#-------------------------------------------------------------------------------


def AffineMtxTS(Translation, Scale):

  u'''Return an affine matrix given a translation and a scale.

  When the tAffineMtx returned is applied to vertices, the translation
  is performed last. From the point of view of transformed reference
  frames in the manner of SVG and OpenGL, the translation is performed
  first.

  The dimension of the resulting affine matrix is made to match the
  dimension of Translation, which defines a local origin relative to
  the origin of the ambient frame.

  If Scale is or contains only a single number, the scaling is uniform.
  If Scale is a list or tuple, say, the scaling can be different for
  each axis. Negative scales are permissible. Excess scale components
  are ignored and unspecified scale components are assumed to be 1.0.

  '''

  #-----------------------------------------------------------------------------

  d = len(Translation)
  dr = range(d)

  if hasattr(Scale, '__iter__'):
    S = tuple(Scale)[:d]
    S += (1.0,) * max(0, d - len(S))
  else:
    S = (Scale,) * d

  BasisVectors = VDiagonalMAV(S)

  return tAffineMtx(Translation, BasisVectors)


#-------------------------------------------------------------------------------


def AffineMtxTRS2D(Translation, Angle, Scale):

  u'''Return an affine matrix given a translation, rotation angle and a scale.

  Translation must be a vector of at least two dimensions, More dimensions
  are permitted but the rotation is performed only in the plane of the first
  two.

  Angle is measured in radians from the +x axis to the +y axis of the ambient
  frame.

  The transformation is applied to vectors in the order scaling, rotation
  and translation. From the point of view of nested reference frames in
  the manner of OpenGL and SCG, the order of nested transformations is
  translation, rotation and scaling.

  '''

  d = len(Translation)
  AM = AffineMtxTS(Translation, Scale)

  c = cos(Angle)
  s = sin(Angle)

  xs = AM.B[0][0]
  ys = AM.B[1][1]
  B = ((xs * c, xs * s), (ys * -s, ys * c))

  return tAffineMtx(AM.T, B)


#-------------------------------------------------------------------------------


def Affine2DMatrices(Origin, X):

  u'''Create matrices for mapping a line in 2D space to (0,0)–(1,0) and back.

  The line’s endpoints lie at Origin and Origin + X. This function gives the
  scale, rotation and translation necessary to map the line onto the x-axis
  between 0 and 1, thus aiding quick intersection and rejection tests.

  The result is in the form (M, InvM) where:

    M is the affine matrix to transform points so Line maps to (0,0)–(1,0) and
    InvM restores points from the UnitX frame back to the original frame.

  If the vector X is too small, an overflow or a divide-by-zero exception
  may be raised.

  '''

  Y = VPerp(X)

  # The scale to use in forming the inverse matrix’s basis vectors is
  # is the inverse square of the length of the X basis vector, not just
  # the inverse length. This is because the lengths of the basis vectors
  # of one matrix must be the reciprocals of those of the other.
  # ‖(‖X‖⁻²X)‖ × ‖X‖ = 1.

  s2 = 1.0 / VLengthSquared(X)

  MX = (s2 * X[0], s2 * Y[0])
  MY = (s2 * X[1], s2 * Y[1])
  MT = (
    -(MX[0] * Origin[0] + MY[0] * Origin[1]),
    -(MX[1] * Origin[0] + MY[1] * Origin[1]),
  )
  M = tAffineMtx(MT, (MX, MY))
  InvM = tAffineMtx(Origin, (X, Y))

  return (M, InvM)


#-------------------------------------------------------------------------------
# Utility functions
#-------------------------------------------------------------------------------


def ValidatedRange(ARange, Length):

  u'''Return a validated range for a given array length.

  The validated range may have a span of zero and it may lie at the end of
  a zero-based array (at an index of Length). It will, however, be sure to
  not be reversed or include intervals beyond either end of the array.

  if ARange is None, the range (0, Length) is returned. This behaviour
  makes it convenient to use this function on optional range arguments.

  '''

  if ARange is None:

    Start, End = (0, Length)

  else:

    Start, End = ARange

    Start = min(Length, Start) if Start >= 0 else max(0, Length + Start)
    End = min(Length, End) if End >= 0 else Length + End
    End = max(Start, End)

  return (Start, End)


#-------------------------------------------------------------------------------


def MergedDictionary(Original, Patch):

  u'''Return the union of two Python dictionaries.

  In the case of a key appearing in both dictionaries, Patch takes
  precedence over Original.

  For the convenience of easily providing defaults or immutable
  attributes to HTML or SVG tags, either argument may be None.
  In any case, the result is a (shallow) copy.

  '''

  if Original is not None:
    if Patch is not None:
      return dict(list(Original.items()) + list(Patch.items()))
    else:
      return dict(Original)
  else:
    if Patch is not None:
      return dict(Patch)
    else:
      return dict()


#-------------------------------------------------------------------------------


def Save(Data, FileName):

  u'''Save data to a new file.

  Data is usually a string. If a file with the given name already exists,
  it is overwritten.

  If the string is a Unicode string, it should be encoded:

    Save(Data.encode('utf_8'), FileName)

  Encoding will fail if Data is a non-Unicode string which contains a
  character outside of the 7-bit ASCII range. This can easily occur
  when an ordinary byte string contains a Latin-1 character such as
  the times symbol (“×”, code 215). Take care to prefix non-ASCII
  string constants with “u”.

  '''

  f = open(FileName, 'wb')

  try:
    f.write(Data)
  finally:
    f.close()


#-------------------------------------------------------------------------------
# Array access functions
#-------------------------------------------------------------------------------


def ArrayDimensions(MDArray):

  u'''Measure the size of the array in each dimension.

  If the given array is three dimensional and indexed with subscripts
  [0…5][0…7][0…2], the result will be (6, 8, 3).

  The array, which in Python is really an array of arrays if it is
  multidimensional, is assumed to be linear, rectangular, cuboid or
  similarly regular for higher dimensions.

  An empty array has a dimension of zero.

  '''

  Result = []
  Axis = MDArray
  while hasattr(Axis, '__iter__'):
    Result.append(len(Axis))
    if len(Axis) < 1:
      break
    Axis = Axis[0]
  Result = tuple(Result)
  return Result


#-------------------------------------------------------------------------------


def NewArray(Dimensions, Value):

  u'''Return a new array of the given dimensions, filled with a given value.

  Dimensions may either be a tuple or a list. When creating one-dimensional
  arrays, remember that the tuple or list constructor is needed around a
  bare integer and that the syntax for a one-element tuple has a comma to
  distinguish a tuple from an parenthesised number.

    NewArray((5,), 42) = [42, 42, 42, 42, 42]

  '''

  n = len(Dimensions)
  if n < 2:
    Result = [Value] * Dimensions[0]
  else:
    Result = []
    for i in range(Dimensions[0]):
      Result.append(NewArray(Dimensions[1:], Value))
  return Result


#-------------------------------------------------------------------------------


def CopyArray(Source, CopyDepth=None):

  u'''Create an arbitrarily deep copy of an array.

  If CopyDepth is 0, the result is another reference to the same array,
  not a copy. If CopyDepth is 1, a shallow copy is made. Higher values of
  CopyDepth result in deeper copies. This allows one to create separately
  mutable multidimensional arrays to refer to objects shared between them.

  Negative values for CopyDepth work in the manner of negative slice
  indices in python: A value of -1, for example, causes the entries of
  the final dimension to be shared.

  If CopyDepth is None (the default), the result will be a completely
  distinct copy.

  The behaviour of this function with CopyDepth set to None is subtly
  different to that for negative values of CopyDepth. A value of -1
  or lower causes the ArrayDimensions() function to be invoked. The
  measurement then makes the assumption of the array being regular
  important.

  This function cannot be used with arrays which contain circular
  references.

  '''

  #-----------------------------------------------------------------------------

  def CopyArray_Recursive(Source, d):
    if d == 0 or not hasattr(Source, '__iter__'):
      Result = Source
    elif d == 1:
      Result = [x for x in Source]
    else:
      Result = [CopyArray_Recursive(x, d - 1) for x in Source]
    return Result

  #-----------------------------------------------------------------------------

  if CopyDepth is None:
    d = -1
  else:
    d = CopyDepth
    if d < 0:
      d = max(0, len(ArrayDimensions(Source)) + d)

  return CopyArray_Recursive(Source, d)


#-------------------------------------------------------------------------------


def At(MDArray, Indices):

  u'''Return an array element of the given indices.

  An array element that would be accessed as A[3][1][0], say, can
  be accessed as At(A, (3, 1, 0)) or as At(A, X) where X = (3, 1, 0).
  This is handy for writing code that is agnostic in regard to the
  number of dimensions being used.

  Remember that Indices must be a tuple, a list or something similar
  and that the Python syntax for a single-element tuple is “(x,)”.

  '''

  Result = MDArray
  for i in Indices:
    Result = Result[i]
  return Result


#-------------------------------------------------------------------------------


def SetAt(MDArray, Indices, Value):

  u'''Set an array element at the given indices.

  An array element that would be set with the statement A[1][5][2] = x,
  say, can be set with SetAt(A, Pos, x) where Pos is (1, 5, 2).

  Remember that Indices must be a tuple, a list or something similar
  and that the Python syntax for a single-element tuple is “(x,)”.

  '''

  Target = MDArray
  for i in Indices[:-1]:
    Target = Target[i]
  Target[Indices[-1]] = Value


#-------------------------------------------------------------------------------


def EnumerateArray(MDArray, Depth=None):

  u'''Enumerate the indices and the elements of a multidimensional array.

  The result is a generator which can be used in the following manner:

    for Pos, Element in EnumerateArray(MDArray):
      ...

  Pos is a tuple of the indices required to access the array using At
  (reading) or SetAt (writing). Element is already set to At(MDArray, Pos).

  Depth, an optional argument in the constructor, allows the traversal
  to be restricted to the major dimensions. In the manner of Python
  array indices, Depth may be given a negative value.

  A value of -1 for Depth causes all but the last dimension to be
  traversed. This can be handy for efficiently updating the contents
  of a multidimensional array. If Depth is zero, the enumeration yields
  nothing.

  '''

  Dim = ArrayDimensions(MDArray)

  if Depth is None:
    d = len(Dim)
  else:
    d = Depth
    if d < 0:
      d += len(Dim)
    Dim = Dim[:d]

  Pos = [0] * len(Dim)
  i = len(Pos) - 1

  while i >= 0:
    yield (tuple(Pos), At(MDArray, Pos))
    while i >= 0:
      x = (Pos[i] + 1)
      if x < Dim[i]:
        Pos[i] = x
        i = len(Pos) - 1
        break
      else:
        Pos[i] = 0
        i -= 1


#-------------------------------------------------------------------------------
# Basic vector functions
#
# For serious work with linear algebra, the numpy module is useful, though
# it’s handy to have basic vector functions which work with the tuples or
# lists commonly used as vectors.
#
# Vectors are assumed to be column vectors represented by zero-based tuples
# such that
#
#       ⎡x⎤
#   A = ⎢y⎥ implies A[0] = x, A[1] = y and A[2] = z.
#       ⎣z⎦
#
# In program code, A = (x, y, z). Though lists are acceptable as arguments,
# tuples are preferred because they consume less memory, are handled much
# more quickly than lists and most importantly, are free from the risk of
# aliasing bugs. Some aliasing bugs, such as which result from using a list
# as a default argument in a function can be surprising.
#
# The vector functions here assume the vector operands have the correct or
# consistent number of dimensions.
#
#-------------------------------------------------------------------------------


def VZeros(n):

  u'''Return an n-dimensional vector of zeros.'''

  return (0.0,) * n


#-------------------------------------------------------------------------------


def VOnes(n):

  u'''Return an n-dimensional vector of ones.'''

  return (1.0,) * n


#-------------------------------------------------------------------------------


def VStdBasis(Dimensions, Index, Scale=1.0):

  u'''Return a standard basis vector, optionally scaled.

  The result is a vector with Dimension elements, all zero except
  for a 1 at the given (zero-based) index. If the argument Scale
  is specified, Scale is used instead of the 1.

  VStdBasis(4, 2, 5) returns

    ⎡0⎤
    ⎢0⎥
    ⎢5⎥
    ⎣0⎦.

  Note that it’s common to use a one-based subscript to identify the
  basis vectors: The basis vectors e₁, e₂, e₃ correspond to x, y, z.
  This function uses zero-based indices to be compatible with the
  zero-based indices of lists and tuples in Python.

  '''

  return((0.0,) * Index) + (Scale,) + ((0.0,) * (Dimensions - 1 - Index))


#-------------------------------------------------------------------------------


def VDim(A, n):

  u'''Procrastinate a vector to the required number of dimensions.'''

  d = len(A)
  if n > d:
    # To the rack!
    Result = tuple(A) + (0.0,) * (n - d)
  elif n < d:
    # To the guillotine!
    Result = tuple(A)[:n]
  else:
    # No help is needed from Procrastus.
    Result = tuple(A)
  return Result


#-------------------------------------------------------------------------------


def VAug(A, *x):

  u'''Return vector augmented with one or more extra components.

  The extra components are supplied with one or more arguments after the
  given vector. If the extra componenets are to come from a vector, use
  the tuple unpacking operator “*”.

  Though Python’s array handling functions make this a trivial operation,
  it’s nice to avoid the use of the "+" operator in a way that might imply
  arithmetic addition to a bleary-eyed programmer.

  '''

  return tuple(A) + x


#-------------------------------------------------------------------------------


def VMajorAxis(A):

  u'''Return the index of the largest component of a vector.

  This function is handy for choosing numerically robust Cartesian-to-Euler
  conversion functions.

  '''

  MajorAbsValue = 0
  MajorIx = 0

  Ix = 0

  while Ix < len(A):
    AbsValue = abs(A[Ix])
    if AbsValue > MajorAbsValue:
      MajorAbsValue = AbsValue
      MajorIx = Ix
    Ix += 1

  return MajorIx


#-------------------------------------------------------------------------------


def VNeg(A):

  u'''Return −A, the negative of a vector.

  A negated vector has the same size as the original, but points in the
  opposite direction.

  '''

  return tuple(-x for x in A)


#-------------------------------------------------------------------------------


def VSum(*VectorArgs):

  u'''Return the sum of vectors.

  The result of the sum of vectors can be described as the result of
  moving in the direction and by the distance implied by each vector
  in turn. Thus if A is 4m due east and B is 3m due north, the sum of
  A and B is 4m east and 3m north (5m at a nautical bearing of 53.13°).

  Vector addition is both commutative and associative.

  In the manner of the built-in function max(), this function can take
  either two or more vector arguments or a single argument which contains
  a list or tuple of vectors.

  '''

  if len(VectorArgs) == 1:
    Vectors = VectorArgs[0]
  else:
    Vectors = VectorArgs
  Result = tuple(Vectors[0])
  for i in range(1, len(Vectors)):
    Result = tuple(a + b for a, b in zip(Result, Vectors[i]))
  return Result


#-------------------------------------------------------------------------------


def VDiff(A, B):

  u'''Return A − B, the difference between two vectors.

  Just as in ordinary arithmetic, A − B = A + −B. If A and B are position
  vectors, the result is the position of A relative to B. Likewise, if A
  and B are velocity vectors, the result is the velocity of A relative
  to B.

  '''

  return tuple(x - y for x, y in zip(A, B))


#-------------------------------------------------------------------------------


def VSchur(*VectorArgs):

  u'''Return the Schur product of vectors.

  The Schur or Hadamard product of two vectors is the element-wise
  product of the vectors.

    ⎡4⎤ ⎡ 3⎤   ⎡ 12⎤
    ⎢7⎥○⎢−2⎥ = ⎢−14⎥
    ⎣3⎦ ⎣ 3⎦   ⎣ 9 ⎦

  In the manner of the built-in function max(), this function can take
  either two or more vector arguments or a single argument which contains
  a list or tuple of vectors.

  '''

  if len(VectorArgs) == 1:
    Vectors = VectorArgs[0]
  else:
    Vectors = VectorArgs
  Result = tuple(Vectors[0])
  for i in range(1, len(Vectors)):
    Result = tuple(a * b for a, b in zip(Result, Vectors[i]))
  return Result


#-------------------------------------------------------------------------------


def VDot(A, B):

  u'''Return A·B, the dot product of two vectors.

  The dot product of two vectors is a scalar (a number from the set of reals)
  that is a product of each of lengths of the two vectors and of the cosine
  of the angle between them. If one vector is a unit vector (a vector whose
  length is exactly 1), the dot product of that and the other vector will
  indicate the length of the projection along the unit vector cast by the
  other vector.

  The dot product of two unit vectors gives the cosine of the angle between
  them. Thus:

    +1 ⇒ Parallel
     0 ⇒ Perpendicular
    −1 ⇒ Antiparallel

  Similarly, the sign of the dot product of any two vectors indicates
  whether they are at an acute, right or obtuse angle.

  The dot product of two (Cartesian) vectors is the sum of the elements
  of the Schur product of those vectors.

  '''

  return sum(x * y for x, y in zip(A, B))


#-------------------------------------------------------------------------------


def VLengthSquared(A):

  u'''Return ‖A‖², the square of the length of a vector.

  The square of the length of a vector A is A·A and thus requires no
  transcendental functions to compute whereas computing the length of
  a vector requires a call to the square root function.

  It is usually more efficient to test the square of a vector’s length
  against the square of a threshold than to test that vector’s length
  against the threshold.

  '''

  return sum(x * x for x in A)


#-------------------------------------------------------------------------------


def VLength(A):

  u'''Return ‖A‖, the length of a vector.

  The length of a vector is the square root of the sum of the squares of its
  Cartesian components in the manner of Pythagoras. Very often, ‖A‖² is
  needed. To save calling the (transcendental) square root function and
  squaring the result, use the VLengthSquared() function wherever possible.

  '''

  return sqrt(VLengthSquared(A))


#-------------------------------------------------------------------------------


def VManhattan(A):

  u'''Return the Manhattan (or taxicab) length of a vector.

  The Manhattan length is the sum of the absolute value of the vector’s
  components. It represents the distance from the origin one must travel
  to reach a given location when only north-south and east-west travel
  is permitted.

  This function is often used to find a rough approximation to the length
  of a vector.

  '''

  return sum(abs(x) for x in A)


#-------------------------------------------------------------------------------


def VScaled(A, Scale):

  u'''Return the scalar multiple of a vector.

  A scalar multiple of a vector is one that is parallel to the original
  vector (antiparallel in the case of a negative scale) but whose length
  is the original vector’s length multiplied by the absolute value of scale.

  Often a vector of a desired length is constructed from a unit vector
  and a scalar. A vehicle with a position P and an orientation given by
  a unit heading vector H made to travel a distance d in a straight line
  will arrive at P + d(H) where d(H) is H scaled by d.

  '''

  return tuple(x * Scale for x in A)


#-------------------------------------------------------------------------------


def VNormalised(A):

  u'''Return ‖A‖⁻¹(A), a unit vector parallel to the given vector.

  Unit vectors are vectors with a length (or "norm") of one. They are often
  used as basis vectors for defining coordinate systems or for indicating
  direction without magnitude.

  No exception is raised if the vector is null or an overflow results.
  Instead, a sensible-looking, made-up unit vector is returned.

  '''

  try:
    Result = VScaled(A, 1.0 / VLength(A))
  except (ZeroDivisionError, OverflowError):
    Result = VStdBasis(len(A), VMajorAxis(A))
  return Result


#-------------------------------------------------------------------------------


def VPerp(A):

  u'''Return the original 2D vector rotated by positive 90 degrees.

  Rotation is always positive when a point lying on the positive
  half of the first axis moves in the direction of the positive
  half of the second axis. On a graph where x is right and y is
  up, the perpendicular vector returned is anticlockwise from the
  original vector.

  The operator is written as superscript “up tack” to the right of
  the vector. In a manner similar to that of the 3D cross product
  operator, a mnemonic for the calculation is a construct resembling
  the determinant of a matrix:

    Perp(A) = ⎢ Ax  Ay  ⎥
              ⎢ <x> <y> ⎥

  '''

  return (-A[1], A[0])


#-------------------------------------------------------------------------------


def VRevPerp(A):

  u'''Return the original 2D vector rotated by negative 90 degrees.

  See VPerp().

  '''

  return (A[1], -A[0])


#-------------------------------------------------------------------------------


def VCrossProduct(A, B):

  u'''Return A × B, the vector cross product of two 3D vectors.

  The returned vector is perpendicular to both A and B, in the direction
  given by the left hand rule or the right hand rule, depending on the
  hand of the coordinate system used. The length of the resulting vector
  is proportional to the length of A, the length of B and the sine of the
  angle between A and B.

  The length of the cross product is the area of a parallelogram spanned
  by A and B. The area of a triangle spanned by A and B is half this value,
  a useful thing to know when it comes to calculating the area of a polygon.

  A mnemonic for calculating the cross product is a construction resembling
  the determinant of a matrix:

            ⎢ Ax  Ay  Az  ⎥
    A × B = ⎢ Bx  By  Bz  ⎥
            ⎢ <x> <y> <z> ⎥

   Some linear algebra textbooks have the standard basis vectors along the
   top row rather than the bottom row. Although that form of the determinant
   mnemonic yields the correct result in 3D or higher odd-numbered dimensions,
   the form shown above works just as well when it is applied to 2D or higher
   even-numbered dimensions.

   Remember that the cross product operator is neither commutative nor
   associative. In fact, A × B = −(B × A).

  '''

  return (
    (A[1] * B[2]) - (A[2] * B[1]),
    (A[2] * B[0]) - (A[0] * B[2]),
    (A[0] * B[1]) - (A[1] * B[0])
  )


#-------------------------------------------------------------------------------


def VCrossProduct4D(A, B, C):

  u'''Return the four-dimensional cross product of three 4D vectors.

  Explaining this function would require four dimensional hands or the help
  of one of the Centaurs in Greg Egan’s book Diaspora but the result can be
  calculated from this determinant-shaped mnemonic:

    ⎢ Ax  Ay  Az  Aw  ⎥
    ⎢ Bx  By  Bz  Bw  ⎥
    ⎢ Cx  Cy  Cz  Cw  ⎥
    ⎢ <x> <y> <z> <w> ⎥

  '''

  x = -(
    A[1] * (B[2] * C[3] - B[3] * C[2]) -
    A[2] * (B[1] * C[3] - B[3] * C[1]) +
    A[3] * (B[1] * C[2] - B[2] * C[1])
  )

  y = (
    A[0] * (B[2] * C[3] - B[3] * C[2]) -
    A[2] * (B[0] * C[3] - B[3] * C[0]) +
    A[3] * (B[0] * C[2] - B[2] * C[0])
  )

  z = -(
    A[0] * (B[1] * C[3] - B[3] * C[1]) -
    A[1] * (B[0] * C[3] - B[3] * C[0]) +
    A[3] * (B[0] * C[1] - B[1] * C[0])
  )

  w = (
    A[0] * (B[1] * C[2] - B[2] * C[1]) -
    A[1] * (B[0] * C[2] - B[2] * C[0]) +
    A[2] * (B[0] * C[1] - B[1] * C[0])
  )

  return (x, y, z, w)


#-------------------------------------------------------------------------------


def VScalarTripleProduct(A, B, C):

  u'''Return A·B×C, the scalar triple product of three 3D vectors.

  The result is a scalar whose absolute value happens to be the volume of a
  parallelepiped spanned by the three vectors. The volume of a tethrahedron
  spanned by the same vectors is 1/6 of this value, a useful thing to know
  when it comes to finding the volume of a polyhedron.

  The effect of reordering the arguments is only a possible change of sign
  of the result. If A, B and C follow the right-hand rule in a right-handed
  coordinate system, the result will be positive.

  If the result is zero, two or all three of the vectors are co-planar.

  u'''

  return VDot(A, VCrossProduct(B, C))


#-------------------------------------------------------------------------------


def VVectorTripleProduct(A, B, C):

  u'''Return A×(B×C), the vector triple product of three vectors.

  This function is included to keep VScalarTripleProduct from getting
  lonely. Apparently it has some meaning in physics.

  There are two forms of the vector triple product:

    A×(B×C) = B(A·C) − C(A·B)
    (A×B)×C = B(A·C) − A(C·B)

  This function returns the first one, Lagrange’s form.

  u'''

  return VDiff(
    VScaled(B, VDot(A, C)),
    VScaled(C, VDot(A, B))
  )


#-------------------------------------------------------------------------------


def VProjectionOnto(Axis, Vector):

  u'''Return the component of Vector that lies along Axis.

  Axis need not be normalised.

             A·V
  Proj (V) = ―――(A)
      A      A·A

  Note that no square root calculation is necessary.

  The component of Vector that is perpendicular to Axis can be
  found by subtracting the result of this function from Vector.

  If Axis is null or an overflow occurs, no exception is raised.
  Instead, a null vector is returned.

  '''

  try:
    Result = VScaled(
      Axis,
      VDot(Vector, Axis) / (1.0 * VLengthSquared(Axis))
    )
  except (ZeroDivisionError, OverflowError):
    Result = VZeros(len(Vector))
  return Result


#-------------------------------------------------------------------------------


def VDiagonalMAV(Diagonals):

    u'''Create a matrix-as-vectors with the entries for the main diagonal set.

                              ⎡1 0 0⎤   ⎛⎡1⎤ ⎡0⎤ ⎡0⎤⎞
    VDiagonalMAV((1, 3, 7)) = ⎢0 3 0⎥ = ⎜⎢0⎥,⎢3⎥,⎢0⎥⎟
                              ⎣0 0 7⎦   ⎝⎣0⎦ ⎣0⎦ ⎣7⎦⎠

    Because a diagonal matrix is its own transpose, the result can be thought
    of as either an array of column vectors or an array of row vectors. Here,
    the convention is that vectors are considered column vectors and matrices
    are arrays of column vectors.

    '''

    return tuple(
      VStdBasis(len(Diagonals), i, x) for i, x in enumerate(Diagonals)
    )


#-------------------------------------------------------------------------------


def VTransposedMAV(MtxAsVectors):

  u'''Return the transpose of a square matrix defined as a bunch of vectors.

  A matrix entry at i,j corresponds to the entries j,i in the transpose.

                  ⎛⎡a⎤ ⎡d⎤ ⎡g⎤⎞   ⎛⎡a⎤ ⎡b⎤ ⎡c⎤⎞
    VTransposedMAV⎜⎢b⎥,⎢e⎥,⎢h⎥⎟ = ⎜⎢d⎥,⎢e⎥,⎢f⎥⎟
                  ⎝⎣c⎦ ⎣f⎦ ⎣i⎦⎠   ⎝⎣g⎦ ⎣h⎦ ⎣i⎦⎠

  Note that matrix subscripts like i,j in maths refers to row i, column j
  (even where column vectors are used) while indexing elements of a matrix
  made of column vectors in Python requires subscripts of the form [j][i]
  (though i and j would both start at zero instead of one).

  '''

  DimRange = range(len(MtxAsVectors))
  return tuple(tuple(MtxAsVectors[j][i] for j in DimRange) for i in DimRange)


#-------------------------------------------------------------------------------


def VRectToPol(A):

  u'''Return the polar (distance, angle) form of a Cartesian (x, y) vector.

  The angle is given in radians y-from-x and ranges from −pi to +pi.
  If the given vector is null (0, 0), the result is also (0, 0).

  '''

  Distance = VLength(A)
  Angle = atan2(A[1], A[0])
  return (Distance, Angle)


#-------------------------------------------------------------------------------


def VPolToRect(DistanceAngle):

  u'''Return the Cartesian (x, y) form of a polar (distance, angle) vector.

  The angle is taken to be in radians y-from-x.

  '''

  c = cos(DistanceAngle[1])
  s = sin(DistanceAngle[1])
  return (DistanceAngle[0] * c, DistanceAngle[0] * s)


#-------------------------------------------------------------------------------


def VLerp(A, B, Progress):

  u'''Linearly interpolate between two vectors.

  If Progress is 0.0, A is returned. If Progress is 1.0, B is returned.
  A value of Progress between 0.0 and 1.0 yields a result that is a linear
  interpolation of A and B.

  This function can be used to blend colours, though if non-linear RGB
  values (such as stored in computer frame buffers) are used, it is
  important to convert them to linear RGB values in order to perform
  interpolation (blending) or indeed any meaningful colour arithmetic.

  Progress is not restricted to the range 0.0 to 1.0. The result of using
  a value for Progress that is less than zero or greater than one is a
  linear extrapolation.

  '''

  return VSum(
    VScaled(A, 1.0 - Progress),
    VScaled(B, Progress)
  )


#-------------------------------------------------------------------------------
# Mathematical functions
#-------------------------------------------------------------------------------


def BinomialCoefficient(n, k):

  u'''Return n-choose-k.

          k
      0 1 2 3 4⋯
     ┌─────────
    0│1
    1│1 1
  n 2│1 2 1
    3│1 3 3 1
    4│1 4 6 4 1
       ⋮

  The binomial coefficients are the coefficients that result from
  the expansion of (x + 1)ⁿ, e.g., 1x⁴ + 4x³ + 6x² + 4x + 1 for n = 4.

  '''

  if k >= 0 and k <= n:

    # The basic algorithm is now sufficiently guarded. All
    # the other “if” statements are merely for optimisation.

    if k == 0 or k == n:

      Result = 1

    else:

      if n < 4:

        Result = n

      else:

        if k <= (n // 2):
          j = k
        else:
          j = n - k

        # The basic algorithm begins here (but using j instead of k).

        Numerator = 1
        Divisor = 1
        i = 1

        while i <= j:
          Numerator *= (n - j + i)
          Divisor *= i
          i += 1

        Result = Numerator / Divisor

  else:

    Result = 0

  return Result


#-------------------------------------------------------------------------------


def BinomialRow(n):

  u'''Return an entire row of binomial coefficients.'''

  if n < 1:

    if n == 0:
      Result = (1,)
    else:
      Result = ()

  else:

    R = [1] + n * [0]
    i = 1

    while i <= n:
      j = i - 1
      while j >= 1:
        R[j] = R[j] + R[j - 1]
        j -= 1
      R[i] = 1
      i += 1

    Result = tuple(R)

  return Result


#-------------------------------------------------------------------------------


def NextBinomialRow(Row):

  u'''Return the successive row of binomial coefficients.

  The given row must be a tuple or list of valid binomial coefficients.
  The first valid row, then, is a list containing 1 (or 1.0).

  '''

  w = len(Row)

  if w > 0:

    R = [1]
    k = 1

    while k < len(Row):
      R.append(Row[k - 1] + Row[k])
      k += 1
    R.append(Row[0])

    Result = tuple(R)

  else:

    Result = (1,)

  return Result



#-------------------------------------------------------------------------------


def ApproxSaggita(ArcLength, ChordLength):

  u'''Approximate the saggita of a circular arc, given arc and chord lengths.

  The saggita is the distance between the midpoint of the arc and
  the midpoint of the chord, the line connecting the arc’s endpoints.
  If the arc is imagined as a bow and the chord the string, the saggita
  is the arrow. (“Saggita” means arrow.)

  '''

  return sqrt(0.1875 * (ArcLength * ArcLength - ChordLength * ChordLength))


#-------------------------------------------------------------------------------


def LGQIntegral25(Interval, Fn, InitalParams, FinalParams):

  u'''Perform 25-point Legendre–Gauss quadrature integration on a function.

  Interval is the range of integration in the form (x-start, x-finish).
  Fn is the function to be integrated, called with varying values of x,
  as determined by a table of Legendre–Gauss quadrature abscissae.
  InitialParams, x and FinalParams form the arguments for the function Fn.

  '''

  # The Gauss quadrature rule only integrates ∫f(x).dx over [−1,+1].
  # To integrate over [a,b], we must use ½(b−a)∫f(½(b−a)x + ½(b+a)).dx.
  # Thus to integrate over [0,t], we use ½t∫f(½tx + ½t).dx.

  a, b = Interval
  Scale = 0.5 * (b - a)
  Offset = 0.5 * (b + a)

  # Assemble the parameters. Just so the parameters don’t have to be
  # repeatedly concatenated, a single entry in the composite argument
  # list is marked for repeated overwriting with the value of x.

  IP = list(InitalParams)
  FP = list(FinalParams)
  Params = IP + [None] + FP
  XParamIx = len(IP)

  WFSum = 0.0
  i = 25

  while i > 0:
    i -= 1
    x = Scale * LGQAbscissae25[i] + Offset;
    Params[XParamIx] = x
    WFSum += LGQWeights25[i] * Fn(*Params)

  return Scale * WFSum

#-------------------------------------------------------------------------------


def IntegralFunctionOfPLF(Vertices, C=0.0):

  u'''Return QPF data for the integral of a piecewise linear function.

  The piecewise linear function is specified with a list of (x,y) vertices,
  the x components of which must be monotonically increasing. The result is
  a more complicated structure representing a piecewise quadratic function
  that is the integral of the given function.

  The linear function is assumed to be zero outside of the domain implied
  by the list of vertices. Thus C is both the integration constant and the
  value of the integral for the minimum value of x in the domain.

  The result is a list of ((x₀, S₀), (x₁, S₁), (a, b, c)) tuples where
  (x₀, S₀) is the start point of a segment, (x₁, S₁) is the segment’s
  end point and a, b and c are the coefficients of the polynomial
  S(x) = ax² + bx + c for that segment.

  '''

  Result = []
  S0 = C
  i = 0

  while i + 1 < len(Vertices):

    x0, y0 = Vertices[i]
    x1, y1 = Vertices[i + 1]
    dx = x1 - x0
    dy = y1 - y0

    if dx > 0.0:

      g = float(dy) / float(dx)

      # Find a, b and c in the expression ax² + bx + c.
      a = 0.5 * g
      b = y0 - g * x0
      c0 = x0 * (x0 * a + b)
      c = S0 - c0

      S1 = x1 * (x1 * a + b) + c
      Result.append(((x0, S0), (x1, S1), (a, b, c)))
      S0 = S1

    i += 1

  return Result


#-------------------------------------------------------------------------------


def EvaluatePQF(PQF, x):

  u'''Evaluate a piecewise quadratic function at x.

  The function is specified with a list of ((x₀, y₀), (x₁, y₁), (a, b, c))
  tuples where (x₀, y₀) is the start point of a segment, (x₁, y₁) is the
  segment’s end point and a, b and c are the coefficients of the polynomial
  y = ax² + bx + c for that segment.

  The segments must be continuous and monotonically increasing in x.

  '''

  FirstPoint = PQF[0][0]

  if x <= FirstPoint[0]:

    Result = FirstPoint[1]

  else:

    FinalPoint = PQF[-1][1]

    if x >= FinalPoint[0]:

      Result = FinalPoint[1]

    else:

      # Start with initial inclusive index bounds.
      LowIx = 0
      HighIx = len(PQF) - 1

      while HighIx > LowIx:
        MidIx = LowIx + ((HighIx - LowIx) // 2)
        x1 = PQF[MidIx][1][0]
        if x1 <= x:
          LowIx = MidIx + 1
        else:
          HighIx = MidIx
      # Whatever happens, LowIx = HighIx

      # The quadratic function is given as the coefficients in ax² + bx + c.
      QF = PQF[LowIx]
      a, b, c = QF[2]
      Result = x * (x * a + b) + c

  return Result


#-------------------------------------------------------------------------------


def EvaluateInvPQF(PQF, y):

  u'''Evaluate at y, the inverse of a piecewise quadratic function.

  The (non-inverted) function is specified with a list of ((x₀, y₀),
  (x₁, y₁), (a, b, c)) tuples where (x₀, y₀) is the start point of a
  segment, (x₁, y₁) is the segment’s end point and a, b and c are the
  coefficients of the polynomial y = ax² + bx + c for that segment.

  The segments must be continuous and monotonically increasing in both
  x and y.

  '''

  FirstPoint = PQF[0][0]

  if y <= FirstPoint[1]:

    Result = FirstPoint[0]

  else:

    FinalPoint = PQF[-1][1]

    if y >= FinalPoint[1]:

      Result = FinalPoint[0]

    else:

      # Start with initial inclusive index bounds.
      LowIx = 0
      HighIx = len(PQF) - 1

      while HighIx > LowIx:
        MidIx = LowIx + ((HighIx - LowIx) // 2)
        y1 = PQF[MidIx][1][1]
        if y > y1:
          LowIx = MidIx + 1
        else:
          HighIx = MidIx
      # Whatever happens, LowIx = HighIx

      QF = PQF[LowIx]

      # The formula for roots of quadratics is x = (−b ± √(b² - 4ac))/(2a)
      # so x = (−b ± √(b² - 4a(c - y)))/(2a).

      a, b, c = QF[2]

      if abs(a) < 1e-6:
        # The segment is close to linear.
        Result = (y - c) / b
      else:
        # The segment is parabolic.
        det = max(0.0, b * b - 4 * a * (c - y))
        Result = (-b + sqrt(det)) / (2 * a)

  return Result


#-------------------------------------------------------------------------------
# Linear intersection functions
#-------------------------------------------------------------------------------


def LineParameter(Point, Line):

  u'''Return a point’s corresponding parameter of a linear parametric function.

  The line is specified with two points, the first of which maps to
  parameter t = 0 and the second of which maps to t = 1. The point’s
  projection onto the line rather than the point itself is measured.

  The line is considered to be infinite in extent and the result may
  have a value less thank zero or greater than one.

  If the length of the line is zero or is very small, an exception is
  likely to be raised.

  '''

  K = VDiff(Point, Line[0])
  L = VDiff(Line[1], Line[0])
  t = VDot(K, L) / VLengthSquared(L)

  return t


#-------------------------------------------------------------------------------


def XInterceptOfLine(Line):

  u'''Return where an infinitely long line crosses the x axis.

  The line is described with two points. If no intersection with
  the x axis is found (because the line is horizontal, say), None
  is returned.

  If an intersection is found, The result is the value of x at the
  intersection rather than a coordinate pair.

  '''

  P1, P2 = Line

  x1, y1 = P1
  x2, y2 = P2

  try:
    Result = (x1 * y2 - y1 * x2) / float(y2 - y1)
  except (ZeroDivisionError, OverflowError):
    Result = None

  return Result


#-------------------------------------------------------------------------------


def UnitXToLineIntersection(Line2):

  u'''Return a [0..1] x-intercept as a pair of line parameters.

  The first line segment lies on the x-axis from x = 0 to x = 1. The
  second line, given by the argument Line2 is defined with two endpoints.
  The result is of the form (t1, t2) where t1 and t2 are parameters
  between 0 and 1 for UnitX and Line2 respectively. If the intersection
  point lies outside either of the line segments or the lines are parallel
  or degenerate, None is returned.

  '''

  Result = None

  x1, y1 = Line2[0]
  x2, y2 = Line2[1]

  if y1 <= 0.0 <= y2 or y2 <= 0.0 <= y1:

    try:

      t2 = max(0.0, min(1.0, y1 / (y1 - y2)))
      t1 = (1.0 - t2) * x1 + t2 * x2

      if 0.0 <= t1 <= 1.0:
        Result = (t1, t2)

    except (ZeroDivisionError, OverflowError):

      MinX, MaxX = (x1, x2) if x1 <= x2 else (x2, y1)

      if MinX <= 1.0 and MaxX >= 0.0:

        t1 = 0.5 * (max(MinX, 0.0) + min(MaxX, 1.0))

        try:
          t2 = (t1 - x1) / (x2 - x1)
        except (ZeroDivisionError, OverflowError):
          t2 = 0.5

        Result = (t1, t2)

  return Result


#-------------------------------------------------------------------------------


def LineToLineIntersectionPoint(Line1, Line2):

  u'''Return the intersection of two infinitely long lines.

  Each line is described with two points. If no intersection is found
  (because the lines are parallel or close to parallel, say), None is
  returned.

  '''

  P1, P2 = Line1
  P3, P4 = Line2

  x1, y1 = P1
  x2, y2 = P2
  x3, y3 = P3
  x4, y4 = P4

  #            ⎛                                      ⎞
  #            ⎜ ⎢⎢x1 y1⎥ ⎢x1 1⎥⎥    ⎢⎢x1 y1⎥ ⎢y1 1⎥⎥ ⎟
  #            ⎜ ⎢⎢x2 y2⎥ ⎢x2 1⎥⎥    ⎢⎢x2 y2⎥ ⎢y2 1⎥⎥ ⎟
  #            ⎜ ⎢              ⎥    ⎢              ⎥ ⎟
  #            ⎜ ⎢⎢x3 y3⎥ ⎢x3 1⎥⎥    ⎢⎢x3 y3⎥ ⎢y3 1⎥⎥ ⎟
  #            ⎜ ⎢⎢x4 y4⎥ ⎢x4 1⎥⎥    ⎢⎢x4 y4⎥ ⎢y4 1⎥⎥ ⎟
  # (x, y)  =  ⎜――――――――――――――――――, ――――――――――――――――――⎟
  #            ⎜ ⎢⎢x1 1⎥  ⎢y1 1⎥⎥    ⎢⎢x1 1⎥  ⎢y1 1⎥⎥ ⎟
  #            ⎜ ⎢⎢x2 1⎥  ⎢y2 1⎥⎥    ⎢⎢x2 1⎥  ⎢y2 1⎥⎥ ⎟
  #            ⎜ ⎢              ⎥    ⎢              ⎥ ⎟
  #            ⎜ ⎢⎢x3 1⎥  ⎢y3 1⎥⎥    ⎢⎢x3 1⎥  ⎢y3 1⎥⎥ ⎟
  #            ⎜ ⎢⎢x4 1⎥  ⎢y4 1⎥⎥    ⎢⎢x4 1⎥  ⎢y4 1⎥⎥ ⎟
  #            ⎝                                      ⎠

  c = x1 - x2
  d = x3 - x4
  e = y1 - y2
  f = y3 - y4

  #            ⎛                ⎞
  #            ⎜ ⎢a c⎥    ⎢a e⎥ ⎟
  #            ⎜ ⎢b d⎥    ⎢b f⎥ ⎟
  # (x, y)  =  ⎜―――――――, ―――――――⎟
  #            ⎜ ⎢c e⎥    ⎢c e⎥ ⎟
  #            ⎜ ⎢d f⎥    ⎢d f⎥ ⎟
  #            ⎝                ⎠

  try:

    z = 1.0 / (c * f - e * d)

    a = x1 * y2 - y1 * x2
    b = x3 * y4 - y3 * x4

    x = (a * d - c * b) * z
    y = (a * f - e * b) * z

    Result = (x, y)

  except (ZeroDivisionError, OverflowError):

    Result = None

  return Result


#-------------------------------------------------------------------------------


def LineToLineIntersection(Line1, Line2):

  u'''Return an intersection point as a vector and as line parameters.

  Each line segment is described with two endpoints. The result is of the
  form (Point, t1, t2) where t1 and t2 are parameters between 0 and 1 for
  Line1 and Line2 respectively. If the intersection point lies outside
  either of the line segments or the lines are parallel or degenerate,
  None is returned.

  '''

  Result = None

  P = LineToLineIntersectionPoint(Line1, Line2)

  if P is not None:

    try:
      t1 = LineParameter(P, Line1)
      if 0.0 <= t1 <= 1.0:
        t2 = LineParameter(P, Line2)
        if 0.0 <= t2 <= 1.0:
          Result = (P, t1, t2)
    except (ZeroDivisionError, OverflowError):
      pass

  return Result


#-------------------------------------------------------------------------------
# Bézier functions
#-------------------------------------------------------------------------------


def CubicBezierArcHandleLength(AngleSweep):

  u'''Return the handle length to use for an approximately circular arc.

  “Handle length” refers to the distance of a cubic Bézier curve’s (inner)
  control point to the anchor (endpoint) nearest to it.

  '''

  return 4.0 / 3.0 * tan(AngleSweep / 4.0)


#-------------------------------------------------------------------------------


def BezierPoint(Curve, t):

  u'''Return the point on a Bézier curve at parameter t.

  The Bézier curve may be of any order and is specified by a list of
  control points, the first and last of which are anchors.

  The parameter t normally ranges from 0.0 to 1.0. Values outside this
  range result in extrapolations of the Bézier curve.

  '''

  # A point on a Bézier curve is a blend of all control points. The first
  # and last of those are anchor points. For a given parameter t, Each
  # successive control point is weighted with the product of a binomial
  # coefficient, an ascending power of t and a descending power of (1 − t).
  #
  # A point at parameter t on a cubic Bézier curve is thus
  #
  #   1s³𝐏₀ + 3s²t𝐏₁ + 3st²𝐏₂ + 1t³𝐏₃
  #
  # where s = (1 − t).

  # Evaluating a Bézier curve directly with a Bernstein polynomial, however
  # leads to numerical problems due to small numbers being raised to high
  # powers.

  # NumTerms = len(Curve)
  # Order = NumTerms - 1
  #
  # s = 1 - t
  #
  # SPowers = [1.0]
  # TPowers = [1.0]
  #
  # for i in range(Order):
  #   SPowers.append(s * SPowers[i])
  #   TPowers.append(t * TPowers[i])
  #
  # Result = VZeros(len(Curve[0]))
  #
  # for i in range(NumTerms):
  #   w = BinomialCoefficient(Order, i) * SPowers[Order - i] * TPowers[i]
  #   Result = VSum(Result, VScaled(Curve[i], w))

  # deCasteljau’s method is superior.

  C = Curve

  while len(C) > 1:
    D = []
    i = 1
    while i < len(C):
      D.append(VLerp(C[i - 1], C[i], t))
      i += 1
    C = D

  Result = C[0]

  return Result


#-------------------------------------------------------------------------------


def BezierPAT(Curve, t):

  u'''Return both the point and a tangent on a Bézier curve at parameter t.

  The Bézier curve may be of any order and is specified by a list of
  control points, the first and last of which are anchors.

  The parameter t normally ranges from 0.0 to 1.0. Values outside this
  range result in extrapolations of the Bézier curve.

  The result is in the form (Point, Tangent). Tangent is not normalised.

  '''

  # deCasteljau’s method

  C = Curve

  while len(C) > 2:
    D = []
    i = 1
    while i < len(C):
      D.append(VLerp(C[i - 1], C[i], t))
      i += 1
    C = D

  Point = VLerp(C[0], C[1], t)
  Tangent = VDiff(C[1], C[0])

  return (Point, Tangent)


#-------------------------------------------------------------------------------


def SplitBezier(Curve, t):

  u'''Split a Bézier curve into two parts.

  The Bézier curve may be of any order and is specified by a list of
  control points, the first and last of which are anchors.

  The parameter t normally ranges from 0.0 to 1.0. Values of t outside
  this range lie on the extrapolated curve and cause the returned curves
  to overlap and to run in opposite directions to each other.

  '''

  # The implementation of deCasteljau’s algorithm is surprisingly
  # straightforward:
  #
  # Successive lists of points describing Bézier curves of successively
  # lower orders are each formed from the linearly interpolated intermediate
  # points at parameter t for each line segment of the immediately previous
  # list. The last list to be generated contains just one point, which is
  # point at parameter t.
  #
  # The first curve segment of the split Bézier curve is formed from the
  # start point of each of the original and successive lists.
  #
  # The second curve segment is formed from the end point of each of the
  # original and successive lists. The second curve is reversed so that
  # its endpoint is the original curve’s endpoint.

  C = Curve

  C1 = []
  C2 = []

  while len(C) > 0:

    C1.append(C[0])
    C2.append(C[-1])

    D = []
    i = 1

    while i < len(C):
      D.append(VLerp(C[i - 1], C[i], t))
      i += 1

    C = D

  C2.reverse()

  return C1, C2


#-------------------------------------------------------------------------------


def BezierDerivative(Curve):

  u'''Return the first derivative of a given Bézier curve.

  Curve must have at least two points.

  The resulting curve, evaluated at parameter t, gives the derivative with
  respect to t of the original curve at evaluated at t.

  The plot of the resulting curve is called a hodograph.

  '''

  Order = len(Curve) - 1

  if Order < 1:
   raise Error(
     'Cannot compute the derivative of a Bézier curve ' +
       'with fewer than two control points.'
   )

  Result = []
  i = 0

  while i < Order:
    Result.append(VScaled(VDiff(Curve[i + 1], Curve[i]), Order))
    i += 1

  return Result


#-------------------------------------------------------------------------------


def ManhattanBezierDeviance(Curve):

  u'''Approximately measure a Bézier curve’s deviation from flatness.

  This function considers a Bézier curve flat if all the control points are
  spaced evenly between the endpoints, representing a line progressing at
  uniform velocity.

  The Manhattan distance, used to avoid a square root calculation, can
  overestimate the deviance by a factor of up to about 1.414.

  The deviance is useful for indicating the maximum distance a point on
  the curve at parameter t could be from a point parameter t on a line
  segment connecting the curve’s endpoints.

  Though strictly lateral deviance is sometimes used, the manner of
  deviance used here is far better for dealing with the small but
  easily perceptible lobes caused by inner control points lying close
  to or beyond the axial extents of the anchor control points. Lateral
  deviances on axially steady curves can be comparatively large before
  they are noticed unless there is an adjacent curve to be tracked.
  In such a case, the tolerance to use can be easily and precisely
  specified.

  '''

  Result = 0.0
  Order = len(Curve) - 1

  if Order >= 2:

    InvOrder = 1.0 / Order
    First = Curve[0]
    Last = Curve[-1]

    i = 1

    while i < Order:

      IdealCP = VLerp(First, Last, i * InvOrder)
      Deviation = VManhattan(VDiff(Curve[i], IdealCP))
      Result = max(Result, Deviation)

      i += 1

  return Result


#-------------------------------------------------------------------------------


def BezierLength(Curve, Interval=(0.0, 1.0)):

  u'''Estimate the length of a Bézier curve over a given parameter interval.

  This function uses 25-point Legendre–Gauss quadrature integration and
  deCasteljau’s algorithm over the curves’s derivative. It should be rather
  accurate and numerically stable for all but absurdly high order curves.

  If Interval is reversed, the result will be negative. As deCasteljau’s
  algorithm can both interpolate and extrapolate Bézier curves, Interval
  need not be confined to the range [0,1].

  '''

  Result = 0.0

  Order = len(Curve) - 1

  if Order < 2:

    if Order == 1:
      Result = VLength(VDiff(Curve[1], Curve[0])) * (Interval[1] - Interval[0])

  else:

    # The function to be integrated is ‖d𝐏/dt‖ where 𝐏 is the curve.
    # In the 2D case, that translates to √((d𝐏x/dt)²+(d𝐏y/dt)²).
    # Because evaluating ∫(√((d𝐏x(t)/dt)²+(d𝐏y(t)/dt)²).dt directly
    # will summon both Great Cthulhu and a great big non-Euclidean
    # jar of K-Y Jelly, the Legendre–Gauss quadrature numerical method
    # is used instead.

    def LenDerivative(H, t):
      # 𝐇(t) = d𝐏/dt, so ‖𝐇(t)‖ = ‖d𝐏/dt‖, the function to be integrated.
      D = BezierPoint(H, t)
      return VLength(D)

    H = BezierDerivative(Curve)
    Result = LGQIntegral25(Interval, LenDerivative, [H], [])

  return Result


#-------------------------------------------------------------------------------
# Bézier intersection functions
#-------------------------------------------------------------------------------


def UnitXToBezierIntersections(Curve, Tolerance=0.0):

  u'''Find intersections between (0, 0)–(1, 0) and a Bézier curve of any order.

  For arbitrary line segments, both the line and the curve will have to be
  scaled and translated so that the line maps to (0, 0)–(1, 0).

  The result is a list with zero or more intersection records. Each record
  is in the form (LParam, CParam) where LParam and CParam are the parameters
  for the line (0, 0)–(1, 0) and Curve respectively.

  '''

  #-----------------------------------------------------------------------------

  # Guard against an excessively small value of Tolerance. If it’s too
  # small, the subdivision will never end.

  MIN_REL_TOLERANCE = 1e-15
  MIN_ABS_TOLERANCE = 1e-315

  mUp = 0x08
  mDown = 0x04
  mLeft = 0x02
  mRight = 0x01

  #---------------------------------------------------------------------------

  def MinimumPermissibleTolerance(Points):

    u'''Determine a safe tolerance for the largest value found in points.'''

    return max(
      MIN_REL_TOLERANCE * max(VManhattan(P) for P in Points),
      MIN_ABS_TOLERANCE
    )

  #---------------------------------------------------------------------------

  def MayIntersect(Curve):

    u'''Quickly test if the curve has any chance of intersecting UnitX.'''

    Result = False
    ClipFlags = 0

    for P in Curve:
      if P[1] >= 0.0:
        ClipFlags |= mUp
      elif P[1] <= 0.0:
        ClipFlags |= mDown
      if ClipFlags == mUp | mDown:
        Result = True
        break

    if Result:

      ClipFlags = 0

      for P in Curve:
        if P[0] <= 0.0:
          ClipFlags |= mLeft
        elif P[0] >= 1.0:
          ClipFlags |= mRight
        else:
          Result = True
          break
        if ClipFlags == mLeft | mRight:
          Result = True
          break

    return Result

  #-----------------------------------------------------------------------------

  def UnitXToBezier_Recursive(Curve, Tolerance):

    u'''Find UnitX-to-Bézier intersections given validated arguments.

    Not only are the arguments taken to be valid, the trivial cases of
    a Bézier curve with an order of less than two is assumed to have
    already been excluded.

    The result is a list containing zero or more (LParam, CParam) pairs.

    '''

    #---------------------------------------------------------------------------

    def UnitXToCurveSegment(Curve, ParentStart, ParentEnd):

      u'''Find intersections expressed with parameters for the parent curve.

      The result is a list containing zero or more (LParam, CParam) pairs.
      LParam still refers to the line (0, 0)–(1, 0) but CParam is measured
      in terms of the Bézier curve of which Curve is a segment.

      '''

      Result = []
      Intercepts = UnitXToBezier_Recursive(Curve, Tolerance)

      for LParam, CParam in Intercepts:
        ParentCParam = (1.0 - CParam) * ParentStart + CParam * ParentEnd
        Result.append((LParam, ParentCParam))

      return Result

    #---------------------------------------------------------------------------

    Result = []

    # Here would be the obvious place to call the quick test function,
    # MayIntersect but it is instead called by this function’s parent
    # and for each of the subcurves below.

    Line2 = (Curve[0], Curve[-1])
    StraightIntercept = UnitXToLineIntersection(Line2)
    Deviance = ManhattanBezierDeviance(Curve)

    if Deviance < Tolerance:

      # The curve is close enough to being a line to be considered a line.

      if StraightIntercept is not None:
        Result.append(StraightIntercept)

    else:

      # The curve must be subdivided. Ideally the curve would be split
      # at a point such that the largest possible subcurve is easily
      # rejected by the quick test function MayIntersect.

      t = 0.5

      if StraightIntercept is not None:

        # The line connecting the endpoints of the curve, the curve’s
        # baseline is used as a guide to determining a good parameter
        # t at which the curve is to be be split. If the the baseline
        # parameter already calculated were used for t, it would likely
        # overshoot the true intersection point and cause only tiny
        # subcurves to be easily rejected, greatly slowing down the
        # convergence.
        #
        # The baseline parameter t0 is modified by a margin which varies
        # according to the deviance of the curve and the slope of the
        # curve’s baseline to the line (0, 0)–(1, 0). Grazing lines
        # require larger margins.

        try:

          t0 = StraightIntercept[1]
          D = VDiff(Line2[1], Line2[0])
          Shallowness = abs(D[0] / D[1])

          # A fudge factor partially accounts for the overestimation
          # of a control point’s ability to impart deviance. Occasional
          # overshoots are acceptable.

          AbsMargin = 0.4 * Deviance * (1.0 + Shallowness)
          Margin = AbsMargin / VManhattan(D)

          if t0 < 0.5:
            t = max(0.001, min(0.5, t0 + Margin))
          else:
            t = min(0.999, max(0.5, t0 - Margin))

        except (ZeroDivisionError, OverflowError):
          t = 0.5

      Curve1, Curve2 = SplitBezier(Curve, t)

      # The quick test is performed on the subcurves here rather than
      # at the start of this function in order to avoid the overhead of
      # calling the intermediate curve parameter-mapping function and
      # then this one again only to find the line obviously misses the
      # subcurve.

      if MayIntersect(Curve1):
        Result += UnitXToCurveSegment(Curve1, 0.0, t)
      if MayIntersect(Curve2):
        Result += UnitXToCurveSegment(Curve2, t, 1.0)

    return Result

  #-----------------------------------------------------------------------------

  Result = []
  Order = len(Curve) - 1

  # Handle the trivial cases.

  if Order < 2:

    if Order == 1:

      Intercept = UnitXToLineIntersection(Curve)

      if Intercept is not None:
        Result = [Intercept]

  else:

    ValTolerance = max(MinimumPermissibleTolerance(Curve), Tolerance)

    if MayIntersect(Curve):
      Result = UnitXToBezier_Recursive(Curve, ValTolerance)

  return Result


#-------------------------------------------------------------------------------


def LineToBezierIntersections(Line, Curve, Tolerance=0.0):

  u'''Find intersections between a line segment and a Bézier curve of any order.

  The result is a list with zero or more intersection records. Each record
  is in the form (Point, Tangent, LParam, CParam) where Point is the location
  of the intersection, Tangent is an unnormalised forward tangent to the curve
  and LParam and CParam are the parameters for Line and Curve respectively.

  '''

  Result = []
  Order = len(Curve) - 1

  # Handle the trivial cases.

  if Order < 2:
    if Order == 1:
      Intercept = LineToLineIntersection(Line, Curve)
      if Intercept is not None:
        Point, LParam, CParam = Intercept
        Tangent = VDiff(Line[1], Line[0])
        Result = [(Point, Tangent, LParam, CParam)]
    return Result

  # Now for the interesting cases.

  try:

    # Transform the curve so the line corresponds to the x-axis between
    # x=0 and x=1.

    Origin = Line[0]
    X = VDiff(Line[1], Origin)
    M, InvM = Affine2DMatrices(Origin, X)
    C = M.MultVectors(Curve)
    Scale = 1.0 / VLength(X)

    Intersections = UnitXToBezierIntersections(C, Scale * Tolerance)

    for LParam, CParam in Intersections:
      Point, Tangent = BezierPAT(Curve, CParam)
      Result.append((Point, Tangent, LParam, CParam))

  except (ZeroDivisionError, OverflowError):

    pass

  return Result


#-------------------------------------------------------------------------------
# Shape functions
#-------------------------------------------------------------------------------


def ShapeDim(Shape, n):

  u'''Return a Shape with vertices of n dimenions.

  Vertices set to None in Shape are left as None in the result.

  '''

  return [(PtType, None if P is None else VDim(P, n)) for PtType, P in Shape]


#-------------------------------------------------------------------------------


def ShapeFromVertices(Vertices, Order):

  u'''Create a poly-Bézier from a list of vertices.

  A poly-Bézier is a piecewise curve of Bézier curves. The poly-Bézier
  returned by this function are all of the same order except perhaps
  for the last one in the case of the number of vertices falling short.

  If Order is 1, a polyline is returned.

  '''

  Result = []

  LastIx = len(Vertices) - 1
  CPIx = 0

  Ix = 0

  while Ix < LastIx:

    PtType = Pt_Anchor if CPIx == 0 else Pt_Control
    Result.append((PtType, Vertices[Ix]))

    CPIx += 1
    if CPIx >= Order:
      CPIx = 0

    Ix += 1

  if LastIx >= 0:
    Result.append((Pt_Anchor, Vertices[LastIx]))

  return Result


#-------------------------------------------------------------------------------


def ShapePoints(Shape, ShapeRange=None):

  u'''Return the bare coordinates of a Shape or a part of one,

  The shape is defined as a list of (PtType, Coords) tuples which mark
  anchors, control points and breaks.

  ShapeRange, if set, selects only a portion of the Shape.

  '''

  RangeStart, RangeEnd = ValidatedRange(ShapeRange, len(Shape))
  Result = [Coords for Point, Coords in Shape[RangeStart:RangeEnd]]

  return Result


#-------------------------------------------------------------------------------


def ShapeSubpathRanges(Shape):

  u'''List the ranges of each subpaths in a Shape.

  The shape is defined as a list of (PtType, Coords) tuples which mark
  anchors, control points and breaks.

  A subpath is defined by a contiguous run of Shape points without any
  marked with Pt_Break. The ranges are suitable for use with the slice
  operator.

  '''

  Result = []
  SubpathStart = None

  for i, ShapePt in enumerate(Shape):

    PtType = ShapePt[0]

    if SubpathStart is None:
      if PtType != Pt_Break:
        SubpathStart = i
    else:
      if PtType == Pt_Break:
        Result.append((SubpathStart, i))
        SubpathStart = None

  if SubpathStart is not None:
    Result.append((SubpathStart, len(Shape)))

  return Result


#-------------------------------------------------------------------------------


def ShapeCurveRanges(Shape, ShapeRange=None):

  u'''List the ranges of each line segment or Bézier curve in a Shape.

  The Shape can be one contiguous piecewise curve or polyline or it
  can be several. A list of curve ranges is returned without regard
  to the Pt_Break items which are used to separate subpaths.

  ShapeRange, if set, selects only a portion of the Shape.

  '''

  Result = []

  RangeStart, RangeEnd = ValidatedRange(ShapeRange, len(Shape))

  SubpathStart = None
  CurveStart = None

  i = RangeStart

  while i < RangeEnd:

    PtType = Shape[i][0]

    if i + 1 < RangeEnd:
      IsEndOfSubpath = Shape[i + 1][0] == Pt_Break
    else:
      IsEndOfSubpath = True

    if SubpathStart is None:
      if PtType != Pt_Break:
        SubpathStart = i
        CurveStart = i
    else:
      if PtType == Pt_Anchor:
        Result.append((CurveStart, i + 1))
        if IsEndOfSubpath:
          CurveStart = None
        else:
          CurveStart = i
      elif PtType == Pt_Break:
        Result.append((CurveStart, i))
        SubpathStart = None
        CurveStart = None

    i += 1

  return Result


#-------------------------------------------------------------------------------


def ShapeLength(Shape):

  u'''Estimate the path length of a Shape.

  A Shape is defined by a list of (PtType, Coords) tuples which mark
  anchors, control points and breaks.

  The discontinuities implied by points tagged with Pt_Break do not
  contribute to the measured length.

  '''

  Result = 0.0

  Ranges = ShapeCurveRanges(Shape)

  for Range in Ranges:
    Curve = ShapePoints(Shape[Range[0]:Range[1]])
    Result += BezierLength(Curve)

  return Result


#-------------------------------------------------------------------------------


def LineToShapeIntersections(Line, Shape, Tolerance=0.0):

  u'''Find intersections between a line segment and a Shape.

  A Shape is defined by a list of (PtType, Coords) tuples which mark
  anchors, control points and breaks.

  The result is a list with zero or more intersection records. Each record
  is in the form (Point, Tangent, LParam, SubpathIx, CurveIx, CParam) where:

    Point is the location of the intersection;
    Tangent is an unnormalised (forward) tangent of the Shape at Point;
    LParam is the parameter for Line;
    SubpathIx is a zero-based index of subpath, a run (or loop) of curves;
    CurveIx is a zero-based index of a line or Bézier curve in a run; and
    CParam is the parameter for that line or curve.

  If no intersection is found, None is returned.

  '''

  Result = []

  try:

    # Transform the curve so that the line corresponds to the x-axis
    # between x = 0 and x = 1.

    Origin = Line[0]
    X = VDiff(Line[1], Origin)
    M, InvM = Affine2DMatrices(Origin, X)
    Scale = 1.0 / VLength(X)

    for SubpathIx, SPRange in enumerate(ShapeSubpathRanges(Shape)):

      for CurveIx, CRange in enumerate(ShapeCurveRanges(Shape, SPRange)):

        Curve = ShapePoints(Shape, CRange)
        TransformedCurve = M.MultVectors(Curve)
        Intersections = UnitXToBezierIntersections(
          TransformedCurve, Scale * Tolerance
        )

        for LParam, CParam in Intersections:
          Point, Tangent = BezierPAT(Curve, CParam)
          Result.append((Point, Tangent, LParam, SubpathIx, CurveIx, CParam))

  except (ZeroDivisionError, OverflowError):

    pass

  return Result


#-------------------------------------------------------------------------------


def TransformedShape(AM, Shape):

  u'''Return a Shape transformed by an affine matrix.

  The shape is defined as a list of (PtType, Coords) tuples which mark
  anchors, control points and breaks.

  '''

  Result = []

  for PtType, Coords in Shape:
    Result.append((PtType, AM.MultV(Coords)))

  return Result


#-------------------------------------------------------------------------------


def PiecewiseArc(Centre, Radius, AngleRange, NumPieces):

  u'''Return a Shape consisting of Bézier curves approximating a circular arc.

  The shape is defined as a list of (PtType, Coords) tuples which mark
  anchors, control points and breaks.

  '''

  Result = []

  StartAngle, EndAngle = AngleRange
  AngleStep = (EndAngle - StartAngle) / float(NumPieces)

  if EndAngle > StartAngle:
    h = CubicBezierArcHandleLength(AngleStep)
  else:
    h = -CubicBezierArcHandleLength(-AngleStep)

  SegStart = VPolToRect((Radius, StartAngle))
  Result.append((Pt_Anchor, VSum(Centre, SegStart)))

  for i in range(NumPieces):

    H1 = VSum(SegStart, VScaled(VPerp(SegStart), h))
    SegEndAngle = EndAngle - (NumPieces - 1 - i) * AngleStep
    SegEnd = VPolToRect((Radius, SegEndAngle))
    H2 = VSum(SegEnd, VScaled(VPerp(SegEnd), -h))
    SegStart = SegEnd

    Result.append((Pt_Control, VSum(Centre, H1)))
    Result.append((Pt_Control, VSum(Centre, H2)))
    Result.append((Pt_Anchor, VSum(Centre, SegEnd)))

  return Result


#-------------------------------------------------------------------------------
# Output formatting functions
#-------------------------------------------------------------------------------


def MaxDP(x, n):

  u'''Return as a string, x at a maximum of n decimal places.'''

  s = '%.*f' % (n, x)

  if '.' in s:
    while s[-1:] == '0':
      s = s[:-1]
    if s[-1:] == '.':
      s = s[:-1]

  return s


#-------------------------------------------------------------------------------


def GFListStr(L):

  u'''Return as a string, a list (or tuple) in general precision format.'''

  return '[' + (', '.join('%g' % (x) for x in L)) + ']'


#-------------------------------------------------------------------------------


def GFTupleStr(T):

  u'''Return as a string, a tuple (or list) in general precision format.'''

  if len(T) == 1:
    return '(%g,)' % (T[0])
  else:
    return '(' + (', '.join('%g' % (x) for x in T)) + ')'


#-------------------------------------------------------------------------------


def HTMLEscaped(Text):

  u'''Return text safe to use in HTML text and in quoted attributes values.

  Using unquoted values in attribute assignments where the values can be
  chosen by an untrusted agent can lead to a script injection attack unless
  the values are very heavily sanitised. It is good practice to always wrap
  attribute values in single or double quotes.

  '''

  EntityMap = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&apos',
    '`': '&#96;'
  }

  Result = ""

  for RawC in Text:
    SafeC = EntityMap[RawC] if RawC in EntityMap else RawC
    Result += SafeC

  return Result


#-------------------------------------------------------------------------------


def AttrMarkup(Attributes, PrependSpace):

  u'''Return HTML-style attribute markup from a dictionary.

  if PrependSpace is True and there is at least one attribute assignment
  generated, a space is added to the beginning of the result.

  Both an empty dictionary and None are valid values for Attributes.

  '''

  Result = ''

  if Attributes is not None:
    for Attr, Value in Attributes.items():
      if PrependSpace or (Result != ''):
        Result += ' '
      Result += HTMLEscaped(Attr) + '="' + HTMLEscaped(Value) + '"'

  return Result


#-------------------------------------------------------------------------------


def ProgressColourStr(Progress, Opacity=None):

  u'''Return an SVG or CSS colour string to indicate progress.'''

  Colours = [
    (1.0, 0.0, 0.0),
    (1.0, 1.0, 0.0),
    (0.0, 1.0, 0.0),
    (0.0, 1.0, 1.0),
    (0.0, 0.0, 1.0),
    (1.0, 0.0, 1.0)
  ]

  a = 4.25 * max(0.0, min(1.0, Progress))
  f = floor(a)
  t = a - f
  i = int(f)

  C0 = Colours[i % 6]
  C1 = Colours[(i + 1) % 6]

  # Surprisingly, working with linear light makes for more readily
  # distinguishable rainbow hues even though the purpose of nonlinear
  # framebuffer encoding is to provide a perceptually linear ramp of
  # brightnesses.

  # Since 0.0 and 1.0 are the same in linear and nonlinear form, no
  # conversion to linear is necessary.
  #
  # C0 = [pow(x, 2.2) for x in C0]
  # C1 = [pow(x, 2.2) for x in C1]

  C = VLerp(C0, C1, t)
  C = [pow(x, 1.0/2.2) for x in C]
  C = VScaled(C, 255.0)

  r = int(round(C[0]))
  g = int(round(C[1]))
  b = int(round(C[2]))

  if Opacity is None:
    OpacityStr = '1'
  else:
    a= max(0.0, min(1.0, Opacity))
    OpacityStr = MaxDP(a, 3)

  if OpacityStr == '1':
    Result = '#%.2x%.2x%.2x' % (r, g, b)
  else:
    Result = 'rgba(%d, %d, %d, %s)' % (r, g, b, OpacityStr)

  return Result


#-------------------------------------------------------------------------------
# SVG functions
#-------------------------------------------------------------------------------


def SVGStart(IT, Title=None, SVGAttributes=None):

  u'''Return a string for the beginning of an SVG file.

  IT is a tIndentTracker object, Title is used in the <title> tag and SVGAttr
  is a dictionary of attributes used to supplement or override the default
  attributes assigned to the <svg> tag.

  '''

  TitleToUse = '(Untitled)' if Title is None or Title == '' else Title

  Attr = {
    'width': '28cm',
    'height': '19cm',
    'viewBox': '0 0 28 19',
    'preserveAspectRatio': 'xMidYMid meet',
    'version': '1.1',
    'xmlns': 'http://www.w3.org/2000/svg',
    'xmlns:xlink': 'http://www.w3.org/1999/xlink'
   }

  Attr = MergedDictionary(Attr, SVGAttributes)

  Result = IT(
    '<?xml version="1.0" standalone="no"?>',
    '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"',
    IT.IndentUnitStr + '"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">',
    '<svg' + AttrMarkup(Attr, True) + '>',
    '',
    '<title>' + HTMLEscaped(TitleToUse) + '</title>',
    ''
  )

  #IT.StepIn()

  return Result


#-------------------------------------------------------------------------------


def SVGEnd(IT):

  u'''Return a string for the end of an SVG file.'''

  #IT.StepOut()

  Result = IT('', '</svg>')

  return Result


#-------------------------------------------------------------------------------


def SVGPathDataSegments(Shape):

  u'''Return a list of SVG path commands from a Shape.

  The result is ready for pretty-printing and stuffing into the
  “d” attribute of a path tag.

  SVG path commands are very much like Postscript commands.

  '''

  def SVGNStr(n):
    u'''Return a string representation of a number, fit for an SVG.'''
    s = MaxDP(n, 6)
    return s

  def SVGVStr(V):
    u'''Return a string representation of a 2D vector, fit for an SVG.'''
    return SVGNStr(V[0]) + ',' + SVGNStr(V[1])

  Result = []

  FirstSegAnchor = None
  LastAnchor = None
  LastSegCP = None
  LastSegWasQuadratic = False

  Segment = []

  for i, ShapePt in enumerate(Shape):

    PtType, Coords = ShapePt

    if PtType == Pt_Anchor:

      if i + 1 < len(Shape):
        IsTerminal = Shape[i + 1][0] == Pt_Break
      else:
        IsTerminal = True

      if LastAnchor is None:

        if not IsTerminal:

          Result.append('M ' + SVGVStr(Coords))

          FirstSegAnchor = Coords
          LastAnchor = Coords
          LastSegCP = None

      else:

        if len(Segment) > 0:

          IsSmooth = False
          IsQuadratic = len(Segment) == 1
          IsCubic = len(Segment) == 2

          if (LastAnchor is not None) and (LastSegCP is not None):
            MirrorCP = VSum(LastAnchor, VDiff(LastAnchor, LastSegCP))
            if LastSegWasQuadratic == IsQuadratic:
              IsSmooth = SVGVStr(Segment[0]) == SVGVStr(MirrorCP)

          if IsQuadratic:
            if IsSmooth:
              CmdStr = 'T'
            else:
              CmdStr = 'Q'
          elif IsCubic:
            if IsSmooth:
              CmdStr = 'S'
            else:
              CmdStr = 'C'
          else:
            raise Error(
              u'SVG requires a Bézier curve to be of the order ' +
                'one, two or three (linear, quadratic or cubic).'
            )

          LastSegWasQuadratic = IsQuadratic
          LastAnchor = Coords
          LastSegCP = Segment[-1]
          Segment.append(Coords)

          if IsSmooth:
            PointsToOutput = Segment[1:]
          else:
            PointsToOutput = Segment[:]

          for V in PointsToOutput:
            CmdStr = CmdStr + ' ' + SVGVStr(V)

          Result.append(CmdStr)
          Segment = []

        else:

          XYStr = SVGVStr(Coords)

          if IsTerminal and XYStr == SVGVStr(FirstSegAnchor):

            Result.append('Z')

            FirstSegAnchor = None
            LastAnchor = None
            LastSegCP = None

          else:

            XStr = SVGNStr(Coords[0])
            YStr = SVGNStr(Coords[1])

            if LastAnchor is not None:
              IsH = YStr == SVGNStr(LastAnchor[1])
              IsV = XStr == SVGNStr(LastAnchor[0])
            else:
              IsH = False
              IsV = False

            if IsH:
              if not IsV:
                Result.append('H ' + XStr)
            else:
              if IsV:
                Result.append('V ' + YStr)
              else:
                Result.append('L ' + XYStr)

            LastAnchor = Coords
            LastSegCP = None

    elif PtType == Pt_Control:

      if LastAnchor is None:
        raise Error('A curve may not start with a control point.')

      Segment.append(Coords)

    elif PtType == Pt_Break:

      if len(Segment) > 0:
        raise Error('A Break command must not occur within a curve.')

      FirstSegAnchor = None
      LastAnchor = None
      LastSegCP = None

    else:

      raise Error('Unhandled point type %s.' % (str(PtType)))

  if len(Segment) > 0:
    raise Error('No anchor point was given for the last curve.')

  return Result


#-------------------------------------------------------------------------------


def SVGPath(IT, Shape, Attributes=None):

  u'''Return SVG markup for a Shape.

  A Shape is defined as a list of (PtType, Coords) tuples which mark
  anchors, control points and breaks.

  Attributes is a dictionary for writing the attribute markup for
  the SVG path tag. Common attributes to set include fill, fill-rule,
  stroke, stroke-width, stroke-linejoin and stroke-linecap. Both an
  empty dictionary and None are valid values for Attributes.

  '''

  Result = ''
  FirstLinePart = '<path' + AttrMarkup(Attributes, True) + ' d="'

  # Defer writing the beginning of the path markup.
  IT.StepIn()

  InnerLines = []
  AvailTextColumns = max(0, 78 - len(IT.LIStr))

  CmdSep = '  '
  LineStr = ''
  Commands = SVGPathDataSegments(Shape)

  for Cmd in Commands:
    if LineStr != '':
      RemColumns = AvailTextColumns - len(LineStr) - len(CmdSep) - len(Cmd)
      if RemColumns < 0:
        InnerLines.append(LineStr)
        LineStr = ''
    if LineStr != '':
      LineStr += CmdSep
    LineStr += Cmd
  if LineStr != '':
    InnerLines.append(LineStr)

  InnerText = IT(*InnerLines)
  IT.StepOut()

  if len(InnerLines) > 0:
    Result += IT(FirstLinePart)
    Result += InnerText
    Result += IT('"/>')
  else:
    Result += IT(FirstLinePart + '"/>')

  return Result


#-------------------------------------------------------------------------------


def SVGText(IT, Position, Text, Attributes=None):

  u'''Return SVG markup for a line of text.

  Several lines of text with similar attributes can have their attributes
  inherited from those of a containing group.

  Attributes is a dictionary for writing the attribute markup for
  the <text> tag. Common attributes to set include font-family,
  font-style, font-variant, font-size, font-weight, kerning,
  letter-spacing, word-spacing, text-decoration, text-anchor, fill,
  stroke and stroke-width. Both an empty dictionary and None are
  valid values for Attributes.

  '''

  BadKeys = ['x', 'X', 'y', 'Y']

  A = Attributes

  if Position is not None:

    PosStr = (
      ' x="' + MaxDP(Position[0], 5) + '" ' +
      'y="' + MaxDP(Position[1], 5) + '"'
    )

    if A is not None:
      for BadKey in BadKeys:
        if BadKey in A:
          if A is Attributes:
            A = dict(Attributes)
          del A[BadKey]

  else:

    PosStr = ''

  Result = IT(
    '<text' + PosStr + AttrMarkup(A, True) + '>' +
    HTMLEscaped(Text) +
    '</text>'
  )

  return Result


#-------------------------------------------------------------------------------


def SVGGroup(IT, Attributes=None):

  u'''Return markup for the beginning of an SVG group.

  A group allows objects to easily share properties in a manner to
  the group function of a desktop publishing package. This allows
  the group to be transformed or styled as one unit.

  Attributes is a dictionary for writing the attribute markup for
  the <g> tag. Common attributes to set include fill, fill-rule,
  stroke, stroke-width, stroke-linejoin and stroke-linecap. Both
  an empty dictionary and None are valid values for Attributes.

  '''

  Result = IT('<g' + AttrMarkup(Attributes, True) + '>')
  IT.StepIn()

  return Result


#-------------------------------------------------------------------------------


def SVGGroupEnd(IT):

  u'''Return markup for the end of an SVG group.'''

  IT.StepOut()
  Result = IT('</g>')

  return Result


#-------------------------------------------------------------------------------


def SVGGrid(IT, Grid):

  u'''Return transformed SVG group markup to facilitate graph plotting.

  Grid is a dictionary with the keys:

    'CanvasMinima': (left, top)
    'CanvasMaxima': (right, bottom)
    'RangeMinima': (x0, y0)
    'RangeMaxima': (x1, y1)
    'YIsUp': True|False
    'Transpose': True|False
    'SquareAlignment': 'Corner'|'Centre'
    'DrawGrid': True|False
    'DrawUnitAxes': True|False
    'GridLineAttributes': SVG Attributes for grid lines
    'GeneralAttributes': SVG Attributes for the group tag

  YIsUp assumes the current reference frame resembles the frame
  SVG begins with: <x> is right and <y> is down.

  If SquareAlignment is “Corner” or is unspecified, integer
  coordinates lie on the intersections of grid lines and
  RangeMinima and RangeMaxima are inclusive. If SquareAlignment
  is “Centre” or “Center”, integer coordinates lie in the centres
  of grid squares, RangeMinima is inclusive and RangeMaxima is
  exclusive in regard to the square indices.

  '''

  #-----------------------------------------------------------------------------

  # Shorthand

  A = Pt_Anchor
  C = Pt_Control
  B = (Pt_Break, None)

  #-----------------------------------------------------------------------------

  def Field(Name, Default):

    u'''Return a value of Grid given a key name or return a default value.'''

    return Grid[Name] if Name in Grid else Default

  #-----------------------------------------------------------------------------

  def DictWithDefaults(ContainerDict, DictName, Defaults):

    u'''Allow an optional dictionary to be merged over some defaults.'''

    Result = Defaults

    if DictName in ContainerDict:
      Result = MergedDictionary(Defaults, ContainerDict[DictName])

    return Result

  #-----------------------------------------------------------------------------

  def T(V):

    u'''Return a 2D vector with its ordinals swapped.'''

    return (V[1], V[0])

  #-----------------------------------------------------------------------------

  Result = ''

  Transposed = Field('Transpose', False)

  CanvasMinima = tuple(Grid['CanvasMinima'])
  CanvasMaxima = tuple(Grid['CanvasMaxima'])
  CanvasCentre = VLerp(CanvasMinima, CanvasMaxima, 0.5)
  CanvasSpan = VDiff(CanvasMaxima, CanvasMinima)

  if Transposed:
    TCanvasSpan = T(CanvasSpan)
  else:
    TCanvasSpan = CanvasSpan

  RangeMinima = tuple(Grid['RangeMinima'])
  RangeMaxima = tuple(Grid['RangeMaxima'])
  RangeCentre = VLerp(RangeMinima, RangeMaxima, 0.5)
  RangeSpan = VDiff(RangeMaxima, RangeMinima)

  s = min(TCanvasSpan[0] / RangeSpan[0], TCanvasSpan[1] / RangeSpan[1])
  Scale = (s, s)
  ScaleStr = str(Scale[0]) + ', ' + str(Scale[1])

  AddressSquareCentres = Field('SquareAlignment', 'Corner') != 'Corner'

  if AddressSquareCentres:
    h = 0.5 * Scale[0]
  else:
    h = 0.0
  GridOffset = (h, h)

  if Field('YIsUp', False):
    GridOffset = (GridOffset[0], -GridOffset[1])
    Scale = (Scale[0], -Scale[1])
    ScaleStr = str(Scale[0]) + ', ' + str(Scale[1])

  StrokeWidth = max(0.0075, min(0.02, (0.15 / Scale[0])))

  if Transposed:
    Origin = VDiff(
      VSum(CanvasCentre, T(GridOffset)),
      T(VSchur(Scale, RangeCentre))
    )
  else:
    Origin = VDiff(VSum(CanvasCentre, GridOffset), VSchur(Scale, RangeCentre))
  OriginStr = str(Origin[0]) + ', ' + str(Origin[1])

  GeneralAttributes = DictWithDefaults(
    Grid, 'GeneralAttributes', {
      'stroke': 'rgba(0, 192, 255, 0.5)',
      'fill': 'none',
      'stroke-linecap': 'butt',
      'stroke-width': '%g' % (StrokeWidth)
  })

  XFormList = []

  if Transposed:
    XFormList.append('matrix(0, %s, 0, %s)' % (ScaleStr, OriginStr))
  else:
    XFormList = []
    if Origin != (0, 0):
      XFormList.append('translate(' + OriginStr + ')')
    if Scale != (1, 1):
      XFormList.append('scale(' + ScaleStr + ')')

  if len(XFormList) > 0:
    GeneralAttributes['transform'] = ' '.join(XFormList)

  GridLineAttributes = DictWithDefaults(
    Grid, 'GridLineAttributes', {
      'fill': 'none',
      'stroke-linecap': 'square',
      'stroke-width': '%g' % (max(0.0075, min(0.02, (0.1 / Scale[0]))))
  })

  Result += SVGGroup(IT, GeneralAttributes)

  if Field('DrawGrid', True):

    Result += IT('<!-- Grid lines -->')
    Result += SVGGroup(IT, GridLineAttributes)

    if AddressSquareCentres:
      GridOffset = (-0.5, -0.5)
    else:
      GridOffset = (0.0, 0.0)

    AM = AffineMtxTS(GridOffset, 1.0)

    Result += IT('<!-- Grid lines parallel to the y axis -->')
    S = []
    for x in range(RangeMinima[0], RangeMaxima[0] + 1):
      S += [(A, (x, RangeMinima[1])), (A, (x, RangeMaxima[1])), B]
    Result += SVGPath(IT, TransformedShape(AM, S))

    Result += IT('<!-- Grid lines parallel to the x axis -->')
    S = []
    for y in range(RangeMinima[1], RangeMaxima[1] + 1):
      S += [(A, (RangeMinima[0], y)), (A, (RangeMaxima[0], y)), B]
    Result += SVGPath(IT, TransformedShape(AM, S))

    if AddressSquareCentres:
      Result += IT('<!-- Grid square centres -->')
      S = []
      h = 0.125
      for x in range(RangeMinima[0], RangeMaxima[0]):
        for y in range(RangeMinima[1], RangeMaxima[1]):
          S += [(A, (x - h, y)), (A, (x + h, y)), B]
          S += [(A, (x, y - h)), (A, (x, y + h)), B]
      Result += SVGPath(IT, S, GridLineAttributes)

    Result += SVGGroupEnd(IT)

  if Field('DrawUnitAxes', False):
    Result += IT('<!-- Unit axes -->')
    Result += SVGGroup(IT, {'stroke': 'none'})
    h = 2.0 * (0.5 * StrokeWidth)
    ahx = 1.0 - 8.0 * h
    S = [
      (A, (-h, -h)), (A, (0.5 * h, h)), (A, (ahx, h)), (A, (ahx, 3.0 * h)),
      (A, (1.0, 0.0)), (A, (ahx, -3.0 * h)), (A, (ahx, -h)),
      (A, (-h, -h))
    ]
    Result += IT('<!-- Origin -->')
    Result += IT('<circle cx="0" cy="r" r="0.1" ' +
      'fill="none" stroke="#777" stroke-width="%g"/>' % (2.0 * h))
    Result += IT('<!-- x -->')
    Result += SVGPath(IT, S, {'fill': '#e00'})
    S[1] = (A, (h, h))
    S = TransformedShape(AffineMtxTRS2D((0.0, 0.0), 0.5 * pi, (1.0, -1.0)), S)
    Result += IT('<!-- y -->')
    Result += SVGPath(IT, S, {'fill': '#0c0'})
    Result += SVGGroupEnd(IT)

  return Result


#-------------------------------------------------------------------------------
# End
#-------------------------------------------------------------------------------
