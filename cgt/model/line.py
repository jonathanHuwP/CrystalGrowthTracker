# -*- coding: utf-8 -*-
"""
Created on Tuesday July 21 13:42: 2020

this module holds an image line across multiple frames

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
#

from cgt.model.imagelinesegment import ImageLineSegment, ImageLineDifference

class Line(dict):
    """
    This container represents a line that is moving in a video. It is a Python
    dictionary subclass mapping frame numbers to ImageLineSegments. Functions
    are provided for finding the distance moved in each time step.
    """

    def __init__(self, note=None):
        """
        initalize the object
        
            Args:
                note (string) a label or note
        """
        ## a text string relating to the line
        self._note = note

    def add_line(self, frame, line_segment):
        """
        add a line to the store
        
            Args:
                frame (int) the frame number
                line_segment (ImageLineSegment) the line segment 
        """
        self[frame] = line_segment
        
    @property
    def note(self):
        return self._note
        
    def number_of_frames(self):
        """
        the number of times the line has been defined
        """
        return len(self)
        
    def get_frame_numbers(self):
        """
        get a list of the frame numbers in ascending order
        
            Returns:
                the frame numbers (list(int))
        """
        tmp = list(self.keys())
        tmp.sort()
        return tmp

    def get_lines(self):
        """
        a getter for the line segments
        
            Returns:
                the line segments (list(ImageLineSegment))
        """
        return list(self.values())
        
    def get_differences(self):
        """
        getter for the motion of the line, will return empty list 
        if the object has less than two lines
        
            Returns:
                the motion of the line in pixels (list(ImageLineDifference))
        """
        differences = []
        if len(self) < 2:
            return differences
            
        keys = self.get_frame_numbers()
        
        # index starts at zero key start at one
        for index, key in enumerate(keys[1:]):
            start = self[keys[index]]
            end = self[key]
            
            differences.append(start.difference(end))
            
        return differences
