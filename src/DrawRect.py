# -*- coding: utf-8 -*-
"""
Created on Wed Jun 10 11:26:28 2020

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

        Parameters
        ----------
        factor : real or integer number
            the scaling factor for the rectangle.

        Returns
        -------
        DrawRect
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
        """
        pass
    
    def reshape(self, del_x, del_y):
        """
        rescale differently in x and y (placeholder)
        """
        pass
    
    def __repr__(self):
        """
        string representation for debugging
        """
        
        return "<DrawRect at {}: ({}, {}, {}, {})>".format(
            id(self), self.top, self.bottom, self.left, self.right)
        
    def __str__(self):
        """
        string representationf for user
        """
        return "({}, {}, {}, {})".format(
            self.top, self.bottom, self.left, self.right)
