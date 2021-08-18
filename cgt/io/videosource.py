## -*- coding: utf-8 -*-
"""
Created on Thur Mar 04 2021

This module contains the top level graphical user interface for measuring the
growth rates of crystals observed in videos taken using an X-ray synchrotron source

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

import PyQt5.QtCore as qc
import PyQt5.QtGui as qg

import ffmpeg
import subprocess

from cgt.io.videodata import VideoData

class VideoSource(qc.QObject):
    """
    a source of images from a video file, it will run
    a reader in a seperate thread.
    """
    ## signal that a frame is ready to display
    display_image = qc.pyqtSignal(qg.QPixmap, int)

    ## the pixel format and number of bytes
    PIX_FMT = ('rgb24', 3)

    def __init__(self, file_name, user_frame_rate=None):
        """
        set up the object
            Args:
                file_name (str): the path and name of video file
                user_frame_rate (int): the frame rate provided by user
        """
        super().__init__()

        ## file name
        self._file_name = file_name

        ## video data
        self._video_data = None

        self.probe_video(file_name, user_frame_rate)

    def probe_video(self, file_path, user_frame_rate):
        """
        load a video file
            Args:
                file_path (string) the file
                user_frame_rate (int): the frame rate provided by user
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

        self._video_data = VideoData(frame_data, frame_rates, VideoSource.PIX_FMT[1])

    def get_pixmap(self, time):
        """
        getter for the pixmap at a given time (user frame rate):
            Args:
                time (float): the time in video internal time
            Returns:
                (QPixmap): the frame
        """
        args = (ffmpeg
                .input(self._file_name, ss=time)
                .output('pipe:', format='rawvideo', pix_fmt=VideoSource.PIX_FMT[0], vframes=1)
                .compile())

        in_bytes = 0
        # create ffmpeg process with piped output and read output
        with subprocess.Popen(args, stdout=subprocess.PIPE) as process:
            in_bytes = process.stdout.read(self._video_data.get_frame_size())

        if not in_bytes == 0:
            return self.make_pixmap(in_bytes)

        return None

    def make_pixmap(self, image_bytes):
        """
        convert bytes to QPixmap
            Args:
                image_bytes (bytes): bytes read from file
            Returns:
                (QPixmap): the pixmap
        """
        im_format = qg.QImage.Format_RGB888

        image = qg.QImage(image_bytes,
                          self._video_data.get_width(),
                          self._video_data.get_height(),
                          self._video_data.get_bytes_per_line(),
                          im_format)

        return qg.QPixmap.fromImage(image)

    def get_length(self):
        """
        getter for the duration of video, user defined, in seconds
        """
        if self._video_data is not None:
            return self._video_data.get_time_duration_actual()

        return 0.0
