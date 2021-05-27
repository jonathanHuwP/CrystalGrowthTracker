## -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 2021

This module contains the top level graphical user interface for measuring the
growth rates of crystals observed in videos taken using an X-ray synchrotron source

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
# pylint: disable = invalid-name

import PyQt5.QtWidgets as qw
import PyQt5.QtGui as qg
import PyQt5.QtCore as qc

class FullDisableSlider(qw.QSlider):
    """
    a modified slider that will not respond to user input when disabled
    """

    @qc.pyqtSlot(qg.QMouseEvent)
    def mousePressEvent(self, event):
        """
        callback for a mouse press
            Args:
                event (QMouseEvent) the event
        """
        if self.isEnabled():
            super().mousePressEvent(event)

    @qc.pyqtSlot(qg.QMouseEvent)
    def mouseMoveEvent(self, event):
        """
        callback for a mouse press
            Args:
                event (QMouseEvent) the event
        """
        if self.isEnabled():
            super().mouseMoveEvent(event)

    @qc.pyqtSlot(qg.QMouseEvent)
    def mouseReleaseEvent(self, event):
        """
        callback for a mouse press
            Args:
                event (QMouseEvent) the event
        """
        if self.isEnabled():
            super().mouseReleaseEvent(event)
