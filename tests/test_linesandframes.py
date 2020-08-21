# -*- coding: utf-8 -*-
"""
Created on Tuesday July 21 13:42: 2020

this module hold low level classes representing artifacts that can
be drawn on an image

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

import unittest

from cgt.imagepoint import ImagePoint
from cgt.imagelinesegment import ImageLineSegment

## class for unit tests of the ImagePoints
class TestImagePoints(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_vertical(self):
        """
        test the is_vertical function
        """
        start = ImagePoint(100, 200)
        end0 = ImagePoint(200, 300)
        end1 = ImagePoint(100, 300)

        line = ImageLineSegment(start, end0, "non_vertical")
        v_line = ImageLineSegment(start, end1, "vertical")

        self.assertFalse(line.is_vertical,
                        "non-vertical line reports vertical")
        self.assertTrue(v_line.is_vertical,
                        "vertical line reports non-vertical")

    def test_dist_to_line(self):
        """
        test the is_vertical function
        """
        start = ImagePoint(100, 200)
        end0 = ImagePoint(200, 300)
        end1 = ImagePoint(100, 300)

        line = ImageLineSegment(start, end0, "non_vertical")
        v_line = ImageLineSegment(start, end1, "vertical")

        test_point = ImagePoint(100, 100)

        flag_l, closest_l = line.is_closest_point_on_segment(test_point)
        flag_vl, closest_vl = v_line.is_closest_point_on_segment(test_point)

        d_l = closest_l.distance_from(test_point)
        d_vl = closest_vl.distance_from(test_point)

        self.assertFalse(flag_l, "claimed test point in line segment")
        self.assertFalse(flag_vl, "claimed test point in vertical line segment")

        self.assertAlmostEqual(d_l, 0.0,
                               msg="distance to line failed",
                               delta=0.0001)

        self.assertAlmostEqual(d_vl, 0.0,
                               msg="distance to line failed",
                               delta=0.0001)

if __name__ == "__main__":
    unittest.main()
