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
# pylint: disable = no-name-in-module
# pylint: disable = too-many-public-methods

import PyQt5.QtWidgets as qw
import PyQt5.QtCore as qc

from cgt.gui.Ui_cgtvideocontrols import Ui_CGTVideoControls

class CGTVideoControls(qw.QWidget, Ui_CGTVideoControls):
    """
    a widget providing a basic forward backward control for a video
    """

    ## the zoom has been changed
    zoom_value = qc.pyqtSignal(float)

    ## signal to indicate change of time
    time_changed = qc.pyqtSignal(float)

    ## signal for start/end of video, end if parameter = true
    start_end = qc.pyqtSignal(bool)

    ## signal to advance one frame
    one_frame_forward = qc.pyqtSignal()

    ## signal to advance one frame
    one_frame_backward = qc.pyqtSignal()

    ## signal to stop video play
    pause = qc.pyqtSignal()

    ## signal for play forward
    forwards = qc.pyqtSignal()

    ## signal for play backwards
    backwards = qc.pyqtSignal()

    def __init__(self, parent=None):
        """
        set up the dialog

            Args:
                frames_per_second (int) the number of frames per second in video
                total_frames (int) the length of video in frames.
                parent (QObject) the parent object

            Returns:
                None
        """
        super().__init__(parent)
        self.setupUi(self)
        self.setup_buttons()

        ## indicate if the slider should be frozenset
        self._frozen = False

    def clear(self):
        """
        reset to initial conditions
        """
        self.set_slider_value(0)
        self.set_frame_currently_displayed(0)
        self.set_range(99)

    def setup_buttons(self):
        """
        set up the button icons
        """
        style = qw.QCommonStyle()
        self._lastFrameButton.setIcon(style.standardIcon(style.SP_MediaSkipForward))
        self._firstFrameButton.setIcon(style.standardIcon(style.SP_MediaSkipBackward))
        self._forwardButton.setIcon(style.standardIcon(style.SP_ArrowForward))
        self._backwardButton.setIcon(style.standardIcon(style.SP_ArrowBack))
        self._pauseButton.setIcon(style.standardIcon(style.SP_MediaPause))

    def set_slider_value(self, value):
        """
        set the sliders current location
            Args:
                value (int) the new value
        """
        old_slider_state = self._frameSlider.blockSignals(True)
        if not self._frozen:
            self._frameSlider.setValue(value)
        self._frameSlider.blockSignals(old_slider_state)

    def set_range(self, maximum, minimum=0):
        """
        set the slider range to 0 to maximum-1 and the type in to 1 to maximum
            Args:
                maximum (int) the largest allowed frame number
        """
        self._frameSlider.setRange(minimum, maximum-1)
        self._gotoSpinBox.setRange(minimum, maximum-1)
        self._frameSlider.setTickInterval(int(maximum/10))

    def get_range(self):
        """
        get the current frame rang of the controls
            Returns:
                tuple (min, max)
        """
        return (self._frameSlider.minimum(), self._frameSlider.maximum())

    def disable_fine_controls(self):
        """
        disable the fine controls
        """
        self._firstFrameButton.setEnabled(False)
        self._stepDownButton.setEnabled(False)
        self._frameSlider.setEnabled(False)
        self._stepUpButton.setEnabled(False)
        self._lastFrameButton.setEnabled(False)
        self._gotoSpinBox.setEnabled(False)
        self._goToButton.setEnabled(False)
        self._zoomSpinBox.setEnabled(False)

    def enable_fine_controls(self):
        """
        enable the fine controls
        """
        self._firstFrameButton.setEnabled(True)
        self._stepDownButton.setEnabled(True)
        self._frameSlider.setEnabled(True)
        self._stepUpButton.setEnabled(True)
        self._lastFrameButton.setEnabled(True)
        self._goToButton.setEnabled(True)
        self._gotoSpinBox.setEnabled(True)
        self._zoomSpinBox.setEnabled(True)
        self._frozen = False

    def freeze(self):
        """
        disable fine controls and freeze slider
        """
        self._frozen = True
        self.disable_all_but_zoom()

    def disable_all_but_zoom(self):
        """
        disable all play controls, but leave zoom working
        """
        self.disable_fine_controls()
        self._backwardButton.setEnabled(False)
        self._forwardButton.setEnabled(False)
        self._pauseButton.setEnabled(False)
        self._zoomSpinBox.setEnabled(True)

    def enable_all(self):
        """
        enable all play controls
        """
        self.enable_fine_controls()
        self._backwardButton.setEnabled(True)
        self._forwardButton.setEnabled(True)
        self._pauseButton.setEnabled(True)
        self._zoomSpinBox.setEnabled(True)

    def play_forwards(self):
        """
        play the video forwards
        """
        self.disable_fine_controls()
        self.forwards.emit()

    def play_backwards(self):
        """
        play the video backwards
        """
        self.disable_fine_controls()
        self.backwards.emit()

    def play_pause(self):
        """
        pause the video
        """
        self.enable_fine_controls()
        self.pause.emit()

    def set_time_currently_displayed(self, time):
        """
        display the current frame
        """
        if self._gotoSpinBox.isEnabled():
            self._gotoSpinBox.setValue(time)
        self.set_slider_value(time)

    @qc.pyqtSlot(float)
    def zoom_changed(self, zoom):
        """
        callback for the changing the zoom
            Args:
                zoom (float) the new zoom
            Returns:
                None
        """
        self.zoom_value.emit(zoom)

    @qc.pyqtSlot()
    def slider_released(self):
        """
        respond to the release of the slider
        """
        value = self._frameSlider.value()
        self.time_changed.emit(float(value))

    @qc.pyqtSlot()
    def step_up(self):
        """
        one frame down
        """
        self.one_frame_forward.emit()

    @qc.pyqtSlot()
    def step_down(self):
        """
        one frame up
        """
        self.one_frame_backward.emit()

    @qc.pyqtSlot()
    def first_frame(self):
        """
        jump to first frame
        """
        self.start_end.emit(False)

    @qc.pyqtSlot()
    def last_frame(self):
        """
        jump to last frame
        """
        self.start_end.emit(True)

    @qc.pyqtSlot()
    def goto_time(self):
        """
        jump to typed in frame
        """
        self.time_changed.emit(self._gotoSpinBox.value())
