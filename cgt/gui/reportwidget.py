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
import enum
import json

import PyQt5.QtWidgets as qw
import PyQt5.QtCore as qc
import PyQt5.QtGui as qg
import PyQt5.QtWebEngineWidgets as qe

from cgt.util.utils import (make_report_file_names,
                            hash_results)

# import UI
from cgt.gui.Ui_reportwidget import Ui_ReportWidget

## status of report
class ReportStatus(enum.Enum):
    ## no directory, no html file, no results hash file
    NO_VALID_REPORT = 0

    ## Report exists but is out of date
    OUT_OF_DATE_REPORT = 1

    ## upto date report exists
    UPTO_DATE_REPORT = 2


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

    def setEnabled(self, enabled):
        """
        enable/disable widget
        """
        status = self.uptodate_report_exists()
        print(status.name)
        if enabled:
            # TODO
            # Rpt status, user in, actions
            # No report, don't make => super().setEnabled(False)
            # No report, make => make_report() display()
            # Out of date, don't make => display
            # Out of date, make => make_report() display()
            # upto date, _ => display()

            if status == ReportStatus.NO_VALID_REPORT:
                make = self.question(self.tr("No valid report can be found. Make one?"))
                if not make:
                    super().setEnabled(False)
                    return
                self.make_report()
            elif status == ReportStatus.OUT_OF_DATE_REPORT:
                make = self.question(self.tr("Report is out of date. Make new?"))
                if make:
                    self.make_report()

            self.load_url()
            super().setEnabled(True)
        else:
            super().setEnabled(False)

    def uptodate_report_exists(self):
        """
        test if there exists a current report
            Retruns:
                True if report exists and is current, else False
        """
        project = self._data_source.get_project()
        report_dir, html_outfile, hash_file = make_report_file_names(project["proj_full_path"])

        if not report_dir.exists() or not html_outfile.exists() or not hash_file.exists():
            return ReportStatus.NO_VALID_REPORT

        data = None
        with hash_file.open('r') as fin:
            data = json.load(fin)

        if data is not None:
            if "results_hash" in data:
                if data["results_hash"] == hash_results(project["results"]):
                    return ReportStatus.UPTO_DATE_REPORT

                return ReportStatus.OUT_OF_DATE_REPORT

        return ReportStatus.NO_VALID_REPORT

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

    def question(self, message):
        """
        ask user a question
            Args:
                message (string): the question
            Returns:
                True/False
        """
        ret = qw.QMessageBox.information(None, 'What', message,
                                         qw.QMessageBox.Yes | qw.QMessageBox.No)

        return (ret == qw.QMessageBox.Yes)

    def make_report(self):
        """
        make a html report
        """
        report_file = self._data_source.make_report()

        self.load_html(report_file)
