""" File responsible for producing svg descriptors of the scene """

# The SVG Plotting for Vegetables module can be found at
# http://pastebin.com/6Aek3Exm

from math import (
    pi
)

from misc.defines import *
from vegesvgplot import (
    # Shape constants
    Pt_Break, Pt_Anchor, Pt_Control,

    # Indent tracker class
    tIndentTracker,

    # Affine matrix creation functions
    AffineMtxTS, VPolToRect, VLerp,

    # Shape functions
    ShapeFromVertices, TransformedShape, PiecewiseArc,

    # Output formatting functions
    HTMLEscaped, ProgressColourStr,

    # SVG functions
    SVGStart, SVGEnd, SVGPath, SVGText,
    SVGGroup, SVGGroupEnd, SVGGrid
)

def fill_visualisation_descriptor(Data):
    Map = Data['Map']
    Data['Title'] = 'KrakRobot 2016 Qualifications'
    Grid = {
        'CanvasMinima': (0.5, 1.5),
        'CanvasMaxima': (27.5, 18.5),
        'RangeMinima': (0, 0),
        'RangeMaxima': (len(Map['board']), len(Map['board'][0])),
        'YIsUp': False,
        'Transpose': True,
        'SquareAlignment': 'Centre',
        'DrawGrid': False,
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
    B = (Pt_Break, None)
    x, y = Centre
    s = ArmLength
    return [
        (A, (x - s, y)), (A, (x + s, y)), B,
        (A, (x, y - s)), (A, (x, y + s))
    ]

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

def PrepareFrame(frame_template, animated_part):
    return frame_template.format(*animated_part)


def RenderAnimatedPart(Data):
    """ Renders list of strings that will be injected to frame """

    # -----------------------------------------------------------------------------

    def Field(Name, Default):
        return Data[Name] if Name in Data else Default

    # -----------------------------------------------------------------------------

    # TODO: string concatenation is slow
    robot_sprite = ""
    path = ""
    sparks = ""

    side = 0.5
    IT = tIndentTracker('  ')

    robot_sprite += SVGGroup(IT, {'transform': 'rotate(%g %g %g)' % (
        (Data['ActualOrientation'] * 180 / pi) + 180.0,
        Data['ActualPosition'][0], Data['ActualPosition'][1])
                                  })
    # robot_sprite += SVGGroup(IT, {'transform': 'scale(2)'})
    robot_sprite += IT('<polygon points="%g,%g %g,%g %g,%g" style="fill:lime;'
                       ''
                       'stroke:purple;stroke-width:0.06" />'
                       % (Data['ActualPosition'][0] + side / 2.0, Data['ActualPosition'][1] - side / 2.0,
                          Data['ActualPosition'][0] + side / 2.0, Data['ActualPosition'][1] + side / 2.0,
                          Data['ActualPosition'][0] - side, Data['ActualPosition'][1]
                          ))
    robot_sprite += SVGGroupEnd(IT)
    # robot_sprite += SVGGroupEnd(IT)


    ActualPath = Field('ActualPath', None)
    if ActualPath is not None:
        path += IT('<!-- Actual path -->')
        path += SVGPath(IT,
                        ShapeFromVertices(ActualPath, 1),
                        {'stroke': '#40f', 'stroke-width': '0.02'}
                        )


    # ??
    # Paths in rainbow colours
    Paths = Field('Paths', None)
    if Paths is not None and len(Paths) > 0:

        NumPaths = len(Paths)

        path += IT('<!-- Paths in rainbow colours -->')
        for PathIx, Path in enumerate(Paths):
            if NumPaths >= 2:
                Progress = float(PathIx) / float(NumPaths - 1)
            else:
                Progress = 1.0
            Opacity = 1.0 if Progress in [0.0, 1.0] else 0.60 + 0.00 * Progress
            ColourStr = ProgressColourStr(Progress, Opacity)
            path += IT('<!-- Path %d, (%.1f%%) -->' % (PathIx, 100.0 * Progress))
            path += SVGPath(IT, Path, {"stroke": ColourStr})

    Sparks = Field('Sparks', None)
    if Sparks is not None and len(Sparks) > 0:
        B = (Pt_Break, None)
        sparks += IT('<!-- Points of interests (sparks) -->')

        for SparkPos in Sparks:
            SparkPos = (SparkPos[0], SparkPos[1])
            S = (
                GreekCross(SparkPos, 0.4) + [B] +
                PiecewiseArc(SparkPos, 0.25, (0, 2.0 * pi), 8)
            )
            sparks += IT('<!-- Goal position -->')
            sparks += SVGPath(IT, S, {
                'stroke': '#d00', 'stroke-width': '0.1', 'stroke-linecap': 'butt'
            })
    # End of plot

    path += SVGGroupEnd(IT)

    return [robot_sprite, path, sparks]


def RenderFrameTemplate(Data, draw_dynamic_elements=True):
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

    # -----------------------------------------------------------------------------

    # Shorthand

    A = Pt_Anchor
    C = Pt_Control
    B = (Pt_Break, None)

    # -----------------------------------------------------------------------------

    def Field(Name, Default):
        return Data[Name] if Name in Data else Default

    # -----------------------------------------------------------------------------

    IT = tIndentTracker('  ')

    Result = ''
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
        '  <path d="M 0,0  L 10,5  L 0,10"/>',
        '</marker>'
    )
    # Sparks are not used
    # Result += SparkSymbolDef(IT, 'spark')  if Sparks is not None else ''

    # More marker, symbol and gradient definitions can go here.
    IT.StepOut()
    Result += IT('</defs>')

    # Background

    Result += IT(
        '<rect x="0" y="0" width="28" height="19" stroke="none" fill="white"/>'
    )

    # Outer group

    Result += IT('<!-- Outer group -->')
    Result += SVGGroup(IT, {'stroke': 'black', 'stroke-width': '0.025'})

    # Plot with grid

    Result += IT('<!-- Grid -->')
    Data['Grid'] = \
        {'SquareAlignment': 'Corner', 'RangeMinima': (0, 0),
         'GridLineAttributes': {'stroke': 'rgba(0, 192, 255, 0.5)', 'stroke-width': '0.02'},
         'CanvasMinima': (0.5, 1.5), 'DrawGrid': True, 'YIsUp': False, 'Transpose': True,
         'DrawUnitAxes': False, 'CanvasMaxima': (27.5, 18.5),
         'GeneralAttributes': {'stroke': 'black', 'stroke-width': '0.05'}, 'RangeMaxima': (9, 9)}

    Result += SVGGrid(IT, Data['Grid'])

    # Maze

    Map = Data['Map']['board']
    ColorMap = Data['Map']['color_board']

    if Map is not None:

        Result += IT('<!-- Hazards -->')
        Result += SVGGroup(IT, {
            'fill': '#a40',
            'stroke': 'black',
            'stroke-width': '0.01',
            'stroke-linecap': 'butt',
        })

        scale_color = 255.0 / len(Map)

        arrow_colors = {MAP_SPECIAL_DIRECTION: '00F5F1', MAP_SPECIAL_OPTIMAL: 'F58F00'}
        for i in range(len(Map)):
            for j in range(len(Map[0])):
                if sum(ColorMap[i][j]) > 0:
                    Result += IT('<rect x="%g" y="%g" width="1" height="1" stroke="none" fill="%s"/>\n'
                    % (i, j, '#%02x%02x%02x' %  (ColorMap[i][j][0], ColorMap[i][j][1], ColorMap[i][j][2])))

                if Map[i][j] == 1:
                    # Result += IT('<circle cx="%g" cy="%g" r="0.495"/>\n' % (i, j))
                    Result += IT('<rect x="%g" y="%g" width="1" height="1" stroke="none" fill="#B30000"/>\n'
                                 % (i, j))
                elif type(Map[i][j]) is list:

                    if Map[i][j][0] == MAP_SPECIAL_EUCLIDEAN_DISTANCE:
                        Result += IT('<rect x="%g" y="%g" width="1" height="1" stroke="none" fill="rgb(%g,%g,%g)"/>\n'
                                     % (i, j,
                                        max(0, 255 - int(scale_color * Map[i][j][1])),
                                        max(0, 255 - int(scale_color * Map[i][j][1])),
                                        max(0, 255 - int(scale_color * Map[i][j][1]))

                                        ))
                    else:
                        Result += SVGGroup(IT, {'transform': 'translate(%g, %g)' % (i, j)})
                        Result += SVGGroup(IT, {'transform': 'scale(0.0005)'})
                        Result += SVGGroup(IT, {
                            'transform': 'rotate(%g, %g, %g)' % (45 * Map[i][j][1] - 270, i - 0.5, i - 0.5)})

                        Result += IT('<polygon style="stroke:none; '
                                     'fill:#%s;" points="100,600 100,-200  '
                                     '500,200 500,-100  0,-600  -500,-100 -500,'
                                     '200 -100,-200 -100,600 "/>' % (arrow_colors[Map[i][j][0]],))
                        Result += SVGGroupEnd(IT)
                        Result += SVGGroupEnd(IT)
                        Result += SVGGroupEnd(IT)

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
    if draw_dynamic_elements:
        Result += '{0}'
    else:
        Result += ''

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
    if draw_dynamic_elements:
        Result += "{2}"
    else:
        Result += ''
    # if Sparks is not None and len(Sparks) > 0:
    #     Result += IT('<!-- Points of interests (sparks) -->')
    #     Result += SVGGroup(IT, {'transform': 'translate(-0.5, -0.5)'})
    #     for SparkPos in Sparks:
    #         Result += IT(
    #             ('<use x="%g" y="%g"' % (SparkPos[0], SparkPos[1])) +
    #             ' width="1" height="1" xlink:href="#spark"/>'
    #         )
    #     Result += SVGGroupEnd(IT)

    # Actual path
    if draw_dynamic_elements:
        Result += "{1}"
    else:
        Result += ''

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
    Result += SVGText(IT, (19.5, 0.82), 'Actual path')

    Result += IT('<!-- Legend lines -->')
    Result += SVGGroup(IT, {
        'fill': 'none',
        'stroke-width': '0.12',
        'stroke-linecap': 'round'
    })

    Result += SVGPath(IT,
                      [(Pt_Anchor, (18.5, 0.7)), (Pt_Anchor, (19.3, 0.7))],
                      {'stroke': '#40f'}
                      )

    Result += SVGGroupEnd(IT)

    # End of title group

    Result += SVGGroupEnd(IT)

    # End of outer group

    Result += SVGGroupEnd(IT)

    Result += SVGEnd(IT)

    return Result
