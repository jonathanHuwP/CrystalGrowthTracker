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

import image_artifacts as ia

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
    def __init__(self, region, name, faces=None):
        """
        initalization function

            Args:
                region (Region) the video region holding the crystal

                faces (image_artifacts.ArtifactStore) the lines defining the faces
        """

        ## the region in which the crystal is defined
        self._region = region

        ## the name or id of the crystal
        self._name = name

        ## ArtifactStore for the lines forming the faces indexed by frame number
        self._faces = ia.ArtifactStore(name)

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

    def add_faces(self, faces, frame_number):
        """
        add a list of faces and the frame number to the crystal

            Args:
                faces ([image_artifacts.ImageLineSegment]) list of lines

                frame_number (int) the frame number associate with the list
        """
        self._faces[frame_number] = faces

    @property
    def number_of_frames_held(self):
        """
        getter for the number of frames held

            Returns:
                number of frames (int)
        """
        return len(self._faces)

    @property
    def list_of_frame_number(self):
        """
        getter for the frames held

            Returns:
                the frames (dict_keys)
        """
        return self._faces.keys()

    def faces_in_frame(self, frame_number):
        """
        getter for the lines in a given frame

            Args:
                frame_number (int) the number of the frame

            Returns:
                the list of lines representing the faces in the frame
        """
        return self._faces[frame_number]

    def face_movement_distances(self, first_frame, second_frame):
        """
        getter for the distances the face have moved, in pixels, between the two frames

            Args:
                first_frame (int) number of the first frame, must be in store

                second_frame (int) number of the second frame, must be in store

            Returns
                a list of image_artifacts.ImageLineDifference objects holding the differences

        TODO implement this
        """
        pass


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

                crystals ([Crystal]) the crystal objects holding faces, times and region
        """

        ## a record of the date and user for all saves
        self._history = []

        if history is not None:
            self._history = history
        else:
            self._history.append(DateUser(date.today(), getlogin()))

        ## the source video on which the analyais is based
        self._video = video

        ## storage for the crystals identified by the user dict(name, crystal)
        self._crystals = {}

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

    def add_crystal(self, crystal):
        """
        add a crystal to the results

            Args:
                crystal (Crystal) the crystal to be added
        """
        self._crystals[crystal.name] = crystal

    @property
    def crystal_names(self):
        """
        getter for a list of the names of the crystals

            Returns:
                list of crystal names
        """
        return [i.name for i in self._crystals]

    def get_crystal(self, name):
        """
        getter for an individual crystal

            Args:
                name the name or id of the crystal

            Returns:
                the chosen crystel crystal

            Throws:
                KeyError if unknow name
        """
        return self._crystals[name]

################
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
        source = VideoSource(self._video_name,
                             self._frame_rate,
                             self._length,
                             self._width,
                             self._height)
        return VideoAnalysisResultsStore(source)

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
        source = VideoSource("ladkj.mp4", 8, 500, 800, 600)
        crystals = [self.make_crystal1(), self.make_crystal2()]

        return VideoAnalysisResultsStore(source, crystals)

    def make_crystal1(self):
        """
        factory function to produce a test crystal
        """
        region = VideoRegion(self._top_left_horizontal,
                             self._top_left_vertical,
                             self._bottom_right_horizontal,
                             self._bottom_right_vertical,
                             self._start_frame,
                             self._stop_frame)

        line1 = ia.ImageLineSegment(ia.ImagePoint(50, 150),
                                    ia.ImagePoint(150, 50),
                                    "01")

        line2 = ia.ImageLineSegment(ia.ImagePoint(50, 50),
                                    ia.ImagePoint(150, 150),
                                    "02")


        crystal = Crystal(region=region, name="01")

        crystal.add_faces([line1, line2], self._start_frame)

    def make_crystal2(self):
        """
        factory function to produce a test crystal
        """
        region = VideoRegion(self._top_left_horizontal,
                             self._top_left_vertical,
                             self._bottom_right_horizontal,
                             self._bottom_right_vertical,
                             self._start_frame,
                             self._stop_frame)

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

        crystal = Crystal(region=region, name="02")

        crystal.add_faces([line1, line2], self._start_frame)
        crystal.add_faces([line1a, line2a], self._stop_frame)

    def test_something(self):
        """
        test whatever
        """
        self.assertEqual(self._test_result.video.name, "alkjd", "store name is wrong")

if __name__ == "__main__":
    unittest.main()
