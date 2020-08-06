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

from collections import namedtuple
import numpy as np

## data-struct for point in pixel coordinates
##
## Args:
##
##     x (int) Y coordinate of the top boundary of the rectangle
##
##     y (int) Y coordinate of the bottom boundary of the rectangle
ImagePointBase = namedtuple("ImagePointBase", ["x", "y"])

class ImagePoint(ImagePointBase):
    """
    class for storing and manipulating a point in the image
    """
    @property
    def float_y(self):
        """
        getter for float value of Y

            Returns:
                the value of Y (numpy.float64)
        """
        return np.float64(self.y)

    @property
    def float_x(self):
        """
        getter for float value of X

            Returns:
                the value of X (numpy.float64)
        """
        return np.float64(self.x)

    @property
    def float_copy(self):
        """
        make a copy with floating point numbers

            Returns:
                the point converted to numpy.float64
        """
        return ImagePoint(self.float_x, self.float_y)

    @property
    def vector_length2(self):
        """
        getter for the square of the length

            Returns:
                the square of the length of the vector from the origin to the point (numpy.float64)
        """
        return self.float_x*self.float_x + self.float_y*self.float_y

    @property
    def vector_length(self):
        """
        getter for the length

            Returns:
                the length of the vector from the origin to the point (numpy.float64)
        """
        return np.sqrt(self.vector_length2)

    def scale(self, zoom):
        """
        make and return a scaled copy

            Args:
                zoom (number) the scalling factor

            Returns:
                a new ImagePoint with self's coordinates scalled by zoom
        """
        return ImagePoint(self.x*zoom, self.y*zoom)

    def distance_from(self, rhs):
        """
        find the distance from self to a point

            Args:
            rhs (ImagePoint) the target point

            Returns:
                distance between self and rhs (numpy.float64)
        """
        tmp = self - rhs
        return tmp.vector_length

    def __add__(self, rhs):
        """
        operator override '+' vector addition

            Args:
                rhs (ImagePoint) the second point in the addition

            Returns:
                a new point with coordinates the sum of self and rhs
        """
        return ImagePoint(self.float_x + rhs.float_x, self.float_y + rhs.float_y)

    def __sub__(self, rhs):
        """
        operator override '-' vector subtraction

            Args:
                rhs (ImagePoint) the second point in the subtraction

            Returns:
                a new point with coordinates the difference of self and rhs
        """
        return ImagePoint(self.float_x - rhs.float_x, self.float_y - rhs.float_y)

    def __mul__(self, rhs):
        """
        operator override '*' vector inner (dot) product

            Args:
                rhs (ImagePoint) the second point in the product

            Returns:
                the inner product of the self and rhs (numpy.float64)
        """
        return self.float_x*rhs.float_x + self.float_y*rhs.float_y

    def __div__(self, rhs):
        """
        operator override '/' devide self's coordinate by a factor

            Args:
                rhs (number) the devisor

            Returns:
                a new point with self's coordinates devided by rhs (numpy.float64)
        """
        return ImagePoint(self.float_x/rhs, self.float_y/rhs)

    @property
    def normalize(self):
        """
        return a normalized floating point copy

            Returns:
                (ImagePoint numpy.float64) self scaled to a length of one
        """
        length = self.vector_length
        return ImagePoint(self.float_x/length, self.float_y/length)

    def __str__(self):
        """
        make a string representation of the object

            Returns:
                string describing object

        """
        return "Point({}, {})".format(self.x, self.y)

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
        start_y = self.start.x + shift_vector.x
        start_y = self.start.y + shift_vector.y

        end_x = self.end.x + shift_vector.x
        end_y = self.end.y + shift_vector.y

        start = ImagePoint(start_y, start_y)
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
            # point is befor start
            flag = False
        elif offset.vector_length2 > vector_direction_raw.vector_length2:
            # point is beyone end
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

class ArtifactStore(dict):
    """
    a store for the sets of lines used in the analysis of one crystal in one video
    """
    def __init__(self, name):
        """
        initalize the class

            Args:
                name (string) a name uniquily identifying the video and crystal

            Returns:
                None
        """
        super().__init__()
        self._name = name

    @property
    def name(self):
        """
        getter for the name

            Returns:
                the name (string)
        """
        return self._name

    def differences(self, key0, key1):
        """
        find the differenced between the equivalent lines in two sets,
        equivalence based on the lines own labels

            Args:
            key0 (dictionary key) the key for the first set of lines
            key1 (dictionary key) the key for the second set of lines

            Returns:
                a list of differences (list(ImageLineDifference))

        """
        tmp = self.match_pairs(key0, key1)

        diffs = []
        for i in tmp:
            start_distance = i[0].start.distance_from(i[1].start)
            end_distance = i[0].end.distance_from(i[1].end)
            diffs.append(ImageLineDifference(start_distance, end_distance, i[0].label))

        return diffs

    def match_pairs(self, key0, key1):
        """
        returns a list of pairs each holding a line from the list at key0,
        and the matching line from the list at key1

            Args:
                key0 : (time key) the first time key.
                key1 : (time key) the second time key.

            Returns:
                a list of pairs each having the key0 line first
                (list(tuple(ImageLineSegment, ImageLineSegment)))
        """

        tmp = []
        for line in self[key0]:
            line_match = line.label_in_set(self[key1])
            if line_match is not None:
                tmp.append((line, line_match))

        return tmp

# TESTING
#########
class AltQPoint():
    """
    substitute for qpqtcore QPoint, allows tests to be run without Qt
    """
    def __init__(self, x, y):
        """
        initalize the object

            Args:
                x (int) the x coordinate
                y (int) the y coordinate

            Returns:
                None
        """
        self._x = x
        self._y = y

    def x(self):
        """
        getter for x coordinate

            Returns:
                the x coordinate (int)
        """
        return self._x

    def y(self):
        """
        getter for y coordinate

            Returns:
                the y coordinate (int)
        """
        return self._y

    def __repr__(self):
        """
        string representation of point

            Returns
                text representation of point (string)
        """
        return "({}, {})".format(self._x, self._y)

def test():
    """
    simple test function

        Returns:
            None
    """
    start = ImagePoint(100, 200)
    end = ImagePoint(200, 300)

    line = ImageLineSegment(start, end, "test00")

    print(line)
    if line.is_vertical:
        print("isVatical Fail")
    else:
        print("isVerticl Pass")

    tmp = AltQPoint(100, 100)

    if line.distance_point_to_line(tmp) - 100.0 > 0.0001:
        print("distance_point_to_line Fail")
    else:
        print("distance_point_to_line Pass")

if __name__ == "__main__":
    test()
