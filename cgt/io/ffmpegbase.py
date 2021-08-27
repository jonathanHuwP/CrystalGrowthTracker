## -*- coding: utf-8 -*-
"""
Created on Fri Aug 27 2021

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
# pylint: disable = too-many-public-methods
# pylint: disable = too-many-instance-attributes
# pylint: disable = c-extension-no-member
# pylint: disable = import-error

import ffmpeg
import PyQt5.QtCore as qc

from cgt.io.videodata import VideoData

class FfmpegBase(qc.QObject):
    """
    base class for video reader, holds file name, user frame rate and video data
    """

    def __init__(self, file_name, parent=None):
        """
        set up the object
            Args:
                file_name (str): the path and name of video file
                parent (QObject): parent object
        """
        super().__init__(parent)

        ## file name
        self._file_name = file_name

        ## video data
        self._video_data = None

    def probe_video(self, file_path, user_frame_rate, bytes_per_pixel):
        """
        open video file and read data
            Args:
                file_path (string) the file
                user_frame_rate (int): the frame rate provided by user
                bytes_per_pixel (int): the numbe of bytes per pixel
            Throws:
                 (ffmpeg.Error): can't probe video
                 (StopIteration): problem with information in video
                 (KeyError): problem with information in video
        """
        probe = ffmpeg.probe(file_path)
        video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')

        print("Video Data\n========")
        for key in video_info.keys():
            print(f"\t{key} => {video_info[key]} {type(video_info[key])}")
        print("\n")

        frame_data = [video_info["width"], video_info["height"], video_info["duration_ts"]]

        parts = video_info["r_frame_rate"].split('/')
        frame_rate_codec = float(parts[0])/float(parts[1])
        frame_rates = []
        if user_frame_rate is None:
            frame_rates.append(frame_rate_codec)
        else:
            frame_rates.append(user_frame_rate)

        frame_rates.append(frame_rate_codec)

        self._video_data = VideoData(frame_data, frame_rates, bytes_per_pixel)

    def get_video_data(self):
        """
        getter for the video data, return None in file has not been probed
        """
        return self._video_data
