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
# pylint: disable = import-error

from enum import IntEnum

import PyQt5.QtWidgets as qw
import PyQt5.QtGui as qg
import PyQt5.QtCore as qc

class CreateStates(IntEnum):
    """
    the possible states of the widget when creating a region
    """
    READY_TO_MAKE = 0
    MAKING = 2
    FINISHED_MAKING = 4

def rectangle_properties(rectangle):
    """
    find the top left, bottom right and centre of a rectangle
        Args:
            rectangle (QRect) the rectangle
        Returns:
            top left, top right, bottom left, bottom right, centre (QPoint)
    """
    top_left = rectangle.topLeft()
    top_right = rectangle.topRight()
    bottom_left = rectangle.bottomLeft()
    bottom_right = rectangle.bottomRight()
    ctr = top_left + bottom_right
    ctr /= 2

    return top_left, top_right, bottom_left, bottom_right, ctr

class RegionCreationLabel(qw.QLabel):
    """
    subclass of label allowing selection of region by drawing rectangle and
    displaying a list of already selected rectangles.
    """

    ## signal to indicate the user has selected a new rectangle
    have_rectangle = qc.pyqtSignal()

    ## signal to indicate the user has deleted the rectangle
    rectangle_deleted = qc.pyqtSignal()

    ## signal to store the current rectangle
    store_rectangle = qc.pyqtSignal()

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
        return self._rectangle

    def clear(self):
        """
        delete the current rectangle and repaint
        """
        self._rectangle = None
        self.repaint()
        self.rectangle_deleted.emit()

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

        if self._create_state == CreateStates.READY_TO_MAKE:
            self.mouse_press_create(event)
        elif self._create_state == CreateStates.FINISHED_MAKING:
            self.save_discarde_options()

    def mouse_press_create(self, event):
        """
        handle mouse press when in crate mode
            Args:
                event (QEvent) the event data
        """
        pix_rect = self.pixmap().rect()
        if pix_rect.contains(event.pos()): # test if event in pixmap
            size = qc.QSize(0,0)
            point = self._inverse_zoom.map(event.pos())
            self._rectangle = qc.QRect(point, size)
            self._create_state = CreateStates.MAKING
            self.repaint()

    def save_discarde_options(self):
        """
        responde to a mouse when a region has been created
            Args:
                event (QEvent) the event data
        """
        message = self.tr("Do you wish to store the region for further use, or delete?")
        title = self.tr("CrystalGrowthTracker")
        m_box = qw.QMessageBox(self)
        m_box.setText(message)
        m_box.setWindowTitle(title)
        button_store = m_box.addButton(self.tr("Store"), qw.QMessageBox.YesRole)
        button_cancel = m_box.addButton(self.tr("Cancel"), qw.QMessageBox.RejectRole)
        m_box.addButton(self.tr("Delete"), qw.QMessageBox.NoRole) #fall through option

        m_box.exec()
        reply = m_box.clickedButton()

        if reply == button_cancel:
            return

        if m_box.clickedButton() == button_store:
            self.store_rectangle.emit()
            print("Label: Store the region")

        # for store or delete clear and reset
        self._rectangle = None
        self._create_state = CreateStates.READY_TO_MAKE

    def mouseMoveEvent(self, event):
        """
        respond to a mouse movement

            Args:
                event (QEvent) the event data

            Returns:
                None
        """
        if self._parent.is_playing() or event.buttons() != qc.Qt.LeftButton:
            return

        if self._rectangle is None:
            return

        if self._create_state == CreateStates.MAKING:
            point = self._inverse_zoom.map(event.pos())
            self._rectangle.setBottomRight(point)
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

        if self._create_state == CreateStates.MAKING:
            size = self._rectangle.size()
            diagonal = size.width()*size.width() + size.height()*size.height()
            if diagonal < 8:
                self._rectangle = None
                self._create_state = CreateStates.READY_TO_MAKE
            else:
                self._create_state = CreateStates.FINISHED_MAKING
                self.have_rectangle.emit()
                self.save_discarde_options()
            self.repaint()

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

        pen = qg.QPen(qg.QColor(255, 7, 58), 2, qc.Qt.DashLine)
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
