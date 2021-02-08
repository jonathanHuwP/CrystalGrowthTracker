## -*- coding: utf-8 -*-
"""
Created on Mon 08 Feb 2021

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

from cgt.gui.wizard.regionswizardpages import RegionsWizardPages as rwp

class RegionsWizardStartPage(qw.QWizardPage):
    """
    the first page of the region selection
    """

    def __init__(self, parent=None):
        """
        set up the page
        """
        super().__init__(parent)
        
        # combo box with some data
        self._comboBox = qw.QComboBox(self)
        self._comboBox.addItem("Arrive", "Hello")
        self._comboBox.addItem("Leave", "Bye")
        
        # add an output widget
        self._label = qw.QLabel(self)
        
        # add a button
        self._button = qw.QPushButton("Make")
        self._button.clicked.connect(self.make_text)
        
        layout = qw.QVBoxLayout()
        layout.addWidget(self._comboBox)
        layout.addWidget(self._label)
        layout.addWidget(self._button)
        self.setLayout(layout)
        
        # register the combobox data function for access by main wizard
        self.registerField("greeting-choice", self._comboBox, "currentData")
        self.registerField("text-displayed", self._label, "text")
        
        # completed flag
        self._complete = False

    qc.pyqtSlot()
    def make_text(self):
        self._label.setText("Once upon a time in Yorkshire ....")
        self._complete = True
        self.completeChanged.emit()
        
    def isComplete(self):
        return self._complete
        
    def nextId(self):
        """
        return the id of the next page
        """
        return rwp.PAGE_FINAL