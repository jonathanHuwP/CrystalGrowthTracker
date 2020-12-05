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
        fill the three lists
        """
        self.clear()

        result = self._data_source.get_result()

        if result is None:
            return

        for i in range(result.number_of_regions):
            text = f"region {i}"

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
        for i, line in enumerate(result.get_lines(region_index)):
            text = f"Line {i}"

            if line.note is not None:
                text += f": {line.note}"

            item = qw.QListWidgetItem(self._linesList)
            item.setText(text)
            item.setData(qc.Qt.UserRole, i)

    def set_data_source(self, data_source):
        """
        set a data source to

            Args:
                data_source (VideoAnalysisResultsStore) the data source
        """
        self._data_source = data_source
        self.display_regions()

    @qc.pyqtSlot(qw.QListWidgetItem)
    def region_selected(self, item):
        region_index = item.data(qc.Qt.UserRole)
        print(f"Region {item.text()}, index {region_index}")
        self.display_lines(region_index)

    @qc.pyqtSlot(qw.QListWidgetItem)
    def line_selected(self, item):
        data = item.data(qc.Qt.UserRole)
        print(f"Line {item.text()}, index {data}")

    @qc.pyqtSlot(qw.QListWidgetItem)
    def frame_selected(self, item):
        print(f"Frame {item.text()}")

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