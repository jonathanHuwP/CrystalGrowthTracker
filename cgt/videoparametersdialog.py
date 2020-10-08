# -*- coding: utf-8 -*-
"""
Created on Thursday 08 Oct 2020

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

from cgt.Ui_videoparametersdialog import Ui_VideoParametersDialog

class VideoParametersDialog(qw.QDialog, Ui_VideoParametersDialog):
    """
    a qDialog the allows the user to start a new project
    """

    def __init__(self, parent=None):
        """
        set up the dialog

            Args:
                parent (QObject) the parent object

            Returns:
                None
        """
        super().__init__(parent)

        ## the parent object, if any
        self._parent = parent

        ## the name in translation, if any
        self._translated_name = self.tr("VideoParametersDialog")

        self.setupUi(self)
        
        units = ["nanometers", "microns", "mm"]
        self._unitsComboBox.addItems(units)

    @qc.pyqtSlot()
    def set_parameters(self):
        """
        callback for setting the parameters

            Returns:
                None
        """
        s = "VideoParametersDialog.set_parameters({} {} {})"
        s = s.format(self._unitsComboBox.currentText(),
                     self._resolutionBox.value(),
                     self._fpsBox.value())

        print(s)


#######################################

def run():
    """
    make and display the object

        Returns:
            None
    """
    app = qw.QApplication(sys.argv)

    window = VideoParametersDialog()
    window.show()
    app.exec_()

if __name__ == "__main__":
    run()
