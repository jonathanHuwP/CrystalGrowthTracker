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

from enum import IntEnum

import PyQt5.QtWidgets as qw
import PyQt5.QtGui as qg
import PyQt5.QtCore as qc

from enum import IntEnum

from cgt.util.utils import rectangle_properties

from cgt.gui.videoregionselectionwidgetstates import VideoRegionSelectionWidgetStates as states

class CreateStates(IntEnum):
    """
    the possible states of the widget when creating a region
    """
    READY_TO_MAKE = 0
    MAKING = 2
    FINISHED_MAKING = 4

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
        self._create_state = CreateStates.READY_TO_MAKE

        ## flag to signal that an adjusement is underway
        self._adjustment_underway = False

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
        if self._rectangle is None:
            return None

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
        if self._parent.is_playing() or event.button() != qc.Qt.LeftButton:
            return
            
        mode = self._parent.get_operating_mode()

        if mode == states.DISPLAY:
            return

        if mode == states.CREATE:
            self.mouse_press_create(event)
        elif mode == states.EDIT:
            self.mouse_press_edit(event)
        elif mode == states.DELETE:
            self.mouse_press_delete(event)
            
    def mouse_press_create(self, event):
        """
        handle mouse press when in crate mode
            Args:
                event (QEvent) the event data
        """
        print("mouse press create")

        if self._rectangle is None:
            pix_rect = self.pixmap().rect()
            if pix_rect.contains(event.pos()): # test if event in pixmap
                size = qc.QSize(0,0)
                point = self._inverse_zoom.map(event.pos())
                self._rectangle = qc.QRect(point, size)
                self._create_state = CreateStates.MAKING
                self.repaint()
                
    def mouse_press_edit(self, event):
        """
        handel mouse press when in adjusting mode
        """
        print("mouse press edit")
        if event.button() == qc.Qt.LeftButton and self._rectangle is not None:
            
            self._adjustment_underway = True
            
    def mouse_press_delete(self, event):
        """
        responde to a mouse press in delet mode
            Args:
                event (QEvent) the event data
        """
        print("mouse press delete")
        if self._rectangle is not None:
            message = self.tr("Do you wish to remove the region?")
            mb_reply = qw.QMessageBox.question(self,
                                               'CrystalGrowthTracker',
                                               message,
                                               qw.QMessageBox.Yes | qw.QMessageBox.No,
                                               qw.QMessageBox.No)
            if mb_reply == qw.QMessageBox.Yes:
                self._rectangle = None
                self._create_state = CreateStates.READY_TO_MAKE
                self.rectangle_deleted.emit()

    def mouseMoveEvent(self, event):
        """
        respond to a mouse movement

            Args:
                event (QEvent) the event data

            Returns:
                None
        """
        if self._parent.is_playing() or event.button() == qc.Qt.LeftButton:
            return

        if self._rectangle is None:
            return
           
        # use buttons() for mouse move as more than one can be held
        if event.buttons() != qc.Qt.LeftButton:
            return
            
        mode = self._parent.get_operating_mode()

        if mode == states.DISPLAY:
            return

        if self._parent.get_operating_mode() == states.CREATE:
            print(f"moveing {CreateStates(self._create_state).name}")
            if self._create_state == CreateStates.MAKING:
            
                point = self._inverse_zoom.map(event.pos())
                self._rectangle.setBottomRight(point)
                self.repaint()

        elif self._parent.get_operating_mode() == states.EDIT:
            if self._adjustment_underway:
                print("move adjusing")

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
            
        mode = self._parent.get_operating_mode()

        if mode == states.DISPLAY:
            return
            
        if self._parent.get_operating_mode() == states.CREATE:
            self.mouse_up_creating(event)
            return
            
        if self._parent.get_operating_mode() == states.EDIT:
            self.mouse_up_adjusting(event)
            return
            
    def mouse_up_creating(self, event):
        """
        respond to a mouse up event in crating mode
            Args:
                event (QEvent) the event object
        """
        if event.button() != qc.Qt.LeftButton:
            return

        print(f"mouse up {CreateStates(self._create_state).name}")
        if self._create_state == CreateStates.MAKING:
            size = self._rectangle.size()
            diagonal = size.width()*size.width() + size.height()*size.height()
            if diagonal < 8:
                self._rectangle = None
                self._create_state = CreateStates.READY_TO_MAKE
            else:
                self.have_rectangle.emit()
                self._create_state = CreateStates.FINISHED_MAKING
            self.repaint()

    def mouse_up_adjusting(self, event):
        """
        mouse up in adjustment mode
        """
        if event.button() != qc.Qt.LeftButton:
            return

        self._adjustment_underway = False

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
