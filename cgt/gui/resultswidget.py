## -*- coding: utf-8 -*-
"""
Created on Thursday 05 Aug 2021

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
import PyQt5.QtGui as qg

import pyqtgraph as pg

from cgt.model.velocitiescalculator import VelocitiesCalculator
from cgt.util.utils import get_region

from cgt.gui.Ui_resultswidget import Ui_ResultsWidget

class ResultsWidget(qw.QWidget, Ui_ResultsWidget):
    """
    class for display of results
    """

    def __init__(self, parent, data_source):
        """
        setup object and window
            Args:
                parent (QWidget): parent widget
                data_source (CrystalGrowthTrackerMain): holder of the results
        """
        super().__init__(parent)
        self.setupUi(self)

        ## holder of the results
        self._data_source = data_source

        ## the graph of the results
        self._graph = None

        self._graph = pg.PlotWidget(title="<b>Marker Displacments</b>")
        self._graph.setBackground('w')
        self._graphScrollArea.setWidget(self._graph)

        self.setup_display()

    def setEnabled(self, enabled):
        """
        enable/disable widget on enable the source
        is connected on disable play is paused
        """
        if enabled:
            super().setEnabled(True)
            self.setup_display()
        elif not enabled:
            super().setEnabled(False)


    def setup_display(self):
        """
        initalize the display
        """
        results = self._data_source.get_results()
        if results is None:
            return

        old_index = self._regionBox.currentIndex()
        self._regionBox.clear()

        for i in range(len(results.get_regions())):
            self._regionBox.addItem(str(i))

        if len(results.get_regions()) > 0:
            if old_index < 0:
                old_index = 0
            self.show_results(old_index)

    @qc.pyqtSlot(int)
    def show_results(self, index):
        """
        show the table and graph
            Args:
                index (int): the index of the region
        """
        self.fill_table(index)
        self.draw_graph_of_region(index)

    def fill_table(self, index):
        """
        fill the tree widget
        """
        self._resultsTable.clear()

        headers = ["Marker", "Start Frame", "End Frame", "Displacement"]
        self._resultsTable.setColumnCount(4)
        self._resultsTable.setHorizontalHeaderLabels(headers)

        self._resultsTable.setRowCount(10)

        calc = self.calculate_speeds(index)
        lines = calc.get_line_displacements()
        points = calc.get_point_displacements()

        row = 0
        for j, line in enumerate(lines):
            for displacement in line:
                self._resultsTable.setItem(row, 0, qw.QTableWidgetItem(self.tr(f"Line {j}")))
                self._resultsTable.setItem(row, 1, qw.QTableWidgetItem(str(displacement.get_start())))
                self._resultsTable.setItem(row, 2, qw.QTableWidgetItem(str(displacement.get_end())))
                self._resultsTable.setItem(row, 3, qw.QTableWidgetItem( f"{displacement.get_length():.2f}"))
                row += 1

        for j, point in enumerate(points):
            for displacement in point:
                self._resultsTable.setItem(row, 0, qw.QTableWidgetItem(self.tr(f"Point {j}")))
                self._resultsTable.setItem(row, 1, qw.QTableWidgetItem(str(displacement.get_start())))
                self._resultsTable.setItem(row, 2, qw.QTableWidgetItem(str(displacement.get_end())))
                self._resultsTable.setItem(row, 3, qw.QTableWidgetItem( f"{displacement.get_length():.2f}"))
                row += 1

    def draw_graph_of_region(self, index):
        """
        callback for change of region
            Args:
                index (int): the array index of the region
        """
        self._graph.clear()

        label_style = {'font-weight': 'bold'}
        calc = self.calculate_speeds(index)
        lines = calc.get_line_displacements()
        points = calc.get_point_displacements()

        tick_font = qg.QFont()
        tick_font.setBold(True)

        self._graph.getAxis('left').setLabel("Displacement (micron)", **label_style)
        self._graph.getAxis('left').setTickFont(tick_font)
        self._graph.getAxis('bottom').setLabel("Frame (number)", **label_style)
        self._graph.getAxis('bottom').setTickFont(tick_font)

        for i, marker in enumerate(lines):
            displacements = [0.0]
            frames = [0]
            for dis in marker:
                new_dis = displacements[-1] + dis.get_length()
                displacements.append(new_dis)
                frames.append(dis.get_end())

            self._graph.plot(frames, displacements, pen='b', name=f"Line {i}")

        for i, marker in enumerate(points):
            displacements = [0.0]
            frames = [0]
            for dis in marker:
                new_dis = displacements[-1] + dis.get_length()
                displacements.append(new_dis)
                frames.append(dis.get_end())

            self._graph.plot(frames, displacements, pen='b', name=f"Point {i}")

        self._graph.addLegend()

    def calculate_speeds(self, index):
        """
        carry out speeds calculation
            Args:
                index (int) the region
        """
        results = self._data_source.get_results()
        lines = []
        for marker in results.get_lines():
            if get_region(marker[0]) == index:
                lines.append(marker)

        points = []
        for marker in results.get_points():
            if get_region(marker[0]) == index:
                points.append(marker)

        fps = self._data_source.get_project()["frame_rate"]
        scale = self._data_source.get_project()["resolution"]
        calculator = VelocitiesCalculator(lines, points, fps, scale)
        calculator.process_latest_data()
        return calculator
