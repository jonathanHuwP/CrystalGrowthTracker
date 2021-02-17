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

    def __init__(self, parent=None):
        """
        the object initalization function

            Returns:
                None
        """
        super().__init__(parent)
        self.setupUi(self)

        self._number_rects = 0
        
        ## instructions
        self._inst_create = self.tr("""
        <p>To draw a region, left click down then drag.</p><p>On release you will have the options of storing, deleting or cancelling.</p><p>If cancelled you can access the options again by left clicking.</p>""")
    
        self._ints_edit = self.tr("""
        <p>Left click and drag on corners to adjust size</P><p>Left click and drag on centre to move region</p>
        """)
        
        self.display_instructions()

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

    def add_rectangle(self, rectangle):
        """
        add a new rectangle to the results
            Args:
                rectangle (int) the index of the rectangle to be added
        """
        self._number_rects += 1
        self._editComboBox.addItem(str(rectangle))

        if not self._editRegionButton.isEnabled():
            self._editRegionButton.setEnabled(True)
            
        if not self._displayMultipleButton.isEnabled():
            self._displayMultipleButton.setEnabled(True)

    def get_current_rectangle(self):
        """
        getter for the rectangle currently displayed in the edit combobox
            Retruns:
                tuple of (rectangle, index) or None if box is empty
        """
        if self._editComboBox.count() < 1:
            return None

        return self._editComboBox.currentIndex()

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
            print("inst multipl")
        elif self._deleteButton.isChecked():
            print("delete")
