# -*- coding: utf-8 -*-
"""
Created on Wed 17 Feb 2021

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

@copyright 2021
@author: j.h.pickering@leeds.ac.uk and j.leng@leeds.ac.uk
"""
# set up linting conditions
# pylint: disable = no-name-in-module
# pylint: disable = c-extension-no-member

import PyQt5.QtWidgets as qw
import PyQt5.QtGui as qg
import PyQt5.QtCore as qc

from cgt.gui.regionbaselabel import RegionBaseLabel

class RegionDisplayLabel(RegionBaseLabel):
    """
    subclass of label allowing display of rectangles.
    """
    
    ## signal a region selected
    region_selected = qc.pyqtSignal(int)

    def __init__(self, parent):
        """
        Set up the label

            Args:
                parent (VideoRegionSelectionWidget) the parent object

            Returns:
                None
        """
        super().__init__(parent)

        ## the index of the rectangle
        self._index = -1

        ## the translated name
        self._translation_name = self.tr("RegionDisplayLabel")

    def display_rectangle(self, index):
        """
        which rectangle should be displayed
            Args:
                index (int) the inde of the rectangle to display None => all
        """
        self._index = index
        self.repaint()

    def mousePressEvent(self, event):
        """
        detect the start of selection

            Args:
                event (QEvent) the event data

            Returns:
                None
        """
        if self.get_parent().is_playing() or event.button() != qc.Qt.LeftButton:
            return
            
        if self._index < 0:
            return

        if self._index == 0:
            for i in range(0, self.get_parent().get_data().length):
                rect = self.get_parent().get_data().get_region(i)
                if rect.contains(event.pos()):
                    self.region_selected.emit(i)
                    return
        else:
            rect = self.get_parent().get_data().get_region(self._index-1)
            if rect.contains(event.pos()):
                self.region_selected.emit(self._index-1)

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
        if self._index == 0:
            stop = self.get_parent().get_data().length
            for i in range(0, stop):
                rectangle = self.get_parent().get_data().get_region(i)
                self.draw_rectangle(rectangle)
        else:
            i = self._index - 1
            rectangle = self.get_parent().get_data().get_region(i)
            self.draw_rectangle(rectangle)
