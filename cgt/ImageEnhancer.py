# -*- coding: utf-8 -*-
"""
Created on Tue Jul  7 12:30:17 2020

classes for possible image analysis techniques

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
from skimage import exposure

class ImageEnhancer(object):
    """
    Class providing various image enhancment methods.
    """
    def __init__(self, image, parameters=None):
        self._source = image
        self._parameter = parameters
        
    def constrast_stretch(self, limits=(2, 98)):
        """
        Eliminate the top an bottom of the intensity 
        and streatch out the rest
        
        Parameters
        ----------
        limits : tuple of two numbers, optional
            Use range_values as explicit min/max intensities (%). 
            The default is (2, 98).

        Returns
        -------
        np.array(type = input)
            the input array streatched so that pixels outside 
            the range are eliminated.
        """
        p2, p98 = np.percentile(self._source, limits)
        return exposure.rescale_intensity(
            self._source, 
            in_range=(p2, p98))

    def equalization(self):
        """
        histogram equalization of image, returns float64
        Returns
        -------
        np.array(float64)
            histogram equalised image.

        """
        return exposure.equalize_hist(self._source)

    def adaptive_equalization(self, c_limit=0.03):
        """
        adaptabe histogram equalization of image, 
        uses histograms computed over different tile 
        regions of the image

        Parameters
        ----------
        c_limit : float, optional
            Clipping limit, normalized between 0 and 1 
            (higher values give more contrast).. The default is 0.03.

        Returns
        -------
        np.array(float64)
            equalized image.
        """
        return exposure.equalize_adapthist(
            self._source, 
            clip_limit=c_limit)
