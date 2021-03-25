# -*- coding: utf-8 -*-
"""
Created on Fri 20 Mar 2021

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

import PyQt5.QtWidgets as qw
import PyQt5.QtGui as qg
import PyQt5.QtCore as qc
import PyQt5.Qt as qt

class VideoBaseView(qw.QGraphicsView):
    """
    provides a viewer for a pixmaps
    """
    def __init__(self, parent):
        """
        set up the scene graph
        """
        super().__init__(parent)

        ## pen width in drawing
        self._pen_width = 3

        ## needed as in PyQt5 .parent() only returns the Qt base class
        self._parent = parent

        ## the pixmap for video display
        self._pixmap_item = None

        ## red pen
        self._red_pen = qg.QPen(qt.Qt.red)
        self._red_pen.setWidth(self._pen_width)

        ## gray pen
        self._gray_pen = qg.QPen(qt.Qt.darkGray)
        self._gray_pen.setWidth(self._pen_width)

        ## set and connect scene
        self.setScene(qw.QGraphicsScene())

    def set_pixmap(self, pixmap):
        """
        set the pixamp
            Args:
                pixmap (QPixmap) the pixmap
        """
        if self._pixmap_item is None:
            self._pixmap_item = self.scene().addPixmap(pixmap)
            rect = self._pixmap_item.boundingRect()
            self.scene().setSceneRect(rect)
        else:
            self._pixmap_item.setPixmap(pixmap)

    def set_zoom(self, zoom_value):
        """
        zoom the pixmap
            Args:
                zoom_value (float) the current zoom
        """
        self.setTransform(qg.QTransform())
        self.scale(zoom_value, zoom_value)

    def set_pen_width(self, width):
        """
        set the width of the drawing pen
            Args:
                width (int) the new width
        """
        self._pen_width = width
        self._red_pen.setWidth(self._pen_width)
        self._gray_pen.setWidth(self._pen_width)

        for item in self.scene().items():
            if isinstance(item, qw.QGraphicsRectItem):
                item.setPen(self._gray_pen)

def length_squared(point):
    """
    square of length from origin of a point
        Args:
            point (QPointF) the point
        Returns
            square of length
    """
    return point.x()*point.x() + point.y()*point.y()


def make_positive_rect(corner, opposite_corner):
    """
    draw a rectangle with positive size (x, y) from two points
        Args:
            corner (QPointF) scene coordinates of a corner
            opposite_corner (QPointF) scene coordinates of the opposing corner
    """
    # get the width and height (strictly positive)
    width = abs(opposite_corner.x()-corner.x())
    height = abs(opposite_corner.y()-corner.y())

    # find the top left of the new adjusted rectangle
    top_left_x = min(opposite_corner.x(), corner.x())
    top_left_y = min(opposite_corner.y(), corner.y())

    return qc.QRectF(top_left_x, top_left_y, width, height)
