## -*- coding: utf-8 -*-
"""
Created on Wed 17 Feb 2021

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

This work was funded by Joanna Leng's EPSRC funded RSE Fellowship (EP/R025819/1)

@copyright 2021
@author: j.h.pickering@leeds.ac.uk and j.leng@leeds.ac.uk
"""
# set up linting conditions

from collections import namedtuple

## Storage of the statistics of one frame of video
FrameStats = namedtuple("FrameStats", ["mean", "std_deviation", "bin_counts"])

class VideoIntensityStats():
    """
    storage for the intensity statistics of  a video
    """

    def __init__(self, bins=None):
        """
        initalize the object
            Args:
                bins [np.float] the bins
        """
        ## the statistics of the individual frames
        self._frames = []

        ## the bins used in the bin counts
        self._bins = bins

    @property
    def bins(self):
        return self._bins

    @property
    def frames(self):
        return self._frames

    def append_frame(self, frame):
        self._frames.append(frame)

    def set_bins(self, bins):
        self._bins = bins
