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

class PlayStates(Enum):
    """
    enumeration of video playing states
    """
    ## use fine stepping controls
    MANUAL        = 1

    ## continusly play forward
    PLAY_FORWARD  = 2

    ## continusly play backward
    PLAY_BACKWARD = 3

class VideoBaseWidget(qw.QWidget):
    """
    The implementation of the GUI, all the functions and
    data-structures required to implement the intended behaviour
    """

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
        self._current_pixmap = None

        ## the currently displayed frame
        self._current_time = 0.0

        ## the current value of the zoom
        self._current_zoom = 1.0

    def enable(self, enabled):
        """
        enable/disable widget on disable play is paused
            Args:
                enabled (bool):  enable else, disable
        """
        super().setEnabled(enabled)
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
        self._videoControl.set_range(video_source.get_video_data().get_time_duration_user())

    def display_frame_at(self, time):
        """
        display a given time (ffmpeg closest frame to time)
            Args:
                time (float): the time of the frame to display (user FPS)
        """
        pixmap = self._video_source.get_pixmap_user(time)
        self.display_image(pixmap, time)

    def redisplay(self):
        """
        get and redisplay the current frame
        """
        self.display_frame_at(self._current_time)

    def connect_controls(self):
        """
        connect the video controls to self
        """
        self._videoControl.zoom_value.connect(self.zoom_value)
        self._videoControl.time_changed.connect(self.display_frame_at)
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
    def display_image(self, pixmap, time):
        """
        display an image, the image must be a pixmap so that
        it can safely be recieved from another thread
            Args:
                pixmap (QPixmap) the image in pixmap form
                time (float): time of frame
        """
        self._current_pixmap = pixmap
        self._current_time = time
        self._videoControl.set_time_currently_displayed(time)

        self.display()
        self.display_extra()

    def display(self):
        """
        display an image, the image must be a pixmap so that
        it can safely be recieved from another thread
        """
        import time
        if self._current_pixmap is None or self.isHidden():
            return

        self._graphicsView.set_pixmap(self._current_pixmap, self._current_time)

        # update the controls
        self._videoControl.set_slider_value(self._current_time)

        # display the current time
        length = self._video_source.get_video_data().get_time_duration_user()
        message = f"Time {self._current_time:0>5.1f} of {length:0>5.1f}"
        self._frameLabel.setText(message)

        delay = self._video_source.get_video_data().get_user_time_step()
        qc.QTimer.singleShot(delay, self.next_pixmap)

    qc.pyqtSlot()
    def next_pixmap(self):
        """
        if in play forwards or backwards get next
        """
        if self._playing == PlayStates.PLAY_FORWARD:
            self.next_pixmap_forwards()
        elif self._playing == PlayStates.PLAY_BACKWARD:
            self.next_pixmap_backwards()

    def next_pixmap_forwards(self):
        """
        in play forwards mode next frame
        """
        data = self._video_source.get_video_data()
        next_frame = data.next_user_time(self._current_time)
        self.display_frame_at(next_frame)

    def next_pixmap_backwards(self):
        """
        in play backwards mode next frame
        """
        data = self._video_source.get_video_data()
        next_frame = data.previous_user_time(self._current_time)
        self.display_frame_at(next_frame)

    def display_extra(self):
        """
        location for additional code beyond displaying the video label
        """
        pass

    @qc.pyqtSlot(bool)
    def start_end(self, end):
        """
        jump to the start or end of the video
            Args:
                end (bool) if true jump to end else start
        """
        data = self._video_source.get_video_data()
        if end:
            self.display_frame_at(data.get_time_duration_user())
        else:
            self.display_frame_at(0.0)

    @qc.pyqtSlot(float)
    def zoom_value(self, value):
        """
        a new value for the zoom has been entered
        """
        self._graphicsView.set_zoom(value)
        self._current_zoom = value

    @qc.pyqtSlot()
    def step_forward(self):
        """
        advance by one frame
        """
        data = self._video_source.get_video_data()
        time = data.next_user_time(self._current_time)
        self.display_frame_at(time)

    @qc.pyqtSlot()
    def step_backward(self):
        """
        reverse by one frame
        """
        data = self._video_source.get_video_data()
        time = data.previous_user_time(self._current_time)
        self.display_frame_at(time)

    @qc.pyqtSlot()
    def play_pause(self):
        """
        pause the playing
        """
        self._playing = PlayStates.MANUAL
        self._videoControl.enable_fine_controls()

    @qc.pyqtSlot()
    def play_forward(self):
        """
        start playing forward
        """
        self._playing = PlayStates.PLAY_FORWARD
        pixmap, time = self._video_source.get_next_pixmap_user(self._current_time)
        self.display_image(pixmap, time)

    @qc.pyqtSlot()
    def play_backward(self):
        """
        start playing in reverse
        """
        self._playing = PlayStates.PLAY_BACKWARD
        pixmap, time = self._video_source.get_previous_pixmap_user(self._current_time)
        self.display_image(pixmap, time)

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
        return self._current_pixmap.copy()

    def clear(self):
        """
        reset to initial conditions
        """
        self._video_source = None
        self._playing = PlayStates.MANUAL
        self._current_pixmap = None
        self._current_time = 0
        self.zoom_value(1.0)
        self._videoControl.clear()
