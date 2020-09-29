# -*- coding: utf-8 -*-
"""
Created on Monday 28 Sept 2020

@copyright 2020
@author: j.h.pickering@leeds.ac.uk
"""
import sys
import os

import PyQt5.QtWidgets as qw
import PyQt5.QtGui as qg
import PyQt5.QtCore as qc

#from pathvalidate import sanitize_filename, validate_filename

from Ui_projectstartdialog import Ui_ProjectStartDialog

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
        super(ProjectStartDialog, self).__init__(parent)

        ## the parent object, if any
        self._parent = parent

        ## the name in translation, if any
        self._translated_name = self.tr("ProjectStartDialog")
        
        self.setupUi(self)
        
        self._projDir.setText(os.getcwd())
        
    @qc.pyqtSlot()
    def find_project_dir(self):
            
        dir_name = qw.QFileDialog.getExistingDirectory(
                    self, 
                    self.tr("Select directory"),
                    os.getcwd(),
                    options=qw.QFileDialog.ShowDirsOnly)
                    #tr("Images (*.png *.xpm *.jpg)"));

        if dir_name is not None:
            self._projDir.setText(dir_name)
        
    @qc.pyqtSlot()
    def find_source_file(self):
        file_name, _ = qw.QFileDialog.getOpenFileName(
                    self, 
                    self.tr("Project Source File"),
                    os.getcwd(),
                    self.tr("AVI (*.avi)"))
                    
        if file_name is not None:
            self._sourceVideo.setText(file_name)
            file = os.path.basename(self._sourceVideo.text())
            file = file.rsplit('.',1)[0]
            #file = sanitize_filename(file)
            self._projName.setText(file)
            
        
    @qc.pyqtSlot()
    def find_processed_file(self):
        file_name, _ = qw.QFileDialog.getOpenFileName(
                    self, 
                    self.tr("Processed Copy of Source"),
                    os.getcwd(),
                    self.tr("AVI (*.avi)"))
                    
        if file_name is not None:
            self._processedVideo.setText(file_name)

    @qc.pyqtSlot()
    def make_project(self):
        # TODO check there is a valid source, name/project, and if present processed video is valid
        source = qc.QFile(self._sourceVideo.text())
        
        if not source.exists():
            message = self.tr("Source file {} dosn't exist")
            message = message.format(source.fileName())
            qw.QMessageBox.warning(self, "Error", message)
            return
            
        if self._processedVideo.text().strip() != "":
            processed = qc.QFile(self._processedVideo.text())
            if not processed.exists():
                message = self.tr("Processed file {} dosn't exist")
                message = message.format(processed.fileName())
                qw.QMessageBox.warning(self, "Error", message)
                return
        else:
            processed = None
        
        proj_name = self._projName.text().strip()
        
        if  proj_name == "":
            message = self.tr("You must provide a project name!")
            qw.QMessageBox.warning(self, "Error", message)
            return
            
        proj_dir = self._projDir.text().strip()
        
        if  proj_name == "":
            message = self.tr("You must provide a project directory path!")
            qw.QMessageBox.warning(self, "Error", message)
            return
            
        notes = self._notesEdit.toPlainText().strip()
            
        #try:
        #    validate_filename(proj_name)
        #except OSError as err:
        #    message = self.tr("Project name, {}, not valid: {}")
        #    message = message.format(proj_name, err)
        #    qw.QMessageBox.warning(self, "Error", message)
        #    return
        
        if self.parent() is not None:
            self.parent().new_project(source, processed, proj_name, notes)
        else:
            s = "Source: {}\nProcessed: {}\nPath: {}\nName: {}"
            s = s.format(source.fileName(), processed, proj_dir, proj_name)
            print(s)
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