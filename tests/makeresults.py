# -*- coding: utf-8 -*-
## @package makeresults
# <PACKAGE DESCRIPTION>
#
# @copyright Jonathan Pickering and Joanna Leng, University of Leeds, Leeds, UK.
"""
Created on 06 Oct 2021

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

@copyright 2021
@author: j.h.pickering@leeds.ac.uk
"""
# set up linting conditions
# pylint: disable = too-many-public-methods
# pylint: disable = c-extension-no-member
from collections import namedtuple

import PyQt5.QtCore as qc
import PyQt5.QtWidgets as qw

from cgt.gui.penstore import PenStore
from cgt.util.scenegraphitems import list_to_g_line, list_to_g_point
from cgt.model.videoanalysisresultsstore import VideoAnalysisResultsStore

## store for test values
TestValues = namedtuple("TestValues", ["fps", "scale", "point_speed", "line_speed"])

def get_test_values():
    """
    get the values needed to set up and carry out a test of calculation of speeds
        Returns:
            frames per seconds
            scale length/pixel
            correct point speed
            correct line speed
    """
    return TestValues(10.0, 1.5, 8.3853, 7.5)

def make_results_object():
    """
    make a complete results object
    """
    store = VideoAnalysisResultsStore(None)

    for region in make_regions():
        store.add_region(region)

    for item in make_key_frames().items():
        for key_frame in item[1]:
            store.add_key_frame(item[0], key_frame)

    store.insert_line_marker(make_test_lines())
    store.insert_point_marker(make_test_points())

    return store

def make_region(x, y, width, height):
    """
    make a region
        Args:
            x (float): x coordinate of top left
            y (float): y coordinage of top left
            width (float): width of rectangle
            height (float):height of rectangle
        Returns:
            (QGraphicsRectItem)
    """
    rect = qc.QRectF(x, y, width, height)
    return qw.QGraphicsRectItem(rect)

def make_regions():
    """
    make a list of regions
        Returns:
            [QRect]
    """
    regions = []
    regions.append(make_region(0, 0, 100, 50))
    regions.append(make_region(20, 20, 200, 200))
    return regions

def make_key_frames():
    """
    make key frames for the regions
    """
    key_frames = {}
    key_frames[0] = [100, 200, 300]
    key_frames[1] = [50, 150]
    return key_frames

def make_test_points():
    """
    make test point data distance moved 55.902 each time step
        Returns:
            [QGraphicsItem]: holding one point marker with 3 keyframes
    """
    string_lists = []
    # id, ctrx, ctry, offsetx, offsety, frame, region
    string_lists.append(["0", "0", "0", "0", "0", "100", "0"])
    string_lists.append(["0", "0", "0", "50", "25", "200", "0"])
    string_lists.append(["0", "0", "0", "100", "50", "300", "0"])

    pen = PenStore()
    points = []
    for string_list in string_lists:
        points.append(list_to_g_point(string_list, pen.get_display_pen()))

    return points

def make_test_lines():
    """
    make test line data distance moved 50 pixels
        Returns:
            [QGraphicsItem]: holding one line marker with 2 keyframes
    """
    line_lists = []
    # id, startx, starty, endx, endy, offsetx, offsety, frame, region
    line_lists.append(["0", "20", "20", "20", "220", "0", "0", "50", "1"])
    line_lists.append(["0", "20", "20", "20", "220", "50", "0", "150", "1"])

    pen = PenStore()
    lines = []
    for line_list in line_lists:
        lines.append(list_to_g_line(line_list, pen.get_display_pen()))

    return lines
