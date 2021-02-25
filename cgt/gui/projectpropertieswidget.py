## -*- coding: utf-8 -*-
"""
Created on Wed Sept 30 2020

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
import sys

import PyQt5.QtWidgets as qw
import PyQt5.QtGui as qg
import PyQt5.QtCore as qc

# import UI
from cgt.gui.Ui_projectpropertieswidget import Ui_ProjectPropertiesWidget

class ProjectPropertiesWidget(qw.QWidget, Ui_ProjectPropertiesWidget):
    """
    The implementation of the GUI, all the functions and
    data-structures required to implement the intended behaviour
    """

    def __init__(self, parent=None, data_source=None):
        """
        the object initalization function

            Args:
                parent (QObject): the parent QObject for this window
                data_source (QObject): the object holding the data

            Returns:
                None
        """
        super().__init__(parent)

        self.setupUi(self)

        ## the class holding the data
        self._data_source = data_source

    def clear(self):
        """
        clear the contents

            Return:
                None
        """
        self._propertiesBrowser.clear()

    def clear_and_display_text(self, text):
        """
        clear widget and display text

            Args:
                text (string) the text to be displayed

            Returns:
                None
        """
        self._propertiesBrowser.clear()
        self._propertiesBrowser.setText(text)
        self._propertiesBrowser.verticalScrollBar().setValue(0)

    def append_text(self, text):
        """
        append text to existing

            Args:
                text (string) the text to be displayed

            Returns:
                None
        """
        self._propertiesBrowser.append(text)

    def show_top_text(self):
        self._propertiesBrowser.verticalScrollBar().setValue(0)

#####################################

def run_main():
    """
    use a local function to make an isolated the QApplication object
        Returns:
            None
    """

    app = qw.QApplication(sys.argv)
    window = ProjectPropertiesWidget()
    window.clear_and_display_text("This is some <b>text</b>")
    window.append_text("<p>More text</p>")
    window.show()
    app.exec_()


if __name__ == "__main__":
    run_main()