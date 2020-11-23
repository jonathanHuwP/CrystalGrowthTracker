# -*- coding: utf-8 -*-
"""
Created on Fri September 25 2020

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
import sys

import PyQt5.QtWidgets as qw
import PyQt5.QtGui as qg
import PyQt5.QtCore as qc

from enum import IntEnum

from cgt.gui.Ui_resultstreewidget import Ui_ResultsTreeWidget

class ResultType(IntEnum):
    """
    type codes for use in QTreeWidgetItem
    """

    ## the item represents a region
    REGION = 0

    ## the item represents a crystal
    CRYSTAL = 10

    ## the set of lines at a given time
    FRAME_NUMBER = 20

    ## the item represents a line
    LINE = 30

class ResultsTreeWidget(qw.QWidget, Ui_ResultsTreeWidget):
    """
    a widget providing a tree view on results data
    """

    def __init__(self, parent=None, data_source=None):
        """
        set up the dialog

            Args:
                parent (QObject) the parent object

            Returns:
                None
        """
        super(ResultsTreeWidget, self).__init__(parent)
        self.setupUi(self)

        ## the data_source object holding the results
        self._data_source = data_source

        # set up the tree and display
        h_list = ["Region", "Crystal", "Time", "Line"]
        self._tree.setColumnCount(len(h_list))
        self._tree.setHeaderLabels(h_list)

        if data_source is not None:
            self.fill_tree()

    def set_data_source(self, data_source):
        """
        setter for the object holding the data to be displayed

            Args:
                data_source (CrystalGrowthTrackerMain) object holding data

            Returns:
                None
        """
        self._data_source = data_source
        self.fill_tree()

    @qc.pyqtSlot()
    def item_selected(self):
        """
        callback for the selection of an item
        """
        item = self._tree.currentItem()
        item_type = item.type()

        if item_type == ResultType.REGION:
            self.region_selected(item)
        elif item_type == ResultType.CRYSTAL:
            self.crystal_selected(item)
        elif item_type == ResultType.FRAME_NUMBER:
            self.frame_selected(item)
        elif item_type == ResultType.LINE:
            self.line_selected(item)

    def region_selected(self, item):
        """
        a line has been selected

            Returns:
                None
        """
        r_index = item.data(0, qc.Qt.UserRole)
        print("region {}".format(r_index))
        if self.parent() is not None:
            self.parent().parent().select_region(r_index)

    def crystal_selected(self, item):
        """
        a line has been selected

            Returns:
                None
        """
        r_index = item.data(0, qc.Qt.UserRole)
        c_index = item.data(1, qc.Qt.UserRole)
        print("region {}, crystal {}".format(r_index, c_index))
        if self.parent() is not None:
            self.parent().parent().select_crystal(r_index, c_index)

    def frame_selected(self, item):
        """
        a line has been selected

            Returns:
                None
        """
        r_index = item.data(0, qc.Qt.UserRole)
        c_index = item.data(1, qc.Qt.UserRole)
        f_index = item.data(2, qc.Qt.UserRole)
        print("region {}, crystal {}, frame {}".format(r_index, c_index, f_index))
        if self.parent() is not None:
            self.parent().parent().select_frame(r_index, c_index, f_index)

    def line_selected(self, item):
        """
        a line has been selected

            Returns:
                None
        """
        r_index = item.data(0, qc.Qt.UserRole)
        c_index = item.data(1, qc.Qt.UserRole)
        f_index = item.data(2, qc.Qt.UserRole)
        l_index = item.data(3, qc.Qt.UserRole)
        print("region {}, crystal {}, frame, {}, line {}".format(
            r_index, c_index, f_index, l_index))
        if self.parent() is not None:
            self.parent().parent().select_line(r_index, c_index, f_index, l_index)

    def fill_tree(self):
        """
        clear the tree and fill with data from the data_source

            Returns:
                None
        """
        self._tree.clear()

        if self._data_source is None:
            return

        result = self._data_source.get_result()

        if result is None:
            return

        items = []

        for r_index, region in enumerate(result.regions):
            r_item = qw.QTreeWidgetItem(self._tree, [str(r_index)], ResultType.REGION)
            r_var = qc.QVariant(r_index)
            r_item.setData(0, qc.Qt.UserRole, r_var)
            items.append(r_item)

            for c_index, crystal in enumerate(result.get_crystals(r_index)):
                c_item = qw.QTreeWidgetItem(r_item, ["", str(c_index)], ResultType.CRYSTAL)
                c_var = qc.QVariant(c_index)
                c_item.setData(0, qc.Qt.UserRole, r_var)
                c_item.setData(1, qc.Qt.UserRole, c_var)

                for frame_number in crystal.list_of_frame_numbers:
                    f_item = qw.QTreeWidgetItem(c_item, ["", "", str(frame_number)], ResultType.FRAME_NUMBER)
                    f_var = qc.QVariant(frame_number)
                    f_item.setData(0, qc.Qt.UserRole, r_var)
                    f_item.setData(1, qc.Qt.UserRole, c_var)
                    f_item.setData(2, qc.Qt.UserRole, f_var)

                    for l_index, line in enumerate(crystal.faces_in_frame(frame_number)):
                        l_item = qw.QTreeWidgetItem(c_item, ["", "", "", str(l_index)], ResultType.LINE)
                        l_var = qc.QVariant(l_index)
                        l_item.setData(0, qc.Qt.UserRole, r_var)
                        l_item.setData(1, qc.Qt.UserRole, c_var)
                        l_item.setData(2, qc.Qt.UserRole, f_var)
                        l_item.setData(3, qc.Qt.UserRole, l_var)

        self._tree.addTopLevelItems(items)

    def clear(self):
        """
        clear the tree

            Returns:
                None
        """
        self._tree.clear()
