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

from cgt.gui.videoregionselectionwidgetstates import VideoRegionSelectionWidgetStates as states

def rectangle_properties(rectangle):
    """
    find the top left, bottom right and centre of a rectangle
        Args:
            rectangle (QRect) the rectangle
        Returns:
            top left, top right, bottom left, bottom right, centre (QPoint)
    """
    top_left = rectangle.topLeft()
    top_right = rectangle.topRight()
    bottom_left = rectangle.bottomLeft()
    bottom_right = rectangle.bottomRight()
    ctr = top_left + bottom_right
    ctr /= 2

    return top_left, top_right, bottom_left, bottom_right, ctr

class RegionEditLabel(qw.QLabel):
    """
    subclass of label allowing selection of region by drawing rectangle and
    displaying a list of already selected rectangles.
    """

    ## signal to indicate the user has deleted the rectangle
    rectangle_changed = qc.pyqtSignal()

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

        ## the zoom transformatin
        self._zoom_transform = qg.QTransform().scale(1.0, 1.0)
        self._inverse_zoom, _= self._zoom_transform.inverted()

        ## the translated name
        self._translation_name = self.tr("RegionSelectionLabel")

    def get_rectangle(self):
        """
        getter for the rectangle
            Returns:
                pointer to the rectangle or None
        """
        return self._rectangle

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
        print(f"Mouse press")

    def mouseMoveEvent(self, event):
        """
        respond to a mouse movement

            Args:
                event (QEvent) the event data

            Returns:
                None
        """
        if self._parent.is_playing() or event.button() != qc.Qt.LeftButton:
            return

        if self._rectangle is None:
            return

        print("mouse move ")

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
            
        print("Mouse up")

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

        pen = qg.QPen(qg.QColor(qc.Qt.black), 1, qc.Qt.DashLine)
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
