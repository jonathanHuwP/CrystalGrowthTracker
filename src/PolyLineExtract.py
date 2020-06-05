# -*- coding: utf-8 -*-
"""
Created on Thu Apr 23 15:05:47 2020

@author: j.h.pickering@leeds.ac.uk
"""
from skimage import data

from skimage.filters import threshold_otsu
from skimage.segmentation import clear_border
from skimage.measure import label, regionprops
from skimage.morphology import square, closing

import logging

class PolyLineExtract(object):
    """Object providing the functions for extractig polylines from images"""
    
    def __init__(self):
        self._image = None
        self._vertices = []
        self.NAME = self.tr("PolyLineExtract")
                    
        self._logger = logging.getLogger(self.NAME)
        self._logger.setLevel(logging.DEBUG)
        
    @property
    def image(self):
        return self._image
    
    @image.setter
    def image(self, image):
        self._image = image
        
    @property
    def size(self):
        return len(self._vertices)
        
    def find_lines(self, i):
        """
        Implements indirection by returning the find_lines_i function

        Parameters
        ----------
        i : int
            the number of the find_lines function you desire.
        """
        
        method_name='find_lines_'+str(i)
        method=getattr(self, method_name)
        
        # run the method and return results.
        return method()
        
    def find_lines_1(self):
        """
        Example from websize, works on coins

        Returns
        -------
        None.

        """
        self._logger.debug("find_lines: 1")
        self._vertices.clear()
        
        # apply threshold
        thresh = threshold_otsu(self._image)
        bw = closing(self._image > thresh, square(3))
        
        # remove artifacts connected to image border
        cleared = clear_border(bw)
        
        # label image regions
        label_image = label(cleared)
        
        for region in regionprops(label_image):
            # take regions with large enough areas
            if region.area >= 8:
               self._vertices.append(region.centroid)
               
    def find_lines_2(self):
        """
        Alternative vertex detector

        Returns
        -------
        None.
        """
        
        import numpy as np
        from skimage.feature import corner_harris, corner_peaks
        self._logger.debug("find_lines: 2")
        
        enhanced = corner_harris(self._image)
        corners = corner_peaks(enhanced, min_distance=3)
        
        c_img = np.zeros(self._image.shape)
        for i in corners:
            c_img[i[0], i[1]] = 255
            
        # label image regions
        label_image = label(c_img)
        
        for region in regionprops(label_image):
            # take regions with large enough areas
            if region.area >= 5:
               self._vertices.append(region.centroid) 

        
    def __iter__(self):
        return iter(self._vertices)
    
def test():
    p = PolyLineExtract()
    
    p.image = data.coins()
    
    p.find_lines_2()
    
    print("Vert list:")
    for vert in p:
        print(vert)
    
if __name__ == "__main__":
    test()
