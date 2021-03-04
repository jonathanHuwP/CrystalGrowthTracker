# -*- coding: utf-8 -*-
"""
Created on Sat December 05 2020

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

# linting conditions
# pylint: disable = import-error

import sys

import PyQt5.QtWidgets as qw
import PyQt5.QtGui as qg
import PyQt5.QtCore as qc

from cgt.gui.Ui_regionslinesframeswidget import Ui_RegionsLinesFramesWidget

class RegionsLinesFramesWidget(qw.QWidget, Ui_RegionsLinesFramesWidget):
    """
    provide the user with a view of Regions, lines and linesegments,
    and a means to navigate the data
    """

    ## signal to indicate change of region
    user_region_selection = qc.pyqtSignal(int)

    ## signal to indicate change of line
    user_line_selection = qc.pyqtSignal(int)

    ## signal to indicate change of frame
    user_frame_selection = qc.pyqtSignal(int)

    def __init__(self, parent=None, data_source=None):
        """
        initialize an object

            Args:
                parent (QWidget) if exists the widget holding this widget.
                data_source (VideoAnalysisResultsStore) the data to be displayed
        """
        super().__init__(parent)
        self.setupUi(self)

        ## pointer to the data for display
        self._data_source = data_source

        if data_source is not None:
            self.display_regions()

    def display_regions(self):
        """
        fill the regions list
        """
        self.clear()

        result = self._data_source.get_results()

        if result is None:
            return

        for i in range(result.number_of_regions):
            text = f"region {i}:"

            l_count = len(result.get_lines(i))
            if l_count > 0:
                text += f" {l_count} lines"
            else:
                text += " no lines"

            item = qw.QListWidgetItem(self._regionsList)
            item.setText(text)
            item.setData(qc.Qt.UserRole, i)

            self._regionsList.addItem(item)

    def display_lines(self, region_index):
        """
        fill the lines list
        """
        self._linesLabel.setText("Lines")
        self._linesList.clear()
        self._framesList.clear()

        result = self._data_source.get_result()

        if result is None:
            return

        self._linesLabel.setText(f"Lines (region {region_index})")
        for (i, line) in result.get_lines_and_indices(region_index):
            text = f"Line {line.note}"
            item = qw.QListWidgetItem(self._linesList)
            item.setText(text)
            item.setData(qc.Qt.UserRole, i)

    def display_frames(self, line_index):
        """
        fill the frames list

            Args:
                line_index (int) the index of the line in the results
        """
        self._framesLabel.setText("Frames")
        self._framesList.clear()

        result = self._data_source.get_result()

        if result is None:
            return

        line = result.lines[line_index]
        self._framesLabel.setText(f"Frames (line {line.note})")
        for frame in line.frame_numbers:
            text = f"Frame {frame}"

            item = qw.QListWidgetItem(self._framesList)
            item.setText(text)
            item.setData(qc.Qt.UserRole, frame)

    def set_data_source(self, data_source):
        """
        set a data source to

            Args:
                data_source (VideoAnalysisResultsStore) the data source
        """
        self._data_source = data_source
        self.display_regions()

    def get_selected_region(self):
        """
        getter for the currently selected region, if any

            Returns:
                the index of the currently selected region, None in no slection
        """
        tmp = self._regionsList.currentRow()

        if tmp < 0:
            return None

        return tmp

    def get_selected_line(self):
        """
        getter for the currently selected line, if any

            Returns:
                the index of the currently selected region, None in no slection
        """
        tmp = self._linesList.currentRow()

        if tmp < 0:
            return None

        # convert to results index
        item = self._linesList.item(tmp)
        line_index = item.data(qc.Qt.UserRole)

        return line_index

    def get_selected_frame(self):
        """
        getter for the currently selected frame, if any

            Returns:
                the index of the currently selected region, None in no slection
        """
        tmp = self._framesList.currentRow()

        if tmp < 0:
            return None

        return tmp

    @qc.pyqtSlot(qw.QListWidgetItem)
    def region_selected(self, item):
        region_index = item.data(qc.Qt.UserRole)
        self.display_lines(region_index)
        self.user_region_selection.emit(region_index)

    @qc.pyqtSlot(qw.QListWidgetItem)
    def line_selected(self, item):
        line_index = item.data(qc.Qt.UserRole)
        self.display_frames(line_index)
        self.user_line_selection.emit(line_index)

    @qc.pyqtSlot(qw.QListWidgetItem)
    def frame_selected(self, item):
        frame = item.data(qc.Qt.UserRole)
        self.user_frame_selection.emit(frame)

    def set_selected_region(self, region_index):
        """
        programmatically set the currently selected region to
            Args:
                region_index (int) the array index of the region to
            Returns:
                None
        """
        if region_index is not None:
            self._regionsList.setCurrentRow(region_index)
            self.display_lines(region_index)

    def clear(self):
        """
        clear the lists
        """
        self._regionsList.clear()
        self._linesList.clear()
        self._framesList.clear()


def run():
    """
    use a local function to make an isolated the QApplication object

        Returns:
            None
    """

    app = qw.QApplication(sys.argv)
    window = RegionsLinesFramesWidget()
    window.show()
    app.exec_()

if __name__ == "__main__":
    run()