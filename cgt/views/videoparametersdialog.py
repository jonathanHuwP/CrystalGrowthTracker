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

#from cgt.Ui_videoparametersdialog import Ui_VideoParametersDialog
from cgt.views.videoparametersdialog_ui import Ui_VideoParametersDialog

class VideoParametersDialog(qw.QDialog, Ui_VideoParametersDialog):
    """
    a qDialog the allows the user to start a new project
    """

    ## the available units for the resolution
    RESOLUTION_UNITS = ["nanometers", "microns", "mm"]

    def get_values_from_user(self, parent, fps, resolution, units):
        window = VideoParametersDialog(parent, fps, resolution, units)
        window.exec_()
        return  window.get_values()

    def __init__(self, parent=None, fps=None, resolution=None, units=None):
        """
        set up the dialog

            Args:
                parent (QObject) the parent object
                fps: (int) frames pre second
                resolution (float) the real world size of a pixel
                unit (string) the units, must be in RESOLUTION_UNITS

            Returns:
                None
        """
        super().__init__(parent)

        ## the parent object, if any
        self._parent = parent

        ## the name in translation, if any
        self._translated_name = self.tr("VideoParametersDialog")

        self.setupUi(self)

        ## storage for the frames per second
        self._fps = fps

        ## storage for the resolution
        self._resolution = resolution

        index = VideoParametersDialog.RESOLUTION_UNITS.index(units)
        ## storage for the resolution units
        self._resolutionUnits = units

        self._unitsComboBox.addItems(VideoParametersDialog.RESOLUTION_UNITS)

        if fps is not None:
            self._fpsBox.setValue(fps)

        if resolution is not None:
            self._resolutionBox.setValue(resolution)

        if units is not None:
            self._unitsComboBox.setCurrentIndex(index)


    @qc.pyqtSlot()
    def set_parameters(self):
        """
        callback for setting the parameters

            Returns:
                None
        """
        self._fps = self._fpsBox.value()
        self._resolution = self._resolutionBox.value()
        self._resolutionUnits = self._unitsComboBox.currentText()

        self.close()

    def get_values(self):
        return self._fps, self._resolution, self._resolutionUnits


#######################################

def run():
    """
    make and display the object

        Returns:
            None
    """
    app = qw.QApplication(sys.argv)

    window = VideoParametersDialog(fps=8, resolution=0.81, units="nanometers")
    window.show()
    app.exec_()

    tmp = window.get_values()
    print(tmp)

if __name__ == "__main__":
    run()
