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
import os

import PyQt5.QtWidgets as qw
import PyQt5.QtCore as qc
import PyQt5.QtGui as qg
import PyQt5.QtPrintSupport as qp
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
                data_source (CrystalGrowhtTrackerMain)
        """
        super().__init__(parent)
        self.setupUi(self)
        self._scrollArea.setWidget(qe.QWebEngineView())

        ## the holder of the results
        self._data_source = data_source

        ## the url of the report
        self._url = None

    def load_html(self, path):
        """
        display a html report
            Args:
                path (pathlib.Path): path to html
        """
        self._url = qc.QUrl.fromLocalFile(str(path))
        self.load_url()

    @qc.pyqtSlot()
    def load_url(self):
        """
        load and display the current ur
        """
        if self._url is not None:
            self._scrollArea.widget().setUrl(self._url)

    @qc.pyqtSlot()
    def save_pdf(self):
        """
        if there is a report save it
        """
        if self._data_source.get_project() is None:
            qw.QMessageBox.warning(self,
                                   "CGT Error",
                                   "You do not have a project to report!")
            return

        if  self._data_source.has_unsaved_data():
            qw.QMessageBox.warning(self,
                                   "CGT Error",
                                   "Please save the data before printing a report!")
            return

        file_types = "PDF (*.pdf)"
        file_path, _ = qw.QFileDialog.getSaveFileName(self,
                                                     "Enter/select file for save",
                                                     os.path.expanduser('~'),
                                                     file_types)
        if file_path is None or file_path == '':
            return

        self.save_doc_pdf(file_path)

        message = self.tr("Report saved to {}")
        qw.QMessageBox.information(self,
                                   self.tr("Save Report"),
                                   message.format(file_path))

    def save_doc_pdf(self, file_path):
        """
        print the current document as a PDF file
            Args:
                file_path (string): the output file
        """
        self._scrollArea.widget().page().printToPdf(file_path)
