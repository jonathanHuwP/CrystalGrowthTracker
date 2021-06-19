## -*- coding: utf-8 -*-
"""
Created on 12 April 2021

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
# pylint: disable = import-error

import PyQt5.QtWidgets as qw
import PyQt5.QtCore as qc

from cgt.model.velocitiescalculator import VelocitiesCalculator
from cgt.gui.Ui_resultswidget import Ui_ResultsWidget

class ResultsWidget(qw.QDialog, Ui_ResultsWidget):
    """display a table of results"""

    def __init__(self, parent, data_source=None):
        """
        initalize an object
            Args:
                parent widget (QWidget) must act as a data source for results
                data_source (VideoAnalysisResultsStore) the supplier of raw data
        """
        super().__init__(parent)
        self.setupUi(self)

        ## save the parent self.parent() will rewrap parent as pyqt widget
        self._data_source = data_source

        ## calculator for the motion velocities
        self._calculator = VelocitiesCalculator(self._data_source)

        ## table headers
        self.horizontal_headers = [["Type", "ID", "Speed"],
                                   ["Start", "End", "Displacement"]]

        self.new_data()

    @qc.pyqtSlot()
    def show_results(self):
        """
        display the current results
        """
        index = self._markerBox.currentIndex()
        if index == 0:
            self.show_all()
        else:
            self.show_selected(index-1)

    def show_selected(self, index):
        """
        show the detailed results for one marker
            Args:
                index (int) index of marker
        """
        lines, _ = self._calculator.number_markers()
        marker_displacments = None
        if index < lines:
            tmp = self._calculator.get_line_displacements()
            marker_displacments = tmp[index]
        else:
            tmp = self._calculator.get_point_displacements()
            marker_displacments = tmp[index-lines]

        self._tableWidget.setRowCount(len(marker_displacments))
        self._tableWidget.setColumnCount(3)

        self._tableWidget.setHorizontalHeaderLabels(self.horizontal_headers[1])

        for i, item in enumerate(marker_displacments):
            start = qw.QTableWidgetItem(str(item.get_start()))
            end = qw.QTableWidgetItem(str(item.get_end()))
            speed_item = qw.QTableWidgetItem(str(item.get_speed()))
            self._tableWidget.setItem(i, 0, start)
            self._tableWidget.setItem(i, 1, end)
            self._tableWidget.setItem(i, 2, speed_item)

        self._tableWidget.resizeColumnsToContents()
        self._tableWidget.resizeRowsToContents()

    def show_all(self):
        """
        show all average velocities for all the results
        """
        average_speeds = self._calculator.get_average_speeds()
        self._tableWidget.setRowCount(len(average_speeds))
        self._tableWidget.setColumnCount(3)

        self._tableWidget.setHorizontalHeaderLabels(self.horizontal_headers[0])

        for i, item in enumerate(average_speeds):
            id_item = qw.QTableWidgetItem(str(item.ID))
            type_item = qw.QTableWidgetItem(item.m_type.name)
            speed_item = qw.QTableWidgetItem(str(item.speed))
            self._tableWidget.setItem(i, 0, type_item)
            self._tableWidget.setItem(i, 1, id_item)
            self._tableWidget.setItem(i, 2, speed_item)

        self._tableWidget.resizeColumnsToContents()
        self._tableWidget.resizeRowsToContents()

    def show_tables(self):
        self._tableWidget.setRowCount(3)
        self._tableWidget.setColumnCount(3)

        self._tableWidget.setHorizontalHeaderLabels(self.horizontal_headers[0])
        for i in range(3):
            id_item = qw.QTableWidgetItem("ID")
            type_item = qw.QTableWidgetItem("Line")
            speed_item = qw.QTableWidgetItem("Velocity")
            self._tableWidget.setItem(i, 0, type_item)
            self._tableWidget.setItem(i, 1, id_item)
            self._tableWidget.setItem(i, 2, speed_item)

        self._tableWidget.resizeColumnsToContents()
        self._tableWidget.resizeRowsToContents()
    def set_up_combo_box(self):
        """
        add the lines and points to the combo box
        """
        self._markerBox.blockSignals(True)
        self._markerBox.clear()
        self._markerBox.addItem("All", ("All", 0))

        numbers = self._calculator.number_markers()

        for i in range(numbers[0]):
            self._markerBox.addItem(f"Line {i}")
        for i in range(numbers[1]):
            self._markerBox.addItem(f"Point {i}")

        self._markerBox.blockSignals(False)

    @qc.pyqtSlot()
    def new_data(self):
        """
        reciever for the signal that the data source has changed
        """
        if self._data_source is None:
            self.show_tables()
            return

        self._calculator.process_latest_data()
        self.set_up_combo_box()
        self.show_results()
