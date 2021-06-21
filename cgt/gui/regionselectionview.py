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
# pylint: disable = import-error

from enum import IntEnum
from collections import namedtuple

import PyQt5.QtWidgets as qw
import PyQt5.QtGui as qg
import PyQt5.QtCore as qc

from cgt.gui.videobaseview import VideoBaseView
from cgt.util.utils import (make_positive_rect, length_squared)

## storage for a rectangle being drawn, start point + current rectangle
UnfinishedRect = namedtuple("UnfinishedRect", ["start_point", "graphics_rect"])

class SelectStates(IntEnum):
    """
    possible states of the widget
    """
    VIEW = 0
    MAKE_REGION = 2
    EDIT_REGION = 4
    DELETE_REGION = 8

class RegionSelectionView(VideoBaseView):
    """
    provides a viewer for a pixmaps
    """

    ## a rectangle needs to be shown
    show_rect = qc.pyqtSignal(qc.QRectF)

    ## stop showing the rectangle
    stop_showing_rect = qc.pyqtSignal()

    def __init__(self, parent):
        """
        set up the scene graph
        """
        super().__init__(parent)

        ##
        self._parent = parent

        ## the state
        self._state = SelectStates.VIEW

        ## the mode the rectangle being drawn
        self._draw_rect = None

        ## the store for results
        self._data_source = None

    def set_data_source(self, data_source):
        """
        setter for the results holder
            Args:
                data_source (CrystalGrowthTrackerMain) the data source
        """
        self._data_source = data_source

        if self._data_source.get_results() is not None:
            self.redisplay_regions()

    def redisplay_regions(self):
        # TODO clear old regions
        for region in self._data_source.get_results().get_regions():
            pen = self._data_source.get_pens().get_display_pen()
            region.setPen(pen)
            self.scene().addItem(region)

    def set_state(self, state):
        """
        setter for the operating state
            Args:
                state (SelectStates) the new state
        """
        self._state = state
        self._draw_rect = None
        self.scene().clearSelection()
        self.stop_showing_rect.emit()

        if self._state == SelectStates.VIEW:
            self.make_regions_selectable()
            return

        if self._state == SelectStates.EDIT_REGION:
            self.make_regions_selectable()
            return

        if self._state == SelectStates.DELETE_REGION:
            self.make_regions_selectable()
            return

        self.make_regions_selectable(False)

    def delete_selected(self):
        """
        callback for the selection of an item in the scenegraph
        """
        if self._state != SelectStates.DELETE_REGION:
            return

        items = self.scene().selectedItems()

        if len(items)==0:
            return

        item = items.pop(0)
        self.show_rect.emit(item.rect())

        mb_reply = qw.QMessageBox.question(self,
                                           self.tr('CrystalGrowthTracker'),
                                           self.tr('Do you wish to delete the selected region?'),
                                           qw.QMessageBox.Yes | qw.QMessageBox.No,
                                           qw.QMessageBox.No)

        if mb_reply == qw.QMessageBox.Yes:
            item.setSelected(False)
            self.scene().removeItem(item)
            self._data_source.remove_region(item)
            self.stop_showing_rect.emit()

    def make_regions_selectable(self, flag=True):
        """
        change the selectable status of the regions
            Args:
                flag (bool) if True items will be selectable, else not selctable
        """
        for item in self.scene().items():
            if isinstance(item, qw.QGraphicsRectItem):
                item.setFlag(qw.QGraphicsItem.ItemIsSelectable, flag)

    @qc.pyqtSlot(qg.QMouseEvent)
    def mousePressEvent(self, event):
        """
        callback for a mouse press
            Args:
                event (QMouseEvent) the event
        """
        self.test_and_select(event)

        if self._state == SelectStates.VIEW:
            self.display_selected()
            return

        if self._state == SelectStates.DELETE_REGION:
            self.delete_selected()

        if self._state == SelectStates.MAKE_REGION:
            self.mouse_down_create(event)

        if self._state == SelectStates.EDIT_REGION:
            self.mouse_down_edit(event)

    def mouse_down_edit(self, event):
        """
        respond to a mouse button press in EDIT_REGION mode
            Args:
                event (QMouseEvent) the event
        """
        items = self.scene().selectedItems()

        if len(items)>0:
            self._draw_rect = UnfinishedRect(None, items[0])
            self.mouse_event_edit(event)

    def mouse_event_edit(self, event):
        """
        handle mouse button press in EDIT_REGION mode
            Args:
                event (QMouseEvent) the event
        """
        if self._draw_rect is None:
            return

        sensitivity = 8
        limit = sensitivity*sensitivity

        # get the event location in scene and rectangle coordinates
        scene_point = self.mapToScene(event.pos())
        item_point = self._draw_rect.graphics_rect.mapFromScene(scene_point)

        # test the coreners of the old rectangle
        rect = self._draw_rect.graphics_rect.rect()

        diff = rect.topLeft() - item_point
        if length_squared(diff) < limit:
            self.new_draw_rect(rect.bottomRight(), item_point)
            return

        diff = rect.topRight() - item_point
        if length_squared(diff) < limit:
            self.new_draw_rect(rect.bottomLeft(), item_point)
            return

        diff = rect.bottomLeft() - item_point
        if length_squared(diff) < limit:
            self.new_draw_rect(rect.topRight(), item_point)
            return

        diff = rect.bottomRight() - item_point
        if length_squared(diff) < limit:
            self.new_draw_rect(rect.topLeft(), item_point)
            return

        self._draw_rect = None

    def new_draw_rect(self, start_point, moving_point):
        """
        make a new drawing rectangle
            Args:
                start_point (QPointF) the fixed point for the drawing, scene coords
                moving_point (QPointF) the point the user is moving, scene coords
        """
        rect = make_positive_rect(start_point, moving_point)
        self._draw_rect.graphics_rect.setRect(rect)
        self._draw_rect = UnfinishedRect(start_point, self._draw_rect.graphics_rect)

        self.show_rect.emit(self._draw_rect.graphics_rect.rect())

    def mouse_down_create(self, event):
        """
         down event in MAKE_REGION mode
            Args:
                event (QMouseEvent) the event
        """
        point = self.mapToScene(event.pos())

        rect = make_positive_rect(point, point)
        pen = self._data_source.get_pens().get_drawing_pen()
        rect = self.scene().addRect(rect, pen)
        self._draw_rect = UnfinishedRect(point, rect)
        self.show_rect.emit(rect.rect())

    def mouseMoveEvent(self, event):
        """
        callback for a mouse movement
            Args:
                event (QMouseEvent) the event
        """
        self.test_and_select(event)

        if self._state == SelectStates.VIEW:
            return

        if self._state == SelectStates.DELETE_REGION:
            return

        if self._state == SelectStates.MAKE_REGION:
            self.mouse_move_create(event)

        if self._state == SelectStates.EDIT_REGION:
            self.mouse_move_edit(event)

    def mouse_move_edit(self, event):
        """
        respond to a mouse movement event in EDIT_REGION mode
            Args:
                event (QMouseEvent) the event
        """
        if self._draw_rect is None:
            return

        moving_point = self.mapToScene(event.pos())

        self.new_draw_rect(self._draw_rect.start_point, moving_point)


    def mouse_move_create(self, event):
        """
        respond to a mouse movement event in MAKE_REGION mode
            Args:
                event (QMouseEvent) the event
        """
        if self._draw_rect is None:
            return

        if self._draw_rect.graphics_rect is None:
            return

        rect = make_positive_rect(self._draw_rect.start_point,
                                  self.mapToScene(event.pos()))
        self._draw_rect.graphics_rect.setRect(rect)
        self.show_rect.emit(rect)

    def mouseReleaseEvent(self, event):
        """
        callback for a mouse button release
            Args:
                event (QMouseEvent) the event
        """
        self.test_and_select(event)
        if self._state == SelectStates.VIEW:
            return

        if self._state == SelectStates.DELETE_REGION:
            return

        if self._state == SelectStates.MAKE_REGION:
            self.mouse_up_create(event)

        if self._state == SelectStates.EDIT_REGION:
            self.mouse_up_edit(event)

        self.scene().clearSelection()

    def mouse_up_create(self, event):
        """
        respond to a user releasing the mouse button in MAKE_REGION mode
            Args:
                event (QMouseEvent) the event
        """
        if self._draw_rect is None:
            return

        rect = make_positive_rect(self._draw_rect.start_point,
                                  self.mapToScene(event.pos()))
        self._draw_rect.graphics_rect.setRect(rect)
        pen = self._data_source.get_pens()
        self._draw_rect.graphics_rect.setPen(pen.get_display_pen())

        self._data_source.append_region(self._draw_rect.graphics_rect)

        self._draw_rect = None

    def mouse_up_edit(self, event):
        """
        respond to a user releasing the mouse button in EDIT_REGION mode
            Args:
                event (QMouseEvent) the event
        """
        if self._draw_rect is None:
            return

        self.mouse_event_edit(event)
        self._draw_rect = None

    def display_selected(self):
        """
        if a rectangle is selected, emit the rectangl using the show_rect signal
        """
        items = self.scene().selectedItems()

        if len(items) <= 0:
            self.stop_showing_rect.emit()
            return

        rect = items[0].rect()
        self.show_rect.emit(rect)

    def test_and_select(self, event):
        """
        test if a mouse event was in a region and if so select the region
            Agrs:
                event (QMouseEvent) the event
        """
        point = self.mapToScene(event.pos())

        self.scene().clearSelection()

        for item in self.scene().items():
            if isinstance(item, qw.QGraphicsRectItem):
                if item.contains(point):
                    item.setSelected(True)
                    return

        self.stop_showing_rect.emit()
