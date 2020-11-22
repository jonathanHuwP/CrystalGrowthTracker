## -*- coding: utf-8 -*-
"""
Created on Tue 22 Nov 2020

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
# pylint: disable = too-few-public-methods
# pylint: disable = c-extension-no-member
# pylint: disable = import-error

import PyQt5.QtWidgets as qw
import PyQt5.QtCore as qc

from cgt.gui.CrystalGrowthTrackerMain import CrystalGrowthTrackerMain

class CGTApp(qw.QApplication):
    """
    the application that runs the main window
    """

    def __init__(self, args):
        super().__init__(args)
        self.setApplicationName("CrystalGrowthTracker")
        self.setApplicationVersion("B0.1")
        self.setOrganizationName("School of Computer Science, University of Leeds, Leeds, UK")
        self.setOrganizationDomain("leeds.ac.uk")
        self.setAttribute(qc.Qt.AA_EnableHighDpiScaling)

        window = CrystalGrowthTrackerMain()
        window.show()

        self.exec_()    # enter event loop