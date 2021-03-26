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

from cgt.gui.regionselectionview import SelectStates as states

# import UI
from cgt.gui.Ui_regionviewcontrol import Ui_RegionViewControl

class RegionViewControl(qw.QWidget, Ui_RegionViewControl):
    """
    the widget that allows the user to select the opreating mode of the regionselectionwidget
    """

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

        ## instructions
        self._inst_create = self.tr("""
        <p>To draw a region, left click down then drag.</p>""")

        self._ints_edit = self.tr("""
        <p>Left click and drag on corners to adjust size</P>
        """)

        self._inst_display = self.tr("""
        <p>Review your work.</p><p>Select regions to view contents in side panel.</p>
        """)

        self._inst_delete = self.tr("""
        <p>Left mouse button to select for delete. Click "yes" on pop-up to complete.</p>
        <p>This is not reversable.</p>
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
            self.state_change.emit(states.MAKE_REGION)
        elif button == self._editRegionButton:
            self.state_change.emit(states.EDIT_REGION)
        elif button == self._displayMultipleButton:
            self.state_change.emit(states.VIEW)
        elif button == self._deleteButton:
            self.state_change.emit(states.DELETE_REGION)

        self.display_instructions()

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
