## -*- coding: utf-8 -*-
"""
Created on 22 March 2021

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
# pylint: disable = import-error

import PyQt5.QtGui as qg
import PyQt5.QtCore as qc

from vb.gui.videobaseview import VideoBaseView

class MarkUpView(VideoBaseView):
    """top level application"""

    def __init__(self, parent):
        """
        initialize a main window and start event loop
        """
        super().__init__(parent)

        ## the state true = lines, false = crosses
        self._state = True

        ## the current line
        self._draw_line = None

    @qc.pyqtSlot(qg.QMouseEvent)
    def mousePressEvent(self, event):
        """
        callback for a mouse press
            Args:
                event (QMouseEvent) the event
        """
        super().mousePressEvent(event)

        if self._state:
            self.start_line(self.mapToScene(event.pos()))
        else:
            self.add_cross(self.mapToScene(event.pos()))

    @qc.pyqtSlot(qg.QMouseEvent)
    def mouseMoveEvent(self, event):
        """
        callback for a mouse press
            Args:
                event (QMouseEvent) the event
        """
        super().mouseMoveEvent(event)

        if self._state:
            self.extend_line(self.mapToScene(event.pos()))

    @qc.pyqtSlot(qg.QMouseEvent)
    def mouseReleaseEvent(self, event):
        """
        callback for a mouse press
            Args:
                event (QMouseEvent) the event
        """
        super().mouseReleaseEvent(event)

        if self._state:
            self.finish_line(self.mapToScene(event.pos()))

    def start_line(self, point):
        """
        start drawing a lines
            Args:
                point (QPointF) start point in scene coordinates
        """
        line = qc.QLineF(point, point)
        self._draw_line = self.scene().addLine(line, self._red_pen)

    def extend_line(self, point):
        """
        change an existing line:
            Args:
                point (QPointF) the new end point (p2)
        """
        line = self._draw_line.line()
        new_line = qc.QLineF(line.p1(), point)
        self._draw_line.setLine(new_line)

    def finish_line(self, point):
        """
        finish and save a line:
            Args:
                point (QPointF) the new end point (p2)
        """
        self.extend_line(point)
        self._draw_line.setPen(self._gray_pen)
        self._parent.add_line(self._draw_line)
        self._draw_line = None

    def add_cross(self, point):
        """
        add a cross to the scene
            Args:
                point (QPointF) location in scene coordinates
        """
        path = qg.QPainterPath()
        up_right = qc.QPointF(10.0, 10.0)
        up_left = qc.QPointF(-10.0, 10.0)
        path.moveTo(point)
        path.lineTo(point+up_right)
        path.moveTo(point)
        path.lineTo(point+up_left)
        path.moveTo(point)
        path.lineTo(point-up_right)
        path.moveTo(point)
        path.lineTo(point-up_left)

        cross = self.scene().addPath(path, self._gray_pen)
        cross.setData(0, point)

        self._parent.add_point(cross)

    @qc.pyqtSlot(int)
    def set_state(self, value):
        """
        set the drawing state
            Args:
                value (int) if 0 draw lines, else crosses
        """
        if value == 0:
            self._state = True
        else:
            self._state = False
