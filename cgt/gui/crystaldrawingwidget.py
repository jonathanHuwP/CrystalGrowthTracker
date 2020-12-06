# -*- coding: utf-8 -*-
"""
Created on Fri Jul 10 21:36:13 2020

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
# pylint: disable = c-extension-no-member
# pylint: disable = import-error

import sys

import PyQt5.QtWidgets as qw
import PyQt5.QtCore as qc

from cgt.model.linesetsandframesstore import LineSetsAndFramesStore
from cgt.model.line import Line

from cgt.gui.drawinglabel import DrawingLabel

from cgt.gui.Ui_crystaldrawingwidget import Ui_CrystalDrawingWidget

class CrystalDrawingWidget(qw.QWidget, Ui_CrystalDrawingWidget):
    """
    the widget in which the user will draw the crystals
    """

    def __init__(self, parent=None, data_source=None):
        """
        set up the dialog

            Args:
                parent (QObject) the parent object
                data_source (CrystalGrowthTrackerMain) the object holding the project data

            Returns:
                None
        """
        super(CrystalDrawingWidget, self).__init__(parent)

        ## the widget holding the project data
        self._data_source = data_source

        ## the name in translation, if any
        self._translated_name = self.tr("CrystalDrawingWidget")
        self.setupUi(self)

        ## store the the region being viewed
        self._current_region = None

        ## the drawing label
        self._drawing = DrawingLabel(self._scrollArea)
        self._scrollArea.setWidget(self._drawing)

        # connect up the change frame signals
        self._videoControl.frame_changed.connect(self.frame_changed)

        # set data source for tree widget
        self._rlfWidget.set_data_source(data_source)

        # connect the signal for the user selecting a region
        self._rlfWidget.user_region_selection.connect(self.select_region)

    def clear(self):
        """
        clear the contents

            Return:
                None
        """
        self._store = LineSetsAndFramesStore()
        self._current_region = None
        self._rlfWidget.clear()
        self._drawing.clear()

    def set_data_source(self, data_source):
        """
        setter for the object holding the data to be displayed

            Args:
                data_source (CrystalGrowthTrackerMain) object holding data

            Returns:
                None
        """
        self._data_source = data_source

    def display_region(self):
        """
        the display function

            Returns:
                None
        """
        if self._current_region is None:
            return

        frame = self._videoControl.get_current_frame()

        pixmap = self._data_source.make_pixmap(self._current_region, frame)

        self._drawing.set_backgroud_pixmap(pixmap)
        self._drawing.redisplay()

    def new_region(self):
        """
        called by data_source to indicate a new region has been added, index added to spin box

            Returns:
                None
        """
        self._rlfWidget.blockSignals(True)
        self._rlfWidget.display_regions()
        self._rlfWidget.blockSignals(False)

    @qc.pyqtSlot()
    def state_toggle(self):
        """
        callback for the changing the Drawing/Adjusting state

            Returns:
                None
        """
        if self._createButton.isChecked():
            self._drawing.set_drawing()
        elif self._adjustButton.isChecked():
            self._drawing.set_adjusting()

    @qc.pyqtSlot()
    def labels_toggled(self):
        """
        callback for the toggeling the display of line labels

            Returns:
                None
        """
        if self._labelsBox.isChecked():
            self._drawing.show_labels(True)
        else:
            self._drawing.show_labels(False)

    @qc.pyqtSlot()
    def clear_crystal(self):
        """
        clear the current crystal

            Returns:
                None
        """
        print("clear_crystal {}".format(id(self)))

    @qc.pyqtSlot()
    def store_adjusted_lines(self):
        """
        update existing lines with adjusted line segments

            Returns:
                None
        """
        print("store_adjusted_lines")

    @qc.pyqtSlot()
    def store_new_lines(self):
        """
        start a new set of lines

            Returns:
                None
        """
        lines = []
        results = self._data_source.get_result()
        start = len(results.get_lines(self._current_region))

        for count, line_segment in enumerate(self._drawing.lines_base):
            note = str(self._current_region)+"-"+str(count + start)
            note += ":"+str(self._videoControl.get_current_frame())
            line = Line(note)
            line.add_line_segment(self._videoControl.get_current_frame(),
                                  line_segment)
            lines.append(line)

        self._data_source.append_lines(self._current_region, lines)
        self._drawing.clear_all()
        self._drawing.redisplay()

    @qc.pyqtSlot()
    def clear_selected_line(self):
        """
        clear a selected line or line segments

            Returns:
                None
        """
        print("clear_selected_line")

    @qc.pyqtSlot()
    def frame_changed(self):
        """
        callback for a change of frame

            Returns:
                None
        """
        self.display_region()

    @qc.pyqtSlot()
    def zoom_changed(self):
        """
        callback for changes to the zoom slider

            Returns:
                None
        """
        self._drawing.set_zoom(self._zoomSpinBox.value())

    @qc.pyqtSlot()
    def showEvent(self, event):
        """
        override qwidget and ensure a safe display

            Returns:
                None
        """
        qw.QWidget.showEvent(self, event)

        if self._data_source is not None:
            if self._data_source.get_video_reader() is not None:
                if len(self._data_source.get_result().regions) > 0:
                    self._videoControl.setEnabled(True)
                    self.display_region()

    @qc.pyqtSlot()
    def hideEvent(self, event):
        """
        override qwidget and ensure a safe hide

            Returns:
                None
        """
        qw.QWidget.hideEvent(self, event)
        self._videoControl.setEnabled(False)

    @qc.pyqtSlot(int)
    def select_region(self, r_index):
        """
        a region has been selected

            Args:
                r_index (int) the array index of the region

            Returns:
                None
        """
        if r_index == self._current_region:
            return

        # TODO put test and save in seperate function
        # has label got unsaved lines?
        if len(self._drawing.lines_base) > 0:
            message = "You have unsaved data do you wish to proceeed?"
            reply = qw.QMessageBox.question(self, "Data loss?", message)

            if reply == qw.QMessageBox.No:
                return

        self._drawing.clear_all()

        self._current_region = r_index
        region = self._data_source.get_result().regions[r_index]

        self._videoControl.set_range(region.start_frame, region.end_frame)
        self.display_region()

    def select_line(self, r_index, l_index):
        """
        a line has been selected

            Args:
                r_index (int) the array index of the region
                l_index (int) the array index of the line

            Returns:
                None
        """
        print(f"CrystalDrawingWidget Select >>> Region {r_index}, Line {l_index}")

    def select_frame(self, r_index, l_index, f_index):
        """
        a frame number has been selected

            Args:
                r_index (int) the array index of the region
                l_indes (int) the array index of the line
                f_indes (int) the array index of the frame number

            Returns:
                None
        """
        print(f"CrystalDrawingWidget Select >>> Region {r_index}, Line {l_index}, Frame {f_index}")
