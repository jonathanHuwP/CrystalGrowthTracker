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

import cv2
import PyQt5.QtCore as qc
import PyQt5.QtGui as qg

from cgt.util.utils import nparray_to_qimage

class VideoBuffer(qc.QObject):
    """
    a video reader that is designed to run as a seperate thread
    from the display object, allowing smoother animation, once started
    the object will spin on the queue of requests, if requests exist
    they will be popped and video display object called to dispaly the
    resultant image.
    """
    
    ## signal that a frame is ready to display
    display_image = qc.pyqtSignal(qg.QPixmap, int)
    
    def __init__(self, path, region_view):
        """
        initalize by usng opencv opening the video file

            Args:
                path (string) the path to the video file
                region_view (qwidget) the viewer for the video
        """
        super().__init__()
        
        ## initiaize the file video stream
        self._video_reader = cv2.VideoCapture(str(path))
        
        ## cache the length
        self._length = int(self._video_reader.get(cv2.CAP_PROP_FRAME_COUNT))

        ## pointer to the region view
        self._region_view = region_view

    def get_length(self):
        """
        get the numer of frames in the video file, the maximum 
        accepted frame number is this minus 1

            Returns:
                the number of frames (int)
        """
        return self._length

    @qc.pyqtSlot()
    def make_frames(self):
        """
        pop the frame numbers form the queue and convert
        to qpixmaps and call display_pixmap on parent object

            Returns:
                None
        """
        while True:
            if not self._region_view.get_frame_queue().is_empty():
                self.make_frame()

    def make_frame(self):
        """
        pop the frame numbers queue, get the frame, convert it
        to a qpixmap and call the display_pixmap function of regions view

            Returns:
                None
        """
        frame = self._region_view.get_frame_queue().pop()

        self._video_reader.set(cv2.CAP_PROP_POS_FRAMES, frame)
        flag, img = self._video_reader.read()

        if not flag:
            message = f"failed to read image for frame {frame}"
            raise ValueError(message)

        # convert to Qt cv2 produces image in green/red/blue
        image = nparray_to_qimage(img, True)
 
        # call the region viewing object with the image and frame
        self.display_image.emit(qg.QPixmap.fromImage(image), frame)
