## -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 15:45:07 2020

This module contains the top level graphical user interface for measuring the
growth rates of crystals observed in videos taken using an X-ray synchrotron source

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
sys.path.insert(0, '..\\CrystalGrowthTracker')
import os
import datetime
from imageio import get_reader as imio_get_reader
import array as arr
from cgt import utils
from cgt.utils import find_hostname_and_ip
from cgt.cgtutility import RegionEnd, VideoSource

import PyQt5.QtWidgets as qw
import PyQt5.QtGui as qg
import PyQt5.QtCore as qc

# set up linting conditions
# pylint: disable = too-many-public-methods
# pylint: disable = c-extension-no-member

from cgt.regionselectionwidget import RegionSelectionWidget
from cgt.crystaldrawingwidget import CrystalDrawingWidget

# import UI
from cgt.Ui_CrystalGrowthTrackerMain import Ui_CrystalGrowthTrackerMain

class CrystalGrowthTrackerMain(qw.QMainWindow, Ui_CrystalGrowthTrackerMain):
    """
    The implementation of the GUI, all the functions and
    data-structures required to implement the intended behaviour
    """

    def __init__(self, parent=None):
        """
        the object initalization function

            Args:
                parent (QObject): the parent QObject for this window

            Returns:
                None
        """
        super(CrystalGrowthTrackerMain, self).__init__(parent)
        ## the parent object
        self._parent = parent

        ## the name in the current translation
        self._translated_name = self.tr("CrystalGrowthTracker")

        self.setupUi(self)

        ## the name of the project
        self._project_name = None

        ## the videos data
        self._video_data = None

        ## storage for the regions
        self._regions = []

        self.set_title()

        ## base widget for region selection tab
        self._selectTab = qw.QWidget(self)
        
        ## the region selection widget
        self._selectWidget = RegionSelectionWidget(self._selectTab, self)
        
        # set up tab
        layout = qw.QVBoxLayout()
        layout.addWidget(self._selectWidget)
        self._selectTab.setLayout(layout)
        self._tabWidget.addTab(self._selectTab, "Select Regions")

        ## base widget of crystal drawing tab
        self._drawingTab = qw.QWidget(self)
        
        ## the crystal drawing widget
        self._drawingWidget = CrystalDrawingWidget(self._drawingTab, self)
        
        # set up tab
        layout = qw.QVBoxLayout()
        layout.addWidget(self._drawingWidget)
        self._drawingTab.setLayout(layout)
        self._tabWidget.addTab(self._drawingTab, "Trace Crystals")
        
        self.read_video("C:\\Users\\jhp11\\Work\\CrystalGrowthTracker\\doc\\video\\file_example_AVI_640_800kB.avi")

    def get_regions(self):
        return self._regions

    def get_regions_iter(self):
        """
        get an iterator for the list of regions

            Returns:
                iterator of regions
        """
        return iter(self._regions)

    def get_selected_region(self, index):
        """
        getter for the region selected via the combo box,

            Args:
                index (int) the list index of the region

            Returns:
                region or None if no regions entered
        """
        if len(self._regions) < 1 or index < 0:
            return None

        return self._regions[index]

    def append_region(self, region):
        print("CGT.append_region: {}".format(region))
        self._regions.append(region)
        self._drawingWidget.new_region()

    def get_video_data(self):
        return self._video_data

    def get_video_reader(self):
        return self._video_reader

    def set_title(self):
        """
        assignes the source and sets window title

            Args:
                source (string): the path (or file name) of the current main image

            Returns:
                None
        """
        name = "No project"

        if self._project_name is not None:
            name = self._project_name

        title = self._translated_name + " - " + name
        self.setWindowTitle(title)

    def make_pixmap(self, index, frame):
        region = self._regions[index]
        
        raw = self._video_reader.get_data(frame)
        tmp = raw[region.top:region.bottom, region.left:region.right]
        img = arr.array('B', tmp.reshape(tmp.size))
        
        im_format = qg.QImage.Format_RGB888
        image = qg.QImage(
            img,
            region.width,
            region.height,
            3*region.width,
            im_format)

        return qg.QPixmap.fromImage(image)


    @qc.pyqtSlot()
    def select_region(self):
        index = self._regionsComboBox.currentIndex()
        pixmap = self.make_pixmap(index)
        self._drawingWidget.set_pixmap(pixmap)

    @qc.pyqtSlot()
    def tab_changed(self):
        """
        callback for the tab widget to use when the tab is changed, put all
        state change required between the two tabs in here. the currentIndex
        function in _tabWidger will act as a state variable.

            Returns:
                None
        """

        pass 

    @qc.pyqtSlot()
    def load_video(self):
        """
        seperate video loding callback for use in development

        TODO remove as function provided in new project
        """

        options = qw.QFileDialog.Options()
        options |= qw.QFileDialog.DontUseNativeDialog
        file_name, _ = qw.QFileDialog.getOpenFileName(
            self,
            self.tr("Select File"),
            "",
            " Audio Video Interleave (*.avi)",
            options=options)

        if file_name:
            self.read_video(file_name)

    def read_video(self, file_name):
        """
        read in a video and display

            Args:
                file_name (string) the file name of the video

            Returns:
                None
        """
        try:
            self._video_reader = imio_get_reader(file_name, 'ffmpeg')
        except (FileNotFoundError, IOError) as ex:
            message = "Unexpected error reading {}: {} => {}".format(file_name, type(ex), ex.args)
            qw.QMessageBox.warning(self,
                                   "VideoDemo",
                                   message)
            return

        # TODO allow for user override of frame rate

        # set up the video data struct
        meta_data = self._video_reader.get_meta_data()
        self._video_data = VideoSource(
            file_name,
            meta_data["fps"],
            self._video_reader.count_frames(),
            meta_data["size"][0],
            meta_data["size"][1])

        self._selectWidget.show_video()

    @qc.pyqtSlot()
    def save_project(self):
        """
        Save the current project

            Returns:
                None
        """
        print("Save Project")

    @qc.pyqtSlot()
    def load_project(self):
        """
        load an existing project

            Returns:
                None
        """
        print("load project")

    @qc.pyqtSlot()
    def save_subimage(self):
        """
        callback for saving the current image

            Returns:
                None
        """
        print("Save image")

    @qc.pyqtSlot()
    def new_project(self):
        """
        Start a new project

            Returns:
                None
        """
        print("New Project")

    @qc.pyqtSlot()
    def project_parameters(self):
        """
        display the paramertes of the current project

            Returns:
                None
        """
        print("Project Parameters")

    @qc.pyqtSlot()
    def closeEvent(self, event):
        """
        Overrides QWidget.closeEvent
        This will be called whenever a MyApp object recieves a QCloseEvent.
        All actions required befor closing widget are here.

            Args:
                event (QEvent) the Qt event object

            Returns:
                None
        """
        mb_reply = qw.QMessageBox.question(self,
                                           self.tr('CrystalGrowthTracker'),
                                           self.tr('Do you want to leave?'),
                                           qw.QMessageBox.Yes | qw.QMessageBox.No,
                                           qw.QMessageBox.No)

        if mb_reply == qw.QMessageBox.Yes:
            #clean-up and exit signalling

            # the event must be accepted
            event.accept()

            # to get rid tell the event-loop to schedul for deleteion
            # do not destroy as a pointer may survive in event-loop
            # which will trigger errors if it recieves a queued signal
            self.deleteLater()

        else:
            # dispose of the event in the approved way
            event.ignore()

######################################

def get_translators(lang):
    """
    find the available translations files for a languages

        Args:
        lang (string) the name of the language

        Returns:
            a list consisting of [<translator>, <system translator>]
    """
    qt_translator = qc.QTranslator()
    system_trans = qc.QTranslator()

    if lang == "German":
        if not qt_translator.load("./translation/cgt_german.qm"):
            sys.stderr.write("failed to load file cgt_german.qm")
        if not system_trans.load("qtbase_de.qm",
                                 qc.QLibraryInfo.location(qc.QLibraryInfo.TranslationsPath)):
            sys.stderr.write("failed to load file qtbase_de.qm")

    return [qt_translator, system_trans]

def select_translator():
    """
    give the user the option to choose the language other than default English

        Returns:
            if English None, else the list of translators
    """
    languages = ["English", "German"]

    lang = qw.QInputDialog.getItem(
        None, "Select Language", "Language", languages)

    if not lang[1]:
        return None

    return get_translators(lang[0])

def run_growth_tracker():
    """
    use a local function to make an isolated the QApplication object

        Returns:
            None
    """

    def inner_run():
        app = qw.QApplication(sys.argv)

        translators = select_translator()
        for translator in translators:
            qc.QCoreApplication.installTranslator(translator)

        window = CrystalGrowthTrackerMain()
        window.show()

        app.exec_()

    inner_run()

if __name__ == "__main__":
    run_growth_tracker()
