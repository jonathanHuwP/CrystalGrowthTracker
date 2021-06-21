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

from cgt.util.utils import (MarkerTypes,
                            get_point_of_point,
                            get_frame,
                            perpendicular_dist_to_position)

class ScreenDisplacement():
    """data type for a single marker displacement"""

    def __init__(self, start_frame, end_frame, length):
        """
        initalize the object
            Args:
                start_frame (int) frame number of the first frame
                end_frame (int) frame number of the end frame
                length (int/float) the length in pixels
        """
        ## first frame of the interval
        self._start_frame = None

        ## end frame the last frame of the interval
        self._end_frame = None

        ## the length of the displacement
        self._length = length

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

    def get_speed(self):
        """
        find the speed of the motion (length/(end-start))
            Returns
                (float) the speed
        """
        raw_speed = (float(self._length))/(float(self._end_frame)-float(self._start_frame))
        return abs(raw_speed)

## data type for the speed of a marker
MarkerSpeed = namedtuple("MarkerSpeed", ["ID", "m_type", "speed"])

class VelocitiesCalculator():
    """
    calculate the velocities of the marker objects
    """

    def __init__(self, data_source):
        """
            initialize object
                Args:
                    data_source the supplier of raw data
        """

        ## the store of markers
        self._data_source = data_source

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
        return (len(self._data_source.get_lines()),
                len(self._data_source.get_points()))

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
        for marker in self._data_source.get_lines():
            previous = marker[0]
            marker_displacements = []

            for i in range(1, len(marker)):
                current = marker[i]

                if not (current.line().dx() == 0.0 and current.line().dy() == 0.0):
                    previous_dist = perpendicular_dist_to_position(previous)
                    current_dist = perpendicular_dist_to_position(current)
                    distance = current_dist - previous_dist

                    start = get_frame(previous)
                    end = get_frame(current)
                    displacement = ScreenDisplacement(start, end, distance)
                    marker_displacements.append(displacement)

                    previous = current

            if len(marker_displacements) > 0:
                self._line_displacements.append(marker_displacements)

    def make_points(self):
        """
        get and convert the marker points to displacements
        """
        self._point_displacements = []

        for marker in self._data_source.get_points():
            previous = marker[0]
            marker_displacements = []

            for i in range(1, len(marker)):
                current = marker[i]
                start = get_point_of_point(previous) + previous.pos()
                end = get_point_of_point(current) + current.pos()
                seperation =  start - end

                length = sqrt(seperation.x()*seperation.x() + seperation.y()*seperation.y())
                start = get_frame(previous)
                end = get_frame(current)

                displacement = ScreenDisplacement(start, end, length)
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
