# -*- coding: utf-8 -*-
"""
Created on Friday July 10 13:42: 2020

@author: j.h.pickering@leeds.ac.uk
"""

import PyQt5.QtWidgets as qw
import PyQt5.QtGui as qg
import PyQt5.QtCore as qc
import numpy as np

from enum import IntEnum

# a state for the user interaction with the lines
class WidgetState(IntEnum):
    DRAWING   = 10
    ADJUSTING = 20

# a state for the objective 
class StorageState(IntEnum):
    CREATING_LINES = 10
    COPYING_LINES  = 20

# a state for the adjusting 
class AdjustingState(IntEnum):
    LINE  = 10
    START = 20
    END   = 30
    
from image_artifacts import ImagePoint, ImageLineSegment

class DrawingLabel(qw.QLabel):
    """
    subclass of label providing functions for drawing using a mouse.
    """
    def __init__(self, parent=None):
        """
        Set up the label
        """
        super(qw.QLabel, self).__init__()
        self._parent = parent
        self.NAME = self.tr("DrawingLabel")
        
        self._state = WidgetState.DRAWING
        self._storageState = StorageState.CREATING_LINES
        
        self._start = None
        self._end = None
        self._currentZoom = 1.0
        self._mouseLeftDown = False
        self._redraw = True
        self._adjustLine = True # if true the whole line is shifted
        self._adjustIndex = 0
        self._showLabels = False
        
        self._linesBase = []
        self._linesNew = []
        
        self._currentLine = None
        
        self.setAlignment(
                qc.Qt.AlignTop | qc.Qt.AlignLeft)
        self.setSizePolicy(
                qw.QSizePolicy.Ignored, qw.QSizePolicy.Fixed)
        self.setSizePolicy(
                qw.QSizePolicy.Minimum, qw.QSizePolicy.Minimum)
        
    def setBackgroudPixmap(self, pix):
        self._background = pix
    
    @property
    def state(self):
        return self._state

    @property
    def storageState(self):
        return self._storageState  
        
    @property
    def size(self):
        """
        getter for the number of line segments

        Returns
        -------
        tuple 
            (the number of line segments in base, the number in the new list)
        """
        return (len(self._linesBase), len(self._linesNew))
        
    @property
    def linesBase(self):
        return self._linesBase
        
    @property
    def linesNew(self):
        return self._linesNew
        
    def setDrawing(self):
        print("drawing")
        self._state = WidgetState.DRAWING
        
    def setAdjusting(self):
        self._state = WidgetState.ADJUSTING
    
    def setCreating(self):
        self._storageState = StorageState.CREATING_LINES
        
    def setCopying(self):
        self._storageState = StorageState.COPYING_LINES

    def setZoom(self, value):
        self._currentZoom = value
        self._redisplay()
        
    def showLabels(self, flag):
        self._showLabels = flag
        self._redisplay()

    @qc.pyqtSlot()
    def mousePressEvent(self, e):
        """
        detect the start of selection
        """
        if self._state == WidgetState.DRAWING:
            if e.button() == qc.Qt.LeftButton:
                self._start = e.pos()
                self._mouseLeftDown = True
            else:
                pass
            self._redisplay()
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

            self._redisplay()
            
    def pick_artifact(self, position, radius=5):
        """
        1. define radius in pixels around click event location
        2. Test all end point to see if they lie in radius 
            if one or more found return the closest end point (index, start/end)
        3. Test for any lines passing within radius of event
            if one or more found return the closest line index
    
        return type (line index, endpoint = None)
        """
        tp = self.test_points(position, radius)
        if tp is not None:
            return tp
        
        tl = self.test_lines(position, radius)
        if tl is not None:
            return tl
    
        return None

    def test_points(self, position, radius):
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
        If selecting draw rectangle
        """
        if self._state == WidgetState.DRAWING and self._mouseLeftDown:
            self._end = e.pos()
            self.make_line()
            self._redisplay()
            
        elif self._state == WidgetState.ADJUSTING and self._mouseLeftDown:
            self.alterChosenLine(e)

    def alterChosenLine(self, event):
        if self._adjustLine == AdjustingState.LINE:
            self.shiftChosenLine(event)
        else:
            self.moveChosenLineEnd(event)
            
    def moveChosenLineEnd(self, event):
        pt = ImagePoint(event.x(), event.y())
        if self._adjustLine == AdjustingState.START:
            self._currentLine = self._linesBase[self._adjustIndex].newStart(pt)
        else:
            self._currentLine = self._linesBase[self._adjustIndex].newEnd(pt)

        self._redisplay()

    def shiftChosenLine(self, event):
        shift_qt = event.pos() - self._start
        shift_vec = ImagePoint(shift_qt.x(), shift_qt.y())
        self._currentLine = self._linesBase[self._adjustIndex].shift(shift_vec)

        self._redisplay()

    @qc.pyqtSlot()    
    def mouseReleaseEvent(self, e):
        """
        select rectangle
        """
        if not e.button() == qc.Qt.LeftButton:
            return
        
        if self._state == WidgetState.DRAWING:
            self._end = e.pos()
            self.make_line()
            self._redisplay()
            reply = qw.QMessageBox.question(
                    self,
                    self.tr("Create Line"),
                    self.tr("Do you wish to save the line?"))
            
            if reply == qw.QMessageBox.Yes:
                self.add_line()

            self.clear_current()
            self._redisplay()
            
        elif self._state == WidgetState.ADJUSTING and self._currentLine is not None:
            self.adjustingRelease()
            
        self._mouseLeftDown = False
        
    def adjustingRelease(self):
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
        self._redisplay()
            
    def make_line(self):
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
        self._start = None
        self._end = None
        self._currentLine = None
        
    def add_line(self):
        if self._currentLine is None:
            return
        
        self._linesBase.append(
            self._currentLine.relabel(str(len(self._linesBase))))

    def _redisplay(self):
        self._redraw = True
        self.repaint()
        
    @qc.pyqtSlot()
    def paintEvent(self, e):
        """
        if selecting than draw a rectagle
        """
        qw.QLabel.paintEvent(self, e)

        if self._redraw:
            self.draw_lines()
            self._redraw = False
        
    def draw_lines(self):
        """
        Draw the lines

        Returns
        -------
        None.
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

        Parameters
        ----------
        file : PyQt5.QtCore.QFile
            the file for writing.

        Returns
        -------
        None.
        """

        file.open(qc.QIODevice.WriteOnly)
        self.pixmap().save(file, "PNG")
        
