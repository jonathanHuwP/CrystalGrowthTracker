## -*- coding: utf-8 -*-
"""
Created on 28 Apr 2021

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

import PyQt5.QtCore as qc

from cgt.util.markers import (ItemDataTypes,
                              MarkerTypes,
                              get_marker_type,
                              get_parent_hash,
                              get_region,
                              get_frame,
                              get_point_of_point,
                              hash_marker,
                              hash_graphics_line,
                              hash_graphics_point)

from cgt.util.scenegraphitems import (make_arrow,
                                      make_arrow_head)

class ResultsStoreProxy():
    """
    The tool for marking up items identified in the video
    """
    def __init__(self, results_store, entry_view, clone_view):
        """
        initalize the object:
            Args:
                results_store (VideoAnalysisResultsStore) the true store
                entry_view (MarkUpView) the left hand view
                clone_view (MarkUpView) ther right hand view
        """
        ## the results store
        self._results_store = results_store

        ## the left hand view
        self._entry_view = entry_view

        ## the right hand view
        self._clone_view = clone_view

        ## the artifacts to arrows dictionary hash(marker) => out arrow
        self._marker_arrow_map = {}

    def get_regions(self):
        """
        getter for the regions array from the data store
            Returns:
                [(QRect)]
        """
        return self._results_store.get_regions()

    def get_lines(self):
        """
        getter for the lines array from the data store
            Returns:
                [(QGraphicsLineItem)]
        """
        return self._results_store.get_lines()

    def get_lines_for_region(self, index):
        """
        getter for the lines associated with a region in the data store
            Args:
                index (int) the region index
            Returns:
                [(QGraphicsLineItem)]
        """
        lines = self._results_store.get_lines()
        tmp = []
        for line in lines:
            if get_region(line[0]) == index:
                tmp.append(line)

        return tmp

    def get_points(self):
        """
        getter for the points array from the data store
            Returns:
                [(QGraphicsPathItem)]
        """
        return self._results_store.get_points()

    def get_points_for_region(self, index):
        """
        getter for the points associated with a region in the data store
            Args:
                index (int) the region index
            Returns:
                [(QGraphicsPathItem)]
        """
        points = self._results_store.get_points()
        tmp = []
        for point in points:
            if get_region(point[0]) == index:
                tmp.append(point)

        return tmp

    def get_key_frames(self, region_index):
        """
        wrapper for the underlying resultf function
            Args:
                region_index (int) the array index of the region
            Returns:
                the list of key frames [int] or None
        """
        return self._results_store.get_key_frames(region_index)

    def redraw_markers(self, region):
        """
        redisplay the markers and arrows
            Args:
                region (int) the index of the region
        """
        if self.get_key_frames(region) is None:
            return

        line_markers = self.get_lines_for_region(region)
        point_markers = self.get_points_for_region(region)

        for marker in line_markers:
            self.redraw_line_marker(marker)

        for marker in point_markers:
            self.redraw_point_marker(marker)

    def redraw_line_marker(self, marker):
        """
        redraw an entire marker array
            Args:
                marker (list(QGraphicsItem))
        """
        self.copy_line_to_view(marker[0], False)

        for line in marker:
            self._clone_view.scene().addItem(line)

        for i, line in enumerate(marker[1:]):
            self.add_arrow_to_lines(marker[i], line)

    def redraw_point_marker(self, marker):
        """
        redraw an entire marker array
            Args:
                marker (list(QGraphicsItem))
        """
        self.copy_point_to_view(marker[0], False)

        for point in marker:
            self._clone_view.scene().addItem(point)

        for i, point in enumerate(marker[1:]):
            self.add_arrow_to_points(marker[i], point)

    def add_marker(self, marker):
        """
        add a marker to the store
            Args:
                marker (QGraphicsItem)
        """
        parent = None
        item_type = get_marker_type(marker)

        if item_type == MarkerTypes.LINE:
            parent = self.add_line(marker)
            self.add_arrow_to_lines(parent, marker)

        elif item_type == MarkerTypes.POINT:
            parent = self.add_point(marker)
            self.add_arrow_to_points(parent, marker)

        return parent

    def add_line(self, line):
        """
        add a line to the data store, and copy
            Args:
                line(QGraphicsLineItem) the line to be added
        """
        if get_parent_hash(line) == "p":
            copy_line = self.copy_line_to_view(line)
            self._results_store.add_line(copy_line)
            self._marker_arrow_map[line] = []
            return None

        return self._results_store.add_line(line)

    def add_point(self, point):
        """
        add a point to the data store, and copy
            Args:
                line(QGraphicsPathItem) the line to be added
        """
        if get_parent_hash(point) == "p":
            copy_point = self.copy_point_to_view(point)
            self._results_store.add_point(copy_point)
            self._marker_arrow_map[point] = []
            return None

        return self._results_store.add_point(point)

    def check_if_marker_already_has_key_frame(self, item):
        """
        test if the marker already has a clone defined in the key frames
            Args:
                item (QGraphicsItem)
            Return:
                True item is a clone of a marker with another clone in this frame; else False
        """
        item_type = get_marker_type(item)

        if item_type is None:
            return False

        frame = get_frame(item)
        if item_type == MarkerTypes.LINE:
            index = self._results_store.find_list_for_new_line(item)
            if frame in self._results_store.get_key_frames_for_lines(index):
                return True

        if item_type == MarkerTypes.POINT:
            index = self._results_store.find_list_for_new_point(item)
            if frame in self._results_store.get_key_frames_for_points(index):
                return True

        return False

    def remove_item_from_views(self, hash_code):
        """
        remove an item from both views
            Args:
                hash_code (int) the hash_code of the item to be removed
        """
        self._entry_view.delete_marker_with_hash(hash_code)
        self._clone_view.delete_marker_with_hash(hash_code)

    def clear(self):
        """
        clear all the current view items:
        """
        self._entry_view.clear()
        self._clone_view.clear()
        self._marker_arrow_map.clear()

    def copy_point_to_view(self, point, clone_view=True):
        """
        make a copy of a point to a view
            Args:
                line (QGraphicsPathItem) the point marker to copy
                clone_view (bool) if true copy to clone_view else copy to entry
            Returns:
                QGraphicsPathItem the new point
        """
        g_point = None
        if clone_view:
            g_point = self._clone_view.scene().addPath(point.path(), point.pen())
        else:
            g_point = self._entry_view.scene().addPath(point.path(), point.pen())

        g_point.setPos(point.pos())
        g_point.setData(ItemDataTypes.ITEM_TYPE, get_marker_type(point))
        g_point.setData(ItemDataTypes.PARENT_HASH, get_parent_hash(point))
        g_point.setData(ItemDataTypes.REGION_INDEX, get_region(point))
        g_point.setData(ItemDataTypes.FRAME_NUMBER, get_frame(point))
        g_point.setData(ItemDataTypes.CROSS_CENTRE, point.data(ItemDataTypes.CROSS_CENTRE))

        return g_point

    def copy_line_to_view(self, line, clone_view=True):
        """
        make a copy of a line to a view
            Args:
                line (QGraphicsLineItem) the line to copy
                clone_view (bool) if true copy to clone_view else copy to entry
            Returns:
                QGraphicsPathItem the new line
        """
        g_line = None
        if clone_view:
            g_line = self._clone_view.scene().addLine(line.line(), line.pen())
        else:
            g_line = self._entry_view.scene().addLine(line.line(), line.pen())

        g_line.setZValue(1.0)
        g_line.setPos(line.pos())
        g_line.setData(ItemDataTypes.ITEM_TYPE, get_marker_type(line))
        g_line.setData(ItemDataTypes.PARENT_HASH, get_parent_hash(line))
        g_line.setData(ItemDataTypes.REGION_INDEX, get_region(line))
        g_line.setData(ItemDataTypes.FRAME_NUMBER, get_frame(line))

        return g_line

    def delete_item(self, item):
        """
        delete a line or point
            Args:
                item (QGraphicsItem) the hash code of the item
        """
        item_type = get_marker_type(item)

        if item_type in (MarkerTypes.LINE, MarkerTypes.POINT):
            parent = self._clone_view.delete_graphics_item(item)
            self._results_store.delete_marker(item)
            self._clone_view.delete_graphics_items(self._marker_arrow_map[parent])

    def delete_marker_all_frames(self, marker):
        """
        delete the item and all clones and parents
            Args:
                marker (QGraphicsItem) the item to be deleted
        """
        item_type = get_marker_type(marker)

        if item_type not in (MarkerTypes.LINE, MarkerTypes.POINT):
            return

        if item_type == MarkerTypes.LINE:
            index = self._results_store.find_list_for_old_line(marker)
            lines = self._results_store.get_lines()
            for line in lines[index]:
                self._clone_view.delete_graphics_item(line)
                if line in self._marker_arrow_map:
                    self._clone_view.delete_graphics_items(self._marker_arrow_map[line])

                self._entry_view.delete_marker_with_hash(hash_graphics_line(line))

        if item_type == MarkerTypes.POINT:
            index = self._results_store.find_list_for_old_point(marker)
            points = self._results_store.get_points()
            for point in points[index]:
                self._clone_view.delete_graphics_item(point)
                if point in self._marker_arrow_map:
                    self._clone_view.delete_graphics_items(self._marker_arrow_map[point])

                self._entry_view.delete_marker_with_hash(hash_graphics_point(point))

        self._results_store.delete_marker(marker)

    def delete_marker_in_frame(self, marker):
        """
        delete the item and fix the chain of descent
            Args:
                marker (QGraphicsItem) the item to be deleted
        """
        hash_code = hash_marker(marker)
        if hash_code is None:
            return

        item_type = get_marker_type(marker)

        if item_type == MarkerTypes.LINE:
            array = self._results_store.remove_line(hash_code)
            self._clone_view.delete_graphics_item(marker)
            self.delete_marker_arrows(marker)
            self.redraw_line_arrows(array)
            was_first = self._entry_view.delete_marker_with_hash(hash_code)
            if was_first and array is not None:
                self.copy_line_to_view(array[0], False)

        elif item_type == MarkerTypes.POINT:
            array = self._results_store.remove_point(hash_code)
            self._clone_view.delete_graphics_item(marker)
            self.delete_marker_arrows(marker)
            self.redraw_point_arrows(array)
            was_first = self._entry_view.delete_marker_with_hash(hash_code)
            if was_first and array is not None:
                self.copy_point_to_view(array[0], False)

    def redraw_line_arrows(self, array):
        """
        redraw all markers for lines in array
            Args:
                arrary ([QGraphicsLineItem]) array holding markers
        """
        self.delete_arrows(array)

        if array is None or len(array)<2:
            return

        for i, line in enumerate(array):
            if i == 0:
                previous = line
            else:
                self.add_arrow_to_lines(previous, line)
                previous = line

    def redraw_point_arrows(self, array):
        """
        redraw all markers for lines in array
            Args:
                arrary ([QGraphicsLineItem]) array holding markers
        """
        self.delete_arrows(array)

        if array is None or len(array)<2:
            return

        for i, point in enumerate(array):
            if i == 0:
                previous = point
            else:
                self.add_arrow_to_points(previous, point)
                previous = point

    def delete_arrows(self, array):
        """
        delete all the arrows associated with the array of markers
            Args:
                array ([QGraphicsItem])
        """
        if array is None or len(array)==0:
            return

        for marker in array:
            if marker in self._marker_arrow_map:
                for item in self._marker_arrow_map[marker]:
                    self._clone_view.delete_graphics_item(item)
                del self._marker_arrow_map[marker]

    def delete_marker_arrows(self, marker):
        """
        delete the arrows associated with the marker
            Args:
                marker (QGraphicsItem)
        """
        if marker in self._marker_arrow_map:
            for item in self._marker_arrow_map[marker]:
                self._clone_view.delete_graphics_item(item)
            del self._marker_arrow_map[marker]

    def add_arrow_to_points(self, parent, child):
        """
        add arrow between parent and child:
            Args:
                parent (QGraphicsPathItem)
                child (QGraphicsPathItem)
        """
        start = get_point_of_point(parent) + parent.pos()
        end = get_point_of_point(child) + child.pos()
        arrow = qc.QLineF(start, end)
        arrow_head = make_arrow_head(arrow)
        self._marker_arrow_map[parent] = self._clone_view.add_arrow(arrow,
                                                                    arrow_head,
                                                                    None)

    def add_arrow_to_lines(self, parent, child):
        """
        add arrow between parent and child:
            Args:
                parent (QGraphicsLineItem)
                child (QGraphicLineItem)
        """
        p_line = parent.line()
        p_pos = parent.pos()
        parent_line = qc.QLineF(p_line.p1()+p_pos, p_line.p2()+p_pos)

        pos = child.pos()
        line = child.line()
        c_line = qc.QLineF(line.p1()+pos, line.p2()+pos)

        arrow, extension = make_arrow(parent_line, c_line)
        arrow_head = make_arrow_head(arrow)
        self._marker_arrow_map[parent] = self._clone_view.add_arrow(arrow,
                                                                    arrow_head,
                                                                    extension)
