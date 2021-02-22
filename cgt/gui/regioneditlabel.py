# -*- coding: utf-8 -*-
"""
Created on Wed Jun 10 11:28:23 2020

provides a class, derived from QLabel, that allows the user to select a
retcangular region of a pixmap in pixmap coordinates

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
# set up linting conditions
# pylint: disable = no-name-in-module
# pylint: disable = c-extension-no-member
# pylint: disable = import-error

from enum import IntEnum

import PyQt5.QtWidgets as qw
import PyQt5.QtCore as qc

from cgt.util.utils import rectangle_properties, qpoint_sepertation_squared
from cgt.gui.regionbaselabel import RegionBaseLabel

class AdjustmentPoints(IntEnum):
    """
    possible rectangle features to be moved
    """
    NONE = 0
    TOP_LEFT = 2
    TOP_RIGHT = 4
    BOTTOM_LEFT = 8
    BOTTOM_RIGHT = 16
    CENTRE = 32

class RegionEditLabel(RegionBaseLabel):
    """
    subclass of label allowing selection of region by drawing rectangle and
    displaying a list of already selected rectangles.
    """

    ## signal to indicate the user has changed the rectangle
    rectangle_changed = qc.pyqtSignal()

    ## signal to indicate the user has selected a new rectangle
    have_rectangle = qc.pyqtSignal()

    def __init__(self, parent):
        """
        Set up the label

            Args:
                parent (VideoRegionSelectionWidget) the parent object

            Returns:
                None
        """
        super().__init__(parent)
        ## the current rectangle
        self._rectangle = None

        ## the index of the rectangle
        self._index = 0

        ## the feature of the rectangle that is being moved
        self._adjustment_point = AdjustmentPoints.NONE

        ## the translated name
        self._translation_name = self.tr("RegionSelectionLabel")

    def get_rectangle_and_index(self):
        """
        getter for the rectangle and it's index
            Returns:
                tuple of (pointer to the rectangle, index) or None
        """
        if self._rectangle is None:
            return None

        return (self._rectangle, self._index)

    def get_rectangle(self):
        """
        getter for the rectangle
            Returns:
                (rectangle) or None
        """
        if self._rectangle is None:
            return None

        return self._rectangle

    def set_rectangle(self, rectangle, index):
        """
        setter for the rectangle
            Args:
                retctangle (QRect) the rectangle to set
                index (int) the rectangle's index
        """
        self._rectangle = rectangle
        self._index = index
        self.repaint()
        self.have_rectangle.emit()

    def mousePressEvent(self, event):
        """
        detect the start of selection

            Args:
                event (QEvent) the event data

            Returns:
                None
        """
        if self.get_parent().is_playing() or event.button() != qc.Qt.LeftButton:
            return

        if self._rectangle is None:
            return

        props = rectangle_properties(self._rectangle)
        pos = self._inverse_zoom.map(event.pos())

        if qpoint_sepertation_squared(props[0], pos) < 25:
            self._adjustment_point = AdjustmentPoints.TOP_LEFT
        elif qpoint_sepertation_squared(props[1], pos) < 25:
            self._adjustment_point = AdjustmentPoints.TOP_RIGHT
        elif qpoint_sepertation_squared(props[2], pos) < 25:
            self._adjustment_point = AdjustmentPoints.BOTTOM_LEFT
        elif qpoint_sepertation_squared(props[3], pos) < 25:
            self._adjustment_point = AdjustmentPoints.BOTTOM_RIGHT
        elif qpoint_sepertation_squared(props[4], pos) < 25:
            self._adjustment_point = AdjustmentPoints.CENTRE
        else:
            self._adjustment_point = AdjustmentPoints.NONE

    def mouseMoveEvent(self, event):
        """
        respond to a mouse movement

            Args:
                event (QEvent) the event data

            Returns:
                None
        """

        if self.get_parent().is_playing() or event.buttons() != qc.Qt.LeftButton:
            return

        if self._rectangle is None:
            return

        if self._adjustment_point == AdjustmentPoints.NONE:
            return

        pos = self._inverse_zoom.map(event.pos())

        if self._adjustment_point == AdjustmentPoints.TOP_LEFT:
            self._rectangle.setTopLeft(pos)
        elif self._adjustment_point == AdjustmentPoints.TOP_RIGHT:
            self._rectangle.setTopRight(pos)
        elif self._adjustment_point == AdjustmentPoints.BOTTOM_LEFT:
            self._rectangle.setBottomLeft(pos)
        elif self._adjustment_point == AdjustmentPoints.BOTTOM_RIGHT:
            self._rectangle.setBottomRight(pos)
        elif self._adjustment_point == AdjustmentPoints.CENTRE:
            self._rectangle.moveCenter(pos)
        else:
            return

        self.repaint()

    def mouseReleaseEvent(self, event):
        """
        select rectangle

            Args:
                event (QEvent) the event data

            Returns:
                None
        """
        if self.get_parent().is_playing() or event.button() != qc.Qt.LeftButton:
            return

        if self._adjustment_point == AdjustmentPoints.NONE:
            return

        self.rectangle_changed.emit()
        self._adjustment_point = AdjustmentPoints.NONE

    def paintEvent(self, event):
        """
        if selecting than draw a rectangle

            Args:
                event (QEvent) the event data

            Returns:
                None
        """
        # pass on to get pixmap displayed
        qw.QLabel.paintEvent(self, event)
        if self._rectangle is not None:
            self.draw_rectangle(self._rectangle)
