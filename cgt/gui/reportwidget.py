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
# set up linting conditions
# pylint: disable = c-extension-no-member

import PyQt5.QtWidgets as qw
import PyQt5.QtCore as qc
import PyQt5.QtGui as qg
import PyQt5.QtPrintSupport as qp

# import UI
from cgt.gui.Ui_reportwidget import Ui_ReportWidget

class ReportWidget(qw.QWidget, Ui_ReportWidget):
    """
    a widget for viewing the current HTML report
    """

    def __init__(self, parent):
        """
        the object initalization function

            Args:
                parent (QObject): the parent QObject for this window
                data_source (QObject): the object holding the data
        """
        super().__init__(parent)

        self.setupUi(self)

        ## the document to display
        self._document = qg.QTextDocument()

    def load_html(self, path):
        """
        display a html report
            Args:
                path (pathlib.Path): path to html
        """
        self._document.clear()

        with path.open('r') as in_file:
            self._document.setHtml(in_file.read())

        self._textBrowser.setHtml(self._document.toHtml())

    def has_content(self):
        """
        test if the document has any contents
            Returns:
                True if the document has content, else False
        """
        return not self._document.isEmpty()

    def save_doc_pdf(self, file_path):
        """
        print the current document as a PDF file
            Args:
                file_path (string): the output file
        """
        printer = qp.QPrinter(qp.QPrinter.PrinterResolution)
        printer.setOutputFormat(qp.QPrinter.PdfFormat)
        printer.setPaperSize(qp.QPrinter.A4)
        printer.setOutputFileName(file_path)

        self._document.print(printer)

    def save_doc_html(self, file_path):
        """
        print the current document as a PDF file
            Args:
                file_path (string): the output file
        """
        utf = 'utf-8'

        # construct a python byte array out of sting "utf-8" using "utf-8" as encoding
        encoding = qc.QByteArray(bytearray(utf, utf))

        with open(file_path, 'w') as out_file:
            out_file.write(self._document.toHtml(encoding))
