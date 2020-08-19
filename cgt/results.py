# -*- coding: utf-8 -*-
"""
Created on Tuesday August 18 2020

module results provides storage classes for CGT results.
IO and analysis are provided seperatly.

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

# set up linting conditions
# pylint: disable = too-many-public-methods
# pylint: disable = c-extension-no-member

from collections import namedtuple
from os import getlogin
from datetime import date

import unittest

## define a date user pair for the history
##
## Args:
##
## date the date on which a results were added
##
## user_name the login of the user who added the results
DateUser = namedtuple("DateUser", ["date", "user_name"])

## a tuple for the video on which the analysis is based
VideoSource = namedtuple("VideoSource", ["name", "frame_rate", "length", "width", "height"])

## representation of a region in the video, rectangluar block of pixels over a time interval
##
VideoRegion = namedtuple("VideoRegion",
                         ["top_left_horizontal",
                          "top_left_vertical",
                          "bottom_right_horizontal",
                          "bottom_right_vertical",
                          "start_frame",
                          "end_frame"])

class Region(VideoRegion):
    """
    subclass of video_region providing ustility functions
    """

    @property
    def width(self):
        """
        getter for the width in pixels

            Returns:
                the width in pixels
        """
        return self.bottom_right_horizontal - self.top_left_horizontal

    @property
    def height(self):
        """
        getter for the height in pixels

            Returns:
                the height in pixels
        """
        return self.top_left_vertical - self.bottom_right_vertical

    @property
    def time_interval(self):
        """
        getter for the time interval in frames

            Returns:
                the number of frames in the time interval
        """
        return self.end_frame - self.start_frame

class Crystal:
    """
    storage for the crystals identifed in the video
    """
    def __init__(self, region=None, faces=None):

        ## the region in which the crystal is defined
        self._region = None

        if region is not None:
            self._region = region

        ## storage for the lines forming the faces
        self._faces = []

        if faces is not None:
            self._faces = faces

    @property
    def region(self):
        """
        getter for the region

            Return:
                the region
        """
        return self._region

    @property
    def faces(self):
        """
        getter for the array of lines representing faces

            Return:
                the array of lines representing faces
        """
        return self._faces

class VideoAnalysisResultsStore:
    """
    a storage class that records the results and history of a video analysis
    """
    def __init__(self, video, history=None, crystals=None):
        """
        initalize an object

            Args:
                video (video_source) description of the original video sequence

                history ([date_user]) a list of (date, unser name) recording changes
        """

        ## a record of the date and user for all saves
        self._history = []

        if history is not None:
            self._history = history
        else:
            self._history.append(DateUser(date.today(), getlogin()))

        ## the source video on which the analyais is based
        self._video = video

        ## storage for the crystals identified by the user
        self._crystals = []

        if crystals is not None:
            self._crystals = crystals

    @property
    def video(self):
        """
        getter for the description of the video

            Returns:
                the description of the video source
        """
        return self._video

    @property
    def history(self):
        """
        getter for the history

            Returns:
                the list of (date, user name) pairs
        """
        return self._history

################
class TestStringMethods(unittest.TestCase):

    def test_history(self):
        """
        test that the history is correct
        """
        self.assertEqual(len(self._test_result.history), 1,
                         "history length is wrong")
        self.assertEqual(self._test_result.history[0].date, date.today(),
                        "date is wrong (careful of midnight)")
        self.assertEqual(self._test_result.history[0].user_name, getlogin(),
                        "the user login is wrong")

    def test_video(self):
        """
        test the video data struct
        """
        self.assertEqual(self._test_result.video.name, self._video_name)
        self.assertEqual(self._test_result.video.frame_rate, self._frame_rate)
        self.assertEqual(self._test_result.video.length, self._length)
        self.assertEqual(self._test_result.video.width, self._width)
        self.assertEqual(self._test_result.video.height, self._height)

    def setUp(self):
        self._video_name = "ladkj.mp4"
        self._frame_rate = 8
        self._length = 500
        self._width = 800
        self._height = 600
        self._test_result = self.make_test_result()

    def tearDown(self):
        self._video_name = None
        self._frame_rate = None
        self._length = None
        self._width = None
        self._height = None
        self._test_result = None

    def make_test_result(self):
        source = VideoSource(self._video_name,
                             self._frame_rate,
                             self._length,
                             self._width,
                             self._height)
        return VideoAnalysisResultsStore(source)

if __name__ == "__main__":
    unittest.main()
