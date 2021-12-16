# -*- coding: utf-8 -*-
## @package editnotesdialog
# <PACKAGE DESCRIPTION>
#
# @copyright Jonathan Pickering and Joanna Leng, University of Leeds, Leeds, UK.
"""
Created on Tuesday 13 Oct 2020

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

# set up linting conditions
# pylint: disable = too-many-public-methods
# pylint: disable = c-extension-no-member
# pylint: disable = too-many-return-statements

import sys

import PyQt5.QtWidgets as qw
import PyQt5.QtCore as qc

from cgt.gui.Ui_editnotesdialog import Ui_EditNotesDialog

class EditNotesDialog(qw.QDialog, Ui_EditNotesDialog):
    """
    a qDialog the allowing the user to view and edit the project notes
    """

    def __init__(self, parent=None, data_source=None):
        """
        set up the Dialog

            Args:
                parent (QObject) the parent object
                parent: (QDialog) pointer to the parent Dialog
                data_source: (CGTProject) the project object

            Returns:
                None
        """
        super().__init__(parent)

        self.setupUi(self)

        ## pointer to the project holding the notes
        self._data_source = data_source

        self.display_notes()

    def display_notes(self):
        """
        display the current notes

            Reuturns:
                None
        """
        self._notesBrowser.clear()

        if self._data_source is None:
            return

        if self._data_source["notes"] is not None:
            self._notesBrowser.setText(self._data_source["notes"])
            self.parent().display_properties()

    @qc.pyqtSlot()
    def change_notes(self):
        """
        update the notes in the data project

            Returns:
                None
        """
        if self._data_source is None:
            return

        if self._data_source["notes"] is not None:
            self._data_source["notes"] = self._notesBrowser.toPlainText()
            self.parent().display_properties()

        self.close()

#####################################

def run_main():
    """
    use a local function to make an isolated the QApplication object

        Returns:
            None
    """

    app = qw.QApplication(sys.argv)
    window = EditNotesDialog()
    window.show()
    app.exec_()
