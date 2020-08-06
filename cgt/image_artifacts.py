# -*- coding: utf-8 -*-
"""
Created on Tuesday July 21 13:42: 2020

@author: j.h.pickering@leeds.ac.uk
"""

import numpy as np
from collections import namedtuple

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
    def floatY(self):
        """
        getter for float value of Y

            Returns:
                the value of Y (numpy.float64)
        """
        return np.float64(self.y)

    @property
    def floatX(self):
        """
        getter for float value of X

            Returns:
                the value of X (numpy.float64)
        """
        return np.float64(self.x)

    @property
    def floatCopy(self):
        """
        make a copy with floating point numbers

            Returns:
                the point converted to numpy.float64
        """
        return ImagePoint(self.floatX, self.floatY)

    @property
    def vectorLength2(self):
        """
        getter for the square of the length

            Returns:
                the square of the length of the vector from the origin to the point (numpy.float64)
        """
        x = self.floatX
        y = self.floatY

        return x*x + y*y

    @property
    def vectorLength(self):
        """
        getter for the length

            Returns:
                the length of the vector from the origin to the point (numpy.float64)
        """
        return np.sqrt(self.vectorLength2)

    def scale(self, zoom):
        """
        make and return a scaled copy

            Args:
                zoom (number) the scalling factor

            Returns:
                a new ImagePoint with self's coordinates scalled by zoom
        """
        return ImagePoint(self.x*zoom, self.y*zoom)

    def distanceFrom(self, rhs):
        """
        find the distance from self to a point

            Args:
            rhs (ImagePoint) the target point

            Returns:
                distance between self and rhs (numpy.float64)
        """
        tmp = self - rhs
        return tmp.vectorLength

    def __add__(self, rhs):
        """
        operator override '+' vector addition

            Args:
                rhs (ImagePoint) the second point in the addition

            Returns:
                a new point with coordinates the sum of self and rhs
        """
        return ImagePoint(self.floatX + rhs.floatX, self.floatY + rhs.floatY)

    def __sub__(self, rhs):
        """
        operator override '-' vector subtraction

            Args:
                rhs (ImagePoint) the second point in the subtraction

            Returns:
                a new point with coordinates the difference of self and rhs
        """
        return ImagePoint(self.floatX - rhs.floatX, self.floatY - rhs.floatY)

    def __mul__(self, rhs):
        """
        operator override '*' vector inner (dot) product

            Args:
                rhs (ImagePoint) the second point in the product

            Returns:
                the inner product of the self and rhs (numpy.float64)
        """
        return self.floatX*rhs.floatX + self.floatY*rhs.floatY

    def __div__(self, rhs):
        """
        operator override '/' devide self's coordinate by a factor

            Args:
                rhs (number) the devisor

            Returns:
                a new point with self's coordinates devided by rhs (numpy.float64)
        """
        return ImagePoint(self.floatX/rhs, self.floatY/rhs)

    @property
    def normalize(self):
        """
        return a normalized floating point copy

            Returns:
                (ImagePoint numpy.float64) self scaled to a length of one
        """
        l = self.vectorLength
        return ImagePoint(self.floatX/l, self.floatY/l)

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
        x0 = np.uint32(np.round(self.start.x * zoom))
        y0 = np.uint32(np.round(self.start.y * zoom))

        x1 = np.uint32(np.round(self.end.x * zoom))
        y1 = np.uint32(np.round(self.end.y * zoom))

        start = ImagePoint(x0, y0)
        end   = ImagePoint(x1, y1)

        if new_label is None:
            return ImageLineSegment(start, end, self.label)
        else:
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
        x0 = self.start.x + shift_vector.x
        y0 = self.start.y + shift_vector.y

        x1 = self.end.x + shift_vector.x
        y1 = self.end.y + shift_vector.y

        start = ImagePoint(x0, y0)
        end   = ImagePoint(x1, y1)
        if new_label is None:
            return ImageLineSegment(start, end, self.label)
        else:
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
        else:
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
        else:
            return ImageLineSegment(self.start, new_e, new_label)

    def distancePointToLine(self, point):
        """
        find the distance from a point to the line,

            Args:
                point (QPoint) the target point.

        Returns:
            minimum distance from line to point, in pixel coordinates (numpy.float64)
        """

        # deal with degenerate case
        if self.isVertical:
            return abs(self.start.floatX - np.float64(point.x()))

        # calculate y - mx -c = 0
        m = np.float64(self.dy)/np.float64(self.dx)
        c = self.start.floatY - m * self.start.floatX

        #pt(xp, yp) d = (yp-mxp-c)/sqrt(1^2 + m^2)
        lower = np.sqrt(1.0 + m*m)
        upper = abs(np.float64(point.y()) - m*np.float64(point.x()) - c)

        return upper/lower

    @property
    def isVertical(self):
        """
        getter for verticality of the line

            Returns:
                True if the line segment is vertical, else false
        """
        if not self.dx:
            return True
        else:
            return False

    @property
    def dx(self):
        """
        getter for change in x along the line segment

            Returns:
                the x value at the start minus that at the end (numpy.float64)
        """
        return np.int64(self.start.x) - np.int64(self.end.x)

    @property
    def dy(self):
        """
        getter for change in y along the line segment

            Returns:
                the y value at the start minus that at the end (numpy.float64)
        """
        return np.int64(self.start.y) - np.int64(self.end.y)

    @property
    def normalLine(self):
        """
        find the normal to the line segment, given by (start, (-dy, dx))

            Returns:
                the normal line (ImageLineSegment)
        """

        label = "{}-normal".format(self.label)
        end = ImagePoint(-self.dy, self.dx)

        return ImageLineSegment(self.start, end, label)

    @property
    def vectorDirection(self):
        """
        the dirction of the line as a vector

            Returns:
                the line direction (ImagePoint)
        """
        return self.end - self.start

    def isClosestPointOnSegment(self, point):
        """
        find the point on the line (not segment) closest to the target point, and
        provide a boolean that is true if the closest point lies on self's segment

            Args:
                point the target (ImagePoint)

            Returns:
                a tuple of a boolean and an ImagePoint (tuple (bool, ImagePoint))
        """

        vp = point - self.start
        vp = vp.floatCopy

        vd = self.vectorDirection.floatCopy
        vdn = vd.normalize

        d = vdn*vp
        offset = vdn.scale(d)
        closest = self.start + offset

        flag = True
        if d<=0.0:
            # point is befor start
            flag = False
        elif offset.vectorLength2 > vd.vectorLength2:
            # point is beyone end
            flag = False

        return (flag, closest)

    def lineLabelEquals(self, line):
        """
        test equality of line labels

            Args:
                line (ImageLineSegment) the test line

            Returns:
                True if self and line have the same label, else false
        """
        return self.label == line.label

    def labelInSet(self, in_lines):
        """
        find the first line with a matching label, if no such return None

            Args:
                in_lines (iterable of ImageLineSegment's) a collection of lines

            Returns:
                the first line that matches selfs label, else None
        """
        for line in in_lines:
            if self.lineLabelEquals(line):
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
        tmp = self.matchPairs(key0, key1)

        diffs = []
        for i in tmp:
            sd = i[0].start.distanceFrom(i[1].start)
            ed = i[0].end.distanceFrom(i[1].end)
            diffs.append(ImageLineDifference(sd, ed, i[0].label))

        return diffs

    def matchPairs(self, key0, key1):
        """
        returns a list of pairs each holding a line from the list at key0,
        and the matching line from the list at key1

            Args:
                key0 : (time key) the first time key.
                key1 : (time key) the second time key.

            Returns:
                a list of pairs each having the key0 line first (list(tuple(ImageLineSegment, ImageLineSegment)))
        """

        tmp = []
        for i in self[key0]:
            l = i.labelInSet(self[key1])
            if l is not None:
                tmp.append((i, l))

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
    st = ImagePoint(100, 200)
    ed = ImagePoint(200, 300)

    line = ImageLineSegment(st, ed, "test00")

    print(line)
    if line.isVertical:
        print("isVatical Fail")
    else:
        print("isVerticl Pass")

    tmp = AltQPoint(100, 100)

    if line.distancePointToLine(tmp) - 100.0 > 0.0001:
        print("distancePointToLine Fail")
    else:
        print("distancePointToLine Pass")

if __name__ == "__main__":
    test()
