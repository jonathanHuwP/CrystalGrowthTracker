# -*- coding: utf-8 -*-
"""
Created on Tuesday July 21 13:42: 2020

this module hold low level classes representing artifacts that can
be drawn on an image

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

This work was funded by Joanna Leng's EPSRC funded RSE Fellowship (EP/R025819/1)

@copyright 2020
@author: j.h.pickering@leeds.ac.uk and j.leng@leeds.ac.uk
"""

# set up linting conditions
# pylint: disable = too-many-public-methods
# pylint: disable = c-extension-no-member

from collections import namedtuple
import numpy as np

from cgt.model.imagepoint import ImagePoint

## data-struct for a directed line segment in pixel coordinates,
## basis for classes providing more functionality
##
## Args:
##
## start (ImagePoint) the start point of the segment
##
## end (ImagePoint) the end point of the segment
ImageLineBase = namedtuple("ImageLineBase", ["start", "end"])

class ImageLineSegment(ImageLineBase):
    """
    class providing a representation of a directed line segment
    """

    def scale(self, zoom):
        """
        make scaled copy of this line segment

            Args:
                zoom (number) the scale factor.

            Returns:
                scaled copy of line segment (ImageLineSegment)

        """
        start_x = np.uint32(np.round(self.start.x * zoom))
        start_y = np.uint32(np.round(self.start.y * zoom))

        end_x = np.uint32(np.round(self.end.x * zoom))
        end_y = np.uint32(np.round(self.end.y * zoom))

        start = ImagePoint(start_x, start_y)
        end = ImagePoint(end_x, end_y)

        return ImageLineSegment(start, end)

    def shift(self, shift_vector):
        """
        make shifted copy of this line segment

            Args:
                zoom (ImagePoint) the shift vector

            Returns:
                shifted copy of line segment (ImageLineSegment)
        """
        start_x = np.uint32(self.start.x + shift_vector.x)
        start_y = np.uint32(self.start.y + shift_vector.y)

        end_x = np.uint32(self.end.x + shift_vector.x)
        end_y = np.uint32(self.end.y + shift_vector.y)

        start = ImagePoint(start_x, start_y)
        end = ImagePoint(end_x, end_y)

        return ImageLineSegment(start, end)

    def new_start(self, new_s):
        """
        make a copy with a new start position

            Args:
                new_s : ImagePoint the new start positin

            Returns:
                altered copy of line segment (ImageLineSegment)
        """
        return ImageLineSegment(new_s, self.end)

    def new_end(self, new_e):
        """
        make a copy with a new end position

            Args:
                new_e : ImagePoint the new end positin

            Returns:
                altered copy of line segment (ImageLineSegment)
        """
        return ImageLineSegment(self.start, new_e)

    def distance_point_to_line(self, point):
        """
        find the distance from a point to the line,

            Args:
                point (QPoint) the target point.

        Returns:
            minimum distance from line to point, in pixel coordinates (numpy.float64)
        """

        # deal with degenerate case
        if self.is_vertical:
            return abs(self.start.float_x - np.float64(point.x()))

        # calculate y - mx -c = 0
        grad = np.float64(self.delta_y)/np.float64(self.delta_x)
        y_intercept = self.start.float_y - grad * self.start.float_x

        #pt(xp, yp) d = (yp-mxp-c)/sqrt(1^2 + m^2)
        lower = np.sqrt(1.0 + grad*grad)
        upper = abs(np.float64(point.y()) - grad*np.float64(point.x()) - y_intercept)

        return upper/lower

    @property
    def is_vertical(self):
        """
        getter for verticality of the line

            Returns:
                True if the line segment is vertical, else false
        """
        if not self.delta_x:
            return True

        return False

    @property
    def delta_x(self):
        """
        getter for change in x along the line segment

            Returns:
                the x value at the start minus that at the end (numpy.float64)
        """
        return np.int64(self.start.x) - np.int64(self.end.x)

    @property
    def delta_y(self):
        """
        getter for change in y along the line segment

            Returns:
                the y value at the start minus that at the end (numpy.float64)
        """
        return np.int64(self.start.y) - np.int64(self.end.y)

    @property
    def normal_line(self):
        """
        find the normal to the line segment, given by (start, (-delta_y, delta_x))

            Returns:
                the normal line (ImageLineSegment)
        """
        end = ImagePoint(-self.delta_y, self.delta_x)

        return ImageLineSegment(self.start, end)

    @property
    def vector_direction(self):
        """
        the dirction of the line as a vector

            Returns:
                the line direction (ImagePoint)
        """
        return self.end - self.start

    def is_closest_point_on_segment(self, point):
        """
        find the point on the line (not segment) closest to the target point, and
        provide a boolean that is true if the closest point lies on self's segment

            Args:
                point the target (ImagePoint)

            Returns:
                a tuple of a boolean and an ImagePoint (tuple (bool, ImagePoint))
        """

        start_to_point = point - self.start
        start_to_point = start_to_point.float_copy

        vector_direction_raw = self.vector_direction.float_copy
        vector_direction = vector_direction_raw.normalize

        distance = vector_direction*start_to_point
        offset = vector_direction.scale(distance)
        closest = self.start + offset

        flag = True
        if distance <= 0.0:
            # point is before start
            flag = False
        elif offset.vector_length2 > vector_direction_raw.vector_length2:
            # point is beyond end
            flag = False

        return (flag, closest)

    def difference(self, rhs):
        """
        find the difference between this line and the new line

            Args:
                rhs (ImageLineSegment) the line for comparison

            Return:
                the difference between the lines (ImageLineDifference)
        """
        start_distance = self.start.distance_from(rhs.start)
        end_distance = self.end.distance_from(rhs.end)

        return ImageLineDifference(start_distance, end_distance)

    def __str__(self):
        """
        override Python.object user string representation.

        Returns:
            string representation of line segment (string)
        """
        return f"ImageLineSegment(Start: {self.start}, End {self.end})"

## data-structure representing the differences between two line segment's, serves as a base
##
## Args:
##
## start_d (number) the distance between the start points
##
## end_d (number) the distance between the end points
DifferenceBase = namedtuple("DifferenceBase", ["start_d", "end_d"])

class ImageLineDifference(DifferenceBase):
    """
    data structure for differenced between two lines the data are:
    """
    @property
    def average(self):
        """
        find the average of the start and end differences

            Returns:
                the average of the start and end distances (numpy.float64)
        """
        return (self.start_d + self.end_d)/2.0

    def __str__(self):
        """
        override Python.object user string representation.

        Returns:
            string representation of line differenc (string)
        """
        return f"ImageLineDifference(Start: {self.start_d}, End {self.end_d})"

