# -*- coding: utf-8 -*-
"""
Created on Fri Jul 10 21:36:13 2020

This class provides a test harness for DrawingLabel allowing all user operations.

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
# set up linting conditions
# pylint: disable = too-many-public-methods
# pylint: disable = c-extension-no-member

import sys

import PyQt5.QtWidgets as qw
import PyQt5.QtGui as qg
import PyQt5.QtCore as qc

from linesetsandframesstore import LineSetsAndFramesStore

from DrawingLabel import DrawingLabel

from Ui_crystaldrawingwidget import Ui_CrystalDrawingWidget

class CrystalDrawingWidget(qw.QWidget, Ui_CrystalDrawingWidget):
    """
    a QDialog that demonstrates the DrawingLabel class
    """

    def __init__(self, parent=None):
        """
        set up the dialog

            Args:
                parent (QObject) the parent object

            Returns:
                None
        """
        super(CrystalDrawingWidget, self).__init__(parent)

        ## the parent object, if any
        self._parent = parent

        ## the name in translation, if any
        self._translated_name = self.tr("CrystalDrawingWidget")
        self.setupUi(self)

        ## the DrawingLabel being tested
        self._drawing = None

        ## an ArtifctStore for testing
        self._store = LineSetsAndFramesStore()
        
    def set_pixmap(self, pixmap):
        self._drawing = DrawingLabel(self._scrollArea)
        self._drawing.set_backgroud_pixmap(pixmap)
        self._scrollArea.setWidget(self._drawing)
        
    @qc.pyqtSlot()
    def state_toggle(self):
        """
        callback for the changing the Drawing/Adjusting state

            Returns:
                None
        """
        if self._drawButton.isChecked():
            self._drawing.set_drawing()
        else:
            self._drawing.set_adjusting()

    @qc.pyqtSlot()
    def labels_toggled(self):
        """
        callback for the toggeling the display of line labels

            Returns:
                None
        """
        if self._labelsBox.isChecked():
            self._drawing.show_labels(True)
        else:
            self._drawing.show_labels(False)

    @qc.pyqtSlot()
    def create_copy_toggled(self):
        """
        callback for the changing the Crating/Copying state

            Returns
                None
        """
        if self._createButton.isChecked():
            self._drawing.set_creating()
            self.set_draw_adjust_enabled(True)
        else:
            self._drawing.set_copying()
            self._adjustButton.setChecked(True)
            self.set_draw_adjust_enabled(False)

    def set_draw_adjust_enabled(self, state):
        """
        enable/disable the Draw/Adjust buttons

            Args:
                state (boolean) the new state

            Returns:
                None
        """
        self._drawButton.setEnabled(state)
        self._adjustButton.setEnabled(state)

    @qc.pyqtSlot()
    def calculate(self):
        """
        calculate the differences and display then in the table.

            Returns:
                None
        """
        tmp = self._drawing.size
        if tmp[0] <= 0 or tmp[1] <= 0:
            message = "You only have {} lines and {} new lines. Both must have one or more."
            print(message.format(tmp[0], tmp[1]))
            return

        if self._drawing.lines_base is None:
            print("lines none")

        if self._drawing.lines_new is None:
            print("new lines none")

        self._store[0] = self._drawing.lines_base
        self._store[1] = self._drawing.lines_new

        diffs = self._store.differences(0, 1)

        self._tableWidget.setColumnCount(2)
        self._tableWidget.setRowCount(len(diffs))

        self._tableWidget.setHorizontalHeaderLabels(["Line", "Displacement (pixels)"])

        i = 0
        for diff in diffs:
            self._tableWidget.setItem(i, 0, qw.QTableWidgetItem(str(diff.lines_label)))
            self._tableWidget.setItem(i, 1, qw.QTableWidgetItem(str(diff.average)))
            i += 1

    @qc.pyqtSlot()
    def save_image(self):
        """
        save image callback

            Returns:
                None
        """

        options = qw.QFileDialog.Options()
        options |= qw.QFileDialog.DontUseNativeDialog
        file_name, file_type = qw.QFileDialog().getSaveFileName(
            self,
            self.tr("Select File"),
            "",
            self.tr("Portable Network graphics (*.png);;JPG Files (*.jpg)"),
            options=options)

        if file_name is None:
            return

        file = qc.QFile(file_name)
        self._drawing.save(file)

    @qc.pyqtSlot()
    def zoom_changed(self):
        """
        callback for changes to the zoom slider

            Returns:
                None
        """
        self._drawing.set_zoom(self._zoomSpinBox.value())

def run():
    """
    use a local function to make an isolated the QApplication object

        Returns:
            None
    """
    def inner_run():
        app = qw.QApplication(sys.argv)

        window = CrystalDrawingWidget()
        window.show()
        app.exec_()

    inner_run()

if __name__ == "__main__":
    run()
