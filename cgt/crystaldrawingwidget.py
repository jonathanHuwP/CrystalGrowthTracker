# -*- coding: utf-8 -*-
"""
Created on Fri Jul 10 21:36:13 2020

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
    the widget in which the user will draw the crystals
    """

    def __init__(self, parent=None, owner=None):
        """
        set up the dialog

            Args:
                parent (QObject) the parent object
                owner (CrystalGrowthTrackerMain) the object holding the project data

            Returns:
                None
        """
        super(CrystalDrawingWidget, self).__init__(parent)

        ## the widget holding the project data
        self._owner = owner

        ## the name in translation, if any
        self._translated_name = self.tr("CrystalDrawingWidget")
        self.setupUi(self)

        ## an ArtifctStore for testing
        self._store = LineSetsAndFramesStore()

        ## the drawing label
        self._drawing = DrawingLabel(self._scrollArea)
        self._scrollArea.setWidget(self._drawing)

        # connect up the change frame signals
        self._videoControl.frame_changed.connect(self.frame_changed)

    def region_chosen(self):
        if not self.isHidden():
            index = self._regionBox.currentIndex()
            region = self._owner.get_selected_region(index)
        
            print("CDW.region_chosen: index: {} region: {}".format(index, region))
        
            self._videoControl.set_range(region.start_frame, region.end_frame)
            self.display_region()

    def display_region(self):
        index = self._regionBox.currentIndex()
        frame = self._videoControl.get_current_frame()
        print("display region (index: {}, frame {})".format(index, frame))

        pixmap = self._owner.make_pixmap(index, frame)

        self._drawing.set_backgroud_pixmap(pixmap)
        self._drawing.redisplay()

    def new_region(self):
        self._regionBox.blockSignals(True)
        
        self._regionBox.clear()
        for i, _ in enumerate(self._owner.get_regions_iter()):
            self._regionBox.addItem(str(i))
            
        self._regionBox.blockSignals(False)
        
        print("added region")

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
        print("clear_crystal")

    @qc.pyqtSlot()
    def add_crystal(self):
        print("add_crystal")

    @qc.pyqtSlot()
    def start_new_crystal(self):
        print("start_new_crystal")

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

        if self._owner is not None:
            if self._owner.get_video_reader() is not None:
                if len(self._owner.get_regions()) > 0:
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
