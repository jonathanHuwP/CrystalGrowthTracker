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

from typing import NamedTuple, List

from cgt.crystal import Crystal

class Region(NamedTuple):
    """
    subclass of video_region providing ustility functions
    """
    top_left_horizontal : int
    top_left_vertical : int
    bottom_right_horizontal : int
    bottom_right_vertical : int
    start_frame : int
    end_frame : int
    crystals : List[Crystal]

    @property
    def width(self):
        """
        getter for the width in pixels

            Returns:
                the width in pixels
        """
        return self.bottom_right_horizontal - self.top_left_horizontal

    @property
    def height(self):
        """
        getter for the height in pixels

            Returns:
                the height in pixels
        """
        return self.top_left_vertical - self.bottom_right_vertical

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
    def get_crystal(self, name):
        return self.crystals[name]
