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
import PyQt5.QtWidgets as qw
import PyQt5.QtCore as qc

from cgt.gui.videoregionselectionwidgetstates import VideoRegionSelectionWidgetStates as states

# import UI
from cgt.gui.Ui_regionviewcontrol import Ui_RegionViewControl

class RegionViewControl(qw.QWidget, Ui_RegionViewControl):

    ## signal a change of state
    state_change = qc.pyqtSignal(int)

    def __init__(self, parent=None):
        """
        the object initalization function

            Returns:
                None
        """
        super().__init__(parent)
        self.setupUi(self)
        
    @qc.pyqtSlot(qw.QAbstractButton)
    def button_clicked(self, button):
        if button == self._viewVideoButton:
            self.state_change.emit(states.VIEW)
        elif button == self._createRegionButton:
            self.state_change.emit(states.CREATE)
        elif button == self._editRegionButton:
            self.state_change.emit(states.EDIT)
        elif button == self._displayMultipleButton:
            self.state_change.emit(states.DISPLAY)
        elif button == self._deleteButton:
            self.state_change.emit(states.DELETE)
            
        self.enable_combo_boxes()
            
    def add_rectangle(self, rectangle):
        number = self._editComboBox.count() + 1
        text = f"{number:0>2d}"
        self._editComboBox.addItem(text, rectangle)
        
        if not self._editRegionButton.isEnabled():
            self._editRegionButton.setEnabled(True)
            
    def enable_combo_boxes(self):
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