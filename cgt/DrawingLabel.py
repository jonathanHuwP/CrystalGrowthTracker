# -*- coding: utf-8 -*-
"""
Created on Friday July 10 13:42: 2020

this widget is a subclass of QLabel allowing the mouse actions of the user, on
the label to be detected, and lines to be created and edited in the coordinates
of the pixmap

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

from enum import IntEnum

class WidgetState(IntEnum):
    """
    the state of the users interaction
    """

    ## the user will create a new line by downclick and drag
    DRAWING   = 10

    ## the user will select a line and adjust the whole line or an endpoint
    ADJUSTING = 20

class StorageState(IntEnum):
    """
    the state of the line storage
    """

    ## new lines are added to the current set
    CREATING_LINES = 10

    ## the adjusted lines are copyed to a new set
    COPYING_LINES  = 20

class AdjustingState(IntEnum):
    """
    records what part of a line the user is adjusting
    """

    ## the whole line should move
    LINE  = 10

    ## the start point should be moved
    START = 20

    ## the end point should be moved
    END   = 30

from image_artifacts import ImagePoint, ImageLineSegment

class DrawingLabel(qw.QLabel):
    """
    subclass of label providing functions for drawing using a mouse.
    """
    def __init__(self, parent=None):
        """
        Set up the objeect

            Args:
                parent (QObject) the parent Object
        """
        super(qw.QLabel, self).__init__()
        ## pointer to the parent object
        self._parent = parent

        ## the class name as in translation, used in dialogs
        self._translated_name = self.tr("DrawingLabel")

        ## store the Drawing/Adjusting state
        self._state = WidgetState.DRAWING

        ## store the Creating/Copying state
        self._storageState = StorageState.CREATING_LINES

        ## start point of the current line
        self._start = None
        ## end point of the current line
        self._end = None
        ## the initial value of the magnification
        self._currentZoom = 1.0
        ## records if the left mouse button is currently held down
        ## Qt does not allow interrogation of the current state of
        ## the mouse buttons, so a state variable must be
        ## provided to record the state for 'drag' operations
        self._mouseLeftDown = False
        ## if true then the label must redraw on the next paint event
        self._redraw = True

        ## the following two variables govern the adjustmen of an existing line
        ## if true the whole line is shifted else an end is shifted
        self._adjustLine = True
        ## the _linesBase array index of the line being adjusted
        self._adjustIndex = 0

        ## if true display the line labesl on the pixmap
        self._showLabels = False

        ## array for the created lines or the base from which the lines are being adjusted
        self._linesBase = []
        ## array for the new lines resulting from adjustment
        self._linesNew = []

        ## the line being worked on, is created by mouse move or mouse release events
        self._currentLine = None

        self.setAlignment(
                qc.Qt.AlignTop | qc.Qt.AlignLeft)
        self.setSizePolicy(
                qw.QSizePolicy.Ignored, qw.QSizePolicy.Fixed)
        self.setSizePolicy(
                qw.QSizePolicy.Minimum, qw.QSizePolicy.Minimum)

    def setBackgroudPixmap(self, pix):
        """
        set the pixmap to be displayed

            Args:
                pix (QPixmap) the pixmap to be displayed

            Returns:
                None
        """
        self._background = pix

    @property
    def state(self):
        """
        getter for the Drawing/Adjusting state

            Returns:
                None
        """
        return self._state

    @property
    def storageState(self):
        """
        getter for the Creating/Copying state

            Returns:
                current storage state
        """
        return self._storageState

    @property
    def size(self):
        """
        getter for the number of line segments

            Returns
                a tuple consisting of (number line segments in base, number in new list)
        """
        return (len(self._linesBase), len(self._linesNew))

    @property
    def linesBase(self):
        """
        getter for the base lines

            Returns:
                the array of lines
        """
        return self._linesBase

    @property
    def linesNew(self):
        """
        getter for the new lines

            Returns:
                the array of lines
        """
        return self._linesNew

    def setDrawing(self):
        """
        set the Drawing/Adjusting state to Drawing

            Returns:
                None
        """
        self._state = WidgetState.DRAWING

    def setAdjusting(self):
        """
        set the Drawing/Adjusting state to Adjusting

            Returns:
                None
        """
        self._state = WidgetState.ADJUSTING

    def setCreating(self):
        """
        set the Creating/Copying state to Creating

            Returns:
                None
        """
        self._storageState = StorageState.CREATING_LINES

    def setCopying(self):
        """
        set the Creating/Copying state to Creating

            Returns:
                None
        """
        self._storageState = StorageState.COPYING_LINES

    def setZoom(self, value):
        """
        change the magnification and redisplay

            Args:
                value (float) the new value of the magnification

            Returns:
                None
        """
        self._currentZoom = value
        self.redisplay()

    def showLabels(self, flag):
        """
        make the label display, or not, the labels by the lines

            Args:
                flag (boolean) the new values of the display labels flag

            Returns:
                None
        """
        self._showLabels = flag
        self.redisplay()

    @qc.pyqtSlot()
    def mousePressEvent(self, e):
        """
        detect the start of a mouse movement

            Args:
                e (QEvent) the mouse event, which stores details

            Returns:
                None
        """
        if self._state == WidgetState.DRAWING:
            if e.button() == qc.Qt.LeftButton:
                self._start = e.pos()
                self._mouseLeftDown = True
            else:
                pass
            self.redisplay()
        else:
            if e.button() == qc.Qt.LeftButton:
                pick = self.pick_artifact(e.pos())
                print(pick)
                if pick is not None:
                    self._adjustIndex = pick[0]
                    self._mouseLeftDown = True

                    if pick[1] is None:
                        self._start = e.pos()
                        self._adjustLine = AdjustingState.LINE
                    elif pick[1] == "start":
                        self._start = None
                        self._adjustLine = AdjustingState.START
                    else:
                        self._start = None
                        self._adjustLine = AdjustingState.END

            self.redisplay()

    def pick_artifact(self, position, radius=5):
        """
        respond to a user mouse click by picking a line or the end point of a
        line.

        1. define radius in pixels around click event location
        2. Test all end point to see if they lie in radius
            if one or more found return the closest end point (index, start/end)
        3. Test for any lines passing within radius of event
            if one or more found return the closest line index
            Args:
            position the location of the mouse click
            radius the size of the region around the event that is significant

            Args:
                position (QPoint) the screen coordinates of the pixel the user has selected

                radius (int) the distance in pixels around the selected pixel that is significant

            Returns:
                (<line array index>, <endpoint = None>)

                if no line detected the return is None, else it is a size two tuple
                consisting of the array index of the line and, if a line end was selected,
                "start" or "end", else the second item is None
        """
        tp = self.test_points(position, radius)
        if tp is not None:
            return tp

        tl = self.test_lines(position, radius)
        if tl is not None:
            return tl

        return None

    def test_points(self, position, radius):
        """
        test if a position is within radius of any line end points

            Args:
            position (QPoint) the target point
            radius (int) the distance in pixels around the selected pixel that is significant

            Returns
                if end point found a tuple (<line array index>, <start/end>) else None
        """

        def in_r(im_pt, target, r):
            # find if pixel is within square (2r + 1) about target
            # return True and seperation if in, else (False, 0)
            dx = abs(im_pt.x - target.x())
            dy = abs(im_pt.y - target.y())

            if dx > r:
                return (False, 0)
            elif dy > r:
                return (False, 0)
            else:
                return (True, np.round(np.sqrt(dx*dx + dy*dy)))

        points = []
        distances = []
        for i in range(len(self._linesBase)):
            line = self._linesBase[i]

            tmp = in_r(
                line.start.scale(self._currentZoom), position, radius)
            if tmp[0]:
                points.append((i, "start"))
                distances.append(tmp[1])
            else:
                tmp = in_r(
                    line.end.scale(self._currentZoom), position, radius)
                if tmp[0]:
                    points.append((i, "end"))
                    distances.append(tmp[1])

        if len(points) == 1:
            return points[0]
        elif len(points) > 1:
            return points[np.argmin(distances)]
        else:
            return None

    def test_lines(self, position, radius):
        """
        find if a line segment lies within radius of the a given point

            Args:
            position (QPoint) the target point

            radius (int) the distance in pixels around the selected pixel that is significant

            Returns
                if line found a tuple (<line array index>, None) else None
        """
        lines = []
        distances = []

        for i in range(len(self._linesBase)):
            line = self._linesBase[i].scale(self._currentZoom)
            tmp = line.distancePointToLine(position)
            if tmp < radius:
                p = ImagePoint(position.x(), position.y())
                cp = line.isClosestPointOnSegment(p)
                if cp[0]:
                    lines.append(i)
                    distances.append(tmp)

        if len(lines) == 1:
            return (lines[0], None)
        elif len(lines) > 1:
            return (lines[np.argmin(distances)], None)
        else:
            return None

    @qc.pyqtSlot()
    def mouseMoveEvent(self, e):
        """
        responde to the morment of the mouse, if drawing redraw the line else
        to the alter chosen line function

            Args:
                e (QEvent) the event holding the button/location data

            Returns:
                None
        """
        if self._state == WidgetState.DRAWING and self._mouseLeftDown:
            self._end = e.pos()
            self.make_line()
            self.redisplay()

        elif self._state == WidgetState.ADJUSTING and self._mouseLeftDown:
            self.alterChosenLine(e)

    def alterChosenLine(self, event):
        """
        the function for altering a line, if adjusting shift the whole line
        else shift the currently selected end.

            Args:
                event (QEvent) the event holding coordinates and source data

            Returns:
                None
        """
        if self._adjustLine == AdjustingState.LINE:
            self.shiftChosenLine(event)
        else:
            self.moveChosenLineEnd(event)

    def moveChosenLineEnd(self, event):
        """
        move the end of the currently chosen line

            Args:
                event (QEvent) the event holding coordinates and source data

            Returns:
                None
        """
        pt = ImagePoint(event.x(), event.y())
        if self._adjustLine == AdjustingState.START:
            self._currentLine = self._linesBase[self._adjustIndex].newStart(pt)
        else:
            self._currentLine = self._linesBase[self._adjustIndex].newEnd(pt)

        self.redisplay()

    def shiftChosenLine(self, event):
        """
        move the the currently chosen line

            Args:
                event (QEvent) the event holding coordinates and source data

            Returns:
                None
        """
        shift_qt = event.pos() - self._start
        shift_vec = ImagePoint(shift_qt.x(), shift_qt.y())
        self._currentLine = self._linesBase[self._adjustIndex].shift(shift_vec)

        self.redisplay()

    @qc.pyqtSlot()
    def mouseReleaseEvent(self, event):
        """
        the mouse button release callback function

            Args:
                event (QEvent) the event holding coordinates and source data

            Returns:
                None
        """

        # ignore anything other than the left mouse button
        if not event.button() == qc.Qt.LeftButton:
            return

        # if mode drawing ask the user if the line is wanted
        if self._state == WidgetState.DRAWING:
            self._end = e.pos()
            self.make_line()
            self.redisplay()
            reply = qw.QMessageBox.question(
                    self,
                    self.tr("Create Line"),
                    self.tr("Do you wish to save the line?"))

            if reply == qw.QMessageBox.Yes:
                self.add_line()

            self.clear_current()
            self.redisplay()

        # else pass the call to the adjusting release function
        elif self._state == WidgetState.ADJUSTING and self._currentLine is not None:
            self.adjustingRelease()

        self._mouseLeftDown = False

    def adjustingRelease(self):
        """
        the mouse button release function for use in the adjusting mode, if
        creating lines current is added to the _linesBase, else if copying
        mode the current line is added to _linesNew

            Returns:
                None
        """
        reply = qw.QMessageBox.question(
            self,
            self.tr("Adjust Line"),
            self.tr("Do you wish to save adjusted line?"))

        if reply == qw.QMessageBox.Yes:
            if self._storageState == StorageState.CREATING_LINES:
                self._linesBase[self._adjustIndex] = self._currentLine
            else:
                self._linesNew.append(self._currentLine)

        self.clear_current()
        self._adjustLine = True # if true the whole line is shifted
        self._adjustIndex = 0
        self.redisplay()

    def make_line(self):
        """
        make the current line allowing for the label's zoom factor,
        the line will be in coordinates of the original pixmap

            Returns:
                None
        """
        zoom = self._currentZoom
        sx = np.float64(self._start.x())/zoom
        sx = np.uint32(np.round(sx))
        sy = np.float64(self._start.y())/zoom
        sy = np.uint32(np.round(sy))

        ex = np.float64(self._end.x())/zoom
        ex = np.uint32(np.round(ex))
        ey = np.float64(self._end.y())/zoom
        ey = np.uint32(np.round(ey))

        self._currentLine = ImageLineSegment(
            ImagePoint(sx, sy),
            ImagePoint(ex, ey),
            "line")

    def clear_current(self):
        """
        delete the current line and the current start and end points

            Returns:
                None
        """
        self._start = None
        self._end = None
        self._currentLine = None

    def add_line(self):
        """
        copy the current line to the _linesBase with its index as its label

            Returns:
                None
        """
        if self._currentLine is None:
            return

        self._linesBase.append(
            self._currentLine.relabel(str(len(self._linesBase))))

    def redisplay(self):
        """
        force the label to redisplay the current contents

            Returns:
                None
        """
        self._redraw = True
        self.repaint()

    @qc.pyqtSlot()
    def paintEvent(self, e):
        """
        if the redraw flag is set then redraw the lines, else nothing

            Returns:
                None
        """
        qw.QLabel.paintEvent(self, e)

        if self._redraw:
            self.draw_lines()
            self._redraw = False

    def draw_lines(self):
        """
        Draw the lines: iterates the _linesBase, then, if COPYING_LINES
        the _linesNew finally the current line

            Returns:
                None
        """

        pen = qg.QPen(qg.QColor(qc.Qt.black), 1, qc.Qt.SolidLine)
        red_pen = qg.QPen(qg.QColor(qc.Qt.red), 1, qc.Qt.DashLine)
        new_pen = qg.QPen(qg.QColor(qc.Qt.black), 1, qc.Qt.DashLine)
        painter = qg.QPainter()

        height = self._background.height()*self._currentZoom
        width = self._background.width()*self._currentZoom
        pix = self._background.scaled(width, height)

        painter.begin(pix) # make copy

        painter.setPen(pen)
        for line in self._linesBase:
            self.drawSingleLine(line, painter)

        if self._storageState == StorageState.COPYING_LINES:
            painter.setPen(new_pen)
            for line in self._linesNew:
                self.drawSingleLine(line, painter)

        if self._currentLine is not None:
            painter.setPen(red_pen)
            zoomed = self._currentLine.scale(self._currentZoom)
            ql = qc.QLine(
                qc.QPoint(int(zoomed.start.x), int(zoomed.start.y)),
                qc.QPoint(int(zoomed.end.x), int(zoomed.end.y)))
            painter.drawLine(ql)

        painter.end()

        self.setPixmap(pix)

    def drawSingleLine(self, line, painter):
        """
        draw a single line segment

            Args:
            line (int) the array index of the line

            painter (QPainter) the painter to be used for the drawing, with pen set

            Returns:
                None
        """
        zoomed = line.scale(self._currentZoom)
        ql = qc.QLine(
            qc.QPoint(int(zoomed.start.x), int(zoomed.start.y)),
            qc.QPoint(int(zoomed.end.x), int(zoomed.end.y)))
        painter.drawLine(ql)
        if self._showLabels:
            # find the bounding box for the text
            bounding_box = qc.QRect(1, 1, 1, 1)
            bounding_box = painter.boundingRect(
                bounding_box,
                qc.Qt.AlignCenter,
                line.label)
            point = zoomed.start
            location = qc.QPoint(point.x, point.y)
            bounding_box = qc.QRect(location, bounding_box.size())
            painter.drawText(
                bounding_box,
                qc.Qt.AlignHorizontal_Mask | qc.Qt.AlignVertical_Mask,
                line.label)

    def save(self, file):
        """
        save the current image as a PNG file

            Args:
                file (PyQt5.QtCore.QFile) the file for writing.

            Returns
                None.
        """

        file.open(qc.QIODevice.WriteOnly)
        self.pixmap().save(file, "PNG")

