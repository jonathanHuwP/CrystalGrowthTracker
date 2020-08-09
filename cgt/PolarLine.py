# -*- coding: utf-8 -*-
"""
Created on Mon Jul  6 13:08:59 2020

a class representing a line segement in both rectanglualr and polar formats,
in pixmap coordinates, together with a storage class for such lines

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

import math
import sys

from collections import namedtuple

## datastruct for a line and segment in both (theta, r), (m, c) and (start, end) formats
## the intention is for it to act as a cache of multiple representations
##
## start the start point
##
## end the end point
##
## theta the angle of the line to the horizontal
##
## r the shortest distance from the line to the origin
##
## m the gradient
##
## c the y intercept
##
## length the length start to end
BaseLine = namedtuple("BaseLine", ["start", "end", "theta", "r", "m", "c", "length"])

class PolarLine(BaseLine):
    """
    multiple representation of a line/line segment
    """

    def equals(self, line, e_theta=0.05, e_r=5.0):
        """
        equalitiy function for lines

            Args:
                line (PolarLine) the comparison line.
                e_theta (float) the epsilon value for the angle
                e_r (float) the epsilon value for the distance to origin

            Returns:
                True if the lines are equal within the epsilon values else False
        """
        e_theta = abs(e_theta)
        e_r = abs(e_r)

        theta_flag = False
        if abs(self.theta - line.theta) <= e_theta:
            theta_flag = True

        r_flag = False
        if abs(self.r - line.r) <= e_r:
            r_flag = True

        return theta_flag and r_flag

    def point_to_line(self, point):
        """
        find the shortes distance from point to the line

            Args:
                p (list (floa)) the point format (y, x)

            Return:
                the shortes distance from the point to the line
        """
        point_x = point[1]
        point_y = point[0]

        return abs(self.m*point_x - point_y + self.c)/math.sqrt(self.m*self.m + 1)

    # disable the linting warnings about x & y variable names in following methods
    # pylint: disable = invalid-name
    def y_polar(self, x):
        """
        find the y value for an x value, polar calculation

            Args:
                x (float) the x coordinate value

            Return
                the y value
        """
        y = self.r - x*math.cos(self.theta)
        y /= math.sin(self.theta)

        return y

    def y_linear(self, x):
        """
        find the y value for an x value, y=mx+c calculation

            Args:
                x (float) the x coordinate value

            Return
                the y value
        """
        return self.m*x + self.c

    def x_polar(self, y):
        """
        find the x value for a y value, polar calculation

            Args:
                y (float) the y coordinate value

            Return
                the x value
        """
        x = self.r - y*math.sin(self.theta)
        x /= math.cos(self.theta)

        return x

    def x_linear(self, y):
        """
        find the x value for a y value, y=mx+c calculation

            Args:
                y (float) the y coordinate value

            Return
                the x value
        """
        return (y-self.c)/self.m

class PolarLineList(list):
    """
    Storage for lines in polar form
    """

    def append(self, obj):
        """
        Overridden method will eliminate duplicates storing the longest

            Args:
            obj (PolarLine) the ploar line to be stored.

            Throws:
                TypeError if obj is not a PolarLine object

            Returns
                None.
        """
        if not isinstance(obj, PolarLine):
            message = "Attempt to stort type {}, in PolarLineList".format(
                type(obj))
            raise TypeError(message)

        if len(self) == 0:
            super().append(obj)
            return

        # find a matching line if any
        match = self.find_match(obj)

        if match is None:
            super().append(obj)
        elif obj.length > match.length:
            # only replace if obj is longer
            self.remove(match)
            super().append(obj)

    def find_match(self, obj):
        """
        find the first PolarLine that matches

            Args:
                obj (PolarLine) the target for which a match is sought.

            Returns:
                the match if one is found, else None.
        """

        for line in self:
            if line.equals(obj):
                return line

        return None


def line_length(start, end):
    """
    find length of line
    """
    del_x = start[1] - end[1]
    del_y = start[0] - end[0]

    return math.sqrt((del_x*del_x) + (del_y*del_y))

def gradient(start, end):
    """
    Find the gradient of a line segment

        Args:
            start (tuple) start point
            end (tuple) end point

        Returns:
            the gradient (float)
    """

    del_x = start[1] - end[1]
    del_y = start[0] - end[0]

    if del_x == 0:
        return sys.float_info.max

    return float(del_y)/float(del_x)

def y_intercept(point, grad):
    """
    find the y intercept of a line (y - m*x)

        Args:
            point (tuple) a point on the line.
            grad (float) the gradient.

        Returns
            the y intercept.
    """
    if grad == sys.float_info.max:
        return sys.float_info.max

    return float(point[0]) - grad*float(point[1])

def line_to_theta_r(start, end):
    """
    convert a line from (start, end) to (theta, r) parameters, where
    r it the shortes distance from the line to the orgin
    theta is the anti-clockwise angle from the x-axis to the shortes distane line

        Args:
            start (tuple) start point
            end (tuple) end point

        Returns:
            the in polar representation
    """
    grad = gradient(start, end)
    theta = math.atan(grad)

    y_inter = y_intercept(start, grad)
    dist_to_origin = abs(y_inter)/math.sqrt(grad*grad + 1.0)

    return PolarLine(
        start, end, theta, dist_to_origin, grad, y_inter, line_length(start, end))

## TESTING FUNCTIONS
####################

def make_lines():
    """
    make a set of lines for testing

        Returns:
            list of lines, list of correct classifications
    """
    classifications = ["A1", "B1", "A1", "B2", "A2",
                       "A1", "B1", "A2", "A2", "A2"]

    lines = []
    lines.append(
        PolarLine((80, 194), (41, 125),
                  0.514451313, 25.8140807,
                  0.5652, 52.4615, 79.25906888))
    lines.append(
        PolarLine((90, 208), (138, 122),
                  -0.509070888, 179.9599543,
                  -0.5581, -369.2500, 98.48857802))
    lines.append(
        PolarLine((47, 135), (35, 113),
                  0.499346722, 23.38394571,
                  0.5455, 48.8333, 25.059928))
    lines.append(
        PolarLine((35, 112), (87, 19),
                  -0.509833229, 85.20845626,
                  -0.5591, -174.5962, 106.5504575))
    lines.append(
        PolarLine((133, 95), (112, 56),
                  0.493941369, 72.0631731,
                  0.5385, 152.0000, 44.29446918))
    lines.append(
        PolarLine((86, 206), (69, 175),
                  0.501604054, 23.64565076,
                  0.5484, 49.1765, 35.35533906))
    lines.append(
        PolarLine((117, 161), (143, 114),
                  -0.505290188, 180.312866,
                  -0.5532, -372.5000, 53.71219601))
    lines.append(
        PolarLine((114, 61), (98, 32),
                  0.504165961, 70.34813806,
                  0.5517, 145.6250, 33.12099032))
    lines.append(
        PolarLine((104, 42), (91, 19),
                  0.514451313, 69.87213045,
                  0.5652, 142.0000, 26.41968963))
    lines.append(
        PolarLine((143, 112), (130, 88),
                  0.496422753, 72.39503858,
                  1.8342, -82.4555, 27.29468813))

    return lines, classifications

def test():
    """
    Unit test

        Returns:
            None
    """
    lines, classifications = make_lines()

    p_lines = PolarLineList()

    type_flag = False
    try:
        p_lines.append(7)
    except TypeError as error:
        type_flag = True
        print("Type Error caught: ", str(error))

    if not type_flag:
        print("Error type error not caught")

    print("RAW LINES")
    for i in enumerate(lines):
        p_lines.append(lines[i])
        print("{} => {}".format(lines[i], classifications[i]))

    print("\nPROCESSED LINES")
    for line in p_lines:
        print(line)

if __name__ == "__main__":
    test()
