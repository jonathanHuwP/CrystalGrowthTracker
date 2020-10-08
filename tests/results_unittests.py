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
import datetime as dt
import sys

import cgt.videoanalysisresultsstore as vas
from cgt.crystal import Crystal
from cgt.region import Region
import cgt.imagelinesegment as ia

sys.path.insert(0, '..\\CrystalGrowthTracker')

# pylint: disable = too-many-instance-attributes

class TestResults(unittest.TestCase):
    """
    advanced tests of Results class
    """

    def setUp(self):
        """
        build a full test class
        """
        self._top = 450
        self._left = 200
        self._bottom = 675
        self._right = 500
        self._start_frame = 250
        self._stop_frame = 500
        self._test_result = self.make_test_result()

    def tearDown(self):
        """
        delete the test class
        """
        self._top = None
        self._left = None
        self._bottom = None
        self._right = None
        self._start_frame = None
        self._stop_frame = None
        self._test_result = None

    def make_test_result(self):
        """
        factory function to procduce a Results object
        """
        region1, crystals1 = self.make_region1()
        region2, crystals2 = self.make_region2()
        regions = [region1, region2]

        store = vas.VideoAnalysisResultsStore(regions)

        for crystal in crystals1:
            store.add_crystal(crystal, 0)

        for crystal in crystals2:
            store.add_crystal(crystal, 1)

        return store

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

        crystal = Crystal(notes="01")

        crystal.add_faces([line1, line2], self._start_frame)

        crystals = [crystal]
        region = Region(self._top,
                        self._left,
                        self._bottom,
                        self._right,
                        self._start_frame,
                        self._stop_frame)

        return region, crystals

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

        crystal = Crystal(notes="02")

        crystal.add_faces([line1, line2], self._start_frame)
        crystal.add_faces([line1a, line2a], self._stop_frame)

        region = Region(self._top,
                        self._left,
                        self._bottom,
                        self._right,
                        self._start_frame,
                        self._stop_frame)

        return region, [crystal]

    def test_data(self):

        test_result = self.make_test_result()

        self.assertEqual(test_result.number_of_regions, 2,
                         msg="number of regions in test result is wrong")

if __name__ == "__main__":
    unittest.main()
