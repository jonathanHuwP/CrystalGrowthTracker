## -*- coding: utf-8 -*-
"""
Created on  Mon 04 Jan 2021

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

from threading import Thread
import cv2
import PyQt5.QtGui as qg
import PyQt5.QtCore as qc

from cgt.model.region import Region
from cgt.util.utils import nparray_to_qimage

class VideoBuffer:
    """
    a video reader that is designed to run as a seperate thread
    from the display object, allowing smoother animation, once started
    the object will spin on the queue of requests, if requests exist
    they will be popped and video display object called to dispaly the
    resultant image.
    """
    def __init__(self, path, parent, region_view):
        """
        initalize by usng opencv opening the video file

            Args:
                path (string) the path to the video file
                parent (object) callback target which must have display_pixmap function
                region_view (qwidget) the viewer for the video
        """
        ## initiaize the file video stream
        self._video_reader = cv2.VideoCapture(str(path))

        ## pointr to the parent
        self._parent = parent

        ## pointer to the region view
        self._region_view = region_view

    def length(self):
        """
        get the numer of frames in the video file

            Returns:
                the number of frames (int)
        """
        return int(self._video_reader.get(cv2.CAP_PROP_FRAME_COUNT))-1

    def start(self):
        """
        start the thread

            Returns:
                None
        """
        thread = Thread(target=self.make_frames, args=())
        thread.daemon = True
        thread.start()

    def make_frames(self):
        """
        pop the frame numbers form the queue and convert
        to qpixmaps and call display_pixmap on parent object

            Returns:
                None
        """
        while True:
            if not self._parent.get_frame_queue().empty():
                self.make_frame()

    def make_frame(self):
        """
        pop the frame numbers queue, get the frame, convert it
        to a qpixmap and call the display_pixmap function of regions view

            Returns:
                None
        """
        frame = self._parent.get_frame_queue().get()

        self._video_reader.set(cv2.CAP_PROP_POS_FRAMES, frame)
        flag, img = self._video_reader.read()

        if not flag:
            message = f"failed to read image for frame {frame}"
            raise ValueError(message)

        # convert to Qt cv2 produces image in green/red/blue
        image = nparray_to_qimage(img, True)

        # call the region viewing object with the image and frame
        self._region_view.display_image(image, frame)
