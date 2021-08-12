## -*- coding: utf-8 -*-
"""
Created on Thursday 12 Aug 2021

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
# pylint: disable = c-extension-no-member
# pylint: disable = import-error

import PyQt5.QtWidgets as qw
import PyQt5.QtCore as qc
import PyQt5.QtGui as qg

class FrameTime():
    """
    class for conversion of time to frame numbers and reverse
    """

    def __init__(self, frames_per_second, video_length):
        """
        set up object
            Args:
                frames_per_second (number): the number of frames per second
                video_length (float): the length of video in seconds
        """

        ## the inter-frame time interval
        self._time_step = 1.0/float(frames_per_second)

        ## the length in seconds
        self._video_length = video_length

        ## the current time of the video
        self._current_time = 0.0

        ## the current frame
        self._current_frame = 0

    def get_time(self):
        """
        getter for the current time
            Returns:
                (float) the vidoe time
        """
        return self._current_time

    def get_frame_number(self):
        """
        getter for the frame number
            Returns:
                (int) the vidoe frame number
        """
        return self._current_frame

    def increment(self):
        """
        increment the time and frame
        """
        self._current_time += self._time_step
        self._current_frame += 1
        if not self._current_time < self._video_length:
                self._current_time = 0.0
                self._current_frame = 0

        return self._current_time, self._current_frame

    def decrement(self):
        """
        increment the time and frame
        """
        self._current_time -= self._time_step
        self._current_frame -= 1
        if not self._current_time > 0.0:
                self._current_time = self._video_length-self._time_step
                self._current_frame = self._video_length

        return self._current_time, self._current_frame
