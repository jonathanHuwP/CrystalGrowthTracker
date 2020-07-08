# -*- coding: utf-8 -*-
"""
Created on Tue Jul  7 12:30:17 2020

@author: J.H.Pickering@leeds.ac.uk
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
