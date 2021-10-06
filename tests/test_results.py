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
import unittest

import PyQt5.QtCore as qc

from cgt.model.videoanalysisresultsstore import VideoAnalysisResultsStore

class TestResults(unittest.TestCase):
    """
    tests of Results class
    """

    def setUp(self):
        """
        build a full test class
        """
        self._store = VideoAnalysisResultsStore(None)

    def tearDown(self):
        """
        delete the test class
        """
        del self._store

    def test_initial_state(self):
        """
        test the inital state of the object
        """
        message = "store initalized in state changed"
        self.assertFalse(self._store.has_been_changed(), message)

    def test_add_region(self):
        """
        test the addition of a region
        """
        rect = self.add_region()
        regions = self._store.get_regions()

        number = len(regions)
        message = f"regions list is the wrong length: {number} instead of 1"
        self.assertEqual(1, number, message)
        message = "region not stored correctly"
        self.assertEqual(rect, regions[0], message)

    def test_add_keyframe(self):
        """
        test the additon of a key frame to region
        """
        frame = 200
        self.add_region()
        self._store.add_key_frame(0, frame)

        frames = self._store.get_key_frames(0)
        number = len(frames)

        message = "wrong number of key frames: {number} should be 1"
        self.assertEqual(1, number, message)
        message = "key frame wrong: {frams[0]} should be {frame}"
        self.assertEqual(frame, frames[0], message)

    def add_region(self):
        """
        add a region
            Returns:
                region (QRect): the region added
        """
        rect = qc.QRect(0, 0, 100, 50)
        self._store.add_region(rect)

        return rect

if __name__ == "__main__":
    unittest.main()
