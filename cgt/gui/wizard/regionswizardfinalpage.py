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

from cgt.gui.wizard.regionswizardpages import RegionsWizardPages as rwp

class RegionsWizardFinalPage(qw.QWizardPage):
    """
    final page of region selection
    """

    def __init__(self, parent=None):
        """
        set up the widget
        """
        super().__init__(parent)
        
        # combo box 
        self._comboBox = qw.QComboBox(self)
        self._comboBox.addItem("Final 1", "Alice")
        self._comboBox.addItem("Final 2", "Bob")
        
        layout = qw.QVBoxLayout()
        layout.addWidget(self._comboBox)
        self.setLayout(layout)
        
        self.registerField("person-choice", self._comboBox, "currentData")
