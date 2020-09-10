# -*- coding: utf-8 -*-
"""
Created on Tuesday August 18 2020

module results provides storage classes for CGT results.
IO and analysis are provided seperatly.

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
# pylint: disable = E0401

from typing import NamedTuple, List

from cgt.crystal import Crystal

class Region(NamedTuple):
    """
    subclass of video_region providing ustility functions
    """
    top: int
    left: int
    bottom: int
    right: int
    start_frame: int
    end_frame: int
    crystals: List[Crystal]

    @property
    def top_left_horizontal(self):
        """
        getter for the top (backward compatability)

            Returns:
                pixel coordinate of the top edge of the region
        """
        return self.top

    @property
    def top_left_vertical(self):
        """
        getter for the left  (backward compatability)

            Returns:
                pixel coordinate of the left edge of the region
        """
        return self.left

    @property
    def bottom_right_horizontal(self):
        """
        getter for the bottom (backward compatability)

            Returns:
                pixel coordinate of the bottom edge of the region
        """
        return bottom

    @property
    def bottom_right_vertical(self):
        """
        getter for the right (backward compatability)

            Returns:
                pixel coordinate of the right edge of the region
        """
        return right

    @property
    def width(self):
        """
        getter for the width in pixels

            Returns:
                the width in pixels
        """
        return self.bottom - self.top

    @property
    def height(self):
        """
        getter for the height in pixels

            Returns:
                the height in pixels
        """
        return self.left - self.right

    @property
    def time_interval(self):
        """
        getter for the time interval in frames

            Returns:
                the number of frames in the time interval
        """
        return self.end_frame - self.start_frame

    @property
    def crystal_names(self):
        """
        getter for a list of the names of the crystals

            Returns:
                list of crystal names
        """
        return [i.name for i in self.crystals]

    @property
    def crystals(self):
        """
        getter for the crystals

            Returns:
                the list of crystals
        """
        return self._crystals
        
    def time_in_region(self, frame):
        """
        return true if the time parameter is in the time interval of the region
        
            Args:
                time (int) frame number
                
            Returns:
                True if time in time range of region, else False
        """
        return (frame >= self.start_frame and frame <= self.end_frame)

    def get_crystal(self, index):
        """
        getter for a named crystal

            Args:
                name the crystals id

            Returns:
                the crystal
        """
        return self.crystals[index]
