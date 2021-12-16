# -*- coding: utf-8 -*-
## @package videoparametersdialog
# a widget allowing the user to enter the parameters for a new project
#
# @copyright 2020 University of Leeds, Leeds, UK.
# @author j.h.pickering@leeds.ac.uk and j.leng@leeds.ac.uk
"""
Created on Thursday 08 Oct 2020

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

This work was funded by Joanna Leng's EPSRC funded RSE Fellowship (EP/R025819/1)
"""
# set up linting conditions
# pylint: disable = too-many-public-methods
# pylint: disable = c-extension-no-member
# pylint: disable = too-many-return-statements

import PyQt5.QtWidgets as qw
import PyQt5.QtCore as qc

from cgt.gui.Ui_videoparametersdialog import Ui_VideoParametersDialog

class VideoParametersDialog(qw.QDialog, Ui_VideoParametersDialog):
    """
    a qDialog the allows the user to start a new project
    """

    ## the available units for the resolution
    RESOLUTION_UNITS = ["nanometers", "microns", "mm"]

    @staticmethod
    def get_values_from_user(parent, fps, resolution, units):
        """
        run VideoParametersDialog to get user input
        """
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
        self._resolution_units = units

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
        self._resolution_units = self._unitsComboBox.currentText()

        self.close()

    def get_values(self):
        """
        getter for the values
            Returns:
                (<frames per second>, <resoultion>, <resolution units>)
        """
        return self._fps, self._resolution, self._resolution_units
