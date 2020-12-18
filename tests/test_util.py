# -*- coding: utf-8 -*-
"""
Created on Friday Dec 18  2020

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

from cgt.model.imagelinesegment import ImageLineDifference
from cgt.util.utils import difference_to_distance, difference_list_to_velocities

class TestUtilFunctions(unittest.TestCase):
    def setUp(self):
        self._difference = ImageLineDifference(2.0, 4.0)

        self._diff_list = []
        self._diff_list.append((20, ImageLineDifference(2.0, 4.0)))
        self._diff_list.append((30, ImageLineDifference(4.0, 8.0)))

    def tearDown(self):
        self._difference = None

    def test_distance(self):
        scale = 1.0
        tmp = difference_to_distance(self._difference, scale)
        self.assertAlmostEqual(tmp, 3.0,
                               msg="difference not coverted to distance correctly 0",
                               delta=0.0001)

        scale = 3.0
        tmp = difference_to_distance(self._difference, scale)
        self.assertAlmostEqual(tmp, 9.0,
                               msg="difference not coverted to distance correctly 1",
                               delta=0.0001)

    def test_velocityself(self):
        scale = 1.0
        fps = 10
        tmp = difference_list_to_velocities(self._diff_list, scale, fps)

        self.assertAlmostEqual(tmp[0], 1.5,
                               msg="difference not coverted to velocity correctly 0",
                               delta=0.0001)

        self.assertAlmostEqual(tmp[1], 2.0,
                               msg="difference not coverted to velocity correctly 1",
                               delta=0.0001)

if __name__ == "__main__":
    unittest.main()
