# -*- coding: utf-8 -*-
"""
Created on Monday December 14  2020

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
# pylint: disable = c-extension-no-member
# pylint: disable = too-few-public-methods

import PyQt5.QtWidgets as qw
import PyQt5.QtCore as qc
import PyQt5.QtGui as qg

from cgt.gui.Ui_linevalueswidget import Ui_LineValuesWidget

class LineValuesWidget(qw.QWidget, Ui_LineValuesWidget):
    """
    an application class that will run the widget
    """

    def __init__(self, parent=None, data_source=None):
        """
        set up the widget

            Args:
                parent (QWidget) the parent widget
        """
        super().__init__(parent)
        self.setupUi(self)

        ## store of data
        self._data_source = None

        if data_source is not None:
            self._data_source = data_source

    def set_data(self, data_source):
        """
        set the results that are to be displayed

            Args:
                data (VideoAnalysisResultsStore) the results to be displayed.
        """
        self._data_source = data_source

    def display_data(self):
        """
        initalize the display
        """
        self.display_segments()
        self.display_regions()

    def display_segments(self):
        """
        initialize the line segments display
        """
        results = self._data_source.get_result()
        self._regionComboBox.clear()
        for region_index in range(len(results.regions)):
            self._regionComboBox.addItem(str(region_index))

        self.region_chosen(self._regionComboBox.currentIndex())

    def display_regions(self):
        """
        display the lines table
        """
        results = self._data_source.get_result()

        size = len(results.lines)
        association = results.region_lines_association

        self._regionsTableWidget.clearContents()

        self._regionsTableWidget.setRowCount(size+1)

        total = 0
        count = 0
        row = 0

        for row, line in enumerate(results.lines):
            differences = [x[1].average for x in line.get_differences()]
            average = None

            item = qw.QTableWidgetItem(str(association.get_region(row)))
            self._regionsTableWidget.setItem(row, 0, item)
            item = qw.QTableWidgetItem(line.note)
            self._regionsTableWidget.setItem(row, 1, item)
            item = qw.QTableWidgetItem(str(line.number_of_frames))
            self._regionsTableWidget.setItem(row, 2, item)

            if len(differences) > 0:
                average = sum(differences)/len(differences)

            if average is not None:
                item = qw.QTableWidgetItem(str(average))
                total += average
                count += 1
            else:
                item = qw.QTableWidgetItem("NA")

            self._regionsTableWidget.setItem(row, 3, item)

        item = qw.QTableWidgetItem("Overall Averge")
        font = qg.QFont()
        font.setBold(True)
        item.setFont(font)
        self._regionsTableWidget.setItem(row+1, 2, item)

        if count > 0:
            average_total = total/count
            item = qw.QTableWidgetItem(str(average_total))
        else:
            item = qw.QTableWidgetItem("NA")
        self._regionsTableWidget.setItem(row+1, 3, item)


    @qc.pyqtSlot(int)
    def region_chosen(self, region_index):
        """
        callback for a region being chosen

            Args:
                region_index (int) the index of the index in the results
        """
        results = self._data_source.get_result()

        self._linesComboBox.clear()
        for line_index, _ in enumerate(results.get_lines(region_index)):
            self._linesComboBox.addItem(str(line_index))

        self.line_chosen(self._linesComboBox.currentIndex())

    @qc.pyqtSlot(int)
    def line_chosen(self, line_index):
        """
        callback for a line being chosen

            Args:
                line_index (int) the index of the line in the current region
        """
        if line_index < 0:
            return

        results = self._data_source.get_result()

        lines = results.get_lines(self._regionComboBox.currentIndex())
        line = lines[line_index]

        self._lineTableWidget.clearContents()
        if line.number_of_frames > 1:
            self._lineTableWidget.setRowCount(line.number_of_frames+1)
        else:
            self._lineTableWidget.setRowCount(line.number_of_frames)

        self._lineTableWidget.setColumnCount(6)

        frames = sorted(line.keys())

        differences = None
        if len(frames) > 1:
            differences = [x[1].average for x in line.get_differences()]

        row = 0
        for row, frame in enumerate(frames):
            segment = line[frame]
            item = qw.QTableWidgetItem(str(frame))
            self._lineTableWidget.setItem(row, 0, item)
            item = qw.QTableWidgetItem(str(segment.start.x))
            self._lineTableWidget.setItem(row, 1, item)
            item = qw.QTableWidgetItem(str(segment.start.y))
            self._lineTableWidget.setItem(row, 2, item)
            item = qw.QTableWidgetItem(str(segment.end.x))
            self._lineTableWidget.setItem(row, 3, item)
            item = qw.QTableWidgetItem(str(segment.end.y))
            self._lineTableWidget.setItem(row, 4, item)
            if row > 0:
                item = qw.QTableWidgetItem(str(differences[row-1]))
            else:
                item = qw.QTableWidgetItem("NA")
            self._lineTableWidget.setItem(row, 5, item)

        if line.number_of_frames > 1:
            item = qw.QTableWidgetItem("Overall Averge")
            font = qg.QFont()
            font.setBold(True)
            item.setFont(font)
            self._lineTableWidget.setItem(row+1, 4, item)

            line_average = sum(differences)/len(differences)
            item = qw.QTableWidgetItem(str(line_average))
            self._lineTableWidget.setItem(row+1, 5, item)

    def clear(self):
        """
        clear the current contents
        """
        self._lineTableWidget.clearContents()
        self._regionsTableWidget.clearContents()
        self._regionComboBox.clear()
        self._linesComboBox.clear()
