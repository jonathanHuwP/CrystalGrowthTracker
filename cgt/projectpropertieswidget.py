## -*- coding: utf-8 -*-
"""
Created on Wed Sept 30 2020

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at
http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

@copyright 2020
@author: j.h.pickering@leeds.ac.uk
"""
import sys

import PyQt5.QtWidgets as qw
import PyQt5.QtGui as qg
import PyQt5.QtCore as qc

# import UI
from Ui_projectpropertieswidget import Ui_ProjectPropertiesWidget

class ProjectPropertiesWidget(qw.QWidget, Ui_ProjectPropertiesWidget):
    """
    The implementation of the GUI, all the functions and
    data-structures required to implement the intended behaviour
    """

    def __init__(self, parent=None, owner=None):
        """
        the object initalization function

            Args:
                parent (QObject): the parent QObject for this window
                owner (QObject): the object holding the data

            Returns:
                None
        """
        super().__init__(parent)

        self.setupUi(self)

        ## the class holding the data
        self._owner = owner

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

    def append_text(self, text):
        """
        append text to existing

            Args:
                text (string) the text to be displayed

            Returns:
                None
        """
        self._propertiesBrowser.append(text)
        
    @qc.pyqtSlot()
    def change_frame_rate_and_resolution(self):
        print("ProjectPropertiesWidget.change_frame_rate_and_resolution")
        if self._owner is not None:
            self._owner.set_video_scale_parameters()

#####################################

def run_main():
    """
    use a local function to make an isolated the QApplication object

        Returns:
            None
    """

    def inner_run():
        app = qw.QApplication(sys.argv)
        window = ProjectPropertiesWidget()
        window.clear_and_display_text("This is some <b>text</b>")
        window.append_text("<p>More text</p>")
        window.show()
        app.exec_()

    inner_run()

if __name__ == "__main__":
    run_main()