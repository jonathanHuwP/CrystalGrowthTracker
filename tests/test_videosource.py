'''
Created on 28 Oct 2020

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

This work was funded by Joanna Leng's EPSRC funded RSE Fellowship (EP/R025819/1)

@copyright 2021
@author: j.h.pickering@leeds.ac.uk and j.leng@leeds.ac.uk
'''
# set up linting condition
# pylint: disable = protected-access
# pylint: disable = c-extension-no-member
# pylint: disable = no-name-in-module
import unittest
from pathlib import Path

from cgt.io.videosource import VideoSource
from tests.make_test_video import make_test, get_frame_count, get_frame_rate

class TestVideoControls(unittest.TestCase):
    """
    test the video vidoe source object
    """

    def setUp(self):
        """
        make a test video
        """
        self._test_file = make_test(Path.cwd())

    def tearDown(self):
        """
        remove
        """
        if self._test_file.exists():
            self._test_file.unlink()

    def test_source(self):
        """
        run tests on the video
        """
        source = VideoSource(self._test_file, get_frame_rate())

        self.data_test(source.get_video_data())

    def data_test(self, data):
        """
        test video data
            data (VideoData): the test object
        """
        self.assertEqual(data.get_frame_rate_internal(),
                         data.get_frame_rate_user(),
                         "internal and user frame rated differnt")
        self.assertEqual(data.get_frame_rate_internal(),
                         get_frame_rate(),
                         "frame rates are not 5")
        self.assertEqual(data.get_frame_count(),
                         get_frame_count(),
                         "wrong number of frames")

if __name__ == '__main__':
    unittest.main(verbosity=2)
