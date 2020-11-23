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

## data-struct for point in pixel coordinates
##
## Args:
##
##     x (int) Y coordinate
##
##     y (int) Y coordinate
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
