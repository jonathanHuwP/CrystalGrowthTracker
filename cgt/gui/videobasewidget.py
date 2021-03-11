# -*- coding: utf-8 -*-
"""
Created on Thur 11 Feb 2021

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
# pylint: disable = import-error

from enum import Enum

import PyQt5.QtWidgets as qw
import PyQt5.QtGui as qg
import PyQt5.QtCore as qc
import PyQt5.Qt as qt

class PlayStates(Enum):
    """
    enumeration of video playing states
    """
    MANUAL        = 1
    PLAY_FORWARD  = 2
    PLAY_BACKWARD = 3

class VideoBaseWidget(qw.QWidget):
    """
    The implementation of the GUI, all the functions and
    data-structures required to implement the intended behaviour
    """
    ## signal that a frame is required
    request_frame = qc.pyqtSignal(int)

    ## signal that the queue should be cleared
    clear_queue = qc.pyqtSignal()

    def __init__(self, parent=None):
        """
        the object initalization function

            Args:
                parent (QWidget): the parent widget
        """
        super().__init__(parent)

        ## the holder of the results data
        self._video_source = None

        ## state variable determines if video is playing
        self._playing = PlayStates.MANUAL

        ## the current image
        self._current_image = None

        ## the currently displayed frame
        self._current_frame = 0

        ## the current value of the zoom
        self._current_zoom = 1.0

    def setEnabled(self, enabled):
        """
        enable/disable widget on enable the source
        is connected on disable play is paused
        """
        if enabled and self._video_source is not None:
            super().setEnabled(True)
            self._video_source.connect_viewer(self)
            self.redisplay()
        elif not enabled:
            super().setEnabled(False)
            self.play_pause()

    def setup_video_widget(self):
        """
        setup featuers that require a complete
        widget and so cannot be done in __init__
        """
        font = qg.QFont( "Monospace", 10, qg.QFont.DemiBold)
        self._frameLabel.setFont(font)
        self.connect_controls()

    def set_video_source(self, video_source):
        """
        setter for the buffer to the video
            video_source (VideoSource): a source of video frames
        """
        self._video_source = video_source
        self._videoControl.set_range(video_source.get_length())

    def redisplay(self):
        """
        get and redisplay the current frame
        """
        self.post_request_frame(self._current_frame)

    def connect_controls(self):
        """
        connect the video controls to self
        """
        self._videoControl.zoom_value.connect(self.zoom_value)
        self._videoControl.frame_changed.connect(self.request_frame)
        self._videoControl.start_end.connect(self.start_end)
        self._videoControl.one_frame_forward.connect(self.step_forward)
        self._videoControl.one_frame_backward.connect(self.step_backward)
        self._videoControl.pause .connect(self.play_pause)
        self._videoControl.forwards.connect(self.play_forward)
        self._videoControl.backwards.connect(self.play_backward)

    def is_playing(self):
        """
        getter for the playing status
            Returns:
                True if the widget is playing video else False
        """
        if self._playing == PlayStates.MANUAL:
            return False

        return True

    @qc.pyqtSlot(qg.QPixmap, int)
    def display_image(self, pixmap, frame_number):
        """
        display an image, the image must be a pixmap so that
        it can safely be recieved from another thread
            Args:
                pixmap (QPixmap) the image in pixmap form
                frame_number
        """
        self._current_image = qg.QImage(pixmap)
        self._current_frame = frame_number
        self._videoControl.set_frame_currently_displayed(frame_number)

        self.display()

    def apply_zoom_to_image(self, image):
        """
        apply the current zoom to an image
            Args:
                image (Qimage) the image to be resized
            Returns
                Qimage resized by current zoom
        """
        height = image.height()*self._current_zoom
        width = image.width()*self._current_zoom

        transform = qt.Qt.SmoothTransformation
        if self._videoControl.use_fast_transform():
            transform = qt.Qt.FastTransformation

        return image.scaled(width, height, transformMode=transform)

    @qc.pyqtSlot(bool)
    def start_end(self, end):
        """
        jump to the start or end of the video
            Args:
                end (bool) if true jump to end else start
        """
        if end:
            self.post_request_frame(self._video_source.get_length()-1)
        else:
            self.post_request_frame(0)

    @qc.pyqtSlot(int)
    def post_request_frame(self, frame_number):
        """
        a specific frame should be displayed
        """
        self.request_frame.emit(frame_number)

    @qc.pyqtSlot(float)
    def zoom_value(self, value):
        """
        a new value for the zoom has been entered
        """
        self._current_zoom = value
        if self._create_label is not None:
            self._create_label.set_zoom(value)
        elif self._edit_label is not None:
            self._edit_label.set_zoom(value)
        elif self._display_label is not None:
            self._display_label.set_zoom(value)
        elif self._delete_label is not None:
            self._delete_label.set_zoom(value)

        self.display()

    @qc.pyqtSlot()
    def step_forward(self):
        """
        advance by one frame
        """
        frame = self._current_frame + 1
        if frame < self._video_source.get_length():
            self.post_request_frame(frame)

    @qc.pyqtSlot()
    def step_backward(self):
        """
        reverse by one frame
        """
        frame = self._current_frame - 1
        if frame >= 0:
            self.post_request_frame(frame)

    @qc.pyqtSlot()
    def play_pause(self):
        """
        pause the playing
        """
        self.clear_queue.emit()
        self._playing = PlayStates.MANUAL
        self._videoControl.enable_fine_controls()

    @qc.pyqtSlot()
    def play_forward(self):
        """
        start playing forward
        """
        self.clear_queue.emit()
        self._playing = PlayStates.PLAY_FORWARD
        self.post_request_frame((self._current_frame+1)%self._video_source.get_length())

    @qc.pyqtSlot()
    def play_backward(self):
        """
        start playing in reverse
        """
        self.clear_queue.emit()
        self._playing = PlayStates.PLAY_BACKWARD
        self.post_request_frame((self._current_frame-1)%self._video_source.get_length())

    def get_data(self):
        """
        get the data store
            Returns:
                pointer to data (SimulatedDataStore)
        """
        return self._video_source

    def get_image_copy(self):
        """
        get the current main image
            Returns:
                deep copy of current image (QImage)
        """
        return self._current_image.copy()

    def clear(self):
        """
        reset to initial conditions
        """
        self._video_source = None
        self._playing = PlayStates.MANUAL
        self._current_image = None
        self._current_frame = 0
        self._current_zoom = 1.0
        self._videoControl.clear()
