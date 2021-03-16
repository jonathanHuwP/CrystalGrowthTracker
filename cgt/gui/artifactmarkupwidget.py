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

from cgt.gui.videobasewidget import VideoBaseWidget, PlayStates
from cgt.gui.drawinglabel import DrawingLabel
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

class ArtifactMarkupWidget(VideoBaseWidget, Ui_ArtifactMarkupWidget):
    """
    The main window provides a tab widget for the video widget
    """

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

        ## a label in which to display video
        self._video_label = DrawingLabel(self)
        self._videoScrollArea.setWidget(self._video_label)
        self.setup_controls()

    def setup_controls(self):
        """
        fill the combo boxes
        """
        if self._data_source.get_results() is None:
            return

        self._regionsComboBox.clear()
        self._framesComboBox.clear()

        for i, _ in enumerate(self._data_source.get_results().regions):
            self._regionsComboBox.addItem(str(i+1))

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

    @qc.pyqtSlot(int)
    def key_frame_selected(self, index):
        """
        callback for selection in the key frame combobox
            Args:
                index (int) index of the clicked value
        """
        print(f"markup: frame({index})")

    @qc.pyqtSlot(int)
    def region_selected(self, index):
        """
        callback for selection in the key region combobox
            Args:
                index (int) index of the clicked value
        """
        self.post_request_frame(self._current_frame)

    def set_zoom_in_labels(self, value):
        """
        apply the zoom to the labels in user
            Args:
                value (float) the value of the zoom
        """
        if self._video_label is not None:
            self._video_label.set_zoom(value)

    def setEnabled(self, enabled):
        """
        enable/disable widget on enable the source
        is connected on disable play is paused
        """
        if enabled:
            self._regionsComboBox.clear()
            for item, _ in enumerate(self._data_source.get_results().regions):
                self._regionsComboBox.addItem(str(item))
        super().setEnabled(enabled)

    def display(self):
        """
        display an image, the image must be a pixmap so that
        it can safely be recieved from another thread
        """
        if self._current_image is None or self.isHidden():
            return

        region_index = self._regionsComboBox.currentIndex()

        if region_index >= 0:
            rectangle = self._data_source.get_results().regions[region_index]
            self._current_image = self._current_image.copy(rectangle)

        super().display()

    def clear(self):
        """
        clear the current contents
        """
        if self._video_label is not None:
            self._video_label.clear()
        super().clear()
