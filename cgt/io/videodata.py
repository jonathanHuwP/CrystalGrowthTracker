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

class VideoData():
    """
    class for storing data about the video in the file. Since actual frame rates
    may be different from the frame rate specified within the video file both are
    stored and conversion functions provided
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

        ## the number of bytes in a pixel
        self._bytes_per_pixel = bytes_per_pixel

        ## the actual frame rate supplied by user
        self._frame_rate_user = frame_rates[0]

        ## the time step for the user frame rate
        self._time_step_user = 1.0/self._frame_rate_user

        ## the actual duration for the video, based on user frame rate
        self._time_duration_user = (self._frame_count-1)*self._time_step_user

        ## the frame rate read from source file
        self._frame_rate_internal = frame_rates[1]

        ## the time step internal to the video
        self._time_step_internal = 1.0/self._frame_rate_internal

        ## the duration of video based on source file frame rate
        self._time_duration_codec = (self._frame_count-1)*self._time_step_internal

        ## the size of a frame in bytes
        self._frame_size = self._width*self._height*self._bytes_per_pixel

        ## conversion factor to codec time
        self._to_codec = float(self._frame_rate_user)/float(self._frame_rate_internal)

        ## conversion factor to user time
        self._to_user = float(self._frame_rate_internal)/float(self._frame_rate_user)

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

    def get_frame_rate_user(self):
        """
        getter for the user input frame rate
        """
        return self._frame_rate_user

    def get_time_duration_user(self):
        """
        getter for the length of video at user input frame rate
        """
        return self._time_duration_user

    def get_frame_rate_internal(self):
        """
        getter for the frame rate read from video file
        """
        return self._frame_rate_internal

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

    def get_bytes_per_line(self):
        """
        getter for the number of bytes in a line (needed by Qt QImage)
        """
        return self._width * self._bytes_per_pixel

    def to_codec_time(self, time):
        """
        convert a time from the user frames per second to the codec FPS
            Args:
                time (float): time in second user FPS
            Returns
                (float): time in codec FPS
        """
        return time * self._to_codec

    def to_user_time(self, time):
        """
        convert a time from the codec frames per second to the user FPS
            Args:
                time (float): time in second codec FPS
            Returns
                (float): time in user FPS
        """
        return time * self._to_user

    def next_frame(self, frame):
        """
        get the next frame wrapping at the end
            Args:
                frame (int): the existing frame
            Returns:
                (int)
        """
        next_frame = frame+1
        if next_frame >= self._frame_count:
            next_frame = 0

        return next_frame

    def previous_frame(self, frame):
        """
        get the previous frame wrapping at the start
            Args:
                frame (int): the existing frame
            Returns:
                (int)
        """
        next_frame = frame-1
        if next_frame < 0:
            next_frame = self._frame_count-1

        return next_frame

    def get_user_time_step(self):
        """
        getter for the inter-frame time step (user FPS)
        """
        return self._time_step_user

    def frame_to_internal_time(self, frame):
        """
        convert a frame number to internal video time
            Args:
                frame (int): frame number
            Returns:
                (float): the time in internal FPS
        """
        return frame * self._time_step_internal

    def frame_to_user_time(self, frame):
        """
        convert a frame number to user FPS time
            Args:
                frame (int): frame number
            Returns:
                (float): the time in user FPS
        """
        return frame * self._time_step_user
