## -*- coding: utf-8 -*-
"""
Created on Tue Oct 19 2021

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
# set up linting
# pylint: disable = c-extension-no-member

import pathlib
import tempfile
import ffmpeg

import PyQt5.QtGui as qg
import PyQt5.QtCore as qc
import PyQt5.Qt as qt

def draw_image(tmp_path, number, size):
    """
    draw and save an image of a square centered in 500, 500 pixels
        Args:
            tmp_path (pathlib.Path): path to the directory
            number (int): frame number
            size (float): size in pixels
    """
    start = 250.0 - (size/2.0)
    image =  qg.QImage(500, 500, qg.QImage.Format_ARGB32)
    image.fill(qc.Qt.white)

    painter = qg.QPainter()
    brush = qt.QBrush(qt.Qt.black)

    painter.begin(image)
    painter.setPen(qt.QPen(brush, 3, qt.Qt.SolidLine))
    painter.drawRect(qc.QRectF(start, start, size, size))
    painter.end()

    path = tmp_path.joinpath(f"frame{number:0>4}.png")
    image.save(str(path))

def save_video(tmp_path, fps, silent=True):
    """
    combine the region images into videos
        Args:
            tmp_path (pathlib.Path): the directory holding frames
            fps (int): the number of frames per second
            silent (bool): if true ffmpeg error output is not printed
    """
    frames_path = tmp_path.joinpath("frame%04d.png")
    out_file = "test_video.mp4"

    command = (ffmpeg
               .input(str(frames_path), framerate=fps)
               .output(out_file, pix_fmt='yuv420p'))

    command.run(capture_stderr=silent)

def make_stills(tmp_path, frame_count):
    """
    draw the animation images
        Args:
            tmp_path (pathlib.Path): the path to the directory
            frame_count (int): the number of frames
    """
    for i in range(frame_count):
        draw_image(tmp_path, i, i*5.0)

def main():
    """
    run everything
    """
    frame_count = 75
    frames_per_second = 5
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = pathlib.Path(tmp_dir)
        make_stills(tmp_path, frame_count)
        save_video(tmp_path, frames_per_second)

if __name__ == "__main__":
    main()
