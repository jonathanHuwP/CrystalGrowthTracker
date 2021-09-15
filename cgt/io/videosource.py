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
import os
import pathlib

from cgt.io.ffmpegbase import FfmpegBase

class VideoSource(FfmpegBase):
    """
    a source of images from a video file, it will run
    a reader in a seperate thread.
    """
    ## signal that a frame is ready to display
    display_image = qc.pyqtSignal(qg.QPixmap, int)

    ## the pixel format and number of bytes
    PIX_FMT = ('rgb24', 3)

    def __init__(self, file_name, user_frame_rate, parent=None, logs=False):
        """
        set up the object
            Args:
                file_name (str): the path and name of video file
                user_frame_rate (int): the frame rate provided by user
                parent (QObject): parent object
                logs (bool): if true save ffmpeg log to file, else devnull
        """
        super().__init__(file_name, parent)

        ## logging flag
        self._logs = logs

        self.probe_video(user_frame_rate, VideoSource.PIX_FMT[1])

    def get_pixmap(self, frame):
        """
        get the pixmap for the frame
            Args:
                frame (int): the time in user fps
            Returns:
                (QPixmap, float): the qixmap and the associated time
        """
        time = self._video_data.frame_to_internal_time(frame)
        return self.get_pixmap_at(time)

    def get_pixmap_at(self, time):
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

        # make path for ffmpeg's logs
        error_path = pathlib.Path(os.devnull)
        if self._logs:
            error_path = pathlib.Path("ffmpeg_log.txt")

        # create ffmpeg process with piped output and read output
        with error_path.open('a') as f_err:
            with subprocess.Popen(args, stdout=subprocess.PIPE, stderr=f_err) as process:
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

    def get_video_data(self):
        """
        getter for the duration of video, user defined, in seconds
        """
        return self._video_data
