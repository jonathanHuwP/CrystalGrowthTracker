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

import logging

from collections import namedtuple
from skimage.transform import probabilistic_hough_line
from skimage.morphology import skeletonize
from skimage.feature import corner_harris
from skimage import data

import skimage.draw as skd

import numpy as np

import lazylogger
import PolarLine



## data-struct for image analysis parameters
##
## line_threshold (int) the size of the count to detect a line
##
## line_length (number) the minimum line length to be detected
##
## line_gap (number) maximum gap allowed in line
##
## verts_min_distance (float [0.0-0.2) skimage.feature.corner_harris sensitivity
IAParameters = namedtuple("IAParameters",
                          ["line_threshold", "line_length", "line_gap", "verts_min_distance"])

class PolyLineExtract():
    """Object providing the functions for extracting polylines from images"""

    def __init__(self, parameters=None):
        """
        set up object

            Returns:
                None
        """
        self._image = None
        self._vertices = []
        self._lines = PolarLine.PolarLineList()
        self._translation_name = "PolyLineExtract"

        if parameters is None:
            self._parameters = IAParameters(5, 20, 2, 3)
        else:
            self._parameters = parameters

        self._logger = logging.getLogger(self._translation_name)
        self._logger.setLevel(logging.DEBUG)

    @property
    def image(self):
        """
        getter for the image

            Returns:
                the image (numpy.array)
        """
        return self._image

    @image.setter
    def image(self, image):
        """
        setter for the image

            Args:
                image (numpy.array) the image

            Returns:
                None
        """
        self._image = image

    @property
    def number_vertices(self):
        """
        getter for the number of vertices in feature

            Returns:
                number of vertices
        """
        return len(self._vertices)

    @property
    def number_lines(self):
        """
        getter for the number of lines in feature

            Returns:
                number of lines
        """
        return len(self._lines)

    @property
    def image_vertices(self):
        """
        getter for image of the vertices only

            Returns:
                a numpy image array set to 255 except for vertices set to 0
        """
        v_image = np.empty(self._image.shape, dtype=np.uint8)
        v_image.fill(255)

        for vertex in self._vertices:
            v_image[vertex[0], vertex[1]] = 0

        return v_image

    @property
    def image_lines(self):
        """
        getter for image of the line segments only

            Returns:
                a numpy image array set to 255 except for lines set to 0
        """
        l_image = np.empty(self._image.shape, dtype=np.uint8)
        l_image.fill(255)

        for line in self._lines:
            # Indices of pixels that belong to the line
            indices0, indices1 = skd.line(
                line.start[0], line.start[1],
                line.end[0], line.end[1])
            l_image[indices1, indices0] = 0

        return l_image

    @property
    def image_polar_lines(self):
        """
        getter for image of the polar lines only

            Returns:
                a numpy image array set to 255 except for lines set to 0
        """
        l_image = np.empty(self._image.shape, dtype=np.uint8)
        l_image.fill(255)

        for line in self._lines:
            indices0, indices1 = skd.line(
                line.start[0], line.start[1],
                line.end[0], line.end[1])
            l_image[indices1, indices0] = 0

        return l_image

    @property
    def image_all(self):
        """
        getter for image of the vertices and lines

            Returns:
                a numpy image array set to 255 except for lines and vertices set to 0
        """
        image = self.image_lines

        for vertex in self._vertices:
            image[vertex[0], vertex[1]] = 0

        return image



    def find_lines(self):
        """
        detect lines in the image

            Returns:
                None
        """
        img = np.empty(self._image.shape, dtype=np.uint8)
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
            self._lines.append(PolarLine.line_to_theta_r(line[0], line[1]))

    def find_vertices(self):
        """
        Vertex detector using corner_peaks

            Returns:
                None
        """
        self._logger.debug("find_vertices")

        enhanced = corner_harris(self._image)
        self._vertices = (
            enhanced, self._parameters.verts_min_distance)

    def merge(self):
        """
        attempt to lines into cryatals
        @TODO finish

            Returns:
                None
        """
        for point in self._vertices:
            tmp = []
            for line in self._lines:
                tmp.append(line.point_to_line(point))

            print(tmp)


    @property
    def vertices(self):
        """
        getter for the array of vertices

            Returns:
                the array of vertices (not copy)
        """
        return self._vertices

    @property
    def lines(self):
        """
        getter for the array of lines

            Returns:
                the array of lines (not copy)
        """
        return self._lines

def test():
    """
    unit test

        Returns:
            None
    """


    p_lines = PolyLineExtract()

    p_lines.image = data.camera()

    p_lines.find_vertices()
    p_lines.find_lines()

    print("Vertices:")
    for vert in p_lines.vertices:
        print(vert)

    print("Lines")
    print("y, x, y, x, theta, r, length")
    for line in p_lines.lines:
        message = "{}, {}, {}, {}, {}, {}, {}".format(
            line.start[0], line.start[1],
            line.end[0], line.end[1],
            line.theta, line.r, line.length)
        print(message)

if __name__ == "__main__":
    FILE_NAME = "PolyLineExtract.log"
    lazylogger.set_up_logging(FILE_NAME, append=True)
    test()
    lazylogger.end_logging(FILE_NAME)
