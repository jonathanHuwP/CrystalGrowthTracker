# -*- coding: utf-8 -*-
"""
Created on Tue 25 May 2021

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

import PyQt5.QtGui as qg
import PyQt5.Qt as qt

class PenStore():
    """
    provides a set of pens for use in drawing, adjustable colour and thickness
    """
    DEFAULT_WIDTH = 8
    NARROW_WIDTH = 3

    def __init__(self):
        """
        initalize the class
        """

        # red brush for drawing
        brush = qt.QBrush(qt.Qt.red)

        ## pen for drawing artifacts
        self._drawing_pen = qt.QPen(brush, PenStore.DEFAULT_WIDTH, qt.Qt.SolidLine)

        # green brush for displaying
        brush = qt.QBrush(qt.Qt.green)

        ## pen for displaying artifacts
        self._display_pen = qt.QPen(brush, PenStore.DEFAULT_WIDTH, qt.Qt.SolidLine)

        ## brush for the arrows
        self._highlight_brush = qt.QBrush(qt.Qt.blue)

        ## pen for arrows
        self._highlight_pen = qt.QPen(self._highlight_brush,
                                      PenStore.NARROW_WIDTH,
                                      qt.Qt.SolidLine)

    def set_drawing_and_display_width(self, width):
        """
        setter for the width of the drawing and display lines
            Args:
                width (int>0) the new width
        """
        self._drawing_pen.setWidth(width)
        self._display_pen.setWidth(width)

    def set_drawing_width(self, width):
        """
        setter for the width of the drawing line
            Args:
                width (int>0) the new width
        """
        self._drawing_pen.setWidth(width)

    def set_display_width(self, width):
        """
        setter for the width of the display line
            Args:
                width (int>0) the new width
        """
        self._display_pen.setWidth(width)

    def set_highlight_width(self, width):
        """
        setter for the width of the highlight line
            Args:
                width (int>0) the new width
        """
        self._highlight_pen.setWidth(width)

    def set_drawing_colour(self, colour):
        """
        setter for the colour of the drawing line
            Args:
                colour (QColor) the new colour
        """
        self._drawing_pen.setColor(colour)

    def set_display_colour(self, colour):
        """
        setter for the colour of the display line
            Args:
                colour (QColor) the new colour
        """
        self._display_pen.setColor(colour)

    def set_highlight_colour(self, colour):
        """
        setter for the highlight colour
            Args:
                colour (QColor) the new colour
        """
        self._highlight_pen.setColor(colour)
        self._highlight_brush.setColor(colour)

    def set_highlight_dashed(self):
        """
        set the highlight pen as dashed
        """
        self._highlight_pen.setStyle(qt.Qt.DashLine)

    def set_highlight_solid(self):
        """
        set the highlight pen as solid
        """
        self._highlight_pen.setStyle(qt.Qt.SolidLine)

    def get_drawing_pen(self):
        """
        getter for the drawing pen
            Returns:
                (QPen) the drawing pen
        """
        return self._drawing_pen

    def get_display_pen(self):
        """
        getter for the display pen
            Returns:
                (QPen) the display pen
        """
        return self._display_pen

    def get_highlight_pen(self):
        """
        getter for the highlight pen
            Returns:
                (QPen) the highlight pen
        """
        return self._highlight_pen

    def get_highlight_brush(self):
        """
        getter for the highlight brush
            Returns:
                (QPen) the highlight brush
        """
        return self._highlight_brush

    def get_plotting_pen(self, index):
        return self._plotting_pens[index%5]
