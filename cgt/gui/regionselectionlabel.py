# -*- coding: utf-8 -*-
"""
Created on Wed Jun 10 11:28:23 2020

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

@copyright 2020
@author: j.h.pickering@leeds.ac.uk and j.leng@leeds.ac.uk
"""
import numpy as np

import PyQt5.QtWidgets as qw
import PyQt5.QtGui as qg
import PyQt5.QtCore as qc

# set up linting conditions
# pylint: disable = too-many-public-methods
# pylint: disable = c-extension-no-member

class RegionSelectionLabel(qw.QLabel):
    """
    subclass of label allowing selection of region by drawing rectangle and
    displaying a list of already selected rectangles.
    """
    
    ## signal to indicate the user has selected a new rectangle
    new_selection = qc.pyqtSignal()
    
    def __init__(self, parent=None):
        """
        Set up the label

            Args:
                parent (QObject) the parent object

            Returns:
                None
        """
        super().__init__(parent)

        ## the widget's state
        self._drawing = False

        ## the translated name
        self._translation_name = self.tr("RegionSelectionLabel")
