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
# pylint: disable = too-many-public-methods
# pylint: disable = too-few-public-methods
# pylint: disable = too-many-instance-attributes

from enum import IntEnum
from itertools import count

import PyQt5.QtGui as qg
import PyQt5.QtCore as qc
import PyQt5.QtWidgets as qw

from cgt.gui.videobaseview import VideoBaseView
from cgt.util.utils import (hash_graphics_line,
                            hash_graphics_point,
                            get_marker_type,
                            MarkerTypes,
                            ItemDataTypes,
                            make_cross_path,
                            hash_marker)

## containger of moving a marker
class MarkerInMotion():
    """
    storage for a marker in the process of bing moved
    """
    def __init__(self, start_point, marker):
        """
        store the start point of the drag and the marker
            Args:
                start_point (QPointF) the drawing tool down point
                marker the graphics item
        """
        self.start_point = start_point
        self.marker = marker

    def move_to(self, point):
        """
        the item has moved so move the marker
            Args:
                point (QPointF) the new drag point
        """
        move = point - self.start_point
        self.start_point = point
        self.marker.moveBy(move.x(), move.y())

class MarkUpStates(IntEnum):
    """
    enumeration of possible states of the view
    """
    ## draw lines in the scene
    DRAW_LINES = 0

    ## draw crosses on the scene
    DRAW_CROSS = 1

    ## move and copy items
    CLONE_ITEM = 2

    ## delete item
    DELETE_ITEM = 3

    ## no activity allowed
    VIEW_ONLY = 4

class MarkUpView(VideoBaseView):
    """top level application"""

    def __init__(self, parent):
        """
        initialize a main window and start event loop
        """
        super().__init__(parent)

        ## the parent widget, set seperatly as setupUi only provides QWidget
        self._parent = None

        ## the state true = lines, false = crosses
        self._state = MarkUpStates.DRAW_LINES

        ## display arrow or not
        self._arrows = True

        ## the index of the region used to define the current pixmap
        self._region_index = None

        ## the current line
        self._draw_line = None

        ## the currently moving item
        self._current_clone = None

        ## marker to out arrow hash(marker) => out arrow
        self._marker_arrow = {}

        ## the pens used in drawing
        self._pens = None

        ## simulate real frames
        self._time_simulation = count(start = 1)

    def set_parent_and_pens(self, parent_widget, pens):
        """
        setter for the parent widget, and the pen store
            Args:
                parent_widget (MarkupWidget) the
                pens (PenStore) the pens
        """
        self._parent = parent_widget
        self._pens = pens

    def clear(self):
        """
        clear the scene and reset instance variables
        """
        self._region_index = None
        for item in self.scene().items():
            if get_marker_type(item) in (MarkerTypes.LINE, MarkerTypes.POINT):
                self.scene().removeItem(item)
        super().clear()

    def set_pixmap(self, pixmap, frame_number, region_index):
        """
        set the pixamp
            Args:
                pixmap (QPixmap) the pixmap
                frame_number (int) the number of the frame in the video
                region_index (int) the index of the region used to define the pixmap
        """
        super().set_pixmap(pixmap, frame_number)
        self._region_index = region_index

    @qc.pyqtSlot(qg.QMouseEvent)
    def mousePressEvent(self, event):
        """
        callback for a mouse press
            Args:
                event (QMouseEvent) the event
        """
        if self._state == MarkUpStates.VIEW_ONLY:
            return

        if event.button() == qc.Qt.MiddleButton:
            return

        left_button = (event.button() == qc.Qt.LeftButton)

        self.scene().clearSelection()
        if self._state == MarkUpStates.DRAW_LINES and left_button:
            self.start_line(self.mapToScene(event.pos()))
        elif self._state == MarkUpStates.DRAW_CROSS and left_button:
            self.add_cross(self.mapToScene(event.pos()))
        elif self._state == MarkUpStates.CLONE_ITEM and left_button:
            self._current_clone = self.select_and_clone_marker(event)
            if self._current_clone is None:
                return
            self.scene().addItem(self._current_clone.marker)
        elif self._state == MarkUpStates.DELETE_ITEM:
            if left_button:
                target = self.select_marker(event)
            else:
                target = self.menu_select_marker(event)
            if target is None:
                return
            target.setSelected(True)
            self.user_choice_delete_item(target)

    def menu_select_marker(self, event):
        """
        select a marker from a menu
            Args:
                event (QMouseEvent) the event
        """
        item_actions = {}
        menu = qw.QMenu(self)

        line_count = 0
        point_count = 0

        for item in self.scene().items():
            item_type = get_marker_type(item)
            if item_type == MarkerTypes.LINE:
                item_actions[menu.addAction(f"Line {line_count}")] = item
                line_count += 1
            elif item_type == MarkerTypes.POINT:
                item_actions[menu.addAction(f"Point {point_count}")] = item
                point_count += 1

        menu.addAction(self.tr("Cancel"))

        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action in item_actions.keys():
            item_actions[action].setSelected(True)
            return item_actions[action]

        return None

    def select_marker(self, event):
        """
        select the artifact under the event, if there is one
            Returns:
                the artifact (QGraphicsItem) or None
        """
        point = self.mapToScene(event.pos())

        items_at_position = self.scene().items(point)

        if len(items_at_position) == 0:
            return None

        # return the first item that is a line or a path
        for item in items_at_position:
            item_type = get_marker_type(item)
            if item_type in (MarkerTypes.LINE, MarkerTypes.POINT):
                return item

        return None

    def select_and_clone_marker(self, event):
        """
        select the artifact under the event, if there is one
        """
        item = self.select_marker(event)

        if item is None:
            return None

        clone = self.moving_clone(item)
        clone.setFlag(qw.QGraphicsItem.ItemIsSelectable)
        clone.setSelected(True)
        clone.setFlag(qw.QGraphicsItem.ItemIsMovable)

        point = self.mapToScene(event.pos())
        return MarkerInMotion(point, clone)

    @qc.pyqtSlot(qg.QMouseEvent)
    def mouseMoveEvent(self, event):
        """
        callback for a mouse press
            Args:
                event (QMouseEvent) the event
        """
        if self._state == MarkUpStates.VIEW_ONLY:
            return

        if event.buttons() != qc.Qt.LeftButton:
            return

        point = self.mapToScene(event.pos())

        if self._state == MarkUpStates.DRAW_LINES:
            self.extend_line(point)
        elif self._state == MarkUpStates.CLONE_ITEM:
            if self._current_clone is not None:
                self._current_clone.move_to(point)

    @qc.pyqtSlot(qg.QMouseEvent)
    def mouseReleaseEvent(self, event):
        """
        callback for a mouse press
            Args:
                event (QMouseEvent) the event
        """
        if self._state == MarkUpStates.VIEW_ONLY:
            return

        if event.button() != qc.Qt.LeftButton:
            return

        if self._state == MarkUpStates.DRAW_LINES:
            self.finish_line(self.mapToScene(event.pos()))
        elif self._state == MarkUpStates.CLONE_ITEM:
            if self._current_clone is not None:
                reply = qw.QMessageBox.question(self,
                                                self.tr("Clone?"),
                                                self.tr("Do you wish to clone marker?"),
                                                qw.QMessageBox.Yes|qw.QMessageBox.No,
                                                qw.QMessageBox.No)

                if reply == qw.QMessageBox.Yes:
                    self._current_clone.marker.setSelected(False)
                    self._current_clone.marker.setPen(self._pens.get_display_pen() )
                    self._current_clone.marker.setFlag(qw.QGraphicsItem.ItemIsMovable, False)
                    self._parent.add_marker(self._current_clone.marker)
                else:
                    self.scene().removeItem(self._current_clone.marker)

                self._current_clone = None

    def start_line(self, point):
        """
        start drawing a new line artifact
            Args:
                point (QPointF) start point in scene coordinates
        """
        line = qc.QLineF(point, point)
        self._draw_line = self.scene().addLine(line, self._pens.get_drawing_pen())
        self._draw_line.setData(ItemDataTypes.ITEM_TYPE, MarkerTypes.LINE)
        self._draw_line.setData(ItemDataTypes.PARENT_HASH, "p")
        self._draw_line.setData(ItemDataTypes.REGION_INDEX, self._region_index)
        self._draw_line.setData(ItemDataTypes.FRAME_NUMBER, self._current_frame)

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
        self._draw_line.setPen(self._pens.get_display_pen())
        self._parent.add_line(self._draw_line)
        self._draw_line = None

    def add_cross(self, point):
        """
        add a cross to the scene and to the data store
            Args:
                point (QPointF) location in scene coordinates
        """

        cross = self.display_cross(point)
        self._parent.add_point(cross)

    def display_cross(self, point):
        """
        add a cross to the scene, but not the data store
            Args:
                point (QPointF) location in scene coordinates
        """
        path = make_cross_path(point)

        cross = self.scene().addPath(path, self._pens.get_display_pen())
        cross.setData(ItemDataTypes.ITEM_TYPE, MarkerTypes.POINT)
        cross.setData(ItemDataTypes.PARENT_HASH, "p")
        cross.setData(ItemDataTypes.FRAME_NUMBER, self._current_frame)
        cross.setData(ItemDataTypes.REGION_INDEX, self._region_index)
        cross.setData(ItemDataTypes.CROSS_CENTRE, point)

        return cross

    def add_arrow(self, arrow, arrow_head, extension):
        """
        add a graphics_item to the scenegraph
            Args:
                graphics_item (QGraphicsItem) the item
        """
        g_arrow = self.scene().addLine(arrow, self._pens.get_highlight_pen())
        g_arrow.setData(ItemDataTypes.ITEM_TYPE, MarkerTypes.DECORATOR)

        g_head = None
        if arrow_head is not None:
            g_head = self.scene().addPolygon(arrow_head,
                                             self._pens.get_highlight_pen(),
                                             self._pens.get_highlight_brush())
            g_head.setData(ItemDataTypes.ITEM_TYPE, MarkerTypes.DECORATOR)

        g_extension = None
        if extension is not None:
            self._pens.set_highlight_dashed()
            g_extension = self.scene().addLine(extension,
                                               self._pens.get_highlight_pen())
            self._pens.set_highlight_solid()
            g_extension.setData(ItemDataTypes.ITEM_TYPE, MarkerTypes.DECORATOR)

        return (g_arrow, g_head, g_extension)

    @qc.pyqtSlot(int)
    def set_state(self, value):
        """
        set the drawing state
            Args:
                value (int) if 0 draw lines, else crosses
        """
        if value == 0:
            self.assign_state(MarkUpStates.DRAW_LINES)
        elif value == 1:
            self.assign_state(MarkUpStates.DRAW_CROSS)
        elif value == 2:
            self.assign_state(MarkUpStates.CLONE_ITEM)
        elif value == 3:
            self.assign_state(MarkUpStates.DELETE_ITEM)
        else:
            self.assign_state(MarkUpStates.VIEW_ONLY)

    def assign_state(self, state):
        """
        assign a new drawing state, changing selectability
            Args:
                state (MarkUpStates) the new state
        """
        self._state = state

        no_select = (MarkUpStates.DRAW_LINES,
                     MarkUpStates.DRAW_CROSS,
                     MarkUpStates.VIEW_ONLY)

        if self._state in no_select:
            self.make_selectable(False)
        else:
            self.make_selectable()

    def get_state(self):
        """
        getter for the state
            Returns:
                current state (MarkUpStates)
        """
        return self._state

    def make_selectable(self, flag=True):
        """
        make lines and crosses selectable
            Args:
                flag (bool) if True make selectable, else not selectable
        """
        for item in self.scene().items():
            flag = get_marker_type(item)
            if flag in (MarkerTypes.LINE, MarkerTypes.POINT):
                item.setFlag(qw.QGraphicsItem.ItemIsSelectable, flag)

    def moving_clone(self, item):
        """
        clone a line or cross
            Args:
                item (QGraphicsItem) the item to clone
            Returns:
                if item is Line or path a clone else None
        """
        item_type = get_marker_type(item)

        if item_type == MarkerTypes.LINE:
            line = item.line()
            graph_line = qw.QGraphicsLineItem(line)
            graph_line.setPos(item.pos())
            graph_line.setPen(self._pens.get_drawing_pen())

            graph_line.setData(ItemDataTypes.ITEM_TYPE, item_type)
            graph_line.setData(ItemDataTypes.PARENT_HASH, hash_graphics_line(item))
            graph_line.setData(ItemDataTypes.FRAME_NUMBER, self._current_frame)
            graph_line.setData(ItemDataTypes.REGION_INDEX, self._region_index)
            return graph_line

        if item_type == MarkerTypes.POINT:
            path = item.path()
            centre = item.data(ItemDataTypes.CROSS_CENTRE)
            graph_path = qw.QGraphicsPathItem(path)
            graph_path.setPos(item.pos())
            graph_path.setPen(self._pens.get_drawing_pen())

            graph_path.setData(ItemDataTypes.ITEM_TYPE, item_type)
            graph_path.setData(ItemDataTypes.PARENT_HASH, hash_graphics_point(item))
            graph_path.setData(ItemDataTypes.FRAME_NUMBER, self._current_frame)
            graph_path.setData(ItemDataTypes.REGION_INDEX, self._region_index)
            graph_path.setData(ItemDataTypes.CROSS_CENTRE, centre)
            return graph_path

        return None

    def insert_marker_lines(self, lines):
        """
        insert a marker consisting of lines
            Args:
                lines [tuple] list of lists of values
        """
        progenitor = lines[0]
        line = qc.QLineF(progenitor[1], progenitor[2], progenitor[3], progenitor[4])
        position = qc.QPointF(progenitor[5], progenitor[6])
        tmp_line = self.scene().addLine(line, self._pens.get_display_pen())
        tmp_line.setData(ItemDataTypes.PARENT_HASH, "p")
        tmp_line.setData(ItemDataTypes.REGION_INDEX, self._region_index)
        tmp_line.setData(ItemDataTypes.FRAME_NUMBER, progenitor[7])

        for data in lines[1:]:
            line = qc.QLineF(data[1], data[2], data[3], data[4])
            position = qc.QPointF(data[5], data[6])
            p_hash = hash_graphics_line(tmp_line)
            tmp_line = self.scene().addLine(line, self._pens.get_display_pen())
            tmp_line.setPos(position)
            tmp_line.setData(ItemDataTypes.PARENT_HASH, p_hash)
            tmp_line.setData(ItemDataTypes.REGION_INDEX, self._region_index)
            tmp_line.setData(ItemDataTypes.FRAME_NUMBER, data[7])

    def insert_marker_points(self, points):
        """
        insert a marker consisting of points
            Args:
                points [tuple] list of lists of values
        """
        progenitor = points[0]
        centre = qc.QPointF(progenitor[1], progenitor[2])
        position = qc.QPointF(progenitor[3], progenitor[4])

        path = make_cross_path(centre)
        tmp_point = self.scene().addPath(path, self._pens.get_display_pen())
        tmp_point.setData(ItemDataTypes.PARENT_HASH, "p")
        tmp_point.setData(ItemDataTypes.FRAME_NUMBER, progenitor[5])
        tmp_point.setData(ItemDataTypes.REGION_INDEX, self._region_index)
        tmp_point.setData(ItemDataTypes.CROSS_CENTRE, centre)

        for data in points[1:]:
            centre = qc.QPointF(data[1], data[2])
            position = qc.QPointF(data[3], data[4])
            p_hash = hash_graphics_point(tmp_point)

            path = make_cross_path(centre)
            tmp_point = self.scene().addPath(path, self._pens.get_display_pen())
            tmp_point.setPos(position)
            tmp_point.setData(ItemDataTypes.PARENT_HASH, p_hash)
            tmp_point.setData(ItemDataTypes.FRAME_NUMBER, data[5])
            tmp_point.setData(ItemDataTypes.REGION_INDEX, self._region_index)
            tmp_point.setData(ItemDataTypes.CROSS_CENTRE, centre)

    def user_choice_delete_item(self, item):
        """
        delete the selected item
            Args:
                item (QGraphicsItem)
        """
        msg_box = qw.QMessageBox()
        msg_box.setText(self.tr("Delete marker in all frames, or just selected!"))
        all_frames = msg_box.addButton(self.tr("All Frames"), qw.QMessageBox.NoRole)
        one_frame = msg_box.addButton(self.tr("Only selected"), qw.QMessageBox.NoRole)
        msg_box.addButton(self.tr("Cancel"), qw.QMessageBox.NoRole)
        msg_box.exec()

        if msg_box.clickedButton() == all_frames:
            self._parent.get_results_proxy().delete_marker_all_frames(item)
        elif msg_box.clickedButton() == one_frame:
            self._parent.get_results_proxy().delete_marker_in_frame(item)

    def delete_marker_with_hash(self, hash_code):
        """
        remove marker matching hash_code if it exists
            Args:
                hash_code (int) hash code of marker to be removed
        """
        for item in self.scene().items():
            item_type = get_marker_type(item)
            if item_type in (MarkerTypes.LINE, MarkerTypes.POINT):
                if hash_marker(item) == hash_code:
                    self.delete_graphics_item(item)
                    return True

        return False
