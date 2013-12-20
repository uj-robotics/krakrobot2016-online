""" File responsible for producing svg descriptors of the scene """


# The SVG Plotting for Vegetables module can be found at
# http://pastebin.com/6Aek3Exm
from math import (
  pi, sqrt, hypot, sin, cos, tan, asin, acos, atan, atan2, radians, degrees,
  floor, ceil, exp
)

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
#TODO: move it from here
def fill_visualisation_descriptor(Data):
    Map = Data['Map']
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
    Data['Grid'] = Grid
    Data['Paths'] = Paths
    Data['Map'] = Map
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
        if Map[i][j] == 1:
          Result += IT('<circle cx="%g" cy="%g" r="0.495"/>\n' % (i, j))
          #Result += IT('<rect x="%g", y="%g" width="1" height="1" />\n' % (i, j))

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



  # Robot
  side = 0.2
  Result += SVGGroup(IT, {'transform': 'rotate(%g %g %g)'%(
                                       (Data['ActualOrientation'] * 180 / pi) + 180.0,
      Data['ActualPosition'][0],  Data['ActualPosition'][1])
  })
  Result += IT('<polygon points="%g,%g %g,%g %g,%g" style="fill:lime;stroke:purple;stroke-width:0.01" />'
  %(Data['ActualPosition'][0] + side/2.0, Data['ActualPosition'][1] - side/2.0,
  Data['ActualPosition'][0] + side/2.0, Data['ActualPosition'][1] + side/2.0,
    Data['ActualPosition'][0] - side, Data['ActualPosition'][1]
  ))
  Result += SVGGroupEnd(IT)

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
