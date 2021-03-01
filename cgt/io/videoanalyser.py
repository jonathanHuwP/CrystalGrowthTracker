## -*- coding: utf-8 -*-
"""
Created on Friday 29 Jan 2021

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
"""
# set up linting conditions
# pylint: disable = c-extension-no-member

import numpy as np
import cv2 as cv

from cgt.util.framestats import FrameStats

def bgr_to_gray(rgb):
    tmp = np.dot(rgb[...,:3], [0.1140, 0.5870, 0.2989])
    return tmp.astype(np.uint8)

class VideoAnalyser(object):
    """
    a video reader that is designed to run as a seperate thread
    from the display object, allowing smoother animation
    """
    def __init__(self, video_file):
        """
        initalize by usng opencv opening the video file

            Args:
                video_file (string) the path to the video file
        """
        ## initiaize the file video stream
        self._video_reader = cv.VideoCapture(video_file)

    @property
    def length(self):
        """
        length of video, the largest allowd frame number is lenght

            Returns:
                the number of frames in the video (int)
        """
        return int(self._video_reader.get(cv.CAP_PROP_FRAME_COUNT))

    def make_histogram(self, frame_number, limit):
        """
        make statistics for a frame
            Args:
                frame_number (int) the number of the frame
            Returns:
                counts ([int]) array of bin counts
                bins ([float]) array of bin bounds
                limit (int) the upper value of the samples
        """
        # bins 0 to 32, holding eavenly spaced values 0 to limit
        bins = np.linspace(0, limit, 32)
        image = self.get_image_values(frame_number)

        return np.histogram(image, bins)

    def stats_whole_film(self):
        """
        get the statistics for every frame of the video
        """
        bins = np.linspace(0, 256, 32)
        vid_statistics = []
        for i in range(self.length):
            vid_statistics.append(self.make_stats(i, bins))
            if i%100 == 0:
                print(f"proc vid {i}")

        return vid_statistics

    def make_stats(self, frame_number, bins):
        image = self.get_image_values(frame_number)

        mean = np.mean(image)
        standard_deviation = np.std(image)
        histo = np.histogram(image, bins)

        return FrameStats(mean, standard_deviation, histo)

    def get_frame(self, frame_number):
        """
        get a frame of video as a numpy image
            Args:
                frame_number (int) the number of the required frame
            Returns:
                image (numpy.array dtype=uint8) the image
        """
        self._video_reader.set(cv.CAP_PROP_POS_FRAMES, frame_number)
        flag, img = self._video_reader.read()

        if not flag:
            message = f"failed to read image for frame {frame}"
            raise ValueError(message)

        return img

    def get_image_values(self, frame_number):
        """
        get image as a one dimensional array
        """
        frame = self.get_frame(frame_number)
        return frame.flatten()
