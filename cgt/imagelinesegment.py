# -*- coding: utf-8 -*-
"""
Created on Tuesday July 21 13:42: 2020

this module hold low level classes representing artifacts that can
be drawn on an image

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at
http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

@copyright 2020
@author: j.h.pickering@leeds.ac.uk
"""

# set up linting conditions
# pylint: disable = too-many-public-methods
# pylint: disable = c-extension-no-member

from collections import namedtuple
import numpy as np

from imagepoint import ImagePoint

## data-struct for a directed line segment in pixel coordinates,
## basis for classes providing more functionality
##
## Args:
##
## start (ImagePoint) the start point of the segment
##
## end (ImagePoint) the end point of the segment
##
## label (string )the string identifying the line
ImageLineBase = namedtuple("ImageLineBase", ["start", "end", "label"])

class ImageLineSegment(ImageLineBase):
    """
    class providing a representation of a directed line segment
    """

    def relabel(self, label):
        """
        return copy with a different label

            Args:
                label (string) the new label.

            Returns:
                copy of same line segment with new label (mageLineSegment).
        """
        return ImageLineSegment(self.start, self.end, label)

    def scale(self, zoom, new_label=None):
        """
        make scaled copy of this line segment, re-labelled if required

            Args:
                zoom (number) the scale factor.

                new_label (string) a new lable (optional)

            Returns:
                scaled copy of line segment (ImageLineSegment)

        """
        start_x = np.uint32(np.round(self.start.x * zoom))
        start_y = np.uint32(np.round(self.start.y * zoom))

        end_x = np.uint32(np.round(self.end.x * zoom))
        end_y = np.uint32(np.round(self.end.y * zoom))

        start = ImagePoint(start_x, start_y)
        end = ImagePoint(end_x, end_y)

        if new_label is None:
            return ImageLineSegment(start, end, self.label)

        return ImageLineSegment(start, end, new_label)

    def shift(self, shift_vector, new_label=None):
        """
        make shifted copy of this line segment

            Args:
                zoom (ImagePoint) the shift vector.
                new_label (string) a new lable. The default is None (optional)

            Returns:
                shifted copy of line segment (ImageLineSegment)
        """
        start_x = self.start.x + shift_vector.x
        start_y = self.start.y + shift_vector.y

        end_x = self.end.x + shift_vector.x
        end_y = self.end.y + shift_vector.y

        start = ImagePoint(start_x, start_y)
        end = ImagePoint(end_x, end_y)

        if new_label is None:
            return ImageLineSegment(start, end, self.label)

        return ImageLineSegment(start, end, new_label)

    def new_start(self, new_s, new_label=None):
        """
        make a copy with a new start position, and optionally a new label

            Args:
                new_s : ImagePoint the new start positin.
                new_label (string) a new label (optional)

            Returns:
                altered copy of line segment (ImageLineSegment)
        """
        if new_label is None:
            return ImageLineSegment(new_s, self.end, self.label)

        return ImageLineSegment(new_s, self.end, new_label)

    def new_end(self, new_e, new_label=None):
        """
        make a copy with a new end position, and optionally a new label

            Args:
                new_s : ImagePoint the new end positin.
                new_label (string) a new label (optional)

            Returns:
                altered copy of line segment (ImageLineSegment)
        """
        if new_label is None:
            return ImageLineSegment(self.start, new_e, self.label)

        return ImageLineSegment(self.start, new_e, new_label)

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

        label = "{}-normal".format(self.label)
        end = ImagePoint(-self.delta_y, self.delta_x)

        return ImageLineSegment(self.start, end, label)

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

    def line_label_equals(self, line):
        """
        test equality of line labels

            Args:
                line (ImageLineSegment) the test line

            Returns:
                True if self and line have the same label, else false
        """
        return self.label == line.label

    def label_in_set(self, in_lines):
        """
        find the first line with a matching label, if no such return None

            Args:
                in_lines (iterable of ImageLineSegment's) a collection of lines

            Returns:
                the first line that matches selfs label, else None
        """
        for line in in_lines:
            if self.line_label_equals(line):
                return line

        return None

    def __str__(self):
        """
        override Python.object user string representation.

        Returns:
            string representation of line segment (string)
        """
        return "Line(Start: {}, End {}, {})".format(
            self.start, self.end, self.label)

## data-structure representing the differences between two line segment's, serves as a base
##
## Args:
##
## start_d (number) the distance between the start points
##
## end_d (number) the distance between the end points
##
## lines_label (string) a label combining the two line's own labels
DifferenceBase = namedtuple("DifferenceBase", ["start_d", "end_d", "lines_label"])

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