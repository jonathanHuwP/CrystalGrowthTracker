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
    frame_changed = qc.pyqtSignal()

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

        # set disabled
        self.enable(self._enabled)

        # set up the buttons
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

    @qc.pyqtSlot()
    def slider_moved(self):
        """
        callback for motion of the slider

            Returns:
                None
        """
        modifiers = qw.QApplication.keyboardModifiers()

        if modifiers == qc.Qt.ControlModifier:
            return

        self.set_frame(self._frameSlider.sliderPosition())

    @qc.pyqtSlot()
    def slider_released(self):
        """
        handle the possibility that the user is holding down
        crtl key at the time of release
        """
        self.set_frame(self._frameSlider.value())

    @qc.pyqtSlot()
    def spin_box_changed(self):
        """
        callback for a change in the frame count slider

            Returns:
                None
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
            self._frameSpinBox.setValue(frame)
            change = True

        if self._frameSlider.sliderPosition() != frame:
            self._frameSlider.setSliderPosition(frame)
            change = True

        if self.is_enabled() and change:
            self.frame_changed.emit()

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
        self._frameSlider.setTickInterval(interval)

        self._frameSlider.setRange(minimum, maximum)
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

        self.enable(tmp)


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
