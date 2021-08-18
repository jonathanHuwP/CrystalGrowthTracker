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
# pylint: disable = too-many-instance-attributes

import PyQt5.QtWidgets as qw
import PyQt5.QtGui as qg

class VideoBaseView(qw.QGraphicsView):
    """
    provides a viewer for a pixmaps
    """
    def __init__(self, parent):
        """
        set up the scene graph
        """
        super().__init__(parent)

        ## needed as in PyQt5 .parent() only returns the Qt base class
        self._parent = parent

        ## the pixmap for video display
        self._pixmap_item = None

        ## the current video time
        self._current_time = None

        ## set and connect scene
        self.setScene(qw.QGraphicsScene())

    def clear(self):
        """
        clear the scene and reset instance variables
        """
        self._pixmap_item = None
        self._current_time = None
        self.scene().clear()

    def set_pixmap(self, pixmap, time):
        """
        set the pixamp
            Args:
                pixmap (QPixmap) the pixmap
                frame_number (int) the number of the frame in the video
        """
        if self._pixmap_item is None:
            self._pixmap_item = self.scene().addPixmap(pixmap)
            self._pixmap_item.setZValue(-1.0)
            rect = self._pixmap_item.boundingRect()
            self.scene().setSceneRect(rect)
        else:
            self._pixmap_item.setPixmap(pixmap)

        self._current_time = time

    def get_frame_number(self):
        """
        getter for the frame number
            Returns:
                the frame number
        """
        return self._current_time

    def set_zoom(self, zoom_value):
        """
        zoom the pixmap
            Args:
                zoom_value (float) the current zoom
        """
        self.setTransform(qg.QTransform())
        self.scale(zoom_value, zoom_value)

    def delete_graphics_item(self, item):
        """
        delete a graphics item
            Args:
                item (QGraphicsItem) the item
        """
        if item is not None:
            self.scene().removeItem(item)

    def delete_graphics_items(self, items):
        """
        delete a collection of graphics items
            Args:
                items (QGraphicsItem) python iterable of items
        """
        if items is None or len(items)==0:
            return

        for item in items:
            if item is not None:
                self.scene().removeItem(item)
