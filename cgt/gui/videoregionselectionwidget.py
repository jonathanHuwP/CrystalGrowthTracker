# -*- coding: utf-8 -*-
"""
Created on Wed 03 Feb 2020

this widget allow the user to select regions in a video

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
# pylint: disable = no-name-in-module
# pylint: disable = import-error

import PyQt5.QtWidgets as qw
import PyQt5.QtGui as qg
import PyQt5.QtCore as qc
from queue import Queue

from cgt.io.videobuffer import VideoBuffer

# import UI
from cgt.gui.Ui_videoregionselectionwidget import Ui_VideoRegionSelectionWidget

class VideoRegionSelectionWidget(qw.QWidget, Ui_VideoRegionSelectionWidget):
    """
    The implementation of the GUI, all the functions and
    data-structures required to implement the intended behaviour
    """

    def __init__(self, video_file, parent=None):
        """
        the object initalization function

            Args:
                video_file (string) the name of the file holding the video
                parent (QObject): the parent QObject for this window

            Returns:
                None
        """
        super().__init__(parent)
        self.setupUi(self)
        
        ## the frame queue
        self._frame_queue = Queue(256)
        
        ## the current image
        self._current_image = None
        
        ## the currently displayed frame
        self._current_frame = None
        
        ## the current value of the zoom
        self._current_zoom = 1.0

        ## the player 
        self._source = VideoBuffer(video_file, self, self)

        ## label for displaying the video
        self._source_label = qw.QLabel()

        self._source_label.setAlignment(qc.Qt.AlignTop | qc.Qt.AlignLeft)
        self._source_label.setSizePolicy(qw.QSizePolicy.Fixed,
                                         qw.QSizePolicy.Fixed)
        self._source_label.setMargin(0)

        self._videoScrollArea.setWidget(self._source_label)
        
        self.connect_controls()
        self.request_frame(0)
        self._source.start()
        
    def connect_controls(self):
        """
        connect the video controls to self
        """
        self._videoControl.zoom_value.connect(self.zoom_value)
        self._videoControl.frame_changed.connect(self.request_frame)
        self._videoControl.frame_step.connect(self.frame_step)
        self._videoControl.start_end.connect(self.start_end)

        #stop = qc.pyqtSignal()
        #forward = qc.pyqtSignal()
        #reverse = qc.pyqtSignal()
        
    def get_frame_queue(self):
        """
        getter for the frame queue
            Returns:
                pointer to the frame queue
        """
        return self._frame_queue
        
    def display_image(self, image, frame_number):
        """
        display an image
            Args:
                image (QImage) the image 
                frame_number
        """
        print(f"VRW: diplay {type(image)} {frame_number}")
        self._current_image = image
        self._current_frame = frame_number
        
        self.display()
        
    def display(self):
        """
        display the current image
            Returns:
                None
        """
        if self._current_image is None or self.isHidden():
            return

        height = self._current_image.height()*self._current_zoom
        width = self._current_image.width()*self._current_zoom
        tmp = self._current_image.scaled(width, height)

        self._source_label.setPixmap(qg.QPixmap(tmp))
        
        message = "Frame {:d} of {:d}, approx {:.2f} seconds"
        #time, _ = self.get_current_video_time()
        message = message.format(self._current_frame+1,
                                 self._source.length(),
                                 0.0)                         
        self._frameLabel.setText(message)

    @qc.pyqtSlot(bool)
    def start_end(self, end):
        """
        jump to the start or end of the video
            Args:
                end (bool) if true jump to end else start
        """
        print(f"VRW start_end start={end}")
        if end:
            self.request_frame(self._source.length()-1)
        else:
            self.request_frame(0)
        
    @qc.pyqtSlot(bool)
    def frame_step(self, forward):
        """
        move one frame
            Args:
                forward (bool) if true move forward else back
        """
        print(f"VRW frame_step forward={forward}")
        
        if forward:
            if self._current_frame <self._source.length():
                self.request_frame(self._current_frame+1)
        else:
            if self._current_frame > 0:
                self.request_frame(self._current_frame-1)
        
    @qc.pyqtSlot(int)
    def request_frame(self, frame_number):
        """
        a specific frame should be displayed
        """
        print(f"VRW request frame {frame_number}")
        self._frame_queue.put(frame_number)
        
    @qc.pyqtSlot(float)
    def zoom_value(self, value):
        """
        a new value for the zoom has been entered
        """
        print(f"VRW zoom_value {value}")
        self._current_zoom = value
        self.display()
