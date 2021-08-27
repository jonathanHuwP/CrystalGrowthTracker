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
# pylint: disable = import-error

import PyQt5.QtCore as qc

import numpy as np

from cgt.util.framestats import FrameStats, VideoIntensityStats

class VideoAnalyser(qc.QObject):
    """
    a video reader that is designed to run as a seperate thread
    from the display object, allowing smoother animation
    """

    ## the progress signal
    frames_analysed = qc.pyqtSignal(int)

    def __init__(self, video_file, parent=None):
        """
        initalize by usng opencv opening the video file

            Args:
                video_file (string) the path to the video file
        """
        super().__init__(parent)

        ## initiaize the file video stream
        # HACK
        # self._video_reader = cv.VideoCapture(video_file)

        ## store the file name
        self._video_file = video_file

        ## the lenght
        # HACK
        self._length = 0#int(self._video_reader.get(cv.CAP_PROP_FRAME_COUNT))

    def get_name(self):
        """
        getter for the file name
            Returns:
                file name (string)
        """
        return self._video_file

    def stats_whole_film(self):
        """
        get the statistics for every frame of the video
            Returns:
                the statistics (VideoIntensityStats)
        """
        bins = np.linspace(0, 256, 32)
        vid_statistics = VideoIntensityStats(bins)
        for i in range(self._length):
            vid_statistics.append_frame(self.make_stats(i, bins))
            if i%10 == 0:
                self.frames_analysed.emit(i)

        self.frames_analysed.emit(self._length)

        return vid_statistics

    def make_stats(self, frame_number, bins):
        """
        make the statistics for a single frame
            Args:
                frame_number (int) the frame
                bins ([int]) the bins for counting
        """
        image = self.get_image_values(frame_number)

        mean = np.mean(image)
        standard_deviation = np.std(image)
        count, _ = np.histogram(image, bins)

        return FrameStats(mean, standard_deviation, count)

    def get_frame(self, frame_number):
        """
        get a frame of video as a numpy image
            Args:
                frame_number (int) the number of the required frame
            Returns:
                image (numpy.array dtype=uint8) the image
        """
        # HACK
        # self._video_reader.set(cv.CAP_PROP_POS_FRAMES, frame_number)
        flag, img = self._video_reader.read()

        if not flag:
            message = f"failed to read image for frame {frame_number}"
            raise ValueError(message)

        # HACK
        return None#cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    def get_image_values(self, frame_number):
        """
        get image as a one dimensional array
        """
        frame = self.get_frame(frame_number)
        return frame.flatten()
