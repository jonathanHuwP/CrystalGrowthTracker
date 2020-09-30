# -*- coding: utf-8 -*-
"""
Created on Monday 28 Sept 2020

@copyright 2020
@author: j.h.pickering@leeds.ac.uk
"""

# set up linting conditions
# pylint: disable = too-many-public-methods
# pylint: disable = c-extension-no-member
# pylint: disable = too-many-return-statements

import sys
import os
from pathlib import Path
from pathvalidate import sanitize_filename, validate_filename, ValidationError
import PyQt5.QtWidgets as qw
import PyQt5.QtCore as qc

from cgt.Ui_projectstartdialog import Ui_ProjectStartDialog

class ProjectStartDialog(qw.QDialog, Ui_ProjectStartDialog):
    """
    a qDialog the allows the user to start a new project
    """

    def __init__(self, parent=None):
        """
        set up the dialog

            Args:
                parent (QObject) the parent object

            Returns:
                None
        """
        super().__init__(parent)

        ## the parent object, if any
        self._parent = parent

        ## the name in translation, if any
        self._translated_name = self.tr("ProjectStartDialog")

        self.setupUi(self)

        self._projDir.setText(os.path.expanduser('~'))

    @qc.pyqtSlot()
    def find_project_dir(self):
        """
        callback for running a file dialog to find the directory
        in which the project directory will reside

            Returns:
                None
        """
        dir_name = qw.QFileDialog.getExistingDirectory(
            self,
            self.tr("Select directory"),
            os.path.expanduser('~'),
            options=qw.QFileDialog.ShowDirsOnly)

        if dir_name is not None:
            self._projDir.setText(dir_name)

    @qc.pyqtSlot()
    def find_source_file(self):
        """
        callback for running a file dialog to find the source file

            Returns:
                None
        """
        file_name, _ = qw.QFileDialog.getOpenFileName(
            self,
            self.tr("Project Source File"),
            os.path.expanduser('~'),
            self.tr("AVI (*.avi)"))

        if file_name is not None:
            self._sourceVideo.setText(file_name)
            file = os.path.basename(self._sourceVideo.text())
            file = file.rsplit('.', 1)[0]
            file = sanitize_filename(file)
            self._projName.setText(file)

    @qc.pyqtSlot()
    def find_processed_file(self):
        """
        callback for running a file dialog to find the processed file

            Returns:
                None
        """
        file_name, _ = qw.QFileDialog.getOpenFileName(
            self,
            self.tr("Processed Copy of Source"),
            os.path.expanduser('~'),
            self.tr("AVI (*.avi)"))

        if file_name is not None:
            self._processedVideo.setText(file_name)

    @qc.pyqtSlot()
    def make_project(self):
        """
        callback for finished, validates data and calls the new_project
        method of the parent

            Returns:
                None
        """
        text = self._sourceVideo.text().strip()
        if not text:
            message = self.tr("You must provide a source file")
            qw.QMessageBox.warning(self, "Error", message)
            return

        source = Path(text)
        if not source.exists():
            message = self.tr("Source file \"{}\" does not exist!")
            message = message.format(source)
            qw.QMessageBox.critical(self, "Error", message)
            return

        text = self._processedVideo.text().strip()
        if text:
            processed = Path(text)
            if not processed.exists():
                message = self.tr("Processed file {} does not exist!")
                message = message.format(processed)
                qw.QMessageBox.critical(self, "Error", message)
                return

            if processed.resolve() == source.resolve():
                message = self.tr("The source and processed files are the same!")
                qw.QMessageBox.critical(self, "Error", message)
                return
        else:
            processed = None

        proj_name = self._projName.text().strip()

        if not proj_name:
            message = self.tr("You must provide a project name!")
            qw.QMessageBox.warning(self, "Error", message)
            return

        text = self._projDir.text().strip()
        if not text:
            message = self.tr("You must provide a project directory path!")
            qw.QMessageBox.warning(self, "Error", message)
            return

        proj_dir = Path(text)
        if not proj_dir.exists():
            message = self.tr("Project directory location {} does not exist!")
            message = message.format(proj_dir)
            qw.QMessageBox.warning(self, "Error", message)
            return

        try:
            validate_filename(proj_name)
        except ValidationError   as err:
            message = self.tr("Project name, {}, not valid: {}")
            message = message.format(proj_name, err)
            qw.QMessageBox.warning(self, "Error", message)
            return

        notes = self._notesEdit.toPlainText().strip()

        if self.parent() is not None:
            self.parent().start_project(
                source,
                processed,
                proj_dir,
                proj_name,
                notes,
                self._copyCheckBox.isChecked())

            self.close()
        else:
            message = "Source: {}\nProcessed: {}\nPath: {}\nName: {}\nCopy video: {}"
            message = message.format(
                source,
                processed,
                proj_dir,
                proj_name,
                self._copyCheckBox.isChecked())
            print(message)
            print(notes)

#######################################

def run():
    """
    use a local function to make an isolated the QApplication object

        Returns:
            None
    """
    def inner_run():
        app = qw.QApplication(sys.argv)

        window = ProjectStartDialog()
        window.show()
        app.exec_()

    inner_run()

if __name__ == "__main__":
    run()
