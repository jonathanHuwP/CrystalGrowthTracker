# -*- coding: utf-8 -*-
"""
Created on Wed Jun 10 11:28:23 2020

provides a class, derived from QLabel, that allows the user to select a
retcangular region of a pixmap in pixmap coordinates

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at
http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

@copyright 2020
@author: j.h.pickering@leeds.ac.uk
"""

import PyQt5.QtWidgets as qw
import PyQt5.QtGui as qg
import PyQt5.QtCore as qc
import numpy as np

from cgt.DrawRect import DrawRect

# set up linting conditions
# pylint: disable = too-many-public-methods
# pylint: disable = c-extension-no-member

class ImageLabel(qw.QLabel):
    """
    subclass of label allowing selection of region by drawing rectangle and
    displaying a list of already selected rectangles.
    """
    def __init__(self, parent=None):
        """
        Set up the label

            Args:
                parent (QObject) the parent object

            Returns:
                None
        """
        super(qw.QLabel, self).__init__()

        ## (QObject) the parent object
        self._parent = parent

        ## the translated name
        self._translation_name = self.tr("ImageLabel")

        ## the state is not selecting
        self._selecting = False

        ## holder for start of drawing in pixel coordinates
        self._start = None

        ## holder for end of drawing in pixel coordinates
        self._end = None

        ## list for storing rectangles
        self._rectangles = []

    def __iter__(self):
        """
        make the class iterable, over rectangles, by implementing
        means of producing an iterator of the rectangles

            Returns:
                iterator of the rectangles list
        """
        return iter(self._rectangles)

    # signal to indicate user selection
    new_selection = qc.pyqtSignal()

    def mousePressEvent(self, event):
        """
        detect the start of selection

            Args:
                event (QEvent) the event data

            Returns:
                None
        """
        if event.button() == qc.Qt.LeftButton:
            if not self._selecting:
                self._selecting = True
                self._start = event.pos()

    def mouseMoveEvent(self, event):
        """
        If selecting draw rectangle

            Args:
                event (QEvent) the event data

            Returns:
                None
        """
        if self._selecting:
            self._end = event.pos()
            self.repaint()

    def mouseReleaseEvent(self, event):
        """
        select rectangle

            Args:
                event (QEvent) the event data

            Returns:
                None
        """
        if event.button() == qc.Qt.LeftButton and self._selecting:
            self._end = event.pos()
            self.repaint()
            reply = qw.QMessageBox.question(
                self,
                self.tr("Region Selection"),
                self.tr("Do you wish to select region?"))

            if reply == qw.QMessageBox.Yes:
                #self._parent.extract_subimage(self._start, self._end)
                self.add_rectangle()

            self._selecting = False

    def add_rectangle(self):
        """
        add a new rectangl to the store and emit a QSignal to notify other QWidgets

            Emits:
                new_selection signal

            Returns:
                None
        """
        # get horizontal range
        horiz = (self._start.x(), self._end.x())
        zoom = self._parent.get_zoom()

        # get horizontal range
        start_h = np.uint32(np.round(min(horiz)/zoom))
        end_h = np.uint32(np.round(max(horiz)/zoom))

        # get vertical range
        vert = (self._start.y(), self._end.y())
        start_v = np.uint32(np.round(min(vert)/zoom))
        end_v = np.uint32(np.round(max(vert)/zoom))

        # add the rectangle to the ImageLabel

        rect = DrawRect(start_v, end_v, start_h, end_h)

        self._rectangles.append(rect)
        self.new_selection.emit()

    def paintEvent(self, event):
        """
        if selecting than draw a rectagle

            Args:
                event (QEvent) the event data

            Returns:
                None
        """
        qw.QLabel.paintEvent(self, event)

        self.draw_rectangles()

    def draw_rectangles(self):
        """
        Draw the alreay selected rectangles and, if in selecting mode
        the current selection

            Returns:
                None
        """
        if not self._selecting and len(self._rectangles) == 0:
            return

        pen = qg.QPen(qg.QColor(qc.Qt.black), 1, qc.Qt.DashLine)
        brush = qg.QBrush(qg.QColor(255, 255, 255, 120))
        painter = qg.QPainter(self)
        painter.setPen(pen)
        painter.setBrush(brush)

        for rect in self._rectangles:
            zoomed = rect.scale(self._parent.get_zoom())
            q_rect = qc.QRect(
                qc.QPoint(int(zoomed.left), int(zoomed.top)),
                qc.QPoint(int(zoomed.right), int(zoomed.bottom)))

            painter.drawRect(q_rect)

        if self._selecting:
            selection_rect = qc.QRect(self._start, self._end)
            painter.drawRect(selection_rect)

    @property
    def number_rectangles(self):
        """
        getter for the number of rectangles

        Returns:
            the number of rectangles currently stored.
        """
        return len(self._rectangles)

    def get_rectangle(self, index):
        """
        getter for a specified DrawRect

            Args:
            index (int) index of the desired DrawRect.

            Returns:
                the selected rectangle
        """
        return self._rectangles[index]
