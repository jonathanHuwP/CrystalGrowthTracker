## -*- coding: utf-8 -*-
"""
Created on  Sunday 01 Aug 2021

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy for the
License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

This work was funded by Joanna Leng's EPSRC funded RSE Fellowship (EP/R025819/1)

@copyright 2021
@author: j.h.pickering@leeds.ac.uk and j.leng@leeds.ac.uk
"""
from collections import namedtuple

## data structure for video data
class VideoData():
    """
    class for storing data about video
    """
    def __init__(self, frame_data, frame_rates, bytes_per_pixel):
        """
        initalize the object
            Args:
                frame_data ([int]): width, height, number of frames
                frame_rates ([float]): user input frame rate, frame rate in file
                bytes_per_pixel (int): the nuber of bytes in one pixel
        """
        ## image width pixels
        self._width = frame_data[0]

        ## image height pixels
        self._height = frame_data[1]

        ## number of frames in video
        self._frame_count = frame_data[2]

        ## the actual frame rate supplied by user
        self._frame_rate_actual = frame_rates[0]

        ## the actual duration for the video, based on user frame rate
        self._time_duration_actual = self._frame_rate_actual*self._frame_count

        ## the frame rate read from source file
        self._frame_rate_codec = frame_rates[1]

        ## the duration of video based on source file frame rate
        self._time_duration_codec = self._frame_rate_codec*self._frame_count

        ## the size of a fram in bytes
        self._frame_size = self._width*self._height*bytes_per_pixel

    def get_width(self):
        """
        getter for the width
        """
        return self._width

    def get_height(self):
        """
        getter for the height
        """
        return self._height

    def get_frame_count(self):
        """
        getter for the frame count
        """
        return self._frame_count

    def get_frame_rate_actual(self):
        """
        getter for the user input frame rate
        """
        return self._frame_rate_actual

    def get_time_duration_actual(self):
        """
        getter for the length of video at user input frame rate
        """
        return self._time_duration_actual

    def get_frame_rate_codec(self):
        """
        getter for the frame rate read from video file
        """
        return self._frame_rate_codec

    def get_time_duration_codec(self):
        """
        getter for the length of video based on frame rate in file
        """
        return self._time_duration_codec

    def get_frame_size(self):
        """
        getter for the size in bytes of a frame
        """
        return self._frame_size
