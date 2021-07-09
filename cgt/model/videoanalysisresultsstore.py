# -*- coding: utf-8 -*-
"""
Created on Tuesday August 18 2020

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
# pylint: disable = too-many-arguments

import bisect

import PyQt5.QtCore as qc

from cgt.util.utils import (ItemDataTypes,
                            MarkerTypes,
                            get_parent_hash,
                            hash_graphics_point,
                            hash_graphics_line,
                            get_frame,
                            get_region,
                            get_marker_type)

class VideoAnalysisResultsStore(qc.QObject):
    """
    a storage class that records the results of a video analysis
    """

    ## signal to indicate that the contents has changed
    data_changed = qc.pyqtSignal()

    def __init__(self, parent):
        """
        initalize an object
        """
        super().__init__(parent)

        ## store of lines
        self._lines = []

        ## store of points
        self._points = []

        ## store of regions
        self._regions = []

        ## store of keyframes mapping of regions to [int]
        self._key_frames = {}

        ## storage for the intensity statistics of the video
        self._video_statistics = None

        ## flag to indicate store has been changed
        self._changed = False

    def has_been_changed(self):
        """
        getter for the changed status

            Returns:
                the changed flag
        """
        return self._changed

    def reset_changed(self):
        """
        make the changed status false

            Returns:
                None
        """
        self._changed = False

    def set_changed(self):
        """
        set the changed status to true

            Returns:
                None
        """
        self.data_changed.emit()
        self._changed = True

    def get_video_statistics(self):
        """
        getter for the video statistics
            Returns:
                [FrameStats]
        """
        return self._video_statistics

    def set_video_statistics(self, video_stats):
        """
        setter for the video statistics
            Args:
                video_stats ([FrameStats]) the statistics
        """
        self._video_statistics = video_stats
        self.set_changed()

    def replace_region(self, region, index):
        """
        replace an existing region
            Args:
                rectangle (QRect) the new region
                index (int) the list index
            Throws:
                IndexError: pop index out of range
        """
        self._regions[index] = region
        self.set_changed()

    def remove_region(self, index):
        """
        remove an item
            Args:
                index (int) the index of the item to be removed
            Throws:
                IndexError: pop index out of range
        """
        markers = []
        markers.append(self.get_lines_for_region(index))
        markers.append(self.get_points_for_region(index))
        markers = [x for x in markers if x is not None]

        self._regions.pop(index)
        for marker in markers:
            self.delete_marker(marker)

        self.set_changed()

    def get_regions(self):
        """
        getter for the regions
            Returns:
                [QRect]
        """
        return self._regions

    def get_lines(self):
        """
        getter for the lines array
            Returns:
                the lines array [[QGraphicsLineItem]]
        """
        return self._lines

    def get_points(self):
        """
        getter for the points array
            Returns:
                the points array [[QGraphicsLineItem]]
        """
        return self._points

    def get_key_frames(self, region_index):
        """
        get the list of key frames for a region_index
            Args:
                region_index (int) the array index of the region
            Returns:
                the list of key frames [int] or None
        """
        if region_index not in self._key_frames.keys():
            return None

        return self._key_frames[region_index]

    def get_key_frames_for_points(self, index):
        """
        get a list of the key-frames for the point markers at index
            Args:
                index (int) the array index of the point marker
            Returns:
                array of key-frames [int]
        """
        key_frames = []
        for point in self._points[index]:
            key_frames.append(get_frame(point))

        return key_frames

    def get_key_frames_for_lines(self, index):
        """
        get a list of the key-frames for the line markers at index
            Args:
                index (int) the array index of the line marker
            Returns:
                array of key-frames [int]
        """
        key_frames = []
        for line in self._lines[index]:
            key_frames.append(get_frame(line))

        return key_frames

    def add_key_frame(self, region_index, frame_number):
        """
        add a new key frame
            Args:
                region_index (int) the array index of the region
                frame_number (int) the key_frame number
        """
        if region_index not in self._key_frames.keys():
            self._key_frames[region_index] = [frame_number]
            self.set_changed()
            return

        if frame_number not in self._key_frames[region_index]:
            bisect.insort(self._key_frames[region_index], frame_number)
            self.set_changed()

    def add_region(self, region):
        """
        add a region
            Args:
                region (QRect) the region
        """
        self._regions.append(region)
        self.set_changed()

    def add_point(self, point):
        """
        add a new point
            Args:
                point (QGraphicsPathItem) the path item
        """
        if get_parent_hash(point) == "p":
            self._points.append([point])
            self.add_key_frame(get_region(point), get_frame(point))
            self.set_changed()
            return None

        index = self.find_list_for_new_point(point)
        if index is None:
            raise LookupError("Graphics path with parent hash not matching any in store")

        self._points[index].append(point)
        self._points[index].sort(key=get_frame)
        self.add_key_frame(get_region(point), get_frame(point))
        self.set_changed()

        tmp = self._points[index].index(point)
        if tmp > 0:
            return self._points[index][tmp-1]

        return None

    def add_line(self, line):
        """
        add a new line
            Args:
                point (QGraphicsLineItem) the line item
        """
        if get_parent_hash(line) == "p":
            self._lines.append([line])
            self.add_key_frame(get_region(line), get_frame(line))
            self.set_changed()
            return None

        index = self.find_list_for_new_line(line)
        if index is None:
            raise LookupError("Graphics item with parent hash not matching any in store")

        self._lines[index].append(line)
        self._lines[index].sort(key=get_frame)
        self.add_key_frame(get_region(line), get_frame(line))
        self.set_changed()

        tmp = self._lines[index].index(line)
        if tmp > 0:
            return self._lines[index][tmp-1]

        return None

    def insert_line_marker(self, marker):
        """
        add a new marker to the lines with no change results call
        """
        self._lines.append(marker)

    def insert_point_marker(self, marker):
        """
        add a new marker to the points with no change results call
        """
        self._points.append(marker)

    def line_frame_number_unique(self, line):
        """
        check if a line is unique, or has a unique frame number
            Args:
                line (QGraphicsLineItem) the line
            Returns:
                True if line is unique, or has unique frame number; else False
        """
        hash_code = get_parent_hash(line)
        if hash_code == "p":
            return True

        # this is a pythonic way of doing
        if self.find_list_for_new_line(line) is None:
            return True

        return False

    def find_list_for_new_line(self, line):
        """
        get the index of the list holding the parent of a line
            Args
                line (QGraphicsLineItem) the line, must not have data(0) == "p"
            Returns:
                index of the list holding the lines parent
            Throws
                LookupError if there is no match
        """
        hash_code = get_parent_hash(line)
        for i in range(len(self._lines)):
            for line_move in self._lines[i]:
                if hash_graphics_line(line_move) == hash_code:
                    return i

        return None

    def find_list_for_old_line(self, line):
        """
        get the index of the list holding a line
            Args
                line (QGraphicsLineItem) the line
            Returns:
                index of the list holding the line
            Throws
                LookupError if there is no match
        """
        target = hash_graphics_line(line)
        for i, markers in enumerate(self._lines):
            hashes = [hash_graphics_line(x) for x in markers]
            if target in hashes:
                return i

        return None

    def find_list_for_new_point(self, point):
        """
        get the index of the list holding the parent of a point
            Args
                point (QGraphicsPathItem) the point, must not have data(0) == "p"
            Returns:
                index of the list holding the points parent
            Throws
                LookupError if there is no match
        """
        hash_code = get_parent_hash(point)
        for i in range(len(self._points)):
            for point_move in self._points[i]:
                if hash_graphics_point(point_move) == hash_code:
                    return i

        return None

    def find_list_for_old_point(self, point):
        """
        get the index of the list holding a point
            Args
                point (QGraphicsPathItem) the point
            Returns:
                index of the list holding the point
            Throws
                LookupError if there is no match
        """
        target = hash_graphics_point(point)
        for i, markers in enumerate(self._points):
            hashes = [hash_graphics_point(x) for x in markers]
            if target in hashes:
                return i

        return None

    def delete_marker(self, marker):
        """
        delete marker and all clones
            Args:
                marker (QGraphicsItem) the marker to be removed
        """
        m_type = get_marker_type(marker)

        if m_type == MarkerTypes.LINE:
            index = self.find_list_for_old_line(marker)
            del self._lines[index]
            self.set_changed()

        if m_type == MarkerTypes.POINT:
            index = self.find_list_for_old_point(marker)
            del self._points[index]
            self.set_changed()

    def remove_point(self, hash_code):
        """
        remove the line with the given hash code
            Args:
                hash_code (int) the hash code of the line to be removed
            Returns:
                None if line was one frame, else remaining lines
        """
        point_index = None
        marker_index = None

        for i, points in enumerate(self._points):
            for j, point in enumerate(points):
                if hash_graphics_point(point) == hash_code:
                    marker_index = j
                    point_index = i

        if point_index is None or marker_index is None:
            return None

        del self._points[point_index][marker_index]
        self.set_changed()

        if len(self._points[point_index]) == 0:
            del self._points[point_index]
            return None

        return self._points[point_index]

    def remove_line(self, hash_code):
        """
        remove the line with the given hash code
            Args:
                hash_code (int) the hash code of the line to be removed
            Returns:
                None if line was one frame, else remaining lines
        """
        line_index = None
        marker_index = None

        for i, lines in enumerate(self._lines):
            for j, line in enumerate(lines):
                if hash_graphics_line(line) == hash_code:
                    marker_index = j
                    line_index = i

        if line_index is None or marker_index is None:
            return None

        del self._lines[line_index][marker_index]
        self.set_changed()

        if len(self._lines[line_index]) == 0:
            del self._lines[line_index]
            return None

        return self._lines[line_index]

    def delete_line(self, line, index):
        """
        remove a line and fix the linked list
            Args:
                line (QGraphicsLineItem) the line
                index (int) the array index of the list holding the line
        """
        root_hash = None

        if get_parent_hash(line) == 'p':
            if len(self._lines[index]) == 1:
                del self._lines[index]
                return

            root_hash = 'p'
        else:
            root_hash = get_parent_hash(line)

        p_hash = hash_graphics_line(line)

        children = [x for x in self._lines[index] if get_parent_hash(x) == p_hash]

        if len(children) > 0:
            new_p = children.pop(0)
            new_p.setData(ItemDataTypes.PARENT_HASH, root_hash)
            p_hash = hash_graphics_line(new_p)

            for child in children:
                child.setData(ItemDataTypes.PARENT_HASH, p_hash)

        self._lines[index].remove(line)
        self.set_changed()

    def delete_point(self, point, index):
        """
        remove a point and fix the linked list
            Args:
                point (QGraphicsPathItem) the point
                index (int) the array index of the list holding the point
        """
        root_hash = None

        if get_parent_hash(point) == 'p':
            if len(self._points[index]) == 1:
                del self._points[index]
                return

            root_hash = 'p'
        else:
            root_hash = get_parent_hash(point)

        p_hash = hash_graphics_point(point)

        children = [x for x in self._points[index] if get_parent_hash(x) == p_hash]

        if len(children) > 0:
            new_p = children.pop(0)
            new_p.setData(ItemDataTypes.PARENT_HASH, root_hash)
            p_hash = hash_graphics_point(new_p)

            for child in children:
                child.setData(ItemDataTypes.PARENT_HASH, p_hash)

        self._points[index].remove(point)
        self.set_changed()

    def get_lines_for_region(self, index):
        """
        get a list of lines associated with a region
            Args:
                index (int) array index of region
            Returns:
                list of lines [line], or None if none found
        """
        tmp = []

        for line in self._lines:
            if get_region(line[0]) == index:
                tmp.append(line)

        if len(tmp) > 0:
            return tmp

        return None

    def get_points_for_region(self, index):
        """
        get a list of points associated with a region
            Args:
                index (int) array index of region
            Returns:
                list of points [points], or None if none found
        """
        tmp = []

        for point in self._points:
            if get_region(point[0]) == index:
                tmp.append(point)

        if len(tmp) > 0:
            return tmp

        return None

    def region_has_markers(self, index):
        """
        find if a region has associated markers defined.
            Args:
                index (int): the index of the region
            Returns:
                True if markers defined else False
        """
        if len(self.get_points_for_region(index)) > 0:
            return True

        if len(self.get_lines_for_region(index)) > 0:
            return True

        return False
