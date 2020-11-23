# -*- coding: utf-8 -*-
"""
Created on Tuesday August 18 2020

module results provides storage classes for CGT results.
IO and analysis are provided seperatly.

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
# pylint: disable = E0401

from typing import NamedTuple

class Region(NamedTuple):
    """
    class defining a region of the video in frame number and pixel space
    """
    ## the of the region in pixel coordinates, user's view
    top: int

    ## the left of the region in pixel coordinates, user's view
    left: int

    ## the bottom of the region in pixel coordinates, user's view
    bottom: int

    ## the right of the region in pixel coordinates, user's view
    right: int

    ## the number of the first frame in the region
    start_frame: int

    ## the number of the last frame in the region
    end_frame: int

    @property
    def width(self):
        """
        getter for the width in pixels

            Returns:
                the width in pixels
        """
        return self.right - self.left

    @property
    def height(self):
        """
        getter for the height in pixels

            Returns:
                the height in pixels
        """
        return self.bottom - self.top

    @property
    def time_interval(self):
        """
        getter for the time interval in frames

            Returns:
                the number of frames in the time interval
        """
        return self.end_frame - self.start_frame

    def time_in_region(self, frame):
        """
        return true if the time parameter is in the time interval of the region

            Args:
                time (int) frame number

            Returns:
                True if time in time range of region, else False
        """
        return self.end_frame >= frame >= self.start_frame #and frame <= self.end_frame

    def point_in_region(self, horizontal, vertical):
        """
            test if a point in pixel coordinates is inside the region

                Args:
                    horizontal (int) the horizontal (x) screen coordinate
                    vertical (int) the vertical (y) screen coordinate

                Returns:
                    True if point in region< else False
        """
        h_flag = self.right >= horizontal >= self.left
        v_flag = self.bottom >= vertical >= self.top

        return h_flag and v_flag

    def __str__(self):
        """
        a to string methods

            Returns:
                String describing object (user view)
        """
        return "(top:{}, bottom:{}, left:{}, right:{}, start frame:{}, end frame:{})".format(
            self.top, self.bottom, self.left, self.right, self.start_frame, self.end_frame)
