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
import PyQt5.QtGui as qg
import PyQt5.QtCore as qc

from cgt.gui.Ui_videocontrolsimple import Ui_VideoControlSimple

class VideoControlSimple(qw.QWidget, Ui_VideoControlSimple):

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

        ## storage for the current frame
        self._current_frame = 0

        ## the maximum
        self._frame_maximum = 0

        ## the minimum
        self._frame_minimum = 0

        # set disabled
        self.setEnabled(False)

    @qc.pyqtSlot()
    def last_clicked(self):
        """
        callback for a click of the last frame button

            Returns:
                None
        """
        self.set_frame(self._frame_maximum)

    @qc.pyqtSlot()
    def first_clicked(self):
        """
        callback for a click of the first frame button

            Returns:
                None
        """
        self.set_frame(self._frame_minimum)

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

        if self._current_frame != frame:
            self._current_frame = frame
            self._frameOut.display(self._current_frame)
            change = True

        if self.isEnabled() and change:
            self.frame_changed.emit()

    def get_current_frame(self):
        """
        getter for the current frame number

            Returns:
                the current frame number
        """
        return self._current_frame

    def setEnabled(self, flag = True):
        """
        enable/disable the component widgets

            Args
                flag (bool) the enabled state

            Returns:
                None
        """
        super().setEnabled(flag)
        self._firstButton.setEnabled(flag)
        self._lastButton.setEnabled(flag)

    def set_range(self, minimum, maximum):
        """
        set the maximum and minimum frame range

            Args:
                minimum (int) the lower bound
                maximum (int) the upper bound
            Returns:
                None
        """
        tmp = self.isEnabled()
        self.setEnabled(False)

        self._frame_minimum = minimum
        self._frame_maximum = maximum
        self._current_frame = self._frame_maximum
        self._frameOut.display(self._current_frame)
        self.setEnabled(tmp)

    def clear(self):
        """
        clear all the current data

            Returns:
                None
        """
        tmp = self.isEnabled()
        self.setEnabled(False)

        self.set_range(0, 0)

        self.setEnabled(tmp)

def run():
    """
    use a local function to make an isolated the QApplication object

        Returns:
            None
    """
    app = qw.QApplication(sys.argv)

    window = VideoControlSimple()
    window.enable()
    window.set_range(5, 25)
    window.show()
    app.exec_()

if __name__ == "__main__":
    run()