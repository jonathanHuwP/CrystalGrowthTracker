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
    """
    a video control that allows the user to navigate between the
    first and last frames of a video sequence
    """

    ## state change: true if first frame
    frame_changed = qc.pyqtSignal(bool)

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

        ## the state if true first frame selected
        self._first_frame = True

        ## the maximum
        self._frame_maximum = 0

        ## the minimum
        self._frame_minimum = 0

        # set up the buttons
        style = qw.QCommonStyle()
        self._firstButton.setIcon(style.standardIcon(style.SP_ArrowBack))
        self._lastButton.setIcon(style.standardIcon(style.SP_ArrowForward))
        self.set_display()

        # set disabled
        self.setEnabled(False)

    @qc.pyqtSlot()
    def last_clicked(self):
        """
        callback for a click of the last frame button

            Returns:
                None
        """
        self._first_frame = False
        self.frame_changed.emit(False)
        self.set_display()

    @qc.pyqtSlot()
    def first_clicked(self):
        """
        callback for a click of the first frame button

            Returns:
                None
        """
        self._first_frame = True
        self.frame_changed.emit(True)
        self.set_display()

    def set_state(self, state):
        """
        set a new state and update display
        """
        self._first_frame = state
        self.set_display()

    def get_state(self):
        """
        getter for the state

            Returns:
                true if first was last button clicked else False + frame number
        """
        if self._first_frame:
            return True, self._frame_minimum

        return False, self._frame_maximum

    def get_minimum(self):
        return self._frame_minimum

    def get_maximum(self):
        return self._frame_maximum

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
        self._first_frame = False
        self.set_display()
        self.setEnabled(tmp)

    def clear(self):
        """
        clear all the current data

            Returns:
                None
        """
        tmp = self.isEnabled()
        self.setEnabled(False)

        self.set_frame(0)
        self.set_range(0, 0)

        self.setEnabled(tmp)

    def set_display(self):
        """
        switch over the highlights of the first and last buttons
        """
        if self._first_frame:
            self.highlight_last()
            self._frameOut.display(self._frame_minimum)
        else:
            self.highlight_first()
            self._frameOut.display(self._frame_maximum)

    def highlight_first(self):
        """
        colourize the up button and blur the down
        """
        self._firstButton.setGraphicsEffect(qw.QGraphicsColorizeEffect())
        self._lastButton.setGraphicsEffect(qw.QGraphicsBlurEffect())
        self._highlight_first = True

    def highlight_last(self):
        """
        colourize the up button and blur the down
        """
        self._lastButton.setGraphicsEffect(qw.QGraphicsColorizeEffect())
        self._firstButton.setGraphicsEffect(qw.QGraphicsBlurEffect())
        self._highlight_first = False

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
