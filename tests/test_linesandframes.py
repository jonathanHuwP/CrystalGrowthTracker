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

from cgt.model.imagepoint import ImagePoint
from cgt.model.imagelinesegment import ImageLineSegment
from cgt.model.line import Line

class TestLines(unittest.TestCase):
    def make_lines(self):
        line_seg1 = ImageLineSegment(ImagePoint(100, 200),
                                 ImagePoint(250, 200))

        line_seg2 = ImageLineSegment(ImagePoint(200, 150),
                                 ImagePoint(200, 300))

        line_seg1a = ImageLineSegment(ImagePoint(100, 225),
                                  ImagePoint(250, 225))

        line_seg2a = ImageLineSegment(ImagePoint(175, 150),
                                  ImagePoint(175, 300))

        self._lines = []
        self._lines.append(Line("test00"))
        self._lines.append(Line("test01"))
        self._lines.append(Line("test02"))

        self._lines[0].add_line(67, line_seg1)

        self._lines[1].add_line(67, line_seg1)
        self._lines[1].add_line(122, line_seg1a)

        self._lines[2].add_line(254, line_seg2)
        self._lines[2].add_line(123, line_seg2a)
        self._lines[2].add_line(345, line_seg2a)

    def setUp(self):
        self._lines = None
        self.make_lines()

    def tearDown(self):
        self._lines = None

    def test_vertical(self):
        """
        test the is_vertical function
        """
        start = ImagePoint(100, 200)
        end0 = ImagePoint(200, 300)
        end1 = ImagePoint(100, 300)

        non_vert_line = ImageLineSegment(start, end0)
        vert_line = ImageLineSegment(start, end1)

        self.assertFalse(non_vert_line.is_vertical,
                        "non-vertical line reports vertical")
        self.assertTrue(vert_line.is_vertical,
                        "vertical line reports non-vertical") 
                      
    def test_differences(self):
        """
        test the is_vertical function
        """
        diffs = self._lines[0].get_differences()    
        self.assertEqual(len(diffs), 0,
                         msg="line with only one time returned non-empty list of differences")

        diffs = self._lines[1].get_differences()    
        self.assertEqual(len(diffs), 1,
                         msg="line with two times did not return one differences")
        self.assertEqual(diffs[0].start_d, 25,
                         msg="difference start did not return 25")
        self.assertEqual(diffs[0].end_d, 25,
                         msg="difference start did not return 25")
                         
        diffs = self._lines[2].get_differences()    
        self.assertEqual(len(diffs), 2,
                         msg="line with three times did not return two differences")
        self.assertEqual(diffs[0].start_d, 25,
                         msg="difference start did not return 25")
        self.assertEqual(diffs[0].end_d, 25,
                         msg="difference start did not return 25")
        self.assertEqual(diffs[1].start_d, 25,
                         msg="difference start did not return 25")
        self.assertEqual(diffs[1].end_d, 25,
                         msg="difference start did not return 25")
                         
## class for unit tests of the ImagePoints
class TestImagePoints(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_dist_to_line(self):
        """
        test the is_vertical function
        """
        start = ImagePoint(100, 200)
        end0 = ImagePoint(200, 300)
        end1 = ImagePoint(100, 300)

        line = ImageLineSegment(start, end0)
        v_line = ImageLineSegment(start, end1)

        test_point = ImagePoint(100, 100)

        flag_l, closest_l = line.is_closest_point_on_segment(test_point)
        flag_vl, closest_vl = v_line.is_closest_point_on_segment(test_point)

        d_l = closest_l.distance_from(test_point)
        d_vl = closest_vl.distance_from(test_point)

        self.assertFalse(flag_l, "claimed test point in line segment")
        self.assertFalse(flag_vl, "claimed test point in vertical line segment")

        self.assertAlmostEqual(d_l, 70.7107,
                               msg="distance to line failed on non-vertical line",
                               delta=0.0001)

        self.assertAlmostEqual(d_vl, 0.0,
                               msg="distance to line failed on vertical line",
                               delta=0.0001)

if __name__ == "__main__":
    unittest.main()
