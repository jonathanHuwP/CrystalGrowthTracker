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
# pylint: disable = too-many-public-methods
# pylint: disable = c-extension-no-member

# TODO handel out of pixmap move/release
# move => freaze untill back
# release => delete and reset

import numpy as np

import PyQt5.QtWidgets as qw
import PyQt5.QtGui as qg
import PyQt5.QtCore as qc

class RegionSelectionLabel(qw.QLabel):
    """
    subclass of label allowing selection of region by drawing rectangle and
    displaying a list of already selected rectangles.
    """
    
    ## signal to indicate the user has selected a new rectangle
    have_rectangle = qc.pyqtSignal()
    
    ## signal to indicate the user has deleted the rectangle
    rectangle_deleted = qc.pyqtSignal()
    
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
        
        ## flag for the creation of a new rectangle
        self._new_rectangle = False

        ## the translated name
        self._translation_name = self.tr("RegionSelectionLabel")
        
    def get_rectangle(self):
        """
        getter for the rectangle
            Returns:
                pointer to the rectangle or None
        """
        return self._rectangle
        
    def clear(self):
        """
        delete the current rectangle and repaint
        """
        self._rectangle = None
        self.rectangle_deleted.emit()
        self.repaint()
        
    def mousePressEvent(self, event):
        """
        detect the start of selection

            Args:
                event (QEvent) the event data

            Returns:
                None
        """
        if self._parent.is_playing():
            return
            
        if event.button() == qc.Qt.LeftButton and self._rectangle is None:
            pix_rect = self.pixmap().rect()
            point = event.pos()
            if pix_rect.contains(point): # test if envent in pixmap
                size = qc.QSize(0,0)
                self._rectangle = qc.QRect(point, size)
                self._new_rectangle = True
                self.repaint()
                
        elif event.button() == qc.Qt.RightButton and self._rectangle is not None:
            message = self.tr("Do you wish to remove the region?")
            mb_reply = qw.QMessageBox.question(self,
                                               'CrystalGrowthTracker',
                                               message,
                                               qw.QMessageBox.Yes | qw.QMessageBox.No,
                                               qw.QMessageBox.No)
            if mb_reply == qw.QMessageBox.Yes:
                self._rectangle = None
                self._new_rectangle = False
                self.rectangle_deleted.emit()

    def mouseMoveEvent(self, event):
        """ting draw rectangle

            Args:
                event (QEvent) the event data

            Returns:
                None
        """
        if self._parent.is_playing():
            return
            
        # use buttons() for mouse move as more than one can be held
        if event.buttons() != qc.Qt.LeftButton:
            return
            
        if self._rectangle is not None and self._new_rectangle:
            self._rectangle.setBottomRight(event.pos())
            self.repaint()

    def mouseReleaseEvent(self, event):
        """
        select rectangle

            Args:
                event (QEvent) the event data

            Returns:
                None
        """
        if self._parent.is_playing():
            return
            
        if event.button() != qc.Qt.LeftButton:
            return
            
        if self._rectangle is not None and self._new_rectangle:
            self.have_rectangle.emit()
            self._new_rectangle = False
            self.repaint()
            
    def paintEvent(self, event):
        """
        if selecting than draw a rectagle

            Args:
                event (QEvent) the event data

            Returns:
                None
        """
        print("paint")
        # pass on to get pixmap displayed
        qw.QLabel.paintEvent(self, event)

        self.draw_rectangle()
            
    def draw_rectangle(self):
        """
        Draw the rectagle

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
        painter.drawRect(self._rectangle)
        s = self._rectangle.size()
        print(f"draw {s.height()} {s.width()}")
        
