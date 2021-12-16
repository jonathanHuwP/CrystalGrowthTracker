# -*- coding: utf-8 -*-
## @package videosourceffmpegtest
# a stand alone test of the ffmpeg based videosourc, it uses the maketestvideo
# package to make a test video then tests reading data and images from the file
#
# @copyright 2020 University of Leeds, Leeds, UK.
# @author j.h.pickering@leeds.ac.uk and j.leng@leeds.ac.uk
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
'''
# set up linting condition
# pylint: disable = protected-access
# pylint: disable = c-extension-no-member
# pylint: disable = no-name-in-module
from pathlib import Path

from cgt.io.videosource import VideoSource
from tests.maketestvideo import make_test, get_frame_count, get_frame_rate

class VSTestResults(list):
    """
    list ignoring append(None)
    """
    def append(self, item):
        if item is not None:
            super().append(item)

def test_video_source():
    """
    test the video vidoe source object
    """
    test_file = Path.cwd()
    try:
        test_file = make_test(test_file)
        test_source(test_file)
    except IOError:
        return None
    finally:
        if test_file.exists() and test_file.is_file():
            test_file.unlink()

def test_source(test_file):
    """
    test constructing a VideoSource, must use QImage as no QEnviroment
    """
    source = VideoSource(test_file, get_frame_rate())
    results = VSTestResults()
    data_test(source.get_video_data(), results)
    image_test(source, results)

    if len(results) > 0:
        for item in results:
            print(item)
    else:
        print("No errors")

def image_test(source, results):
    """
    test if a pixmap can be extracted from VideoSource
        Args:
            source (VideoSource): the test object
            results (VSTestResults): results list
    """
    image = source.get_image_at(1.0)
    results.append(assert_equal(image.width(), 500, "image has wrong width"))

def data_test(data, results):
    """
    test video data
        data (VideoData): the test object
    """
    results.append(assert_equal(data.get_frame_rate_internal(),
                                data.get_frame_rate_user(),
                                "internal and user frame rated differnt"))

    results.append(assert_equal(data.get_frame_rate_internal(),
                                get_frame_rate(),
                                "frame rates are not 5"))

    results.append(assert_equal(data.get_frame_count(),
                                get_frame_count(),
                                "wrong number of frames"))

def assert_equal(first, second, message):
    """
    if first == second return None: else else message
    """
    if first == second:
        return None

    return message

if __name__ == '__main__':
    test_video_source()
