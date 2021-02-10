# -*- coding: utf-8 -*-
"""
Created on Wed Feb 10 2021

provides a class, derived from QLabel, that allows the user to select a
retcangular region of a pixmap in pixmap coordinates

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

# import UI
from cgt.gui.Ui_regionviewcontrol import Ui_RegionViewControl

class RegionViewControl(qw.QWidget, Ui_RegionViewControl):

    def __init__(self, parent=None):
        """
        the object initalization function

            Returns:
                None
        """
        super().__init__(parent)
        self.setupUi(self)