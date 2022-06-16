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
import subprocess
import os
import pathlib

import PyQt5.QtCore as qc

import numpy as np
import ffmpeg

from cgt.io.ffmpegbase import FfmpegBase
from cgt.util.framestats import FrameStats, VideoIntensityStats
from cgt.util import config

class VideoAnalyser(FfmpegBase):
    """
    an object to analyse statistic of a video
    """

    ## the pixel format and number of bytes
    PIX_FMT = ('gray', 1)

    ## the progress signal
    frames_analysed = qc.pyqtSignal(int)

    def __init__(self, video_file, parent=None):
        """
        initalize by usng opencv opening the video file
            Args:
                video_file (string) the path to the video file
                parent (QObject): parent object
        """
        super().__init__(video_file, parent)

        self.probe_video(1, VideoAnalyser.PIX_FMT[1])

    def stats_whole_film(self):
        """
        get the statistics for every frame of the video
            Returns:
                the statistics (VideoIntensityStats)
        """
        length = self._video_data.get_frame_count()

        args = (ffmpeg
                .input(self.get_name())
                .output('pipe:', format='rawvideo', pix_fmt=VideoAnalyser.PIX_FMT[0], vframes=length)
                .compile())

        result = None
        error_path = pathlib.Path(os.devnull)

        if config.STATS_ANALYSER_LOG:
            error_path = pathlib.Path("stats_analyser_log.txt")

        with open(error_path, 'w', encoding="UTF-8") as f_err:
            video_proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=f_err)
            result = self.read_and_analyse(video_proc)

        return result

    def read_and_analyse(self, video_proc):
        """
        read the frame and analyse them
            Args:
                video_proc (subprocess): ffmpeg process producing frames
            Retruns:
                (VideoIntensityStats)
        """
        bins = np.linspace(0, 256, 32)
        vid_statistics = VideoIntensityStats(bins)
        count = 0
        flag = True
        while flag:
            in_bytes = video_proc.stdout.read(self._video_data.get_frame_size())
            if not len(in_bytes) == 0:
                vid_statistics.append_frame(self.make_stats(in_bytes, bins))
                count += 1
                if count%10 == 0:
                    self.frames_analysed.emit(count)
            else:
                flag = False

        self.frames_analysed.emit(count)

        return vid_statistics

    @staticmethod
    def make_stats(image_bytes, bins):
        """
        make the statistics for a single frame
            Args:
                image_bytes (bytes): the image in raw bytes
                bins ([int]) the bins for counting
        """
        image = np.frombuffer(image_bytes, dtype=np.uint8)
        mean = np.mean(image)
        standard_deviation = np.std(image)
        count, _ = np.histogram(image, bins)

        return FrameStats(mean, standard_deviation, count)

    def get_number_frames(self):
        """
        get number of frames in video
        """
        return self._video_data.get_frame_count()
