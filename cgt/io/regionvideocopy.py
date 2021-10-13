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
import os

import PyQt5.QtGui as qg

from cgt.io.ffmpegbase import FfmpegBase
from cgt.util.scenegraphitems import get_rect_even_dimensions

class RegionVideoCopy(FfmpegBase):
    """
    an object for copying videos of regions
    """

    ## the input pixel format
    IN_PIX_FMT = ('rgb24', 3)

    ## the output pixel format
    OUT_PIX_FMT = 'yuv420p'

    def __init__(self, project, parent=None):
        """
        set up the object
            Args:
                file_name (str): the path and name of video file
                project (CGTProject): the project holding results
                parent (QObject): parent object
        """
        super().__init__(project["enhanced_video"], parent)

        ## pointer to the project object
        self._project = project

        ## the directory name of output
        self._dir_name = None

        ## the file name root for output
        self._name_root = "region"

        ## the temporary directory that will hold images during production of video
        self._tmp_dir = None

        self.probe_video(1, RegionVideoCopy.IN_PIX_FMT[1])

    def copy_region_videos(self, dir_name):
        """
        copy each region to a seperate video file
            dir_name (str): the path to the directory
        """
        self._dir_name = pathlib.Path(dir_name)
        length = self._video_data.get_frame_count()
        args = (ffmpeg
                .input(self.get_name())
                .output('pipe:', format='rawvideo', pix_fmt=RegionVideoCopy.IN_PIX_FMT[0], vframes=length)
                .compile())

        with open(os.devnull, 'w') as f_err:
            with subprocess.Popen(args, stdout=subprocess.PIPE, stderr=f_err) as proc:
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
        regions = self._project["results"].get_regions()
        frame = f"_{frame_number:0>4}.png"
        image = self.make_image(in_bytes)
        for i, region in enumerate(regions):
            name = f"{self._name_root}_{i}{frame}"
            file_path = pathlib.Path(self._tmp_dir.name).joinpath(name)
            out_image = image.copy(get_rect_even_dimensions(region))
            out_image.save(str(file_path))

    def finish_conversion(self):
        """
        combine the region images into videos, clear and remove the tmp directory
        """
        regions = self._project["results"].get_regions()
        frame = "_%04d.png"
        fps = int(self._project['frame_rate'])

        for i in range(len(regions)):
            name = f"{self._name_root}_{i}{frame}"
            frames_path = pathlib.Path(self._tmp_dir.name).joinpath(name)
            out_file = f"{self._name_root}_{i}.mp4"
            out_path = pathlib.Path(self._dir_name).joinpath(out_file)

            if out_path.exists():
                out_path.unlink()

            command = (ffmpeg
                       .input(str(frames_path), framerate=fps)
                       .output(str(out_path), pix_fmt=RegionVideoCopy.OUT_PIX_FMT))
            command.run(capture_stderr=True)

        self._tmp_dir.cleanup()

    def make_image(self, image_bytes):
        """
        convert bytes and save to image file (file type determined by postfix .jpg .png)
            Args:
                image_bytes (bytes): bytes read from file
        """
        im_format = qg.QImage.Format_RGB888

        image = qg.QImage(image_bytes,
                          self._video_data.get_width(),
                          self._video_data.get_height(),
                          self._video_data.get_bytes_per_line(),
                          im_format)

        return image
