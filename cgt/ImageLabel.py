# -*- coding: utf-8 -*-
"""
Created on Wed Jun 10 11:28:23 2020

@author: j.h.pickering@leeds.ac.uk
"""

import lazylogger
from DrawRect import DrawRect

import PyQt5.QtWidgets as qw
import PyQt5.QtGui as qg
import PyQt5.QtCore as qc
import numpy as np

class ImageLabel(qw.QLabel):
    """
    subclass of label allowing selection of region by drawing rectangle and 
    displaying a list of already selected rectangles.
    """
    def __init__(self, parent=None):
        """
        Set up the label
        """
        super(qw.QLabel, self).__init__()
        self._parent = parent
        self.NAME = self.tr("ImageLabel")
        
        self._selecting = False
        self._start = None
        self._end = None
        
        self._rectangles = []
        
        self._logger = lazylogger.logging.getLogger(self.NAME)
        self._logger.setLevel(lazylogger.logging.WARNING)       
        
    def __iter__(self):
        return iter(self._rectangles)
        
    # signal to indicate user selection
    new_selection = qc.pyqtSignal()

    def mousePressEvent(self, e):
        """
        detect the start of selection
        """
        if e.button() == qc.Qt.LeftButton:
            if not self._selecting:
                self._selecting = True
                self._start = e.pos()
        
    def mouseMoveEvent(self, e):
        """
        If selecting draw rectangle
        """
        if self._selecting:
            self._end = e.pos()
            self.repaint()
            
    def mouseReleaseEvent(self, e):
        """
        select rectangle
        """
        if e.button() == qc.Qt.LeftButton and self._selecting:
            self._end = e.pos()
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
        # get horizontal range
        horiz = (self._start.x(), self._end.x())
        zoom = self._parent.get_zoom()
        
        sh = np.uint32(np.round(min(horiz)/zoom))
        eh = np.uint32(np.round(max(horiz)/zoom))
        
        # get vertical range
        vert = (self._start.y(), self._end.y())
        sv = np.uint32(np.round(min(vert)/zoom))
        ev = np.uint32(np.round(max(vert)/zoom))
                
        # add the rectangle to the ImageLabel

        rect = DrawRect(sv, ev, sh, eh)

        self._rectangles.append(rect)
        self.new_selection.emit()
            
    def paintEvent(self, e):
        """
        if selecting than draw a rectagle
        """
        qw.QLabel.paintEvent(self, e)
        
        self.draw_rectangles()
        
    def draw_rectangles(self):
        """
        Draw the alreay selected rectangles and, if in selecting mode
        the current selection

        Returns
        -------
        None.
        """
        if not self._selecting and not len(self._rectangles):
            return
        
        pen = qg.QPen(qg.QColor(qc.Qt.black), 1, qc.Qt.DashLine)
        brush = qg.QBrush(qg.QColor(255,255,255,120))
        painter = qg.QPainter(self)
        painter.setPen(pen)
        painter.setBrush(brush)
        
        for rect in self._rectangles:
            zoomed = rect.scale(self._parent.get_zoom())
            qr = qc.QRect(
                qc.QPoint(int(zoomed.left), int(zoomed.top)), 
                qc.QPoint(int(zoomed.right), int(zoomed.bottom)))
            
            painter.drawRect(qr)
        
        if self._selecting:
            selectionRect = qc.QRect(self._start, self._end)
            painter.drawRect(selectionRect)
            
    @property
    def number_rectangles(self):
        """
        getter for the number of rectangles

        Returns
        -------
        int
            the number of rectangles currently stored.
        """
        return len(self._rectangles)
    
    def get_rectangle(self, index):
        return self._rectangles[index]
        