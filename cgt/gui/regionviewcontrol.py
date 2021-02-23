# -*- coding: utf-8 -*-
"""
Created on Wed Feb 10 2021

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
# pylint: disable = import-error

import PyQt5.QtWidgets as qw
import PyQt5.QtCore as qc

from cgt.gui.videoregionselectionwidgetstates import VideoRegionSelectionWidgetStates as states

# import UI
from cgt.gui.Ui_regionviewcontrol import Ui_RegionViewControl

class RegionViewControl(qw.QWidget, Ui_RegionViewControl):
    """
    the widget that allows the user to select the opreating mode of the regionselectionwidget
    """

    ## signal a change of state
    state_change = qc.pyqtSignal(int)

    ## signal to change the editing region
    change_edit_region = qc.pyqtSignal()

    ## signal to change the editing region
    change_display_region = qc.pyqtSignal()

    ## signal to change the editing region
    change_delete_region = qc.pyqtSignal()

    def __init__(self, parent=None):
        """
        the object initalization function

            Returns:
                None
        """
        super().__init__(parent)
        self.setupUi(self)

        # the parent holding the data store
        self._data_source = None

        ## instructions
        self._inst_create = self.tr("""
        <p>To draw a region, left click down then drag.</p><p>On release you will have the options of storing, deleting or cancelling.</p><p>If cancelled you can access the options again by left clicking.</p>""")

        self._ints_edit = self.tr("""
        <p>Left click and drag on corners to adjust size</P><p>Left click and drag on centre to move region</p>
        """)

        self._inst_display = self.tr("""
        <p>Review your work.</p><p>Use the selection box to choose the region, or all.</p>
        """)

        self._inst_delete = self.tr("""
        <p>Left mouse button to select for delete. Click "yes" on pop-up to complete.</p>
        <p>This is not reversable.</p>
        """)

        self.display_instructions()

    def set_data_source(self, data_source):
        """
        assign the object holding the data on rectangles
            Args:
                data_source (object) the widget holding the data
        """
        self._data_source = data_source

    @qc.pyqtSlot(qw.QAbstractButton)
    def button_clicked(self, button):
        """
        callback for a button click
            Args:
                button (QAbstractButton) pointer to the button
        """
        if button == self._createRegionButton:
            self.state_change.emit(states.CREATE)
        elif button == self._editRegionButton:
            self.state_change.emit(states.EDIT)
        elif button == self._displayMultipleButton:
            self.state_change.emit(states.DISPLAY)
        elif button == self._deleteButton:
            self.state_change.emit(states.DELETE)

        self.enable_combo_boxes()
        self.display_instructions()

    @qc.pyqtSlot(int)
    def edit_combo_changed(self):
        """
        emit the signal for editing box changed
        """
        self.change_edit_region.emit()

    @qc.pyqtSlot(int)
    def display_combo_changed(self):
        """
        emit the signal for display box changed
        """
        self.change_display_region.emit()

    @qc.pyqtSlot(int)
    def delete_combo_changed(self):
        """
        emit the signal for delete box changed
        """
        self.change_delete_region.emit()

    def data_changed(self):
        """
        the results have changed reload combo boxes
        """
        all_text = self.tr("All")

        self._editComboBox.clear()
        self._displayComboBox.clear()
        self._displayComboBox.addItem(all_text)
        self._deleteComboBox.clear()
        self._deleteComboBox.addItem(all_text)

        for rectangle_index in range(0, self._data_source.get_data().length):
            text = str(rectangle_index + 1)
            self._editComboBox.addItem(text)
            self._displayComboBox.addItem(text)
            self._deleteComboBox.addItem(text)

        if not self._editRegionButton.isEnabled():
            self._editRegionButton.setEnabled(True)

        if not self._displayMultipleButton.isEnabled():
            self._displayMultipleButton.setEnabled(True)

        if not self._deleteButton.isEnabled():
            self._deleteButton.setEnabled(True)

    def get_current_rectangle(self):
        """
        getter for the rectangle currently displayed in the edit combobox
            Returns:
                index (int) or -1 if box is empty
        """
        if self._editRegionButton.isChecked():
            return self._editComboBox.currentIndex()

        if self._displayMultipleButton.isChecked():
            return self._displayComboBox.currentIndex()

        if self._deleteButton.isChecked():
            return self._deleteComboBox.currentIndex()

        return -1

    def enable_combo_boxes(self):
        """
        enable disable the combo boxes according to the checked radio buttons
        """
        edit_box = False
        display_box = False
        delete_box = False

        if self._editRegionButton.isChecked():
            edit_box = True
        elif self._displayMultipleButton.isChecked():
            display_box = True
        elif self._deleteButton.isChecked():
            delete_box = True

        self._editComboBox.setEnabled(edit_box)
        self._displayComboBox.setEnabled(display_box)
        self._deleteComboBox.setEnabled(delete_box)

    qc.pyqtSlot(int)
    def show_hide_instructions(self, value):
        """
        toggel the instructions on/off
            Args:
                value (bool) if True instructions visible else hidden
        """
        if value == 0:
            self._instructionsBrowser.setVisible(False)
            self._instructionsBrowser.clear()
        else:
            self._instructionsBrowser.setVisible(True)
            self.display_instructions()

    def display_instructions(self):
        """
        display the instructions
        """
        self._instructionsBrowser.clear()

        if self._createRegionButton.isChecked():
            self._instructionsBrowser.append(self._inst_create)
        elif self._editRegionButton.isChecked():
            self._instructionsBrowser.append(self._ints_edit)
        elif self._displayMultipleButton.isChecked():
            self._instructionsBrowser.append(self._inst_display)
        elif self._deleteButton.isChecked():
            self._instructionsBrowser.append(self._inst_delete)
