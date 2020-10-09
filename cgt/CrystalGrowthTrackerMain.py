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

from imageio import get_reader as imio_get_reader
import array as arr

sys.path.insert(0, '..\\CrystalGrowthTracker')
import getpass

from cgt import utils
from cgt.utils import find_hostname_and_ip
from cgt.cgtutility import RegionEnd
from videoanalysisresultsstore import VideoAnalysisResultsStore

import PyQt5.QtWidgets as qw
import PyQt5.QtGui as qg
import PyQt5.QtCore as qc

from shutil import copy2
from pathlib import Path

from ImageLabel import ImageLabel
from cgt.projectstartdialog import ProjectStartDialog
from cgt.projectpropertieswidget import ProjectPropertiesWidget

from cgt.regionselectionwidget import RegionSelectionWidget
from cgt.crystaldrawingwidget import CrystalDrawingWidget
from cgt.videoparametersdialog import VideoParametersDialog
from cgt.reportviewwidget import ReportViewWidget

# import UI
from cgt.Ui_CrystalGrowthTrackerMain import Ui_CrystalGrowthTrackerMain

from cgt import htmlreport
from cgt import writecsvreports
from cgt import readcsvreports

class CGTProject(dict):
    """
    a store for a the project data and results

    Contents:
        prog: (string) name of program
        description: (string) description of the program
        start_datetime: (string) timestamp of start of project
        host: (string) name of computer
        ip_address: (string) ip address of computer
        operating_system: (string) operating system of computer
        enhanced_video_path: (pathlib.Path) the full path of the image enhanced video
        enhanced_video_no_path: the name of the enhanced video file
        enhanced_video_no_extension: name of the enhanced video file without extension
        raw_video: (pathlib.Path) the full path and name of the original video
        raw_video_no_path: (string) the name of the original video file
        raw_video_no_extension: (string) the name of the original video file without extension
        proj_name: (string) the name of the projcect
        notes: (string) notes input by user
        frame_rate: (int) the frame rate
        resolution: (float) the real world size of a pixel
        resolution_units: (string) the units of size of a pixel
        results: (VideoAnalysisResultsStore) the results
    """
    def __init__(self):
        """
        initalize the class

            Returns:
                None
        """
        super().__init__()
        # program name
        self["prog"] = None

        # program description
        self["description"] = None

        # a time stamp for the start of the project
        self["start_datetime"] = None

        # name of computer on which we are running
        self['host'] = None

        # ip address of computer on which the project started
        self['ip_address'] = None

        # operating system on we which the project started
        self['operating_system'] = None

        # the video on which the program will operate
        self["enhanced_video"] = None

        # the original video before image enhancment, may be null
        self["raw_video"] = None

        # the name of the project
        self["proj_name"] = None

        # the full path to the project
        self["proj_full_path"] = None

        # the users notes
        self["notes"] = None

        # the video frame rate
        self["frame_rate"] = None

        # the results
        self["results"] = None

        # the path to the enhanced_video
        self["enhanced_video_path"] = None

        # the plain file name of the enhanced_video
        self['enhanced_video_no_path'] = None

        # the file name of the enhanced_video without postfix
        self['enhanced_video_no_extension'] = None

        # the path to the raw_video video file
        self['raw_video_path'] = None

        # the plain file name of the raw_video video file
        self['raw_video_no_path'] = None

        # the file extension of the raw_video video file
        self['raw_video_no_extension'] = None

        # the user who stated the project
        self['start_user'] = None

        # the video frame rate
        self['frame_rate'] = None

        # the real world distance represented by the edge length of a pixel
        self['resolution'] = None

        # the units of the resolution
        self['resolution_units'] = None

    def init_new_project(self):
        """
        fill in the data for a new project
        """
        prog = 'CGT'
        description = 'Semi-automatically tracks the growth of crystals from X-ray videos.'

        self["prog"] = prog
        self["description"] = description
        self["start_datetime"] = utils.timestamp()
        self['host'], self['ip_address'], self['operating_system'] = utils.find_hostname_and_ip()
        self["start_user"] = getpass.getuser()

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

        ## a pointer for the video file reader
        self._video_reader = None

        ## the project data structure
        self._project = None


        ## base widget for properties tab
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
        
        
        ## base widget for results tab
        self._resultsTab = qw.QWidget(self)

        ## the results widget
        self._resultsWidget = None #ResultsDisplayWidget(self._selectTab, self)

        # set up tab
        self.add_tab(self._resultsTab, self._resultsWidget, "Results Overview")
        
  
        ## base widget for Report tab
        self._reportTab = qw.QWidget(self)

        ## the report widget
        self._reportWidget = ReportViewWidget(self._selectTab, self)
        self._reportWidget.set_html("<!DOCTYPE html><html><body><h1 style=\"color:blue;\">Hello World!</h1><p style=\"color:red;\">There is no report.</p></body></html>")

        # set up tab
        self.add_tab(self._reportTab, self._reportWidget, "Current Report")  
        

        # set up the title
        self.set_title()

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
        if target_widget is not None:
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
        
        if self._project is not None:
            mb_reply = qw.QMessageBox.question(self,
                                               self.tr('CrystalGrowthTracker'),
                                               self.tr('You have a project that will be overwriten. Proceed?'),
                                               qw.QMessageBox.Yes | qw.QMessageBox.No,
                                               qw.QMessageBox.No)

            if mb_reply == qw.QMessageBox.No:
                return
            

        dir_name = qw.QFileDialog().getExistingDirectory(
            self,
            self.tr("Select the Project Directory."),
            "")
            
        # TODO use Path to check result dir is valid
        if dir_name != '':
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

    def start_project(self,
                      enhanced_video,
                      raw_video,
                      proj_dir,
                      proj_name,
                      notes,
                      copy_files):
        """
        function for starting a new project

            Args
                enhanced_video (pathlib.Path) the video on which the program will run
                raw_video (pathlib.Path) secondary raw_video video
                proj_dir  (pathlib.Path) parent directory of project directory
                proj_name (string) the name of project, will be directory name
                notes (string) project notes
                copy_files (bool) if true the enhanced_video and raw_video files are copied to project dir

            Returns:
                None
        """
        # make the full project path
        path = proj_dir.joinpath(proj_name)

        if path.exists():
            message = "Project {} already exists you are not allowd to overwrite.".format(proj_name)
            qw.QMessageBox.critical(self, "Project Exists!", message)
            return

        self._project = CGTProject()
        self._project.init_new_project()

        try:
            path.mkdir()
        except (FileNotFoundError, OSError) as err:
            message = "Error making project directory \"{}\"".format(err)
            qw.QMessageBox.critical(self, "Cannot Create Project!", message)
            return

        self._project["proj_name"] = proj_name
        self._project["proj_full_path"] = path

        if copy_files:
            try:
                copy2(enhanced_video, path)
                # if copied enhanced_video is project path + file name
                self._project["enhanced_video"] = path.joinpath(enhanced_video.name)

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

            if raw_video is not None:
                try:
                    copy2(raw_video, path)
                    # if used and copied raw_video is project path + file name
                    self._project["raw_video"] = path.joinpath(raw_video.name)
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
            # set sourec and project to their user input values
            self._project["enhanced_video"] = enhanced_video
            if raw_video is not None:
                self._project["raw_video"] = raw_video

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

        self._project['enhanced_video_path'] = enhanced_video.parent
        self._project['enhanced_video_no_path'] = enhanced_video.name
        self._project['enhanced_video_no_extension'] = enhanced_video.stem

        if raw_video is not None:
            self._project['raw_video_path'] = raw_video.parent
            self._project['raw_video_no_path'] = raw_video.name
            self._project['raw_video_no_extension'] = raw_video.stem
        
        self.set_video_scale_parameters()

        print(self._project)
        self.read_video()
        
    def set_video_scale_parameters(self):
        """
        get the video scaling parameters from the user
        
            Returns:
                None
        """
        if self._project['frame_rate'] is not None:
            fps = self._project['frame_rate']
        else:
            fps = 8
            
        if self._project['resolution'] is not None:
            resolution = self._project['resolution']
        else:
            resolution = 0.81
            
        if self._project['resolution_units'] is not None:
            units = self._project['resolution_units']
        else:
            units = VideoParametersDialog.RESOLUTION_UNITS[1]
        
        fps, resolution, units = VideoParametersDialog.get_values_from_user(self, fps, resolution, units)
        
        self._project['frame_rate'] = fps
        self._project['resolution'] = resolution
        self._project['resolution_units'] = units
        
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

    def get_video_reader(self):
        return self._video_reader

    def get_fps_and_resolution(self):
        """
        getter for the frames per second and the resolution of the video

            Returns:
                frames per second (int), resolution (float)
        """
        if self._project is not None:
            return self._project["frame_rate"], self._project["resolution"]

        return None, None
        
    def get_result(self):
        """
        getter for the current results object

            Return:
                the current results object
        """
        if self._project:
            return self._project["results"]

        return None
        
    def append_region(self, region):
        """
        add a region to the results and notify the crystal drawing widget
        
            Args:
                region (Region) the region

            Returns:
                None
        """
        self._project["results"].add_region(region)
        self._drawingWidget.new_region()

    def set_title(self):
        """
        sets window title

            Returns:
                None
        """
        name = "No project"

        if self._project is not None:
            name = self._project["proj_name"]

        title = self._translated_name + " - " + name
        self.setWindowTitle(title)

    def make_pixmap(self, index, frame):
        region = self._project["results"].regions[index]

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
        dir_name = self._project["proj_full_path"]

        print("dir_name: ", dir_name)

        if dir_name is not None:

            print("Printing html report.")
            prog = 'CGT'
            description = 'Semi-automatically tracks the growth of crystals from X-ray videos.'

            info = {'prog':prog,
                    'description':description}
            info['in_file_no_path'] = "filename_in.avi"
            info['in_file_no_extension'] = os.path.splitext("filename_in")[0]
            info['frame_rate'] = 20
            info['resolution'] = 10
            info['resolution_units'] = "nm"
            start = utils.timestamp()
            info['start_datetime'] = start
            print(start)
            info['host'], info['ip_address'], info['operating_system'] = utils.find_hostname_and_ip()
            print(find_hostname_and_ip())
            htmlreport.save_html_report(dir_name, info)
            writecsvreports.save_csv_reports(dir_name, info)

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

    def read_video(self):
        """
        read in a video and display

            Returns:
                None
        """
        try:
            self._video_reader = imio_get_reader(self._project["enhanced_video"], 'ffmpeg')
        except (FileNotFoundError, IOError) as ex:
            message = "Unexpected error reading {}: {} => {}".format(file_name, type(ex), ex.args)
            qw.QMessageBox.warning(self,
                                   "Video Read Error",
                                   message)
            return

        self._project["results"] = VideoAnalysisResultsStore()
        self._selectWidget.show_video()

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
    app = qw.QApplication(sys.argv)
    translators = select_translator()
    for translator in translators:
        qc.QCoreApplication.installTranslator(translator)

    window = CrystalGrowthTrackerMain()

    window.show()

    app.exec_()

if __name__ == "__main__":
    run_growth_tracker()
