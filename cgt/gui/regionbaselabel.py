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
# pylint: disable = c-extension-no-member
# pylint: disable = no-name-in-module

import PyQt5.QtWidgets as qw
import PyQt5.QtGui as qg
import PyQt5.QtCore as qc

from cgt.util.utils import rectangle_properties

class RegionBaseLabel(qw.QLabel):
    """
    subclass of QLabel used as the base of all region
    selection/editing labels
    """

    def __init__(self, parent):
        """
        Set up the label
            Args:
                parent (VideoRegionSelectionWidget) the parent widget
        """
        super().__init__(parent)

        ## store seperatly as the PyQt5 .parent() returns a vanilla QWidget
        self._select_widget = parent

        ## the zoom transformatin
        self._zoom_transform = qg.QTransform().scale(1.0, 1.0)
        self._inverse_zoom, _= self._zoom_transform.inverted()

    def set_data_source(self, data_source):
        """
        assign the data source
        """
        self._data_source = data_source

    def draw_rectangle(self, rectangle):
        """
        Draw the rectangle
            Args:
                rectangle (QRect) the rectangle to be drawn
            Returns:
                None
        """
        pen = qg.QPen(qg.QColor(70, 102, 255), 2, qc.Qt.DashLine)
        brush = qg.QBrush(qg.QColor(255, 255, 255, 120))
        painter = qg.QPainter(self)
        painter.setPen(pen)
        painter.setBrush(brush)
        rect = self._zoom_transform.mapRect(rectangle)
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

    def get_select_widget(self):
        """
        getter for the select widget
            Returns:
                the data source (Object)
        """
        return self._select_widget
