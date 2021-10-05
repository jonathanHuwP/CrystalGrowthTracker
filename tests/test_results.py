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

import cgt.model.videoanalysisresultsstore as vas

class TestResults(unittest.TestCase):
    """
    tests of Results class
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

    def test_data(self):
        pass

if __name__ == "__main__":
    unittest.main()
