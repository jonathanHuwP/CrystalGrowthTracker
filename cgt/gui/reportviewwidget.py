## -*- coding: utf-8 -*-
"""
Created on Fri Oct 09 2020

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

import pathlib 

import PyQt5.QtWidgets as qw
import PyQt5.QtGui as qg
import PyQt5.QtCore as qc

# import UI
from Ui_reportviewwidget import Ui_ReportViewWidget

class ReportViewWidget(qw.QWidget, Ui_ReportViewWidget):
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

        self._text = qw.QTextBrowser(self)
        self._layout = qw.QVBoxLayout(self._text)
        self._scrollArea.setWidget(self._text)
        
    def clear(self):
        """
        clear any text and set up default
        
            Returns:
                None
        """
        self._text.clear()

    def set_html(self, text=None):
        self._text.setText(text)
        
    def read_report(self, path, name="CGT_report.html"):
        """
        read a report file and display text
            
            Args:
                path (string) the directory path to the report file
                name (string) the name of the report file
                
            Returns:
                None
        """
        input_path = pathlib.Path(path).joinpath(name)
        with open(input_path, 'r') as infile:
            self.set_html(infile.read())
        
#########################

def run_main():
    """
    run the demo

        Returns:
            None
    """
    str_html = """
        <!DOCTYPE html>
        <html>
        <body>

        <h1 style="color:blue;">Hello World!</h1>
        <p style="color:red;">Lorem ipsum dolor sit amet.</p>

        </body>
        </html>
        """
    app = qw.QApplication(sys.argv)
    window = ReportViewWidget()
    window.show()
    window.set_html(str_html)
    app.exec_()

if __name__ == "__main__":
    run_main()


