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

import sys

import PyQt5.QtWidgets as qw
import PyQt5.QtCore as qc

from cgt.gui.Ui_videocontrolwidget import Ui_VideoControlWidget

class VideoControlWidget(qw.QWidget, Ui_VideoControlWidget):
    """
    a widget providing a basic forward backward control for a video
    """

    ## signal to indicate change of frame
    frame_changed = qc.pyqtSignal(int)

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

        ## storage for enabled/disabled state
        self._enabled = False

        ## a flag to record if effects are in use
        self._highlights = False

        # set disabled
        self.enable(self._enabled)

        style = qw.QCommonStyle()
        self._downButton.setIcon(style.standardIcon(style.SP_ArrowBack))
        self._upButton.setIcon(style.standardIcon(style.SP_ArrowForward))

    @qc.pyqtSlot()
    def up_clicked(self):
        """
        callback for a click of the up button

            Returns:
                None
        """
        if self._frameSpinBox.value() < self._frameSpinBox.maximum():
            self.set_frame(self._frameSpinBox.value()+1)

    @qc.pyqtSlot()
    def down_clicked(self):
        """
        callback for a click of the down button

            Returns:
                None
        """
        if self._frameSpinBox.value() > self._frameSpinBox.minimum():
            self.set_frame(self._frameSpinBox.value()-1)

    @qc.pyqtSlot(int)
    def slider_moved(self, value):
        """
        callback for motion of the slider

            Returns:
                None
        """
        modifiers = qw.QApplication.keyboardModifiers()

        if modifiers == qc.Qt.ControlModifier:
            return

        self.set_frame(value)

    @qc.pyqtSlot()
    def slider_released(self):
        """
        handle the possibility that the user is holding down
        crtl key at the time of release
        """
        self.set_frame(self._frameSlider.value())

    @qc.pyqtSlot()
    def frame_sbox_edited(self):
        """
        callback when editing the frame box is completed
        """
        self.set_frame(self._frameSpinBox.value())

    def set_frame(self, frame):
        """
        set a new value of the frame

            Args:
                frame (int) the new frame number

            Returns:
                None

            Emits:
                frame_changed if a change has occured
        """
        change = False
        if self._frameSpinBox.value() != frame:
            self._frameSpinBox.blockSignals(True)
            self._frameSpinBox.setValue(frame)
            self._frameSpinBox.blockSignals(False)
            change = True

        if self._frameSlider.sliderPosition() != frame:
            self._frameSlider.blockSignals(True)
            self._frameSlider.setSliderPosition(frame)
            self._frameSlider.blockSignals(False)
            change = True

        if self.is_enabled() and change:
            self.clear_highlights()
            self.frame_changed.emit(frame)

    def get_current_frame(self):
        """
        getter for the current frame number

            Returns:
                the current frame number
        """
        return self._frameSpinBox.value()

    def enable(self, flag = True):
        """
        enable/disable the component widgets

            Args
                flag (bool) the enabled state

            Returns:
                None
        """
        self._downButton.setEnabled(flag)
        self._upButton.setEnabled(flag)
        self._frameSlider.setEnabled(flag)
        self._frameSpinBox.setEnabled(flag)
        self._enabled = flag

    def is_enabled(self):
        """
        getter for the enabled/disabled state

            Returns:
                (bool) enabled/disabled state
        """
        return self._enabled

    def set_range(self, minimum, maximum):
        """
        set the maximum and minimum frame range

            Args:
                minimum (int) the lower bound
                maximum (int) the upper bound
            Returns:
                None
        """
        tmp = self.is_enabled()
        self.enable(False)

        interval = maximum - minimum
        interval = int(interval/10)

        self._frameSlider.setRange(minimum, maximum)
        self._frameSlider.setTickInterval(interval)
        self._frameSpinBox.setRange(minimum, maximum)

        self.enable(tmp)

    def clear(self):
        """
        clear all the current data

            Returns:
                None
        """
        tmp = self.is_enabled()
        self.enable(False)

        self.set_frame(0)
        self.set_range(0, 0)
        self.clear_highlights()
        self.enable(tmp)

    def highlight_up(self):
        """
        colourize the up button and blur the down
        """
        self._upButton.setGraphicsEffect(qw.QGraphicsColorizeEffect())
        self._downButton.setGraphicsEffect(qw.QGraphicsBlurEffect())
        self._highlights = True

    def highlight_down(self):
        """
        colourize the down button and blue the up
        """
        self._downButton.setGraphicsEffect(qw.QGraphicsColorizeEffect())
        self._upButton.setGraphicsEffect(qw.QGraphicsBlurEffect())
        self._highlights = True

    def clear_highlights(self):
        """
        clear the graphics effects
        """
        self._upButton.setGraphicsEffect(None)
        self._downButton.setGraphicsEffect(None)
        self._highlights = False

def run():
    """
    use a local function to make an isolated the QApplication object

        Returns:
            None
    """
    app = qw.QApplication(sys.argv)

    window = VideoControlWidget()
    window.enable()
    window.set_range(0, 25)
    window.show()
    app.exec_()

if __name__ == "__main__":
    run()
