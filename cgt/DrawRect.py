# -*- coding: utf-8 -*-
"""
Created on Wed Jun 10 11:26:28 2020

This class represents a rectangluar region of an image in pixmap coordinates

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

import numpy as np

# data struct for a use selected rectangle in numpy unsigned int format.
from collections import namedtuple
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
        t = np.uint32(np.round(self.top*factor))
        b = np.uint32(np.round(self.bottom*factor))
        l = np.uint32(np.round(self.left*factor))
        r = np.uint32(np.round(self.right*factor))
        
        return DrawRect(t, b, l, r)
    
    def shift(self, x, y):
        """
        shift the rectangle by the x and y (placeholder)
        
            Args:
                x (number) the shift on X axis
                y (number) the shift on Y axis
                
            Retuns:
                None
        """
        pass
    
    def reshape(self, del_x, del_y):
        """
        rescale differently in x and y (placeholder)
        
            Args:
                del_x (number) the scale factor for the X axis
                del_y (number) the scale factor for the Y axis
                
            Retuns:
                None
        """
        pass
    
    def __repr__(self):
        """
        string representation for debugging
        
            Returns:
                string describing object (including memory address)
        """
        
        return "<DrawRect at {}: ({}, {}, {}, {})>".format(
            id(self), self.top, self.bottom, self.left, self.right)
        
    def __str__(self):
        """
        string representationf for user
        
            Returns:
                string describing object
        """
        return "({}, {}, {}, {})".format(
            self.top, self.bottom, self.left, self.right)
