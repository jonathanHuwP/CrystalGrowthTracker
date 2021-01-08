## -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 15:45:07 2020

This module contains the top level graphical user interface for measuring the
growth rates of crystals observed in videos taken using an X-ray synchrotron source

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
# pylint: disable = too-many-instance-attributes
# pylint: disable = c-extension-no-member

import sys
import os
import array as arr
from shutil import copy2
from queue import Queue

import PyQt5.QtWidgets as qw
import PyQt5.QtGui as qg
import PyQt5.QtCore as qc

from cgt.io.videobuffer import VideoBuffer
from cgt.model.videoanalysisresultsstore import VideoAnalysisResultsStore

from cgt.gui.projectstartdialog import ProjectStartDialog
from cgt.gui.projectpropertieswidget import ProjectPropertiesWidget
from cgt.gui.regionselectionwidget import RegionSelectionWidget
from cgt.gui.crystaldrawingwidget import CrystalDrawingWidget
from cgt.gui.videoparametersdialog import VideoParametersDialog
from cgt.gui.reportviewwidget import ReportViewWidget
from cgt.gui.linevalueswidget import LineValuesWidget

from cgt.io import htmlreport
from cgt.io import writecsvreports
from cgt.io import readcsvreports

import cgt.util.utils as utils
from cgt.util.cgtautosave import CGTAutoSave

from cgt.model.cgtproject import CGTProject

# import UI
from cgt.gui.Ui_crystalgrowthtrackermain import Ui_CrystalGrowthTrackerMain

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
        super().__init__(parent)
        ## the parent object
        self._parent = parent

        ## the name in the current translation
        self._translated_name = self.tr("CrystalGrowthTracker")

        self.setupUi(self)

        ## the name of the project
        self._project_name = None

        ## a pointer for the video file reader
        self._video_reader = None

        ## the project data structure
        self._project = None

        ## queue for the selection widget, holds frame numbers
        self._video_queue = Queue(256)

        ## queue for the drawing widget, holds (fram number, region)
        self._regions_queue = Queue(256)


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
        self._resultsWidget = LineValuesWidget(self._selectTab, self)

        # set up tab
        self.add_tab(self._resultsTab, self._resultsWidget, "Results Overview")


        ## base widget for Report tab
        self._reportTab = qw.QWidget(self)

        ## the report widget
        self._reportWidget = ReportViewWidget(self._selectTab, self)
        text = "<h1 style=\"color:blue;\">No Report!</h1>"
        text += "<p style=\"color:red;\">No report has been saved.</p></body></html>"
        self._reportWidget.set_html(text)

        # set up tab
        self.add_tab(self._reportTab, self._reportWidget, "Current Report")


        # set up the title
        self.set_title()

        ## pointer for an autosave file
        self._autosave = None

    def request_video_frame(self, frame_number):
        """
        add frame number to video Queue

            Args:
                frame_number (int) the frame number to

            Returns:
                None
        """
        self._video_queue.put(frame_number)

    def request_drawing_frame(self, frame_number, region):
        """
        add frame number to drawing Queue

            Args:
                frame_number (int) the frame number to
                region (Region) the region that is requested

            Returns:
                None
        """
        print(f"request_drawing_frame({frame_number})")
        self._regions_queue.put((frame_number, region))

    def video_queue(self):
        """
        getter for the queue of frame requests from the region selection widget

            Returns:
                the regions selection widget frame queue
        """
        return self._video_queue

    def drawing_queue(self):
        """
        getter for the queue of (frame, region) requests from the drawing widget

            Returns:
                the drawing widget's queue
        """
        return self._drawing_queue

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

        self._propertiesWidget.show_top_text()

        self._tabWidget.setCurrentWidget(self._propertiesTab)

    def active_tab(self):
        """
        determin which tab is running

            Returns
                (int) 1, region selection; 2, drawing; 0 else
        """
        if self._tabWidget.currentWidget() == self._selectTab:
            return 1
        elif self._tabWidget.currentWidget() == self._drawingTab:
            return 2

        return 0

    @qc.pyqtSlot()
    def new_project(self):
        """
        callback for starting a new project

            Returns:
                None
        """
        if self.has_unsaved_data():
            mb_reply = qw.QMessageBox.question(
                self,
                self.tr('CrystalGrowthTracker'),
                self.tr('You have a project with unsaved data that will be lost.\nProceed?'),
                qw.QMessageBox.Yes | qw.QMessageBox.No,
                qw.QMessageBox.No)

            if mb_reply == qw.QMessageBox.No:
                return

        dia = ProjectStartDialog(self)
        dia.show()

    @qc.pyqtSlot()
    def load_project(self):
        """
        callback for loading an existing project
            Returns:
                None
        """
        if self.has_unsaved_data():
            mb_reply = qw.QMessageBox.question(
                self,
                self.tr('CrystalGrowthTracker'),
                self.tr('You have a project with unsaved dat that will be lost. Proceed?'),
                qw.QMessageBox.Yes | qw.QMessageBox.No,
                qw.QMessageBox.No)

            if mb_reply == qw.QMessageBox.No:
                return

        dir_name = qw.QFileDialog.getExistingDirectory(
            self,
            self.tr("Select the Project Directory."),
            os.path.expanduser('~'))

        if dir_name == '':
            return

        project = CGTProject()
        try:
            readcsvreports.read_csv_project(dir_name, project)
        except (IOError, OSError, EOFError) as exp:
            message = f"Could not load project: {exp}"
            qw.QMessageBox.warning(self,
                                   "CGT Error Loading Projcet",
                                   message)
            return

        backup, back_file = self.check_for_backup(dir_name, project["proj_name"])

        # check for a recent backup
        if backup is not None:
            message = "A more recent backup exists, do you want to recover?"
            reply = qw.QMessageBox.question(self,
                                            'CrystalGrowthTracker',
                                            message,
                                            qw.QMessageBox.Yes | qw.QMessageBox.No,
                                            qw.QMessageBox.No)
            if reply == qw.QMessageBox.Yes:
                # assign the backup
                self._project = backup
                # set the has changed flag
                self._project.set_changed()
                # ensure autosave points to the correct file
                self._autosave = CGTAutoSave.make_autosave_from_file(back_file)
                self.project_created_or_loaded()
                return

        self._project = project
        self._autosave = CGTAutoSave.make_autosave_from_project(self._project)
        self._project.reset_changed()
        self.project_created_or_loaded()

    def check_for_backup(self, dir_name, proj_name):
        """
        check if directory holds autosave backup

            Args:
                dir_name (string) path to directory
                proj_name (string) the name of the project

            Returns:
                if backup file projcet (CGTProject), else None
        TODO check backup is more recent that project
        """
        if self._autosave is None:
            self._autosave = CGTAutoSave()

        files = self._autosave.list_backups(dir_name)
        if len(files) < 1:
            return None, None

        matches = [tmp[0] for tmp in files if tmp[1] == proj_name]
        if len(matches) < 1:
            return None, None
        elif len(matches) == 1:
            return self._autosave.get_backup_project(matches[0]), matches[0]

        # find most recent save
        most_recent = matches[0]
        r_time = os.path.getmtime(most_recent)
        for match in matches[1:]:
            m_time = os.path.getmtime(most_recent)
            if m_time>r_time:
                most_recent = match
                r_time = m_time

        return self._autosave.get_backup_project(most_recent), most_recent

    def project_created_or_loaded(self):
        """
        carry out action for a newly created or loaded project

            Returns:
                None
        """
        self.reset_tab_wigets()

        # remove old reader
        self._video_reader = None

        # dispaly project
        self.display_properties()
        self.set_title()

        # if project has regions
        if self._project["results"] is not None:
            if self._project["results"].number_of_regions > 0:
                self._selectWidget.reload_combobox()
                self._drawingWidget.new_region()

        self._selectWidget.setEnabled(False)
        self._drawingWidget.setEnabled(False)
        self._resultsWidget.display_data()

        if self._project["latest_report"] is not None:
            if self._project["latest_report"] != "":
                self._reportWidget.read_report(self._project["latest_report"])

    def reset_tab_wigets(self):
        """
        reset the tab widgets to inital conditions

            Returns:
                None
        """
        self._drawingWidget.clear()
        self._selectWidget.clear()
        self._propertiesWidget.clear()
        self._reportWidget.clear()
        self._resultsWidget.clear()

    @qc.pyqtSlot()
    def save_image(self):
        # if no project, or video loaded error
        if self._project is None or self._video_reader is None:
            message = self.tr("To save you must have a project and load a video.")
            qw.QMessageBox.information(self, self.tr("Save Image"), message)
            return

        # find if a tab holding image is in use
        current_tab_widget=self._tabWidget.currentWidget()
        widget = None

        if current_tab_widget == self._selectTab:
            widget = self._selectWidget
        elif current_tab_widget == self._drawingTab:
            widget = self._drawingWidget
        else:
            message = self.tr("You must be using either the Select Regions or the Draw Crystals tabs.")
            qw.QMessageBox.information(self, self.tr("Save Image"), message)
            return

        # grab tab image
        pixmap = widget.get_pixmap()
        if pixmap is None:
            message = self.tr("You do not appear to be displaying an image.")
            qw.QMessageBox.information(self, self.tr("Save Image"), message)
            return

        file_types = "Portable Network Graphics (*.png)"
        file_path, _ = qw.QFileDialog.getSaveFileName(self,
                                                     "Enter/select file for save",
                                                     os.path.expanduser('~'),
                                                     file_types)

        if file_path is None or file_path == '':
            return

        pixmap.save(file_path)

        message = f"Image saved to {file_path}"
        qw.QMessageBox.information(self, self.tr("Save Image"), message)


    @qc.pyqtSlot()
    def save_project(self):
        '''
        Function to write all the csv files needed to define a project.
        Args:
            self    Needs to access the project dictionary.
        Returns:
            None
        '''
        if self._project is None:
            qw.QMessageBox.warning(self,
                                   "CGT Error",
                                   "You do not have a project to save!")
            return

        try:
            writecsvreports.save_csv_project(self._project)
            self._project.reset_changed()
        except OSError as err:
            message = f"Error opening writing file: {err}"
            qw.QMessageBox.warning(self, "CGT File Error", message)
            return

        if self._autosave is not None:
            self._autosave.erase_data()

        message = "Project saved to: {}".format(self._project["proj_full_path"])
        qw.QMessageBox.information(self, "CGT File", message)

    @qc.pyqtSlot()
    def save_report(self):
        """
        generate and save a report of the current state of the project

            Returns:
                None
        """
        if self._project is None:
            qw.QMessageBox.warning(self,
                                   "CGT Error",
                                   "You do not have a project to report!")
            return

        if self.has_unsaved_data():
            qw.QMessageBox.warning(self,
                                   "CGT Error",
                                   "Please save the data before printing a report!")
            return

        if self._project["proj_full_path"] is not None:
            time_stamp = utils.timestamp()
            try:
                self._project["latest_report"] = htmlreport.save_html_report1(self._project, time_stamp)
            except OSError as err:
                message = "Problem creating report directory and file: {}".format(err)
                qw.QMessageBox.warning(self,
                                       "Report Error",
                                       message)

            # read back in to the reports tab
            try:
                self._reportWidget.read_report(self._project["latest_report"])
            except OSError as err:
                message = "Could not open report file for reading: {}".format(err)
                qw.QMessageBox.warning(self,
                                       "Report Error",
                                       message)

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
                copy_files (bool) if true video files are copied to project dir

            Returns:
                None
        """
        # make the full project path
        path = proj_dir.joinpath(proj_name)

        if path.exists():
            message = "Project {} already exists you are not allowd to overwrite.".format(proj_name)
            qw.QMessageBox.critical(self, "Project Exists!", message)
            return

        project = CGTProject()
        project.init_new_project()

        try:
            path.mkdir()
        except (FileNotFoundError, OSError) as err:
            message = "Error making project directory \"{}\"".format(err)
            qw.QMessageBox.critical(self, "Cannot Create Project!", message)
            return

        project["proj_name"] = proj_name
        project["proj_full_path"] = path

        if copy_files:
            try:
                copy2(enhanced_video, path)
                # if copied enhanced_video is project path + file name
                self._project["enhanced_video"] = path.joinpath(enhanced_video.name)

            except (IOError, os.error) as why:
                qw.QMessageBox.warning(
                    self,
                    "Problem copying video file",
                    f"Error message: {why}")

            if raw_video is not None:
                try:
                    copy2(raw_video, path)
                    # if used and copied raw_video is project path + file name
                    self._project["raw_video"] = path.joinpath(raw_video.name)
                except (IOError, os.error) as why:
                    qw.QMessageBox.warning(
                        self,
                        "Problem copying raw video file",
                        f"Error message: {why}")

        else:
            # set sourec and project to their user input values
            project["enhanced_video"] = enhanced_video
            if raw_video is not None:
                project["raw_video"] = raw_video

        if notes is not None and not notes.isspace() and notes:
            notes_file_name = proj_name + "_notes.txt"
            notes_file = path.joinpath(notes_file_name)
            project["notes"] = notes

            try:
                with open(notes_file, 'w') as n_file:
                    n_file.write(notes)
            except IOError as error:
                message = f"Can't open file for notes {error}"
                qw.QMessageBox.critical(self, "Error making writing notes", message)

        project['enhanced_video_path'] = enhanced_video.parent
        project['enhanced_video_no_path'] = enhanced_video.name
        project['enhanced_video_no_extension'] = enhanced_video.stem

        if raw_video is not None:
            project['raw_video_path'] = raw_video.parent
            project['raw_video_no_path'] = raw_video.name
            project['raw_video_no_extension'] = raw_video.stem

        project["results"] = VideoAnalysisResultsStore()

        self._project = project
        self.set_video_scale_parameters()
        self.save_project()
        self._autosave = CGTAutoSave.make_autosave_and_save_from_project(project)
        self.project_created_or_loaded()

    def set_video_scale_parameters(self):
        """
        get the video scaling parameters from the user

            Returns:
                None
        """
        if self._project['frame_rate'] is not None:
            fps = int(self._project['frame_rate'])
        else:
            fps = 8

        if self._project['resolution'] is not None:
            resolution = float(self._project['resolution'])
        else:
            resolution = 0.81

        if self._project['resolution_units'] is not None:
            units = self._project['resolution_units']
        else:
            units = VideoParametersDialog.RESOLUTION_UNITS[1]

        fps, res, units = VideoParametersDialog.get_values_from_user(self,
                                                                     fps,
                                                                     resolution,
                                                                     units)

        self._project['frame_rate'] = fps
        self._project['resolution'] = res
        self._project['resolution_units'] = units

        self.display_properties()

    def get_video_reader(self):
        """
        getter for the video reader object

            Returns:
                (imageio.reader) video reader
        """
        return self._video_reader

    def get_fps_and_resolution(self):
        """
        getter for the frames per second and the resolution of the video

            Returns:
                frames per second (int), resolution (float)
        """
        if self._project is not None:
            return int(self._project["frame_rate"]), float(self._project["resolution"])

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
        self._resultsWidget.display_data()
        self.autosave()

    def append_lines(self, region_index, lines):
        """
        add a list of lines to a region

            Args:
                region_index (int) the array index of the region
                lines [Line] array of lines to be added

            Returns:
                None
        """
        for line in lines:
            self._project["results"].add_line(region_index, line)

        self._drawingWidget.new_region()
        self._resultsWidget.display_data()
        self.autosave()

    @qc.pyqtSlot()
    def autosave(self):
        """
        make digital copy of project, to be called on any change in the data

            Reuturns:
                None
        """
        self._autosave.save_data(self._project)

    def set_title(self):
        """
        sets window title

            Returns:
                None
        """
        name = self._translated_name

        if self._project is not None and self._project["proj_name"] is not None:
            proj_name = self._project["proj_name"]
            name += f": {proj_name}"

        self.setWindowTitle(name)

    def make_pixmap(self, index, frame):
        """
        make a pixmap of a given region in a given frame

            Args:
                index (int) the index of the region
                frame (int) the frame in the video

            Returns:
                QPixmap of the region
        """
        region = self._project["results"].regions[index]

        # TODO replace with new
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
    def load_video(self):
        """
        read in a video and display

            Returns:
                None
        """
        print(f"active tab {self.active_tab()}")
        error_title = self.tr("CGT Video File Error")
        if self._project is None:
            message = self.tr("You must load/create a project before loading video")
            qw.QMessageBox.warning(self,
                                   error_title,
                                   message)
            return

        if self._project["enhanced_video"] is None:
            message = self.tr("The current project contains no video file")
            qw.QMessageBox.warning(self,
                                   error_title,
                                   message)
            return

        message_box = qw.QMessageBox()
        message_box.setText("Loading Video.")
        message_box.setInformativeText("Loading video may take some time.")
        try:
            message_box.show()
            self._video_reader = VideoBuffer(self._project["enhanced_video"],
                                             self,
                                             self._selectWidget,
                                             self._drawingWidget)
            self._video_reader.start()

        except (FileNotFoundError, IOError) as ex:
            message_box.close()
            message = self.tr("Unexpected error reading {}: {} => {}")
            message = message.format(self._project["enhanced_video"],
                                    type(ex),
                                    ex.args)
            qw.QMessageBox.warning(self,
                                   error_title,
                                   message)
            return

        message_box.close()

        self._selectWidget.setEnabled(True)
        self._selectWidget.show_video()
        self._drawingWidget.setEnabled(True)

    qc.pyqtSlot()
    def print_results(self):
        scale = self._project["resolution"]
        fps = self._project["frame_rate"]

        if isinstance(scale, (str)) or isinstance(fps, (str)):
            print("Error scale or fps still string")
            return

        print("Results\n=======")
        for line in self._project["results"].lines:
            if line.number_of_frames > 1:
                print(line)
                differences = line.get_differences()
                for diff in differences:
                    distance = diff[1].average*scale
                    time = diff[0]/fps
                    print(f"\t{distance/time}")

    def has_unsaved_data(self):
        """
        find if window is holding unsaved data

            Returns:
                True if unsaved data is held, False otherwise
        """
        return self._project is not None and self._project.has_been_changed()

    @qc.pyqtSlot()
    def save_results_widget(self):
        """
        callback for triggering save results
        """
        if self._project is None:
            message = self.tr("You must have a project.")
            qw.QMessageBox.warning(self, self.tr("No Project"), message)
            return

        file_types = "Commer Seperated Value (*.csv)"
        file_path, _ = qw.QFileDialog.getSaveFileName(self,
                                                     self.tr("Enter/select file for save"),
                                                     os.path.expanduser('~'),
                                                     file_types)

        if file_path is None or file_path == '':
            return

        self._resultsWidget.save(file_path)

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
        message = self.tr('Do you want to leave?')
        changed = self.tr('You have unsaved data.')

        if self.has_unsaved_data():
            message = changed + "\n" + message

        mb_reply = qw.QMessageBox.question(self,
                                           'CrystalGrowthTracker',
                                           message,
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

            # remove the binary backup if there is no unsaved data
            if not self.has_unsaved_data() and self._autosave is not None:
                self._autosave.clean_up()

        else:
            # dispose of the event in the approved way
            event.ignore()
