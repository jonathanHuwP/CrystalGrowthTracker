# -*- coding: utf-8 -*-
"""
Created on Thu Apr 23 15:05:47 2020

a class intended to extract lines representing crystal edges from an image

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

import logging
import lazylogger

import PolarLine

from collections import namedtuple

# data-struct for image analysis parameters
IAParameters = namedtuple("IAParameters", 
        ["line_threshold", "line_length", "line_gap", "verts_min_distance"])

class PolyLineExtract(object):
    """Object providing the functions for extracting polylines from images"""
    
    def __init__(self, parameters=None):
        """
        set up object
        """
        self._image = None
        self._vertices = []
        self._lines = PolarLine.PolarLineList()
        self.NAME = "PolyLineExtract"
        
        if parameters is None:
            self._parameters = IAParameters(5, 20, 2, 3)
        else:
            self._parameters = parameters
                    
        self._logger = logging.getLogger(self.NAME)
        self._logger.setLevel(logging.DEBUG)
        
    @property
    def image(self):
        """
        getter for the image
        """
        return self._image
    
    @image.setter
    def image(self, image):
        """
        setter for the image
        """
        self._image = image
        
    @property
    def number_vertices(self):
        """
        getterf for the number of vertices in feature
        """
        return len(self._vertices)
    
    @property
    def number_lines(self):
        """
        getter for the number of lines in feature
        """
        return len(self._lines)
    
    @property
    def image_vertices(self):
        """
        getter for image of the vertices only
        
        Returns
        -------
            a numpy image array set to 255 except for vertices set to 0
        """
        v_image = np.empty(self._image.shape, dtype=np.uint8)
        v_image.fill(255)
        
        for v in self._vertices:
            v_image[v[0], v[1]] = 0

        return v_image
    
    @property
    def image_lines(self):
        """
        getter for image of the line segments only
        
        Returns
        -------
            a numpy image array set to 255 except for lines set to 0
        """
        from skimage.draw import line

        l_image = np.empty(self._image.shape, dtype=np.uint8)
        l_image.fill(255)
        
        for l in self._lines:
            rr, cc = line(
                l.start[0], l.start[1], 
                l.end[0], l.end[1])
            l_image[cc, rr] = 0

        return l_image
    
    @property
    def image_polar_lines(self):
        """
        getter for image of the polar lines only
        
        Returns
        -------
            a numpy image array set to 255 except for lines set to 0
        """
        from skimage.draw import line

        l_image = np.empty(self._image.shape, dtype=np.uint8)
        l_image.fill(255)
        
        for l in self._lines:
            rr, cc = line(
                l.start[0], l.start[1], 
                l.end[0], l.end[1])
            l_image[cc, rr] = 0

        return l_image
    
    @property
    def image_all(self):
        """
        getter for image of the vertices and lines
        
        Returns
        -------
            a numpy image array set to 255 except for lines and vertices set to 0
        """
        image = self.image_lines
        
        for v in self._vertices:
            image[v[0], v[1]] = 0

        return image
        
        
    
    def find_lines(self):
        """
        detect lines in the image

        Returns
        -------
        None.
        """
        from skimage.transform import probabilistic_hough_line
        from skimage.morphology import skeletonize
        
        img = np.empty(self._image.shape, dtype = np.uint8) 
        img.fill(0)  

        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                if self._image[i, j] == 255:
                    img[i, j] = 0
                else:
                    img[i, j] = 1

        edges = skeletonize(img)

        tmp = probabilistic_hough_line(
            edges, 
            threshold=self._parameters.line_threshold,    # the size of the count to detect a line
            line_length=self._parameters.line_length, # the minimum line length to be detected
            line_gap=self._parameters.line_gap)     # maximum gap allowed in line

        for line in tmp:
            start, end = line
            self._lines.append(PolarLine.line_to_theta_r(line[0], line[1]))
        
    def find_vertices(self):
        """
        Vertex detector

        Returns
        -------
        None.
        """
        from skimage.feature import corner_harris, corner_peaks
        self._logger.debug("find_vertices")
        
        enhanced = corner_harris(self._image)
        self._vertices = corner_peaks(
            enhanced, self._parameters.verts_min_distance)
        
    def merge(self):
        # PROBLEM
        for p in self._vertices:
            tmp = []
            for l in self._lines:
                tmp.append(l.point_to_line(p))
                
            print(tmp)
            
        
    @property
    def vertices(self):
        """
        getter for the array of vertices
        """
        return self._vertices
    
    @property
    def lines(self):
        """
        getter for the array of lines
        """
        return self._lines

def test():
    from skimage import data
    
    p = PolyLineExtract()
    
    p.image = data.camera()
    
    p.find_vertices()
    p.find_lines()
    
    print("Vertices:")
    for vert in p.vertices:
        print(vert)
        
    print("Lines")
    print("y, x, y, x, theta, r, length")
    for line in p.lines:
        s = "{}, {}, {}, {}, {}, {}, {}".format(
            line.start[0], line.start[1], 
            line.end[0], line.end[1],
            line.theta, line.r, line.length)
        print(s)
        
if __name__ == "__main__":
    file_name = "PolyLineExtract.log"
    lazylogger.set_up_logging(file_name, append=True)
    test()
    lazylogger.end_logging(file_name)