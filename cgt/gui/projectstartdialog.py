# -*- coding: utf-8 -*-
"""
Created on Monday 28 Sept 2020

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
# pylint: disable = too-many-public-methods
# pylint: disable = c-extension-no-member
# pylint: disable = too-many-return-statements

import sys
import os
from pathlib import Path

import PyQt5.QtWidgets as qw
import PyQt5.QtCore as qc

from cgt.util.utils import timestamp

from cgt.gui.Ui_projectstartdialog import Ui_ProjectStartDialog

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
    def find_enhanced_video_file(self):
        """
        callback for running a file dialog to find the enhanced_video file

            Returns:
                None
        """
        file_name, _ = qw.QFileDialog.getOpenFileName(
            self,
            self.tr("Project Source File"),
            os.path.expanduser('~'),
            self.tr("AVI (*.avi)"))

        if file_name is not None:
            self._enhancedVideo.setText(file_name)
            file = os.path.basename(self._enhancedVideo.text())
            file = file.rsplit('.', 1)[0]
            file += "_" + timestamp()
            self._projName.setText(file)

    @qc.pyqtSlot()
    def find_raw_video_file(self):
        """
        callback for running a file dialog to find the raw_video file

            Returns:
                None
        """
        file_name, _ = qw.QFileDialog.getOpenFileName(
            self,
            self.tr("Processed Copy of Source"),
            os.path.expanduser('~'),
            self.tr("AVI (*.avi)"))

        if file_name is not None:
            self._rawVideo.setText(file_name)

    @qc.pyqtSlot()
    def make_project(self):
        """
        callback for finished, validates data and calls the start_project
        method of the parent

            Returns:
                None
        """
        text = self._enhancedVideo.text().strip()
        if not text:
            message = self.tr("You must provide a enhanced_video file")
            qw.QMessageBox.warning(self, "Error", message)
            return

        enhanced_video = Path(text)
        if not enhanced_video.exists():
            message = self.tr("Source file \"{}\" does not exist!")
            message = message.format(enhanced_video)
            qw.QMessageBox.critical(self, "Error", message)
            return

        text = self._rawVideo.text().strip()
        if text:
            raw_video = Path(text)
            if not raw_video.exists():
                message = self.tr(f"Source file \"{raw_video}\" does not exist!")
                qw.QMessageBox.critical(self, "Error", message)
                return
            if raw_video == enhanced_video:
                message = self.tr(f"Enhanced video file \"{enhanced_video}\" ")
                message += self.tr("and raw video file \"{raw_video}\" are the same!")
                qw.QMessageBox.critical(self, "Error", message)
                return
        else:
            raw_video = None

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

        notes = self._notesEdit.toPlainText().strip()

        if self.parent() is not None:
            self.parent().start_project(
                enhanced_video,
                raw_video,
                proj_dir,
                proj_name,
                notes,
                self._copyCheckBox.isChecked())

            self.close()
        else:
            message = "Enhanced: {}\nRaw: {}\nPath: {}\nName: {}\nCopy video: {}"
            message = message.format(
                enhanced_video,
                raw_video,
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

    app = qw.QApplication(sys.argv)

    window = ProjectStartDialog()
    window.show()
    app.exec_()

if __name__ == "__main__":
    run()
