## -*- coding: utf-8 -*-
"""
Created on Tuesday 31 Aug 2021

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
import ffmpeg
import subprocess
import pathlib
import tempfile
import itertools

import PyQt5.QtGui as qg

from cgt.io.ffmpegbase import FfmpegBase
from cgt.model.videoanalysisresultsstore import VideoAnalysisResultsStore

class RegionVideoCopy(FfmpegBase):
    """
    an object for copying videos of regions
    """

    ## the input pixel format
    IN_PIX_FMT = ('rgb24', 3)

    ## the output pixel format
    OUT_PIX_FMT = 'yuv420p'

    def __init__(self, file_name, results, parent=None):
        """
        set up the object
            Args:
                file_name (str): the path and name of video file
                results (VideoAnalysisResultsStore): the results
                parent (QObject): parent object
        """
        super().__init__(file_name, parent)

        ## pointer to the results object
        self._results = results

        ## the directory name of output
        self._dir_name = None

        ## the file name root for output
        self._name_root = "frame"

        ## the temporary directory that will hold images during production of video
        self._tmp_dir = None

        self.probe_video(file_name, 1, RegionVideoCopy.IN_PIX_FMT[1])

    def copy_region_videos(self, dir_name, base_name="region"):
        """
        copy each region to a seperate video file
            dir_name (str): the path to the directory
            base_name (str) the base name of the output files
        """
        self._dir_name = pathlib.Path(dir_name)
        length = self._video_data.get_frame_count()
        args = (ffmpeg
                .input(self.get_name())
                .output('pipe:', format='rawvideo', pix_fmt=RegionVideoCopy.IN_PIX_FMT[0], vframes=length)
                .compile())

        proc = subprocess.Popen(args, stdout=subprocess.PIPE)
        self.process_film(proc)

    def process_film(self, video_proc):
        """
        read one frame from the ffmpeg process
            video_proc (subprocess.Popen): the ffmpeg process
        """
        self.start_conversion()
        flag = True
        count = itertools.count()
        while flag:
            in_bytes = video_proc.stdout.read(self._video_data.get_frame_size())

            if not len(in_bytes) == 0:
                self.save_frame(in_bytes, next(count))
            else:
                flag = False

        self.finish_conversion()

    def start_conversion(self):
        """
        create the tmp directory for the images
        """
        self._tmp_dir = tempfile.TemporaryDirectory()

    def save_frame(self, in_bytes, frame_number):
        """
        save the region images in the frame
            Args:
                in_bytes (bytes): the raw frame
                frame_number (int): the frame number
        """
        name = f"{self._name_root}_{frame_number:0>4}.png"
        path = pathlib.Path(self._tmp_dir.name)
        file_path = path.joinpath(name)
        self.make_and_save_image(in_bytes, str(file_path))

    def finish_conversion(self):
        """
        combine the region images into videos, clear and remove the tmp directory
        """
        name = f"{self._name_root}_%04d.png"
        path = pathlib.Path(self._tmp_dir.name)
        file_path = path.joinpath(name)

        command = (ffmpeg
                    .input(file_path, framerate=8)
                    .output("out_file.mp4", pix_fmt=RegionVideoCopy.OUT_PIX_FMT))
        command.run()

        self._tmp_dir.cleanup()

    def make_and_save_image(self, image_bytes, file_path):
        """
        convert bytes and save to image file (file type determined by postfix .jpg .png)
            Args:
                image_bytes (bytes): bytes read from file
                file_path (str): path and file name for output
        """
        im_format = qg.QImage.Format_RGB888

        image = qg.QImage(image_bytes,
                          self._video_data.get_width(),
                          self._video_data.get_height(),
                          self._video_data.get_bytes_per_line(),
                          im_format)

        image.save(file_path)
