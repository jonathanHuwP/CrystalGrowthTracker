# -*- coding: utf-8 -*-
"""
Created on Fri Sept 18 2020

various support classes and functions

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

from collections import namedtuple

## a tuple representing one end of a region
##
## Args:
##
## rectangle the subimage in screen pixel coordinates
##
## frame the number of the frame
RegionEnd = namedtuple("RegionEnd", ["rectangle", "frame"])

## a tuple for the video on which the analysis is based
##
## Args:
##
## name the video file name or path
##
## frame_rate number of frames per second
##
## frame_count the numer of frames in the video
##
## width the horizontal size of the video in pixels
##
## height the vertical size of the video in pixels
VideoSource = namedtuple("VideoSource", ["name", "frame_rate", "frame_count", "width", "height"])