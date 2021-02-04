# -*- coding: utf-8 -*-
"""
Created on Tue September 09 2020

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

This work was funded by Joanna Leng's EPSRC funded RSE Fellowship (EP/R025819/1)

@copyright 2020
@author: j.h.pickering@leeds.ac.uk and j.leng@leeds.ac.uk
"""

# set up linting condition
# pylint: disable = c-extension-no-member
# pylint: disable = import-error
# pylint: disable = f-string-without-interpolation

import PyQt5.QtWidgets as qw
import PyQt5.QtCore as qc

from cgt.gui.Ui_cgtvideocontrols import Ui_CGTVideoControls

class CGTVideoControls(qw.QWidget, Ui_CGTVideoControls):
    """
    a widget providing a basic forward backward control for a video
    """

    ## the zoom has been changed
    zoom_value = qc.pyqtSignal(float)

    ## signal to indicate change of frame
    frame_changed = qc.pyqtSignal(int)

    ## signal to indicate a one step move, forward if parameter = true
    frame_step = qc.pyqtSignal(bool)

    ## signal for start/end of video, start if parameter = true
    start_end = qc.pyqtSignal(bool)

    ## signal to stop video play
    stop = qc.pyqtSignal()

    ## signal for play forward
    forward = qc.pyqtSignal()

    ## signal for play reverse
    reverse = qc.pyqtSignal()

    def __init__(self, parent=None):
        """
        set up the dialog

            Args:
                parent (QObject) the parent object

            Returns:
                None
        """
        super().__init__(parent)
        self.setupUi(self)

        # set up the buttons
        style = qw.QCommonStyle()
        self._forwardButton.setIcon(style.standardIcon(style.SP_MediaSeekForward))
        self._reverseButton.setIcon(style.standardIcon(style.SP_MediaSeekBackward))
        self._lastFrameButton.setIcon(style.standardIcon(style.SP_MediaSkipForward))
        self._firstFrameButton.setIcon(style.standardIcon(style.SP_MediaSkipBackward))
        self._startStopButton.setIcon(style.standardIcon(style.SP_MediaStop))
        self._stepUpButton.setIcon(style.standardIcon(style.SP_ArrowForward))
        self._stepDownButton.setIcon(style.standardIcon(style.SP_ArrowBack))

    @qc.pyqtSlot(float)
    def zoom_changed(self, zoom):
        """
        callback for the changing the zoom
            Args:
                zoom (float) the new zoom
            Returns:
                None
        """
        print(f"VidControls: zoom_changed {zoom}")
        self.zoom_value.emit(zoom)

    @qc.pyqtSlot()
    def slider_released(self):
        """
        respond to the release of the slider
        """
        print(f"VidControls: slider_released {self._frameSlider.value()}")
        self.frame_changed.emit(self._frameSlider.value())

    @qc.pyqtSlot()
    def step_up(self):
        """
        one frame down
        """
        print(f"VidControls: step_up")
        self.frame_step.emit(True)

    @qc.pyqtSlot()
    def step_down(self):
        """
        one frame up
        """
        print(f"VidControls: step_down")
        self.frame_step.emit(False)

    @qc.pyqtSlot()
    def first_frame(self):
        """
        jump to first frame
        """
        print(f"VidControls: first_frame")
        self.start_end.emit(True)

    @qc.pyqtSlot()
    def last_frame(self):
        """
        jump to last frame
        """
        print(f"VidControls: last_frame")
        self.start_end.emit(False)

    @qc.pyqtSlot()
    def play_forward(self):
        """
        engage fast forward
        """
        print(f"VidControls: ffw")
        self.forward.emit()

    @qc.pyqtSlot()
    def play_backward(self):
        """
        engage fast reverse
        """
        print(f"VidControls: rev")
        self.reverse.emit()

    @qc.pyqtSlot()
    def stop_video(self):
        """
        start stop
        """
        print(f"VidControls: stop")
        self.play_stop.emit()
