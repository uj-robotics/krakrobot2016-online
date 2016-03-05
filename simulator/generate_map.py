#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""
Simple script for generating maps for KrakRobot 2016. Generates .svg and .png file for
given .map file.

TODO: Add generating capabilities for .map file and add blur filters

Usage: ./generate_map.py -h
"""

import optparse

from misc.visualisation import *
from misc.vegesvgplot import *
from map import *


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

    # -----------------------------------------------------------------------------

    # Shorthand

    A = Pt_Anchor
    C = Pt_Control
    B = (Pt_Break, None)

    # -----------------------------------------------------------------------------

    def Field(Name, Default):

        u'''Return a value of Grid given a key name or return a default value.'''

        return Grid[Name] if Name in Grid else Default

    # -----------------------------------------------------------------------------

    def DictWithDefaults(ContainerDict, DictName, Defaults):

        u'''Allow an optional dictionary to be merged over some defaults.'''

        Result = Defaults

        if DictName in ContainerDict:
            Result = MergedDictionary(Defaults, ContainerDict[DictName])

        return Result

    # -----------------------------------------------------------------------------

    def T(V):

        u'''Return a 2D vector with its ordinals swapped.'''

        return (V[1], V[0])

    # -----------------------------------------------------------------------------

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
    StrokeWidth = max(0.0075, min(0.02, (0.15 / Scale[0])))
    GridOffset = (0, 0)

    Origin = VDiff(VSum(CanvasCentre, GridOffset), VSchur(Scale, RangeCentre))
    OriginStr = str(Origin[0]) + ', ' + str(Origin[1])

    GeneralAttributes = DictWithDefaults(
        Grid, 'GeneralAttributes', {
            'stroke': 'rgba(0, 0, 0, 0.9)',
            'fill': 'none',
            'stroke-linecap': 'butt',
            'stroke-width': '%g' % (StrokeWidth)
        })

    print GeneralAttributes

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
    # GridLineAttributes['stroke'] = "rgba(0, 0, 0, 1)
    # Grid['GeneralAttributes']['stroke'] = 'black'
    Result += SVGGroup(IT, GeneralAttributes)
    if Field('DrawGrid', True):

        Result += IT('<!-- Grid lines -->')
        Result += SVGGroup(IT, GridLineAttributes)
        GridOffset = (0.0, 0.0)
        h = 1
        AM = AffineMtxTS(GridOffset, 1.0)

        Result += IT('<!-- Grid lines parallel to the y axis -->')
        S = []
        for x in range(RangeMinima[0] + 2, RangeMaxima[0] - 1):
            S += [(A, (x, RangeMinima[1] + 2 * h)), (A, (x, RangeMaxima[1] - 2 * h)), B]
        Result += SVGPath(IT, TransformedShape(AM, S))

        Result += IT('<!-- Grid lines parallel to the x axis -->')
        S = []
        for y in range(RangeMinima[1] + 2, RangeMaxima[1] - 1):
            S += [(A, (RangeMinima[0] + 2 * h, y)), (A, (RangeMaxima[0] - 2 * h, y)), B]
        Result += SVGPath(IT, TransformedShape(AM, S))

        Result += SVGGroupEnd(IT)

    return Result


def RenderFrameTemplate(Data):
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
    #
    # Result += SVGStart(IT, Title, {
    #     'width': '28cm'.format(Data['Map']['M']),
    #     'height': '19cm'.format(Data['Map']['N']),
    #     'viewBox': '0 0 {} {}'.format(Data['Map']['M'], Data['Map']['N'])
    # })

    Result += SVGStart(IT, Title, {
        'width': '9cm',
        'height': '9cm',
        'viewBox': '0 0 9 9'
    })

    # Background

    Result += IT(
        '<rect x="0" y="0" width="{}" height="{}" stroke="none" fill="white"/>'.format(Data['Map']['M'], Data['Map']['N'])
    )

    # Maze
    Result += IT('<!-- Board -->')
    Map = Data['Map']
    Board = Map['board']
    color_values ={
        'red': (255, 0, 0),
        'green': (0, 255, 0),
        'blue': (0, 0, 255)
    }

    fields = {color_name: [] for color_name in color_values.keys()}

    if Map.has_key('beeps'):
        Beeps = Map['beeps']
        assert len(Beeps)==3, "The beeps list must have exactly 3 elements. NOTE: beeps is deprecated. Use separate red, green and blue field lists."
        fields['red'].append(Beeps[0])
        fields['green'].append(Beeps[1])
        fields['blue'].append(Beeps[2])

    for color in color_values.keys():
        if Map.has_key(color):
            new_fields = Map[color]
            if len(new_fields) > 0:
                if isinstance(new_fields[0], list):
                    fields[color].extend(new_fields)
                else:
                    fields[color].append(new_fields)

    Result += SVGGroup(IT, {
        'fill': '#a40',
        'stroke': 'black',
        'stroke-width': '0.01',
        'stroke-linecap': 'butt',
    })

    for color in color_values.keys():
        for field in fields[color]:
            Result += IT('<rect x="%g" y="%g" width="1" height="1" stroke="none" fill="%s"/>\n'
                     % (field[0], field[1], '#%02x%02x%02x' % color_values[color]))

    # Result += IT('<rect x="%g" y="%g" width="1" height="1" stroke="none" fill="%s"/>\n'
    #          % (Beeps[1][0], Beeps[1][1], '#%02x%02x%02x' % (0, 255 ,0)))
    # Result += IT('<rect x="%g" y="%g" width="1" height="1" stroke="none" fill="%s"/>\n'
    #          % (Beeps[2][0], Beeps[2][1], '#%02x%02x%02x' % (0, 0 ,255)))

    for i in range(len(Board)):
        for j in range(len(Board[0])):
            if Board[i][j] == 1:
                # Result += IT('<circle cx="%g" cy="%g" r="0.495"/>\n' % (i, j))
                Result += IT('<rect x="%g" y="%g" width="1" height="1" stroke="none" fill="#B30000"/>\n'
                             % (i, j))

    Result += SVGGroupEnd(IT)
    Data['Grid'] = \
        {'SquareAlignment': 'Corner', 'RangeMinima': (0, 0),
         'GridLineAttributes': {'stroke': 'rgba(0, 0, 0, 1)', 'stroke-width': '0.1'},
         'CanvasMinima': (0, 0), 'DrawGrid': True, 'YIsUp': False, 'Transpose': True,
         'DrawUnitAxes': False, 'CanvasMaxima': (9, 9),
         'GeneralAttributes': {'stroke': 'black', 'stroke-width': '0.1'}, 'RangeMaxima': (9, 9)}

    Result += SVGGrid(IT, Data['Grid'])
    Result += SVGGroupEnd(IT)
    Result += IT('<!-- Board -->')
    Result += SVGEnd(IT)

    return Result


parser = optparse.OptionParser()
parser.add_option("--png_output_file", type="string")
parser.add_option("--svg_output_file", type="string")
parser.add_option("--map_file", type="string", default="maps/1.map")

if __name__ == "__main__":
    (opts, args) = parser.parse_args()
    map_ = load_map(opts.map_file, load_graphics=False)

    print map_

    if opts.svg_output_file:
        svg_output_file = opts.svg_output_file
    else:
        svg_output_file = map_["vector_graphics_file"]

    if opts.png_output_file:
        png_output_file = opts.png_output_file
    else:
        png_output_file = map_["color_bitmap_file"]

    svg_file = open(svg_output_file, "w")
    svg_file.write(RenderFrameTemplate({"Map": map_}))
    svg_file.close()
    print "Successfully generated SVG file '{}'. Converting to PNG '{}' now...".format(svg_output_file, png_output_file)
    res = os.system("inkscape -z -e {} -w 512 -h 512 {}".format(png_output_file, svg_output_file))
    if res != 0:
        print "Failed convert call"
