## -*- coding: utf-8 -*-
"""
Created on 12 April 2021

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

This work was funded by Joanna Leng's EPSRC funded RSE Fellowship (EP/R025819/1)

@copyright 2021
@author: j.h.pickering@leeds.ac.uk and j.leng@leeds.ac.uk
"""
# set up linting conditions
# pylint: disable = import-error

from collections import namedtuple
from math import sqrt

from cgt.util.markers import (MarkerTypes,
                              get_point_of_point,
                              get_frame)
from cgt.util.scenegraphitems import perpendicular_dist_to_position
from cgt.util.markers import get_region

def calculate_speeds(index, results, fps, scale):
    """
    carry out speeds calculation
        Args:
            index (int) the region
            results (VideoAnalysisResultsStore) the results object
            fps (float) the number of frames per second
            scale (float) the size of a pixel
    """
    #results = self._data_source.get_results()
    lines = []
    for marker in results.get_lines():
        if get_region(marker[0]) == index:
            lines.append(marker)

    points = []
    for marker in results.get_points():
        if get_region(marker[0]) == index:
            points.append(marker)

    calculator = VelocitiesCalculator(lines, points, fps, scale)
    calculator.process_latest_data()

    return calculator

class ScreenDisplacement():
    """data type for a single marker displacement"""

    def __init__(self, start_frame, end_frame, fps, length):
        """
        initalize the object
            Args:
                start_frame (int) frame number of the first frame
                end_frame (int) frame number of the end frame
                fps (float) the number of frames per second
                length (int/float) the length in pixels
        """
        ## first frame of the interval
        self._start_frame = None

        ## end frame the last frame of the interval
        self._end_frame = None

        ## the length of the displacement
        self._length = length

        ## the number of frames per second
        self._fps = fps

        if start_frame < end_frame:
            self._start_frame = start_frame
            self._end_frame = end_frame
        else:
            self._start_frame = end_frame
            self._end_frame = start_frame

    def get_start(self):
        """
        getter for start of time interval
        """
        return self._start_frame

    def get_end(self):
        """
        getter for end of time interval
        """
        return self._end_frame

    def get_length(self):
        """
        getter for the length
        """
        return self._length

    def get_speed(self):
        """
        find the speed of the motion (length/(end-start))
            Returns
                (float) the speed
        """
        time_interval = (float(self._end_frame)-float(self._start_frame))/self._fps
        raw_speed = (float(self._length))/time_interval
        return abs(raw_speed)

## data type for the speed of a marker
MarkerSpeed = namedtuple("MarkerSpeed", ["ID", "m_type", "speed"])

class VelocitiesCalculator():
    """
    calculate the velocities of the marker objects
    """

    def __init__(self, lines, points, fps, scale):
        """
            initialize object
                Args:
                    lines ([]): array of line markers
                    points ([]): array of point markers
                    fps (float): the number of frames per second
                    scale (float): the size of a pixel
        """

        ## the store of markers
        self._lines = lines
        self._points = points
        self._frames_per_second = fps
        self._scale = scale

        ## the velocities of the lines
        self._line_displacements = None

        ## the velocities of the points
        self._point_displacements = None

    def get_line_displacements(self):
        """
        getter for the array of line displacments
        """
        return self._line_displacements

    def get_point_displacements(self):
        """
        getter for the array of point displacments
        """
        return self._point_displacements

    def number_markers(self):
        """
        get the number of line and point markers
            Returns:
                tuple (number lines, number points)
        """
        return (len(self._lines),
                len(self._points))

    def process_latest_data(self):
        """
        get the latest data and calculate the screen displacements
        """
        self.make_lines()
        self.make_points()

    def make_lines(self):
        """
        get and convert the marker lines to displacements
        """
        self._line_displacements = []
        for marker in self._lines:
            previous = marker[0]
            marker_displacements = []

            for i in range(1, len(marker)):
                current = marker[i]

                if not (current.line().dx() == 0.0 and current.line().dy() == 0.0):
                    previous_dist = perpendicular_dist_to_position(previous, self._scale)
                    current_dist = perpendicular_dist_to_position(current, self._scale)
                    distance = current_dist - previous_dist

                    start = get_frame(previous)
                    end = get_frame(current)
                    # start_frame, end_frame, fps, length
                    displacement = ScreenDisplacement(start, end, self._frames_per_second, distance)
                    marker_displacements.append(displacement)

                    previous = current

            if len(marker_displacements) > 0:
                self._line_displacements.append(marker_displacements)

    def make_points(self):
        """
        get and convert the marker points to displacements
        """
        self._point_displacements = []

        for marker in self._points:
            previous = marker[0]
            marker_displacements = []

            for i in range(1, len(marker)):
                current = marker[i]
                start = get_point_of_point(previous) + previous.pos()
                end = get_point_of_point(current) + current.pos()
                seperation =  start - end

                del_x = seperation.x()*self._scale
                del_y = seperation.y()*self._scale

                length = sqrt(del_x*del_x + del_y*del_y)
                start = get_frame(previous)
                end = get_frame(current)

                # start_frame, end_frame, fps, length
                displacement = ScreenDisplacement(start, end, self._frames_per_second, length)
                marker_displacements.append(displacement)

                previous = current

            if len(marker_displacements) > 0:
                self._point_displacements.append(marker_displacements)

    def get_average_speeds(self):
        """
        make a list of average speeds of all markers
            Returns:
                [MarkerSpeed] the averages
        """
        averages = []

        for i, marker in enumerate(self._line_displacements):
            speed = 0.0
            for item in marker:
                speed += item.get_speed()

            speed /= float(len(marker))

            averages.append(MarkerSpeed(i, MarkerTypes.LINE, speed))

        for i, marker in enumerate(self._point_displacements):
            speed = 0.0
            for item in marker:
                speed += item.get_speed()

            speed /= float(len(marker))

            averages.append(MarkerSpeed(i, MarkerTypes.POINT, speed))

        return averages
