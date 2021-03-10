## -*- coding: utf-8 -*-
"""
Created on Thur Mar 04 2021

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
# pylint: disable = too-many-public-methods
# pylint: disable = too-many-instance-attributes
# pylint: disable = c-extension-no-member
# pylint: disable = import-error

from enum import IntEnum

import PyQt5.QtWidgets as qw
import PyQt5.QtCore as qc
import PyQt5.QtGui as qg

from cgt.gui.Ui_artifactmarkupwidget import Ui_ArtifactMarkupWidget

class DrawingStates(IntEnum):
    """
    specify the number of the pages in the wizard
    """
    DRAW = 0
    MOVE = 2
    DELETE = 4

class Artifacts(IntEnum):
    """
    specify the things being drawn
    """
    LINE = 0
    POINT = 2

class ArtifactMarkupWidget(qw.QWidget, Ui_ArtifactMarkupWidget):
    """
    The main window provides a tab widget for the video widget
    """
    ## signal that a frame is required
    request_frame = qc.pyqtSignal(int)

    ## signal that the queue should be cleared
    clear_queue = qc.pyqtSignal()

    def __init__(self, parent, data_source):
        """
        the object initalization function
            Args:
                parent (QObject): the parent QObject for this window
                data_source (CrystalGrowthTrackerMain): the holder of the results
        """
        super().__init__(parent)
        self.setupUi(self)
        self._splitter.setSizes([500, 124])

        ## the holder of the results data
        self._data_source = data_source

        ## the top state
        self._state = DrawingStates.DRAW

        ## the artifct to drawing
        self._artifact = Artifacts.LINE

        self._regionsComboBox.addItem("Region 1")
        self._regionsComboBox.addItem("Region 2")
        self._framesComboBox.addItem("234")
        self._framesComboBox.addItem("789")

    @qc.pyqtSlot(qw.QAbstractButton)
    def mark_type_selected(self, button):
        """
        callback for click on button in the mark type group
            Args:
                button (QAbstractButton) pointer to the button that was clicked
        """
        if button == self._linesButton and not self._artifact == Artifacts.LINE:
            self._artifact = Artifacts.LINE
        elif button == self._pointsButton and not self._artifact == Artifacts.POINT:
            self._artifact = Artifacts.POINT

        print(f"Artifact {self._artifact.name}")

    @qc.pyqtSlot(qw.QAbstractButton)
    def marking_state_selected(self, button):
        """
        callback for click on button in the widget state group
            Args:
                button (QAbstractButton) pointer to the button that was clicked
        """
        if button == self._drawButton and not self._state == DrawingStates.DRAW:
            self._state = DrawingStates.DRAW
        elif button == self._moveButton and not self._state == DrawingStates.MOVE:
            self._state = DrawingStates.MOVE
        elif button == self._deleteButton and not self._state == DrawingStates.DELETE:
            self._state = DrawingStates.DELETE

        print(f"state {self._state.name}")

    @qc.pyqtSlot(int)
    def key_frame_selected(self, index):
        """
        callback for selection in the key frame combobox
            Args:
                index (int) index of the clicked value
        """
        print(f"frame {index}")

    @qc.pyqtSlot(int)
    def region_selected(self, index):
        """
        callback for selection in the key region combobox
            Args:
                index (int) index of the clicked value
        """
        print(f"region {index}")

    @qc.pyqtSlot(qg.QPixmap, int)
    def display_image(self, pixmap, frame_number):
        """
        display an image, the image must be a pixmap so that
        it can safely be recieved from another thread
            Args:
                pixmap (QPixmap) the image in pixmap form
                frame_number
        """
        print(f"markup widget display {pixmap} {frame_number}")

    @qc.pyqtSlot()
    def stop_play(self):
        """
        stop the playing
        """
        print("markup widget stop play")
