"""
Created on Thur 16 June 2022

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

This work was funded by Joanna Leng's EPSRC funded RSE Fellowship (EP/R025819/1)

@copyright 2022
@author: j.h.pickering@leeds.ac.uk and j.leng@leeds.ac.uk
"""
import unittest

from cgt.tests.test_io import TestIO
from cgt.tests.test_project import TestProject
from cgt.tests.test_results import TestResults
from cgt.tests.test_velocities import (TestDisplacements, TestVelocities)
from cgt.tests.test_videocontrols import TestVideoControls

def make_suite():
    """
    make a unittest TestSuite object
        Returns
            (unittest.TestSuite)
    """
    suite = unittest.TestSuite()

    suite.addTest(TestIO('test_write_read'))

    suite.addTest(TestProject('test_create_project'))
    suite.addTest(TestProject('test_add_data'))

    suite.addTest(TestResults('test_state_raw_object'))
    suite.addTest(TestResults('test_state_with_new_data'))
    suite.addTest(TestResults('test_add_region'))
    suite.addTest(TestResults('test_add_keyframe'))

    suite.addTest(TestDisplacements('test_velocity'))

    suite.addTest(TestVelocities('test_calculator'))

    suite.addTest(TestVideoControls('test_initial_state'))
    suite.addTest(TestVideoControls('test_one_frame_forward'))
    suite.addTest(TestVideoControls('test_one_frame_backward'))
    suite.addTest(TestVideoControls('test_goto_end'))
    suite.addTest(TestVideoControls('test_goto_start'))
    suite.addTest(TestVideoControls('test_goto_frame_button'))
    suite.addTest(TestVideoControls('test_goto_frame_box'))
    suite.addTest(TestVideoControls('test_play_pause'))
    suite.addTest(TestVideoControls('test_play_forwards'))
    suite.addTest(TestVideoControls('test_play_backwards'))
    suite.addTest(TestVideoControls('test_zoom_box'))
    suite.addTest(TestVideoControls('test_slider'))

    return suite

def run_all_tests():
    """
    run all tests in the TestSuite
    """
    runner = unittest.TextTestRunner()
    runner.run(make_suite())

if __name__ == '__main__':
    run_all_tests()
