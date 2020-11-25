# -*- coding: utf-8 -*-
"""
Created on Wed Jun 10 11:26:28 2020

This class represents a rectangluar region of an image in pixmap coordinates

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

from collections import namedtuple
import numpy as np

## data struct for a rectangle defined on a pixmap, this will serve
## as base for more sophisticated subclasses
##
## Args:
##
##     top (int) Y coordinate of the top boundary of the rectangle
##
##     bottom (int) Y coordinate of the bottom boundary of the rectangle
##
##     left (int) X coordinate of the left boundary of the rectangle
##
##     right (int) X coordinate of the right boundary of the rectangle
BaseRect = namedtuple("BaseRect", "top, bottom, left, right")

class DrawRect(BaseRect):
    """
       extends the BaseRect structure with a scale function, the intention
       is to define a rectangle within a grayscale image defined as a numpy
       array, and allow for rescaling of the image.
    """

    def scale(self, factor):
        """
        make a new rectangle that is a scaled copy of the existing rectangle

            Args:
                factor (real or integer number) the scaling factor for the rectangle.

            Returns:
                the scaled rectangle.
        """
        top = np.uint32(np.round(self.top*factor))
        bottom = np.uint32(np.round(self.bottom*factor))
        left = np.uint32(np.round(self.left*factor))
        right = np.uint32(np.round(self.right*factor))

        return DrawRect(top, bottom, left, right)

    def shift(self, x_shift, y_shift):
        """
        shift the rectangle by the x and y (placeholder)

            Args:
                x_shift (np.uint32) the shift on X axis (horiziontal)
                y_shift (np.uint32) the shift on Y axis

            Retuns:
                shifted copy of this rectangle shifted by x_shift, y_shift
        """

        top = self.top + y_shift
        bottom = self.bottom + y_shift
        left = self.left + x_shift
        right = self.right + x_shift

        return DrawRect(top, bottom, left, right)

    def reshape(self, del_x, del_y):
        """
        rescale differently in x and y (placeholder)

            Args:
                del_x (number) the scale factor for the X axis
                del_y (number) the scale factor for the Y axis

            Retuns:
                None
        """
        top = np.uint32(np.round(self.top*del_y))
        bottom = np.uint32(np.round(self.bottom*del_y))
        left = np.uint32(np.round(self.left*del_x))
        right = np.uint32(np.round(self.right*del_x))

        return DrawRect(top, bottom, left, right)

    @property
    def width(self):
        """
        getter for the width of the region

            Return
                width (int)
        """
        return self.right - self.left

    @property
    def height(self):
        """
        getter for the height of the region

            Return
                height (int)
        """
        return self.bottom - self.top

    def __repr__(self):
        """
        string representation for debugging

            Returns:
                string describing object (including memory address)
        """

        return "<{} at {}>".format(self.__class__.__name__, id(self))

    def __str__(self):
        """
        string representation for user

            Returns:
                string describing object
        """
        return "(top: {}, bottom:{}, left:{}, right:{}, height:{}, width:{})".format(
            self.top, self.bottom, self.left, self.right, self.height, self.width)
