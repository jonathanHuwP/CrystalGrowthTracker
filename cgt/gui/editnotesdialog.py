# -*- coding: utf-8 -*-
"""
Created on Tuesday 13 Oct 2020

@copyright 2020
@author: j.h.pickering@leeds.ac.uk
"""

# set up linting conditions
# pylint: disable = too-many-public-methods
# pylint: disable = c-extension-no-member
# pylint: disable = too-many-return-statements

import sys

import PyQt5.QtWidgets as qw
import PyQt5.QtCore as qc

from cgt.gui.Ui_editnotesdialog import Ui_EditNotesDialog

# TODO upgrade to Dialog

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


if __name__ == "__main__":
    run_main()