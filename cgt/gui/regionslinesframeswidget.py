# -*- coding: utf-8 -*-
"""
Created on Sat December 05 2020

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

# linting conditions
# pylint: disable = import-error

import sys

import PyQt5.QtWidgets as qw
import PyQt5.QtGui as qg
import PyQt5.QtCore as qc

from cgt.gui.Ui_regionslinesframeswidget import Ui_RegionsLinesFramesWidget

class RegionsLinesFramesWidget(qw.QWidget, Ui_RegionsLinesFramesWidget):
    """
    provide the user with a view of Regions, lines and linesegments,
    and a means to navigate the data
    """

    def __init__(self, parent=None, data_source=None):
        """
        initialize an object

            Args:
                parent (QWidget) if exists the widget holding this widget.
                data_source (VideoAnalysisResultsStore) the data to be displayed
        """
        super().__init__(parent)
        self.setupUi(self)

        ## pointer to the data for display
        self._data_source = data_source

        if data_source is not None:
            self.display_data()

    def display_data(self):
        print(id(self))



def run():
    """
    use a local function to make an isolated the QApplication object

        Returns:
            None
    """

    app = qw.QApplication(sys.argv)

    window = RegionsLinesFramesWidget()
    window.show()
    app.exec_()

if __name__ == "__main__":
    run()