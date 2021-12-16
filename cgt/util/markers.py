# -*- coding: utf-8 -*-
## @package markers
# functions and enumerations for using QGraphicsItems as marker object in a video
#
# @copyright 2021 University of Leeds, Leeds, UK.
# @author j.h.pickering@leeds.ac.uk and j.leng@leeds.ac.uk
"""
Created on 05 Oct 2021

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

This work was funded by Joanna Leng's EPSRC funded RSE Fellowship (EP/R025819/1)
"""
import enum

class MarkerTypes(enum.IntEnum):
    """
    define the types of marker used in images
    """
    ## mark a line
    LINE = 1

    ## mark a point
    POINT = 2

    ## a region
    REGION=4

    ## not in any other.
    DECORATOR = 8

class ItemDataTypes(enum.IntEnum):
    """
    define the indices for storing data in QGraphicsItem
    """
    ## store for the type of data item
    ITEM_TYPE = 0

    ## store for parent hash code
    PARENT_HASH = 1

    ## store for the number of the frame in which the artifact was defined
    FRAME_NUMBER = 2

    ## the index number of the region in which the mark is defined
    REGION_INDEX = 3

    ## for a cross the centre point
    CROSS_CENTRE = 4

def hash_marker(marker):
    """
    find hash code for marker
        Args:
            marker (QGraphicsItem) the item to hash
        Returns:
            hash code or None if not appropriate type
    """
    m_type = get_marker_type(marker)

    if m_type == MarkerTypes.LINE:
        return hash_graphics_line(marker)

    if m_type == MarkerTypes.POINT:
        return hash_graphics_point(marker)

    return None

def hash_graphics_line(line):
    """
    a hash function for QGraphicsLineItem,
        Args:
            line (QGraphicsLineItem) the line
        Returns:
            hash of tuple (line hash, position hash, frame)
    """
    hashes = (hash_qlinef(line.line()),
                          hash_qpointf(line.pos()),
                          hash(line.data(ItemDataTypes.FRAME_NUMBER)))

    return hash(hashes)

def hash_graphics_point(point):
    """
    a hash function for QGraphicsPathItem,
        Args:
            line (QGraphicsPathItem) the line
        Returns:
            hash of tuple (centre hash, position hash, frame number)
    """
    hashes = (hash_qpointf(point.data(ItemDataTypes.CROSS_CENTRE)),
              hash_qpointf(point.pos()),
              hash(point.data(ItemDataTypes.FRAME_NUMBER)))

    return hash(hashes)

def hash_qlinef(line):
    """
    a hash function for QLineF,
        Args:
            line (QLineF) the line
        Returns:
            hash of tuple formed from end point coordinates (x1, x2, y1, y2)
    """
    coords = (line.x1(), line.x2(), line.y1(), line.y2())
    return hash(coords)

def hash_qpointf(point):
    """
    a hash function for QPontF,
        Args:
            point (QpointF) the point
        Returns:
            hash of tuple formed from end point coordinates (x, y)
    """
    coords = (point.x(), point.y())
    return hash(coords)

def hash_framestats(stats):
    """
    get a hash code for the statistics of one frame of video
        Return:
            (int) hash code
    """
    items = []
    items.append(stats.mean)
    items.append(stats.std_deviation)
    for count in stats.bin_counts:
        items.append(count)

    return hash(tuple(items))

def hash_videointensitystats(stats):
    """
    get hashcode for a complet set of video stats
        Return:
            (int) hash code
    """
    items = []
    for stat in stats.get_frames():
        items.append(hash_framestats(stat))

    for s_bin in stats.get_bins():
        items.append(hash(s_bin))

    return hash(tuple(items))

def hash_graphics_region(region):
    """
    get hash code for a QGraphicsRectItem
        Args:
            region (QGraphicsRectItem): the region
        Returns:
            (int) hash code
    """
    rect = region.rect()
    tmp = (hash_qpointf(rect.topLeft()), hash_qpointf(rect.bottomRight()))
    return hash(tmp)

def hash_results(results):
    """
    find hash of results store
        Return:
            (int) hash code
    """
    items = []
    stats = results.get_video_statistics()
    if stats is not None:
        items.append(hash_videointensitystats(stats))

    for marker in results.get_lines():
        for line in marker:
            items.append(hash_graphics_line(line))

    for marker in results.get_points():
        for point in marker:
            items.append(hash_graphics_point(point))

    for region in results.get_regions():
        items.append(hash_graphics_region(region))

    return hash(tuple(items))

def get_marker_type(item):
    """
    get the type enum of the item
        Args:
            item (QGraphicsItem)
        Returns:
            the type enum or None
    """
    return item.data(ItemDataTypes.ITEM_TYPE)

def get_parent_hash(item):
    """
    get the parent hash code of the item
        Args:
            item (QGraphicsItem)
        Returns:
            the parent hash code (int): 'p' if progenitor, or None
    """
    return item.data(ItemDataTypes.PARENT_HASH)

def get_frame(item):
    """
    get the frame number of the item
        Args:
            item (QGraphicsItem)
        Returns:
            the frame number (int), or None
    """
    return item.data(ItemDataTypes.FRAME_NUMBER)

def get_region(item):
    """
    get the index of the region in which the item is defined
        Args:
            item (QGraphicsItem)
        Returns:
            the region index (int), or None
    """
    return item.data(ItemDataTypes.REGION_INDEX)

def get_point_of_point(item):
    """
    get the centre point of a cross
        Args:
            item (QGraphicsItem)
        Returns:
            the centre point (QPontF), or None
    """
    return item.data(ItemDataTypes.CROSS_CENTRE)
