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
import PyQt5.QtGui as qg
import cv2 as cv

from cgt.model.region import Region

class VideoBuffer:
    """
    a video reader that is designed to run as a seperate thread
    from the display object, allowing smoother animation
    """
    def __init__(self, path, parent, region_view, drawing_view):
        """
        initalize by usng opencv opening the video file

            Args:
                path (string) the path to the video file
                parent (object) callback target which must have display_pixmap function
                region_view (qwidget) the viewer for the video
                drawing_view (qwidget) the viewer for the crystals
        """
        ## initiaize the file video stream
        self._video_reader = cv.VideoCapture(path)

        ## pointr to the parent
        self._parent = parent

        ## pointer to the region view
        self._region_view = region_view

        ## pointer to the drawing view
        self._drawing_view = drawing_view

    def length(self):
        """
        get the numer of frames in the video file

            Returns:
                the number of frames (int)
        """
        return int(self._video_reader.get(cv.CAP_PROP_FRAME_COUNT))-1

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
            if self._parent.active_tab() == 1:
                if not self._parent.video_queue().empty():
                    self.make_frame()
            elif self._parent.active_tab() == 1:
                if not self._parent.drawing_queue().empty():
                    self.make_region()

    def make_region(self):
        """
        pop the regions queue, get the frame and region, convert them
        to a qpixmap and call the display_pixmap function of drawing view

            Returns:
                None
        """
        tmp = self._parent.drawing_queue().get()
        frame = tmp[0]
        region = tmp[1]

        self._video_reader.set(cv.CAP_PROP_POS_FRAMES, frame)
        flag, img = self._video_reader.read()

        if not flag:
            message = f"failed to read image for frame {frame}"
            raise ValueError(message)

        img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        # TODO add region crop
        image = qg.QImage(
            img.data,
            img.shape[1],
            img.shape[0],
            3*img.shape[1],
            qg.QImage.Format_RGB888)

        pixmap = qg.QPixmap.fromImage(image)

        self._region_view.display_pixmap(pixmap)

    def make_frame(self):
        """
        pop the frame numbers queue, get the frame, convert it
        to a qpixmap and call the display_pixmap function of regions view

            Returns:
                None
        """
        frame = self._parent.video_queue().get()

        self._video_reader.set(cv.CAP_PROP_POS_FRAMES, frame)
        flag, img = self._video_reader.read()

        if not flag:
            message = f"failed to read image for frame {frame}"
            raise ValueError(message)

        img = cv.cvtColor(img, cv.COLOR_BGR2RGB)

        image = qg.QImage(
            img.data,
            img.shape[1],
            img.shape[0],
            3*img.shape[1],
            qg.QImage.Format_RGB888)

        pixmap = qg.QPixmap.fromImage(image)

        self._region_view.display_pixmap(pixmap, frame)
