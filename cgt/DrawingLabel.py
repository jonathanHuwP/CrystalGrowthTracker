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
# set up linting conditions
# pylint: disable = too-many-public-methods
# pylint: disable = c-extension-no-member

from enum import IntEnum

import PyQt5.QtWidgets as qw
import PyQt5.QtGui as qg
import PyQt5.QtCore as qc
import numpy as np

from image_artifacts import ImagePoint, ImageLineSegment

class WidgetState(IntEnum):
    """
    the state of the users interaction
    """

    ## the user will create a new line by downclick and drag
    DRAWING = 10

    ## the user will select a line and adjust the whole line or an endpoint
    ADJUSTING = 20

class StorageState(IntEnum):
    """
    the state of the line storage
    """

    ## new lines are added to the current set
    CREATING_LINES = 10

    ## the adjusted lines are copyed to a new set
    COPYING_LINES = 20

class AdjustingState(IntEnum):
    """
    records what part of a line the user is adjusting
    """

    ## the whole line should move
    LINE = 10

    ## the start point should be moved
    START = 20

    ## the end point should be moved
    END = 30

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
        self._storage_state = StorageState.CREATING_LINES

        ## start point of the current line
        self._start = None

        ## end point of the current line
        self._end = None

        ## the initial value of the magnification
        self._current_zoom = 1.0

        ## records if the left mouse button is currently held down
        ## Qt does not allow interrogation of the current state of
        ## the mouse buttons, so a state variable must be
        ## provided to record the state for 'drag' operations
        self._mouse_left_down = False

        ## if true then the label must redraw on the next paint event
        self._redraw = True

        ## the following two variables govern the adjustmen of an existing line
        ## if true the whole line is shifted else an end is shifted
        self._adjust_line = True

        ## the _lines_base array index of the line being adjusted
        self._adjust_index = 0

        ## if true display the line labesl on the pixmap
        self._show_labels = False

        ## array for the created lines or the base from which the lines are being adjusted
        self._lines_base = []

        ## array for the new lines resulting from adjustment
        self._lines_new = []

        ## the line being worked on, is created by mouse move or mouse release events
        self._current_line = None

        ## the pixmap on which we are to draw
        self._background_pixmap = None

        self.setAlignment(
            qc.Qt.AlignTop | qc.Qt.AlignLeft)
        self.setSizePolicy(
            qw.QSizePolicy.Ignored, qw.QSizePolicy.Fixed)
        self.setSizePolicy(
            qw.QSizePolicy.Minimum, qw.QSizePolicy.Minimum)

    def set_backgroud_pixmap(self, pix):
        """
        set the pixmap to be displayed

            Args:
                pix (QPixmap) the pixmap to be displayed

            Returns:
                None
        """
        self._background_pixmap = pix

    @property
    def state(self):
        """
        getter for the Drawing/Adjusting state

            Returns:
                None
        """
        return self._state

    @property
    def storage_state(self):
        """
        getter for the Creating/Copying state

            Returns:
                current storage state
        """
        return self._storage_state

    @property
    def size(self):
        """
        getter for the number of line segments

            Returns
                a tuple consisting of (number line segments in base, number in new list)
        """
        return (len(self._lines_base), len(self._lines_new))

    @property
    def lines_base(self):
        """
        getter for the base lines

            Returns:
                the array of lines
        """
        return self._lines_base

    @property
    def lines_new(self):
        """
        getter for the new lines

            Returns:
                the array of lines
        """
        return self._lines_new

    def set_drawing(self):
        """
        set the Drawing/Adjusting state to Drawing

            Returns:
                None
        """
        self._state = WidgetState.DRAWING

    def set_adjusting(self):
        """
        set the Drawing/Adjusting state to Adjusting

            Returns:
                None
        """
        self._state = WidgetState.ADJUSTING

    def set_creating(self):
        """
        set the Creating/Copying state to Creating

            Returns:
                None
        """
        self._storage_state = StorageState.CREATING_LINES

    def set_copying(self):
        """
        set the Creating/Copying state to Creating

            Returns:
                None
        """
        self._storage_state = StorageState.COPYING_LINES

    def set_zoom(self, value):
        """
        change the magnification and redisplay

            Args:
                value (float) the new value of the magnification

            Returns:
                None
        """
        self._current_zoom = value
        self.redisplay()

    def show_labels(self, flag):
        """
        make the label display, or not, the labels by the lines

            Args:
                flag (boolean) the new values of the display labels flag

            Returns:
                None
        """
        self._show_labels = flag
        self.redisplay()

    @qc.pyqtSlot()
    def mousePressEvent(self, event):
        """
        detect the start of a mouse movement

            Args:
                event (QEvent) the mouse event, which stores details

            Returns:
                None
        """
        if self._state == WidgetState.DRAWING:
            if event.button() == qc.Qt.LeftButton:
                self._start = event.pos()
                self._mouse_left_down = True
            else:
                pass
            self.redisplay()
        else:
            if event.button() == qc.Qt.LeftButton:
                pick = self.pick_artifact(event.pos())

                if pick is not None:
                    self._adjust_index = pick[0]
                    self._mouse_left_down = True

                    if pick[1] is None:
                        self._start = event.pos()
                        self._adjust_line = AdjustingState.LINE
                    elif pick[1] == "start":
                        self._start = None
                        self._adjust_line = AdjustingState.START
                    else:
                        self._start = None
                        self._adjust_line = AdjustingState.END

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
        points = self.test_points(position, radius)
        if points is not None:
            return points

        lines = self.test_lines(position, radius)
        if lines is not None:
            return lines

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

        def in_r(im_pt, target):
            # find if pixel is within square (2r + 1) about target
            # return True and seperation if in, else (False, 0)
            del_x = abs(im_pt.x - target.x())
            del_y = abs(im_pt.y - target.y())

            if del_x > radius:
                return (False, 0)

            if del_y > radius:
                return (False, 0)

            return (True, np.round(np.sqrt(del_x*del_x + del_y*del_y)))

        points = []
        distances = []
        for i in range(len(self._lines_base)):
            line = self._lines_base[i]

            tmp = in_r(
                line.start.scale(self._current_zoom), position)
            if tmp[0]:
                points.append((i, "start"))
                distances.append(tmp[1])
            else:
                tmp = in_r(
                    line.end.scale(self._current_zoom), position)
                if tmp[0]:
                    points.append((i, "end"))
                    distances.append(tmp[1])

        if len(points) == 1:
            return points[0]

        if len(points) > 1:
            return points[np.argmin(distances)]

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

        for i in range(len(self._lines_base)):
            line = self._lines_base[i].scale(self._current_zoom)
            dist_to_line = line.distance_point_to_line(position)
            if dist_to_line < radius:
                point = ImagePoint(position.x(), position.y())
                close_points = line.is_closest_point_on_segment(point)
                if close_points[0]:
                    lines.append(i)
                    distances.append(dist_to_line)

        if len(lines) == 1:
            return (lines[0], None)

        if len(lines) > 1:
            return (lines[np.argmin(distances)], None)

        return None

    @qc.pyqtSlot()
    def mouseMoveEvent(self, event):
        """
        responde to the morment of the mouse, if drawing redraw the line else
        to the alter chosen line function

            Args:
                event (QEvent) the event holding the button/location data

            Returns:
                None
        """
        if self._state == WidgetState.DRAWING and self._mouse_left_down:
            self._end = event.pos()
            self.make_line()
            self.redisplay()

        elif self._state == WidgetState.ADJUSTING and self._mouse_left_down:
            self.alter_chosen_line(event)

    def alter_chosen_line(self, event):
        """
        the function for altering a line, if adjusting shift the whole line
        else shift the currently selected end.

            Args:
                event (QEvent) the event holding coordinates and source data

            Returns:
                None
        """
        if self._adjust_line == AdjustingState.LINE:
            self.shift_chosen_line(event)
        else:
            self.move_chosen_line_end(event)

    def move_chosen_line_end(self, event):
        """
        move the end of the currently chosen line

            Args:
                event (QEvent) the event holding coordinates and source data

            Returns:
                None
        """
        point = ImagePoint(event.x(), event.y())
        if self._adjust_line == AdjustingState.START:
            self._current_line = self._lines_base[self._adjust_index].new_start(point)
        else:
            self._current_line = self._lines_base[self._adjust_index].new_end(point)

        self.redisplay()

    def shift_chosen_line(self, event):
        """
        move the the currently chosen line

            Args:
                event (QEvent) the event holding coordinates and source data

            Returns:
                None
        """
        shift_qt = event.pos() - self._start
        shift_vec = ImagePoint(shift_qt.x(), shift_qt.y())
        self._current_line = self._lines_base[self._adjust_index].shift(shift_vec)
        
        m = []
        m.append("shift: {}".format(shift_vec))
        m.append("From: {}".format(self._lines_base[self._adjust_index]))
        m.append("To: {}".format(self._current_line))
        
        for i in m:
            print(i)
         

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
            self._end = event.pos()
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
        elif self._state == WidgetState.ADJUSTING and self._current_line is not None:
            self.adjusting_release()

        self._mouse_left_down = False

    def adjusting_release(self):
        """
        the mouse button release function for use in the adjusting mode, if
        creating lines current is added to the _lines_base, else if copying
        mode the current line is added to lines_new

            Returns:
                None
        """
        reply = qw.QMessageBox.question(
            self,
            self.tr("Adjust Line"),
            self.tr("Do you wish to save adjusted line?"))

        if reply == qw.QMessageBox.Yes:
            if self._storage_state == StorageState.CREATING_LINES:
                self._lines_base[self._adjust_index] = self._current_line
            else:
                self._lines_new.append(self._current_line)

        self.clear_current()
        self._adjust_line = True # if true the whole line is shifted
        self._adjust_index = 0
        self.redisplay()

    def make_line(self):
        """
        make the current line allowing for the label's zoom factor,
        the line will be in coordinates of the original pixmap

            Returns:
                None
        """
        zoom = self._current_zoom
        start_x = np.float64(self._start.x())/zoom
        start_x = np.uint32(np.round(start_x))
        start_y = np.float64(self._start.y())/zoom
        start_y = np.uint32(np.round(start_y))

        end_x = np.float64(self._end.x())/zoom
        end_x = np.uint32(np.round(end_x))
        end_y = np.float64(self._end.y())/zoom
        end_y = np.uint32(np.round(end_y))

        self._current_line = ImageLineSegment(
            ImagePoint(start_x, start_y),
            ImagePoint(end_x, end_y),
            "line")
            
        print("line: {}; zoom: {}".format(self._current_line, self._current_zoom))

    def clear_current(self):
        """
        delete the current line and the current start and end points

            Returns:
                None
        """
        self._start = None
        self._end = None
        self._current_line = None

    def add_line(self):
        """
        copy the current line to the _lines_base with its index as its label

            Returns:
                None
        """
        if self._current_line is None:
            return

        self._lines_base.append(
            self._current_line.relabel(str(len(self._lines_base))))

    def redisplay(self):
        """
        force the label to redisplay the current contents

            Returns:
                None
        """
        self._redraw = True
        self.repaint()

    @qc.pyqtSlot()
    def paintEvent(self, event):
        """
        if the redraw flag is set then redraw the lines, else nothing

            Args:
                event (QEvent) data relating to cause of paint event

            Returns:
                None
        """
        qw.QLabel.paintEvent(self, event)

        if self._redraw:
            self.draw_lines()
            self._redraw = False

    def draw_lines(self):
        """
        Draw the lines: iterates the _lines_base, and if COPYING_LINES,
        the iterate the_lines_new, finally draw the current line

            Returns:
                None
        """
        pen = qg.QPen(qg.QColor(qc.Qt.black), 3, qc.Qt.SolidLine)
        red_pen = qg.QPen(qg.QColor(qc.Qt.red), 3, qc.Qt.DashLine)
        new_pen = qg.QPen(qg.QColor(qc.Qt.black), 3, qc.Qt.DashLine)
        painter = qg.QPainter()

        height = self._background_pixmap.height()*self._current_zoom
        width = self._background_pixmap.width()*self._current_zoom
        pix = self._background_pixmap.scaled(width, height)

        painter.begin(pix) # make copy
        
        font = painter.font()
        font.setPointSize(font.pointSize() * 2)
        painter.setFont(font)
        
        painter.setPen(pen)
        for line in self._lines_base:
            self.draw_single_line(line, painter)

        if self._storage_state == StorageState.COPYING_LINES:
            painter.setPen(new_pen)
            for line in self._lines_new:
                self.draw_single_line(line, painter)

        if self._current_line is not None:
            painter.setPen(red_pen)
            zoomed = self._current_line.scale(self._current_zoom)
            qt_line = qc.QLine(
                qc.QPoint(int(zoomed.start.x), int(zoomed.start.y)),
                qc.QPoint(int(zoomed.end.x), int(zoomed.end.y)))
            painter.drawLine(qt_line)

        painter.end()

        self.setPixmap(pix)

    def draw_single_line(self, line, painter):
        """
        draw a single line segment

            Args:
            line (int) the array index of the line

            painter (QPainter) the painter to be used for the drawing, with pen set

            Returns:
                None
        """
        zoomed = line.scale(self._current_zoom)
        qt_line = qc.QLine(
            qc.QPoint(int(zoomed.start.x), int(zoomed.start.y)),
            qc.QPoint(int(zoomed.end.x), int(zoomed.end.y)))
        painter.drawLine(qt_line)
        if self._show_labels:
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
