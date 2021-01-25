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
import PyQt5.QtGui as qg

from cgt.model.linesetsandframesstore import LineSetsAndFramesStore
from cgt.model.line import Line
from cgt.gui.drawinglabel import DrawingLabel
from cgt.util.utils import nparray_to_qimage

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
        print("CDW: init")
        super().__init__(parent)

        ## the widget holding the project data
        self._data_source = data_source

        ## the name in translation, if any
        self._translated_name = self.tr("CrystalDrawingWidget")
        self.setupUi(self)

        ## the drawing label
        self._drawing = DrawingLabel(self._scrollArea)
        self._scrollArea.setWidget(self._drawing)

        # connect up the change frame signals
        self._videoControl.frame_changed.connect(self.frame_changed)

        # set data source for tree widget
        self._rlfWidget.set_data_source(data_source)

        # connect the signals for the user selecting a region
        self._rlfWidget.user_region_selection.connect(self.region_selected)
        self._rlfWidget.user_line_selection.connect(self.line_selected)

    def clear(self):
        """
        clear the contents

            Return:
                None
        """
        print("CDW: clear")
        self._store = LineSetsAndFramesStore()
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
        print("CDW: set_data_source")
        self._data_source = data_source

    def new_region(self):
        """
        called by data_source to indicate a new region has been added

            Returns:
                None
        """
        print("CDW: new_region")
        self._rlfWidget.blockSignals(True)
        region = self._rlfWidget.get_selected_region()
        self._rlfWidget.display_regions()
        self._rlfWidget.set_selected_region(region)
        self._rlfWidget.blockSignals(False)

    @qc.pyqtSlot()
    def state_toggle(self):
        """
        callback for the changing the Drawing/Adjusting state

            Returns:
                None
        """
        print("CDW: state_toggle")
        if self._createButton.isChecked():
            self._drawing.set_drawing()
        elif self._adjustNewButton.isChecked():
            self._drawing.set_adjusting()
        elif self._moveButton.isChecked():
            self._drawing.set_moving()

    @qc.pyqtSlot()
    def labels_toggled(self):
        """
        callback for the toggeling the display of line labels

            Returns:
                None
        """
        print("CDW: labels_toggled")
        if self._labelsBox.isChecked():
            self._drawing.show_labels(True)
        else:
            self._drawing.show_labels(False)

    @qc.pyqtSlot()
    def store_new_lines(self):
        """
        start a new set of lines

            Returns:
                None
        """
        print("CDW: store_new_lines")
        lines = []
        results = self._data_source.get_result()
        current_region = self._rlfWidget.get_selected_region()
        start = len(results.get_lines(current_region))

        for count, line_segment in enumerate(self._drawing.lines_base):
            note = str(current_region)+"-"+str(count + start)
            line = Line(note)
            _, frame = self._videoControl.get_state()
            line.add_line_segment(frame, line_segment)
            lines.append(line)

        self._data_source.append_lines(current_region, lines)
        self._drawing.clear_all()
        self._drawing.redisplay()

    @qc.pyqtSlot()
    def clear_drawing(self):
        """
        clear a selected line or line segments

            Returns:
                None
        """
        print("CDW: clear_drawing")
        self._drawing.clear_all()

    @qc.pyqtSlot(bool)
    def frame_changed(self, first_frame):
        """
        callback for a change of frame

            Args:
                first_frame (bool) true if first frame chosen

            Returns:
                None
        """
        print("CDW: frame_changed")
        region_index = self._rlfWidget.get_selected_region()

        #TODO if unsaved lines warn than clear
        print(f"CDW: drawing size {self._drawing.size}")
        if self._drawing.size[0] > 0:
            message = "You have unsaved lines, which will be lost if you change frame. Continue?"
            mb_reply = qw.QMessageBox.question(self,
                                               'CrystalGrowthTracker',
                                               message,
                                               qw.QMessageBox.Yes | qw.QMessageBox.No,
                                               qw.QMessageBox.No)
            if mb_reply == qw.QMessageBox.Yes:
                self._drawing.clear_all()
            else:
                # reset the control widget
                self._videoControl.set_state(not first_frame)
                return

        print(f"CDW: region index {region_index}")
        self.display_image(first_frame, region_index)

    def display_image(self, first_frame, region_index):
        """
        display a selected image
            Args:
                first_frame (bool) if true display the first frame of the region
                region_index (int) the array index of the region
            Returns:
                None
        """
        print("CDW: display_image")
        images = self._data_source.get_result().region_images[region_index]

        frame_number = 0
        image = None
        if first_frame:
            image = nparray_to_qimage(images[0])
            frame_number = self._videoControl.get_minimum()
        else:
            image = nparray_to_qimage(images[1])
            frame_number = self._videoControl.get_maximum()

        self._drawing.set_backgroud_pixmap(qg.QPixmap(image), frame_number)

        line = None
        line_index = self._rlfWidget.get_selected_line()
        if line_index is not None:
            line = self._data_source.get_result().lines[line_index]

        self._drawing.set_display_line(line)

        self._drawing.redisplay()

    @qc.pyqtSlot()
    def zoom_changed(self):
        """
        callback for changes to the zoom slider

            Returns:
                None
        """
        print("CDW: zoom_changed")
        self._drawing.set_zoom(self._zoomSpinBox.value())

    @qc.pyqtSlot()
    def showEvent(self, event):
        """
        override qwidget and ensure a safe display

            Returns:
                None
        """
        print("CDW: showEvent")
        qw.QWidget.showEvent(self, event)

        if self._data_source is not None:
            if self._data_source.get_result() is not None:
                if len(self._data_source.get_result().regions) > 0:
                    self._videoControl.setEnabled(True)

    @qc.pyqtSlot()
    def hideEvent(self, event):
        """
        override qwidget and ensure a safe hide

            Returns:
                None
        """
        print("CDW: hideEvent")
        qw.QWidget.hideEvent(self, event)
        self._videoControl.setEnabled(False)

    @qc.pyqtSlot(int)
    def region_selected(self, r_index):
        """
        a region has been selected

            Args:
                r_index (int) the array index of the region

            Returns:
                None
        """
        print("CDW: region_selected")
        # has label got unsaved lines?
        if len(self._drawing.lines_base) > 0:
            message = "You have unsaved data do you wish to proceeed?"
            reply = qw.QMessageBox.question(self, "Data loss?", message)

            if reply == qw.QMessageBox.No:
                return

        self._drawing.clear_all()

        region = self._data_source.get_result().regions[r_index]


        self._videoControl.set_range(region.start_frame, region.end_frame)
        self._videoControl.setEnabled(True)
        self.display_image(False, r_index)

    @qc.pyqtSlot(int)
    def line_selected(self, l_index):
        """
        a line has been selected

            Args:
                l_index (int) the array index of the line

            Returns:
                None
        """
        print("CDW: line_selected")
        r_index = self._rlfWidget.get_selected_region()
        first, _ = self._videoControl.get_state()

        self.display_image(first, r_index)

    def frame_selected(self, frame):
        """
        a frame number has been selected

            Args:
                frame (int) the frame number

            Returns:
                None
        """
        print(f"CDW select_frame {frame}")

    def get_pixmap(self):
        """
        get a pixmap of the current image, if there is one

            Returns:
                QPixmap of image or None if no image has been set
        """
        print("CDW: get_pixmap")
        pixmap = self._drawing.pixmap()
        if pixmap is None:
            return None

        return self._drawing.grab(pixmap.rect())
