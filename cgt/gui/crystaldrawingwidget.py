# -*- coding: utf-8 -*-
"""
Created on Fri Jul 10 21:36:13 2020

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
# pylint: disable = import-error

import sys

import PyQt5.QtWidgets as qw
import PyQt5.QtCore as qc

from cgt.model.linesetsandframesstore import LineSetsAndFramesStore

from cgt.gui.DrawingLabel import DrawingLabel
from cgt.model.crystal import Crystal

from cgt.gui.Ui_crystaldrawingwidget import Ui_CrystalDrawingWidget

class CrystalDrawingWidget(qw.QWidget, Ui_CrystalDrawingWidget):
    """
    the widget in which the user will draw the crystals
    """

    def __init__(self, parent=None, data_source=None):
        """
        set up the dialog

            Args:
                parent (QObject) the parent object
                data_source (CrystalGrowthTrackerMain) the object holding the project data

            Returns:
                None
        """
        super(CrystalDrawingWidget, self).__init__(parent)

        ## the widget holding the project data
        self._data_source = data_source

        ## the name in translation, if any
        self._translated_name = self.tr("CrystalDrawingWidget")
        self.setupUi(self)


        ## an ArtifctStore for testing
        self._store = LineSetsAndFramesStore()

        ## store the the region being viewed
        self._current_region = None

        ## the drawing label
        self._drawing = DrawingLabel(self._scrollArea)
        self._scrollArea.setWidget(self._drawing)

        # connect up the change frame signals
        self._videoControl.frame_changed.connect(self.frame_changed)

        # set data source for tree widget
        self._treeWidget.set_data_source(data_source)
        
    def clear(self):
        """
        clear the contents
        
            Return:
                None
        """
        self._store = LineSetsAndFramesStore()
        self._current_region = None
        self._treeWidget.clear()
        self._drawing.clear()

    def set_data_source(self, data_source):
        """
        setter for the object holding the data to be displayed

            Args:
                data_source (CrystalGrowthTrackerMain) object holding data

            Returns:
                None
        """
        self._data_source = data_source

    def display_region(self):
        """
        the display function

            Returns:
                None
        """
        if self._current_region is None:
            return

        frame = self._videoControl.get_current_frame()

        pixmap = self._data_source.make_pixmap(self._current_region, frame)

        self._drawing.set_backgroud_pixmap(pixmap)
        self._drawing.redisplay()

    def new_region(self):
        """
        called by data_source to indicate a new region has been added, index added to spin box

            Returns:
                None
        """
        self._treeWidget.blockSignals(True)
        self._treeWidget.fill_tree()
        self._treeWidget.blockSignals(False)

    @qc.pyqtSlot()
    def state_toggle(self):
        """
        callback for the changing the Drawing/Adjusting state

            Returns:
                None
        """
        if self._createButton.isChecked():
            self._drawing.set_drawing()
        elif self._adjustButton.isChecked():
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
    def clear_crystal(self):
        """
        clear the current crystal

            Returns:
                None
        """
        print("clear_crystal {}".format(id(self)))

    @qc.pyqtSlot()
    def add_crystal(self):
        """
        add the curren crystal to the results

            Returns:
                None
        """
        print("add_crystal {}".format(id(self)))
        self.save_crystal()

    @qc.pyqtSlot()
    def start_new_crystal(self):
        """
        start a new crystal

            Returns:
                None
        """
        print("start_new_crystal {}".format(id(self)))

    @qc.pyqtSlot()
    def frame_changed(self):
        """
        callback for a change of frame

            Returns:
                None
        """
        self.display_region()

    @qc.pyqtSlot()
    def zoom_changed(self):
        """
        callback for changes to the zoom slider

            Returns:
                None
        """
        self._drawing.set_zoom(self._zoomSpinBox.value())

    @qc.pyqtSlot()
    def showEvent(self, event):
        """
        override qwidget and ensure a safe display

            Returns:
                None
        """
        qw.QWidget.showEvent(self, event)

        if self._data_source is not None:
            if self._data_source.get_video_reader() is not None:
                if len(self._data_source.get_result().regions) > 0:
                    self._videoControl.enable(True)
                    self.display_region()

    @qc.pyqtSlot()
    def hideEvent(self, event):
        """
        override qwidget and ensure a safe hide

            Returns:
                None
        """
        qw.QWidget.hideEvent(self, event)
        self._videoControl.enable(False)

    def select_region(self, r_index):
        """
        a region has been selected

            Args:
                r_index (int) the array index of the region

            Returns:
                None
        """
        print("CrystalDrawingWidget Region {}".format(r_index))

        if r_index == self._current_region:
            return

        # TODO put test and save in seperate function
        # has label got unsaved lines?
        if len(self._drawing.lines_base) > 0:
            message = "You have unsaved data do you wish to save?"
            reply = qw.QMessageBox.question(self, "Data loss?", message)

            if reply == qw.QMessageBox.Yes:
                self.save_crystal()

        self._drawing.clear_all()

        self._current_region = r_index
        region = self._data_source.get_result().regions[r_index]

        self._videoControl.set_range(region.start_frame, region.end_frame)
        self.display_region()

    def save_crystal(self):
        """
        get a crystal from drawing and add it to the results in main

            Returns:
                None
        """
        note = qw.QInputDialog.getText(self, "Crystal Note", "If needed add note.")
        
        if note[1]:
            crystal = Crystal(notes=note[0])
            
        lines = []
        for line in self._drawing.lines_base:
            print("\tadding: {}".format(line))
            lines.append(line)

        crystal.add_faces(lines, self._videoControl.get_current_frame())

        results = self._data_source.get_result()
        results.add_crystal(crystal, self._current_region)
        self._drawing.clear_all()
        self._treeWidget.fill_tree()

    def select_crystal(self, r_index, c_index):
        """
        a crystal has been selected

            Args:
                r_index (int) the array index of the region
                c_indes (int) the array index of the crystal

            Returns:
                None
        """
        print("CrystalDrawingWidget Region {}, Crystal {}".format(r_index, c_index))

    def select_frame(self, r_index, c_index, f_index):
        """
        a frame number has been selected

            Args:
                r_index (int) the array index of the region
                c_indes (int) the array index of the crystal
                f_indes (int) the array index of the frame number


            Returns:
                None
        """
        print("CrystalDrawingWidget.select_frame Region {}, Crystal {}, Frame {}".format(r_index, c_index, f_index))
        if self._current_region != r_index:
            self.select_region(r_index)
            print("changed region")
        else:
            # TODO add test and save function
            self._drawing.clear_all()
            print("clear all")

        results = self._data_source.get_result()
        crystals = results.get_crystals(r_index)
        crystal = crystals[c_index]
        lines = crystal.faces_in_frame(f_index)
        self._videoControl.set_frame(f_index)
        self._drawing.set_lines_base(lines)

    def select_line(self, r_index, c_index, f_index, l_index):
        """
        a line has been selected

            Args:
                r_index (int) the array index of the region
                c_indes (int) the array index of the crystal
                f_indes (int) the array index of the frame number
                l_index (int) the array index of the line

            Returns:
                None
        """
        print("CrystalDrawingWidget Region {}, Crystal {}, Frame {}, Line {}".format(r_index, c_index, f_index, l_index))


def run():
    """
    use a local function to make an isolated the QApplication object

        Returns:
            None
    """
    app = qw.QApplication(sys.argv)

    window = CrystalDrawingWidget()
    window.show()
    app.exec_()
        
if __name__ == "__main__":
    run()
