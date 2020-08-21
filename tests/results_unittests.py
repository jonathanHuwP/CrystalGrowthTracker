# -*- coding: utf-8 -*-
"""
Created on Tuesday August 18 2020

module results provides unit tests for the CGT results storage classes

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

import sys
sys.path.insert(0, '..\\CrystalGrowthTracker')

import cgt.videoanalysisresultsstore as vas
from cgt.crystal import Crystal
from cgt.region import Region
import cgt.image_artifacts as ia

import unittest
import os
import datetime as dt

class TestResults1(unittest.TestCase):
    """
    basic tests of the Results class
    """

    def setUp(self):
        """
        build a full test class
        """
        self._video_name = "ladkj.mp4"
        self._frame_rate = 8
        self._length = 500
        self._width = 800
        self._height = 600
        self._test_result = self.make_test_result()

    def tearDown(self):
        """
        delete the test class
        """
        self._video_name = None
        self._frame_rate = None
        self._length = None
        self._width = None
        self._height = None
        self._test_result = None

    def make_test_result(self):
        """
        factory function to procduce a Results object
        """
        source = vas.VideoSource(self._video_name,
                             self._frame_rate,
                             self._length,
                             self._width,
                             self._height)
        return vas.VideoAnalysisResultsStore(source)

    def test_history(self):
        """
        test that the history is correct
        """
        self.assertEqual(len(self._test_result.history), 1,
                         "history length is wrong")
        self.assertEqual(self._test_result.history[0].date, str(dt.date.today()),
                         "date is wrong (careful of midnight)")
        self.assertEqual(self._test_result.history[0].user_name, os.getlogin(),
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

class TestResults2(unittest.TestCase):
    """
    advanced tests of Results class
    """

    def setUp(self):
        """
        build a full test class
        """
        self._top_left_horizontal = 450
        self._top_left_vertical = 200
        self._bottom_right_horizontal = 675
        self._bottom_right_vertical = 500
        self._start_frame = 250
        self._stop_frame = 500
        self._test_result = self.make_test_result()

    def tearDown(self):
        """
        delete the test class
        """
        self._top_left_horizontal = None
        self._top_left_vertical = None
        self._bottom_right_horizontal = None
        self._bottom_right_vertical = None
        self._start_frame = None
        self._stop_frame = None
        self._test_result = None

    def make_test_result(self):
        """
        factory function to procduce a Results object
        """
        source = vas.VideoSource("ladkj.mp4", 8, 500, 800, 600)
        regions = [self.make_region1(), self.make_region2()]

        return vas.VideoAnalysisResultsStore(source, regions)

    def make_region1(self):
        """
        factory function to produce a test crystal
        """

        line1 = ia.ImageLineSegment(ia.ImagePoint(50, 150),
                                    ia.ImagePoint(150, 50),
                                    "01")

        line2 = ia.ImageLineSegment(ia.ImagePoint(50, 50),
                                    ia.ImagePoint(150, 150),
                                    "02")


        crystal = Crystal(name="01")

        crystal.add_faces([line1, line2], self._start_frame)

        crystals = [crystal]
        region = Region(self._top_left_horizontal,
                        self._top_left_vertical,
                        self._bottom_right_horizontal,
                        self._bottom_right_vertical,
                        self._start_frame,
                        self._stop_frame,
                        [crystal])

    def make_region2(self):
        """
        factory function to produce a test crystal
        """

        line1 = ia.ImageLineSegment(ia.ImagePoint(100, 200),
                                    ia.ImagePoint(250, 200),
                                    "01")

        line2 = ia.ImageLineSegment(ia.ImagePoint(200, 150),
                                    ia.ImagePoint(200, 300),
                                    "02")

        line1a = ia.ImageLineSegment(ia.ImagePoint(100, 225),
                                     ia.ImagePoint(250, 225),
                                     "01")

        line2a = ia.ImageLineSegment(ia.ImagePoint(175, 150),
                                     ia.ImagePoint(175, 300),
                                     "02")

        crystal = Crystal(name="02")

        crystal.add_faces([line1, line2], self._start_frame)
        crystal.add_faces([line1a, line2a], self._stop_frame)

        region = Region(self._top_left_horizontal,
                        self._top_left_vertical,
                        self._bottom_right_horizontal,
                        self._bottom_right_vertical,
                        self._start_frame,
                        self._stop_frame,
                        [crystal])

    def test_something(self):
        """
        test whatever
        """
        self.assertEqual(self._test_result.video.name, "ladkj.mp4", "store name is wrong")

if __name__ == "__main__":
    unittest.main()
