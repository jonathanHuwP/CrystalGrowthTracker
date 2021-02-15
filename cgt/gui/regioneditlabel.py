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
# pylint: disable = too-many-instance-attributes
# pylint: disable = too-many-public-methods
# pylint: disable = c-extension-no-member

# TODO handel out of pixmap move/release
# move => freaze untill back
# release => delete and reset

import PyQt5.QtWidgets as qw
import PyQt5.QtGui as qg
import PyQt5.QtCore as qc

from enum import IntEnum

from cgt.util.utils import rectangle_properties, qpoint_sepertation_squared

from cgt.gui.videoregionselectionwidgetstates import VideoRegionSelectionWidgetStates as states

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

class RegionEditLabel(qw.QLabel):
    """
    subclass of label allowing selection of region by drawing rectangle and
    displaying a list of already selected rectangles.
    """

    ## signal to indicate the user has changed the rectangle
    rectangle_changed = qc.pyqtSignal()

    ## signal to indicate the user has selected a new rectangle
    have_rectangle = qc.pyqtSignal()

    def __init__(self, parent=None):
        """
        Set up the label

            Args:
                parent (VideoRegionSelectionWidget) the parent object

            Returns:
                None
        """
        super().__init__(parent)

        ## store drawing widget
        self._parent = parent

        ## the current rectangle
        self._rectangle = None

        ## the index of the rectangle
        self._index = 0

        ## the feature of the rectangle that is being moved
        self._adjustment_point = AdjustmentPoints.NONE

        ## the zoom transformatin
        self._zoom_transform = qg.QTransform().scale(1.0, 1.0)
        self._inverse_zoom, _= self._zoom_transform.inverted()

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
        if self._parent.is_playing() or event.button() != qc.Qt.LeftButton:
            return

        if self._rectangle is None:
            return

        props = rectangle_properties(self._rectangle)

        if qpoint_sepertation_squared(props[0], event.pos()) < 25:
            self._adjustment_point = AdjustmentPoints.TOP_LEFT
        elif qpoint_sepertation_squared(props[1], event.pos()) < 25:
            self._adjustment_point = AdjustmentPoints.TOP_RIGHT
        elif qpoint_sepertation_squared(props[2], event.pos()) < 25:
            self._adjustment_point = AdjustmentPoints.BOTTOM_LEFT
        elif qpoint_sepertation_squared(props[3], event.pos()) < 25:
            self._adjustment_point = AdjustmentPoints.BOTTOM_RIGHT
        elif qpoint_sepertation_squared(props[4], event.pos()) < 25:
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

        if self._parent.is_playing() or event.buttons() != qc.Qt.LeftButton:
            return

        if self._rectangle is None:
            return

        if self._adjustment_point == AdjustmentPoints.NONE:
            return

        if self._adjustment_point == AdjustmentPoints.TOP_LEFT:
            self._rectangle.setTopLeft(event.pos())
        elif self._adjustment_point == AdjustmentPoints.TOP_RIGHT:
            self._rectangle.setTopRight(event.pos())
        elif self._adjustment_point == AdjustmentPoints.BOTTOM_LEFT:
            self._rectangle.setBottomLeft(event.pos())
        elif self._adjustment_point == AdjustmentPoints.BOTTOM_RIGHT:
            self._rectangle.setBottomRight(event.pos())
        elif self._adjustment_point == AdjustmentPoints.CENTRE:
            self._rectangle.moveCenter(event.pos())
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
        if self._parent.is_playing() or event.button() != qc.Qt.LeftButton:
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
        self.draw_rectangle()

    def draw_rectangle(self):
        """
        Draw the rectangle

            Returns:
                None
        """
        if self._rectangle is None:
            return

        #pen = qg.QPen(qg.QColor(qc.Qt.black), 1, qc.Qt.DashLine)
        pen = qg.QPen(qg.QColor(70, 102, 255), 1, qc.Qt.DashLine)
        brush = qg.QBrush(qg.QColor(255, 255, 255, 120))
        painter = qg.QPainter(self)
        painter.setPen(pen)
        painter.setBrush(brush)
        rect = self._zoom_transform.mapRect(self._rectangle)
        painter.drawRect(rect)

        props = rectangle_properties(rect)
        ctr = props[4]
        left = qc.QPoint(ctr.x()-5, ctr.y())
        right = qc.QPoint(ctr.x()+5, ctr.y())
        top = qc.QPoint(ctr.x(), ctr.y()-5)
        bottom = qc.QPoint(ctr.x(), ctr.y()+5)
        painter.drawLine(left, right)
        painter.drawLine(top, bottom)

    def set_zoom(self, value):
        """
        set the current zoom and inverse zoom matrices
        """
        self._zoom_transform = qg.QTransform().scale(value, value)
        self._inverse_zoom, _= self._zoom_transform.inverted()
