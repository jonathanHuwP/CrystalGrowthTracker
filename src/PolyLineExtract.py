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

class PolyLineExtract(object):
    """Object providing the functions for extractig polylines from images"""
    
    def __init__(self):
        self._image = None
        self._vertices = []
        
    @property
    def image(self):
        return self._image
    
    @image.setter
    def image(self, image):
        self._image = image
        
    @property
    def size(self):
        return len(self._vertices)
        
    def find_lines(self):
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
            if region.area >= 100:
               self._vertices.append(region.centroid)
        
    def __iter__(self):
        return iter(self._vertices)
    
def test():
    p = PolyLineExtract()
    
    p.image = data.coins()
    
    p.find_lines()
    
    for vert in p:
        print(vert)
    
if __name__ == "__main__":
    test()
