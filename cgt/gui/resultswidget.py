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

        self._graph = pg.PlotWidget(title="<b>Marker Speeds</b>")
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
            self.fill_tree()

            if old_index >=0:
                self.draw_graph_of_region(old_index)

    def fill_tree(self):
        """
        fill the tree widget
        """
        print("fill tree")
        results = self._data_source.get_results()

        headers = ["Region", "Marker Type", "Interval", "Speed"]
        self._resultsTree.setColumnCount(3)
        self._resultsTree.setHeaderLabels(headers)

        for i, _ in enumerate(results.get_regions()):
            calc = self.calculate_speeds(i)
            region_item = qw.QTreeWidgetItem(self._resultsTree)
            region_item.setText(0, str(i))
            lines = calc.get_line_displacements()

            for line in lines:
                marker_item = qw.QTreeWidgetItem(region_item)
                marker_item.setText(1, self.tr("Line"))
                print(f"dis type is {type(line)}")

                # for line in marker:
                #     interval_item = qw.QTreeWidgetItem(marker_item)
                #     interval_item.setText(2, "hi")
                #     interval_item.setText(3, "ho")

    @qc.pyqtSlot(int)
    def draw_graph_of_region(self, index):
        """
        callback for change of region
            Args:
                index (int): the array index of the region
        """
        print("draw")

        # label_style = {'font-weight': 'bold'}
        # result = self._data_source.get_results()[index]

        # tick_font = qg.QFont()
        # tick_font.setBold(True)

        # self._graph.getAxis('left').setLabel("Speed (Level)", **label_style)
        # self._graph.getAxis('left').setTickFont(tick_font)
        # self._graph.getAxis('bottom').setLabel("Interval (number)", **label_style)
        # self._graph.getAxis('bottom').setTickFont(tick_font)

        # x_axis = [1, 2]

        # for marker in result:
        #     speeds = []
        #     for speed in marker[1]:
        #         speeds.append(speed[1])

        #     self._graph.plot(x_axis, speeds, pen='b', name="Speed")

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
                print(f"Region {index} line {marker[0]}")
                lines.append(marker)

        points = []
        for marker in results.get_points():
            if get_region(marker[0]) == index:
                print(f"Region {index} point {marker[0]}")
                points.append(marker)

        fps = self._data_source.get_project()["frame_rate"]
        scale = self._data_source.get_project()["resolution"]
        calculator = VelocitiesCalculator(lines, points, fps, scale)
        calculator.process_latest_data()
        return calculator
