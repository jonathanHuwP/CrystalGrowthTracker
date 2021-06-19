## -*- coding: utf-8 -*-
"""
Created on Sat June 19 2021

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
import PyQt5.QtGui as qg
import PyQt5.QtCore as qc
import PyQt5.QtWebEngineWidgets as qe

# import UI
from cgt.gui.Ui_reportwidget import Ui_ReportWidget

class ReportWidget(qw.QWidget, Ui_ReportWidget):
    """
    a widget for viewing the current HTML report
    """

    def __init__(self, parent, data_source):
        """
        the object initalization function

            Args:
                parent (QObject): the parent QObject for this window
                data_source (QObject): the object holding the data
        """
        super().__init__(parent)

        self.setupUi(self)

        ## the main window
        self._data_source = data_source

        self._view = qe.QWebEngineView()
        self._scrollArea.setWidget(self._view)
        self._scrollArea.setWidgetResizable(True)
