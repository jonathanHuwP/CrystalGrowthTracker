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
# set up linting conditions
# pylint: disable = too-many-public-methods
# pylint: disable = c-extension-no-member
# pylint: disable = too-many-instance-attributes

import sys
import os

import array as arr
import pickle as pk
import numpy as np
from PIL import Image
import matplotlib.image as mpimg
from skimage import color

# TODO check if needed
#import datetime

from imageio import get_reader as imio_get_reader
import array as arr

# TODO check if needed
#from astropy.table import info

sys.path.insert(0, '..\\CrystalGrowthTracker')
from pathlib import Path

from cgt import utils
from cgt.utils import find_hostname_and_ip
from cgt.cgtutility import RegionEnd
from videoanalysisresultsstore import VideoAnalysisResultsStore, DateUser, VideoSource

import PyQt5.QtWidgets as qw
import PyQt5.QtGui as qg
import PyQt5.QtCore as qc

from shutil import copy2
#from pathlib import Path

from cgt import ImageLabel
from cgt.projectstartdialog import ProjectStartDialog
from cgt.projectpropertieswidget import ProjectPropertiesWidget

# set up linting conditions
# pylint: disable = too-many-public-methods
# pylint: disable = c-extension-no-member

from cgt.regionselectionwidget import RegionSelectionWidget
from cgt.crystaldrawingwidget import CrystalDrawingWidget

# import UI
from cgt.Ui_CrystalGrowthTrackerMain import Ui_CrystalGrowthTrackerMain

#from cgt import htmlreport
from cgt.readwrite import htmlreport
#from cgt import writecsvreports
from cgt.readwrite import writecsvreports
from cgt.readwrite import readcsvreports
#from cgt import readcsvreports
from cgt import utils


sys.path.insert(0, '..\\CrystalGrowthTracker')



class CGTProject(dict):
    """
    a store for a the project meta data
    """
    def __init__(self):
        """
        initalize the class

            Returns:
                None
        """
        super().__init__()

        prog = 'CGT'
        description = 'Semi-automatically tracks the growth of crystals from X-ray videos.'

        self["prog"] = prog
        self["description"] = description
        start = utils.timestamp()
        self["start"] = start
        self['host'], self['ip_address'], self['operating_system'] = utils.find_hostname_and_ip()

        self["source"] = None
        self["processed"] = None
        self["proj_dir"] = None
        self["proj_name"] = None
        self["notes"] = None

        self["latest_report"] = None


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

        ## storage for the open video source
        self._video_reader = None

        ## storage for the result
        self._result = None

        ## the project data structure
        self._project = CGTProject()

        ## base widget for region selection tab
        self._propertiesTab = qw.QWidget(self)

        ## the region selection widget
        self._propertiesWidget = ProjectPropertiesWidget(self._propertiesTab, self)

        # set up tab
        self.add_tab(self._propertiesTab, self._propertiesWidget, "Project Properties")

        ## base widget for region selection tab
        self._selectTab = qw.QWidget(self)

        ## the region selection widget
        self._selectWidget = RegionSelectionWidget(self._selectTab, self)

        # set up tab
        self.add_tab(self._selectTab, self._selectWidget, "Select Regions")

        ## base widget of crystal drawing tab
        self._drawingTab = qw.QWidget(self)

        ## the crystal drawing widget
        self._drawingWidget = CrystalDrawingWidget(self._drawingTab, self)

        # set up tab
        self.add_tab(self._drawingTab, self._drawingWidget, "Trace Crystals")

        # set up the title
        self.set_title()

        #self.read_video("..\\doc\\video\\file_example_AVI_640_800kB.avi")



    def add_tab(self, tab_widget, target_widget, title):
        """
        add a new tab

            Args:
                tab_widget (QWidget) the widget forming the tab
                target_widget (QWidget subclass) the widget to be used
                title (string) the tabbox title

            Returns:
                None
        """
        layout = qw.QVBoxLayout()
        layout.addWidget(target_widget)
        tab_widget.setLayout(layout)

        self._tabWidget.addTab(tab_widget, title)



    def display_properties(self):
        """
        display the properties tab with the current properties

            Returns:
                None
        """
        self._propertiesWidget.clear_and_display_text("<h1>Properties</h1>")
        for key in self._project:
            text = "<p><b>{}:</b> {}"
            text = text.format(key, self._project[key])
            self._propertiesWidget.append_text(text)

        self._tabWidget.setCurrentWidget(self._propertiesTab)


    def get_result(self):
        """
        getter for the current results object
            Return:
                the current results object
        """
        return self._result

    def get_regions(self):
        """
        getter for the list of regions
            Returns:
                regions list
        """
        return self._result.regions

    @qc.pyqtSlot()
    def new_project(self):
        """
        callback for starting a new project

            Returns:
                None
        """
        print("CrystalGrowthTrackerMain.new_project()")
        dia = ProjectStartDialog(self)
        dia.show()

    @qc.pyqtSlot()
    def load_project(self):
        """
        callback for loading an existing project
            Returns:
                None
        """
        print("CrystalGrowthTrackerMain.load_project()")

        dir_name = qw.QFileDialog().getExistingDirectory(
            self,
            self.tr("Select the Project Directory."),
            "")

        if dir_name is not None:
            print("Loading Project.")
            data, error_code = readcsvreports.read_csv_project(dir_name, self._project)
            if error_code == 0:
                print("The project was loaded.")
                self._project = data
            else:
                print("The project was not loaded.")

            self.display_properties()

    @qc.pyqtSlot()
    def save_project(self):
        '''
        Function to write all the csv files needed to define a project.
        Args:
            self    Needs to access the project dictionary.
        Returns:
            None
        '''
        print("save project")
        writecsvreports.save_csv_project(self._project)

    @qc.pyqtSlot()
    def start_project(
            self,
            source,
            processed,
            proj_dir,
            proj_name,
            notes,
            copy_files):
        """
        function for starting a new project

            Args
                source (pathlib.Path) the main source video
                processed (pathlib.Path) secondary processed video
                proj_dir  (pathlib.Path) parent directory of project directory
                proj_name (string) the name of project, will be directory name
                notes (string) project notes
                copy_files (bool) if true the source and processed files are copied to project dir

            Returns:
                None
        """
        # make the full project path
        path = proj_dir.joinpath(proj_name)

        if path.exists():
            message = "Project {} already exists you are not allowd to overwrite.".format(proj_name)
            qw.QMessageBox.critical(self, "Project Exists!", message)
            return

        try:
            path.mkdir()
        except (FileNotFoundError, OSError) as err:
            message = "Error making project directory \"{}\"".format(err)
            qw.QMessageBox.critical(self, "Cannot Create Project!", message)
            return

        self._project["proj_name"] = proj_name
        self._project["proj_dir"] = proj_dir
        self._project["proj_full_path"] = path

        if copy_files:
            try:
                copy2(source, path)
                # if copied source is project path + file name
                self._project["source"] = path.joinpath(source.name)

            except (IOError, os.error) as why:
                qw.QMessageBox.warning(
                    self,
                    "Problem copying File",
                    "Error message: {}".format(why))
            except Error as err:
                qw.QMessageBox.warning(
                    self,
                    "Problem copying File",
                    "Error message: {}".format(err.args[0]))

            if processed is not None:
                try:
                    copy2(processed, path)
                    # if used and copied processed is project path + file name
                    self._project["processed"] = path.joinpath(processed.name)
                except (IOError, os.error) as why:
                    qw.QMessageBox.warning(
                        self,
                        "Problem copying File",
                        "Error message: {}".format(why))
                except Error as err:
                    qw.QMessageBox.warning(
                        self,
                        "Problem copying File",
                        "Error message: {}".format(err.args[0]))
        else:
            # set source and project to their user input values
            self._project["source"] = source
            if processed is not None:
                self._project["processed"] = processed

        if notes is not None and not notes.isspace() and notes:
            notes_file_name = proj_name + "_notes.txt"
            notes_file = path.joinpath(notes_file_name)
            self._project["notes"] = notes

            try:
                with open(notes_file, 'w') as n_file:
                    n_file.write(notes)
            except IOError as error:
                message = "Can't open file for the notes"
                qw.QMessageBox.critical(self, "Error making directory!", message)
                
        # TODO simplify using pathlib
        source_path, source_no_path = os.path.split(source)
        self._project['source_path'] = source_path
        self._project['source_no_path'] = source_no_path
        self._project['source_no_extension'] = os.path.splitext(source_no_path)[0]

        if processed is not None:
            # TODO simplify using pathlib
            processed_path, processed_no_path = os.path.split(processed)
            self._project['processed_path'] = processed_path
            self._project['processed_no_path'] = processed_no_path
            self._project['processed_no_extension'] = os.path.splitext(processed_no_path)[0]
        else:
            print("Processed in None.")
            self._project['processed_path'] = None
            self._project['processed_no_path'] = None
            self._project['processed_no_extension'] = None

        # TODO these must be user input
        self._project['frame_rate'] = 8
        self._project['resolution'] = 10
        self._project['resolution_units'] = "nm"

        print(self._project)
        self.display_properties()

    @qc.pyqtSlot()
    def tab_changed(self):
        """
        callback for the tab widget to use when the tab is changed, put all
        state change required between the two tabs in here. the currentIndex
        function in _tabWidger will act as a state variable.

            Returns:
                None
        """
        print("tab changed")

    def get_regions_iter(self):
        """
        get an iterator for the list of regions

            Returns:
                iterator of regions
        """
        return iter(self._result.regions)

    def get_selected_region(self, index):
        """
        getter for the region selected via the combo box,

            Args:
                index (int) the list index of the region

            Returns:
                region or None if no regions entered
        """
        if len(self._result.regions) < 1 or index < 0:
            return None

        return self._result.regions[index]

    def append_region(self, region):
        self._result.add_region(region)
        self._drawingWidget.new_region()

    def get_video_data(self):
        return self._result.video

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

        if self._project["proj_name"] is not None:
            name = self._project["proj_name"]

        title = self._translated_name + " - " + name
        self.setWindowTitle(title)

    def make_pixmap(self, index, frame):
        region = self._result.regions[index]

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
    def save_results(self):
        """
        Save the current set of results

            Returns:
                None
        """
        #dir_name = qw.QFileDialog().getExistingDirectory(
        #    self,
        #    self.tr("Select Directory for the Report"),
        #    "")

        dir_name = self._project["proj_full_path"]

        print("dir_name: ", dir_name)

        if dir_name is not None:

            print("Printing html report.")
            #prog = 'CGT'
            #description = 'Semi-automatically tracks the growth of crystals from X-ray videos.'

            #info = {'prog':prog,
            #        'description':description}
            #info['in_file_no_path'] = "filename_in.avi"
            #info['in_file_no_extension'] = os.path.splitext("filename_in")[0]
            #info['frame_rate'] = 20
            #info['resolution'] = 10
            #info['resolution_units'] = "nm"
            time_stamp = utils.timestamp()
            #info['start'] = start
            print(time_stamp)
            #info['host'], info['ip_address'], info['operating_system'] = utils.find_hostname_and_ip()
            #print(find_hostname_and_ip())
            self._project["latest_report"] = htmlreport.save_html_report1(self._project, time_stamp)
            #htmlreport.save_html_report1(self._project, time_stamp)
            #writecsvreports.save_csv_reports(dir_name, info)

    @qc.pyqtSlot()
    def reload_results(self):
        """
        reload a set of results

            Returns:
                None
        """
        print("reload results")
        dir_name = qw.QFileDialog().getExistingDirectory(
            self,
            self.tr("Select Directory for Reload"),
            "")

        if dir_name is not None:
            readcsvreports.read_csv_reports(dir_name)
            pass


            readcsvreports.read_csv_reports(dir_name)

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
        elif file_type == tracker_files:
            self.read_ga_image(file_name)
        elif file_type == subimage_files:
            self.read_numpy_image(file_name)
        else:
            message = self.tr("Unknown file type: {}").format(file_type)
            #self._logger.error("bad file type: %s, should be %s", file_type, image_files)
            qw.QMessageBox.warning(self,
                                   self._translated_name,
                                   message)

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
                                   "Video Read Error",
                                   message)
            return

        # TODO allow for user override of frame rate
        # set up the video data struct
        meta_data = self._video_reader.get_meta_data()
        video_data = VideoSource(
            file_name,
            meta_data["fps"],
            self._video_reader.count_frames(),
            meta_data["size"][0],
            meta_data["size"][1])

        self._result = VideoAnalysisResultsStore(video_data)
        self._result.append_history()

        self._selectWidget.show_video()


    @qc.pyqtSlot()
    def save_subimage(self):
        """
        callback for saving the current image

            Returns:
                None
        """
        print("Save image")

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

# TODO move to qt utility
def ndarray_to_qpixmap(data):

    tmp = arr.array('B', data.reshape(data.size))

    im_format = qg.QImage.Format_Grayscale8

    image = qg.QImage(
        tmp,
        data.shape[1],
        data.shape[0],
        data.shape[1],
        im_format)

    return qg.QPixmap.fromImage(image)

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
