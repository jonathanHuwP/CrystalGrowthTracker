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
import PyQt5.QtWidgets as qw

from tests.makeresults import make_results_object
from cgt.model.videoanalysisresultsstore import VideoAnalysisResultsStore

class TestResults(unittest.TestCase):
    """
    tests of Results class
    """

    def setUp(self):
        """
        build a full test class
        """
        self._store = make_results_object()

    def tearDown(self):
        """
        delete the test class
        """
        del self._store

    def test_state_raw_object(self):
        """
        test the inital state of the object with no added data
        """
        results = VideoAnalysisResultsStore(None)
        message = "store in state changed"
        self.assertFalse(results.has_been_changed(), message)


    def test_state_with_new_data(self):
        """
        test the inital state of the object with data added
        """
        message = "store in state unchanged"
        self.assertTrue(self._store.has_been_changed(), message)

    def test_add_region(self):
        """
        test the addition of a region
        """
        region = self.add_region()
        regions = self._store.get_regions()

        message = "regions list is the wrong length"
        self.assertEqual(len(regions), 3, message)
        message = "region not stored correctly"
        self.assertEqual(region.rect(), regions[2].rect(), message)

    def test_add_keyframe(self):
        """
        test the additon of a key frame to region
        """
        frame = 200
        self.add_region()
        self._store.add_key_frame(2, frame)

        frames = self._store.get_key_frames(2)
        number = len(frames)

        message = "wrong number of key frames"
        self.assertEqual(1, number, message)
        message = "key frame wrong"
        self.assertEqual(frame, frames[0], message)

    def add_region(self):
        """
        add a region
            Returns:
                region (QRect): the region added
        """
        region = qw.QGraphicsRectItem(qc.QRectF(0, 0, 100, 50))
        self._store.add_region(region)

        return region

if __name__ == "__main__":
    unittest.main()
