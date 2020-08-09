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

class ImageEnhancer():
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

            Args:
                limits (tuple 2 x numbers) explicit min/max intensities (%)

            Returns:
                (np.array of input type) input streatched to eliminate pixels outside range
        """
        percent2, percent98 = np.percentile(self._source, limits)
        return exposure.rescale_intensity(
            self._source,
            in_range=(percent2, percent98))

    def equalization(self):
        """
        histogram equalization of image, returns float64

            Returns:
                histogram equalised image np.array(float64)
        """
        return exposure.equalize_hist(self._source)

    def adaptive_equalization(self, c_limit=0.03):
        """
        adaptabe histogram equalization of image, uses histograms
        computed over different tile regions of the image, the clipping
        is governed by c_limit, with higher values giving more contrast

            Args:
                c_limit (float) clipping limit, normalized between 0 and 1

            Returns:
                equalized image np.array(float64)
        """
        return exposure.equalize_adapthist(
            self._source,
            clip_limit=c_limit)
