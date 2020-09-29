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
import os
import datetime
sys.path.insert(0, '..\\CrystalGrowthTracker')

from cgt import utils
from cgt.utils import find_hostname_and_ip

import array as arr
import pickle as pk
import numpy as np
from PIL import Image
import matplotlib.image as mpimg
from skimage import color

import PyQt5.QtWidgets as qw
import PyQt5.QtGui as qg
import PyQt5.QtCore as qc

from pathvalidate import validate_filename, ValidationError
from shutil import copy2

import lazylogger
from ImageLabel import ImageLabel
from cgt.projectstartdialog import ProjectStartDialog

#from PolyLineExtract import PolyLineExtract, IAParameters
#from ImageEnhancer import ImageEnhancer

# set up linting conditions
# pylint: disable = too-many-public-methods
# pylint: disable = c-extension-no-member

# import UI
from cgt.Ui_CrystalGrowthTrackerMain import Ui_CrystalGrowthTrackerMain

from cgt import htmlreport
from cgt import writecsvreports
#from cgt import reports

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
        super(CrystalGrowthTrackerMain, self).__init__()
        ## the parent object
        self._parent = parent

        ## the name in the current translation
        self._translated_name = self.tr("CrystalGrowthTracker")

        self.setupUi(self)

        ## the label for displaying the current main image
        self._source_label1 = None

        ## @todo is this really needed (check/remove)
        self._source_label2 = None

        ## the reader for the video file
        self._video_reader = None

        ## the QLabel for displaying the current subimage
        self._subimage_label = qw.QLabel(self)
        self._subimage_label.setAlignment(qc.Qt.AlignTop | qc.Qt.AlignLeft)
        self._subimage_label.setSizePolicy(
            qw.QSizePolicy.Ignored, qw.QSizePolicy.Fixed)

        source_width = int(round(self.size().width()*0.6))
        sub_width = int(round(source_width))

        sizes = list()
        sizes.append(source_width)
        sizes.append(200)
        sizes.append(sub_width)
        sizes.append(200)

        self._splitter.setSizes(sizes)

        self._subScrollArea.setWidget(self._subimage_label)

        ## the image as numpy.array
        self._raw_image = None

        ## the path to the image source
        self._image_source = None

        ## the current zoom  @todo do we need this as is should always be the same as the spinBox
        self._zoom = 1.0

        ## the project data structure
        self._project = {}

        ## the current logger
        self._logger = lazylogger.logging.getLogger(self._translated_name)
        self._logger.setLevel(lazylogger.logging.WARNING)

    def set_title(self, source):
        """
        assignes the source and sets window title

            Args:
                source (string): the path (or file name) of the current main image

            Returns:
                None
        """
        self._image_source = source
        title = self._translated_name + " - " + source
        self.setWindowTitle(title)

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
        #TODO implement function
        print("CrystalGrowthTrackerMain.load_project()")

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
                source (QFile) the main source video
                processed (QFile) secondary processed video
                proj_dir  (QDir) parent directory of project directory
                proj_name (string) the name of project, will be directory name
                notes (string) project notes
                copy_files (bool) if true the source and processed files are copied to project dir

            Returns:
                None
        """
        message = "Source: {}\nProcessed: {}\nPath: {}\nName: {}\nCopy video: {}"
        message = message.format(
                source.fileName(),
                processed,
                proj_dir,
                proj_name,
                copy_files)
        print(message)
        print("NOTES {}".format(notes))

        if proj_dir.exists(proj_name):
            message = "Project {} already exists you are not allowd to overwrite.".format(proj_name)
            qw.QMessageBox.critical(self, "Project Exists!", message)
            return

        if not proj_dir.mkdir(proj_name):
            message = "Can't make directory {} in {}".format(proj_name, proj_dir.absolutePath())
            qw.QMessageBox.critical(self, "Error making directory!", message)
            return

        # path of newly created dir
        path =  proj_dir.absoluteFilePath(proj_name)

        if copy_files:
            try:
                copy2(source.fileName(), path)
            except (IOError, os.error) as why:
                qw.QMessageBox.warning(self, "Problem copying File", "Error message: {}".format(why))
            except Error as err:
                qw.QMessageBox.warning(self, "Problem copying File", "Error message: {}".format(err.args[0]))

            if processed is not None:
                try:
                    copy2(processed.fileName(), path)
                except (IOError, os.error) as why:
                    qw.QMessageBox.warning(self, "Problem copying File", "Error message: {}".format(why))
                except Error as err:
                    qw.QMessageBox.warning(self, "Problem copying File", "Error message: {}".format(err.args[0]))

        if notes is not None and not notes.isspace() and len(notes) > 0:
            notes_dir = qc.QDir(path)
            notes_file = proj_name + "_notes.txt"
            try:
                with open(notes_dir.absoluteFilePath(notes_file), 'w') as n_file:
                    n_file.write(notes)
            except IOError as error:
                message = "Can't open file for the notes"
                qw.QMessageBox.critical(self, "Error making directory!", message)

    @qc.pyqtSlot()
    def tab_changed(self):
        """
        callback for the tab widget to use when the tab is changed, put all
        state change required between the two tabs in here. the currentIndex
        function in _tabWidger will act as a state variable.

            Returns:
                None
        """

        self._logger.info(
            "tab changed to %s", self._tabWidget.currentIndex())

    @qc.pyqtSlot()
    def save_results(self):
        """
        Save the current set of results

            Returns:
                None
        """
        dir_name = qw.QFileDialog().getExistingDirectory(
            self,
            self.tr("Select Directory for the Report"),
            "")

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
            start = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            info['start'] = start
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
            pass

    @qc.pyqtSlot()
    def save_current_subimage(self):
        """
        callback for saving the current image

            Returns:
                None
        """
        if self._source_label1 is None or self._source_label1.number_rectangles < 1:
            qw.QMessageBox.information(
                self,
                self.tr('Save'),
                self.tr("You have not made any subimages yet!"))
            return

        options = qw.QFileDialog.Options()
        options |= qw.QFileDialog.DontUseNativeDialog
        file_name, file_type = qw.QFileDialog().getSaveFileName(
            self,
            self.tr("Select File"),
            "",
            self.tr("CrystalGrowthTracker Files (*.pki);;JPG Files (*.jpg)"),
            options=options)

        if file_name:
            if file_type == "CrystalGrowthTracker Files (*.pki)":
                self.save_image_pickel(file_name)
            elif file_type == "JPG Files (*.jpg)":
                self.save_image_jpg(file_name)

    def save_image_pickel(self, file_name):
        """
        Save image a pickeled np.array

            Args:
                file_name (string) the file into which the image is to be saved

        Returns:
            None
        """
        if not file_name.endswith('.pki'):
            file_name = file_name + '.pki'

        img = self.get_current_subimage()

        with open(file_name, 'wb') as out_f:
            pk.dump(img, out_f)

        qw.QMessageBox.information(
            self,
            self.tr('Save Pickle'),
            self.tr("Subimage written to: {}").format(file_name))

    def save_image_jpg(self, file_name):
        """
        save image in JPG format

            Args:
                image (numpy.array) the image to be saved.

                file_name (string) the file to which the image is to be aved.

            Returns:
                None
        """
        if not file_name.endswith('.jpg'):
            file_name = file_name + '.jpg'

        image = Image.fromarray(self.get_current_subimage())
        image.save(file_name)

        qw.QMessageBox.information(
            self,
            self.tr('Save JPG'),
            self.tr("Subimage written to: {}").format(file_name))

    @qc.pyqtSlot()
    def load_image(self):
        """
        Get file name from user and, if good

            Returns:
                None
        """

        # file types
        video_files = self.tr("Video Files (*.avi)")
        tracker_files = self.tr("CrystalGrowthTracker Files (*.ga)")
        subimage_files = self.tr("CrystalGrowthTracker Subimage Files(*.pki)")
        all_files = self.tr("All Files (*)")

        files_all = [video_files, tracker_files, subimage_files, all_files]
        files = ";;".join(files_all)

        options = qw.QFileDialog.Options()
        options |= qw.QFileDialog.DontUseNativeDialog
        file_name, file_type = qw.QFileDialog.getOpenFileName(
            self,
            self.tr("Select File"),
            "",
            files,
            options=options)

        if not file_name:
            return

        if file_type == video_files:
            self.read_video(file_name)
        elif file_type == tracker_files:
            self.read_ga_image(file_name)
        elif file_type == subimage_files:
            self.read_numpy_image(file_name)
        else:
            message = self.tr("Unknown file type: {}").format(file_type)
            self._logger.error("bad file type: %s, should be %s", file_type, image_files)
            qw.QMessageBox.warning(self,
                                   self._translated_name,
                                   message)

    def read_video(self, file_name):
        """
        read in a video file

            Args:
                file_name the file name and path

            Returns
                None
        """
        from imageio import get_reader as imio_get_reader
        print("read_video({})".format(file_name))

        try:
            self._video_reader = imio_get_reader(file_name, 'ffmpeg')
        except Exception as ex:
            message = "Unexpected error: {}, {}".format(type(ex), ex.args)
            qw.QMessageBox.warning(self,
                                   self._translated_name,
                                   message)
            return

        # analyse the frame
        count = 0
        for frame in self._video_reader.iter_data():
            count += 1

        self._frameSlider.setMaximum(count-1)

        self.display()

    def display(self):
        """
        display one frame of the video

            Returns:
                None
        """
        # convert 0.0 to 1.0 float to 0 to 255 unsigned int
        def to_gray(value):
            return np.uint8(np.round(value*255))

        # get the fram as numpy.ndarray
        frame = self._frameSlider.value()
        img = color.rgb2gray(self._video_reader.get_data(frame))
        print(img.shape)
        img = to_gray(img)

        self._raw_image = img

        pixmap = ndarray_to_qpixmap(img)

        if self._source_label1 is None:
            self._source_label1 = ImageLabel(self)
            self._source_label1.setAlignment(qc.Qt.AlignTop | qc.Qt.AlignLeft)
            self._source_label1.setSizePolicy(
                qw.QSizePolicy.Ignored, qw.QSizePolicy.Fixed)
            self._source_label1.new_selection.connect(self.new_subimage)
            self._sourceScrollArea.setWidget(self._source_label1)

        self._source_label1.setPixmap(pixmap)
        self._source_label1.setScaledContents(True)
        self._source_label1.setSizePolicy(
            qw.QSizePolicy.Fixed, qw.QSizePolicy.Fixed)
        self._source_label1.setMargin(0)

    @qc.pyqtSlot()
    def frame_changed(self):
        """
        callback for the frame slider

            Returns:
                None
        """
        self.display()

    def read_numpy_image(self, file_name):
        """
        read a pickeled numpy image array

            Args:
                file_name (string) the file name

            Returns:
                None
        """

        with open(file_name, 'rb') as in_f:
            self._raw_image = pk.load(in_f)

        self.display_image()
        self.set_title(file_name)

    def read_ga_image(self, file_name):
        """
        read a numpy array

            Args:
                file_name (string) the file name

            Returns:
                None
        """

        with open(file_name, 'rb') as in_f:
            tmp = pk.load(in_f)

        self._raw_image = tmp["image"]
        self.display_image()
        self.set_title(file_name)

    def read_image(self, file_name):
        """
        Load an image file (jpg or png), convert to numpy grayscal in process

            Args:
                file_name (string) the file name

            Returns:
                None
        """
        # convert 0.0 to 1.0 float to 0 to 255 unsigned int
        def to_gray(value):
            return np.uint8(np.round(value*255))

        img = color.rgb2gray(mpimg.imread(file_name))
        self._raw_image = to_gray(img)

        self.display_image()
        self.set_title(file_name)

    def get_zoom(self):
        """
        getter for the zoom

            Returns:
                the current zoom
        """
        return self._zoom

    @property
    def has_image(self):
        """
        returns true if the object has an raw image set

            Returns:
                True if the _raw_image is set else False
        """
        return isinstance(self._raw_image, np.ndarray)

    def display_image(self):
        """
        diseplay the raw image

            Returns:
                None
        """
        if not self.has_image:
            return

        self._source_label1 = ImageLabel(self)
        self._source_label1.setAlignment(qc.Qt.AlignTop | qc.Qt.AlignLeft)
        self._source_label1.setSizePolicy(
            qw.QSizePolicy.Ignored, qw.QSizePolicy.Fixed)
        self._source_label1.new_selection.connect(self.new_subimage)
        self._sourceScrollArea.setWidget(self._source_label1)

        self.redisplay_image()

    def redisplay_image(self):
        """
        display the raw image in the existing label

            Returns:
                None
        """

        # cash the zoom
        self._zoom = self._sourceZoomSpinBox.value()

        height, width = self._raw_image.shape

        display_image = arr.array(
            'B',
            self._raw_image.reshape(self._raw_image.size))

        # use constructor with bytes per line
        image = qg.QImage(
            display_image,
            width,
            height,
            width,
            qg.QImage.Format_Grayscale8)

        pixmap = qg.QPixmap.fromImage(image)
        size = pixmap.size()
        size *= self._zoom

        pixmap = pixmap.scaled(
            size,
            qc.Qt.KeepAspectRatio,
            qc.Qt.SmoothTransformation)

        self._source_label1.setPixmap(pixmap)

        self._source_label1.setScaledContents(True)
        self._source_label1.setSizePolicy(
            qw.QSizePolicy.Fixed, qw.QSizePolicy.Fixed)
        self._source_label1.setMargin(0)

    @qc.pyqtSlot()
    def new_subimage(self):
        """
        update the combobox of subimages

            Returns:
                None
        """
        self._subimageComboBox.addItem(str(self._source_label1.number_rectangles))

        self._subimageComboBox.setCurrentIndex(
            self._source_label1.number_rectangles-1)

    @qc.pyqtSlot()
    def source_zoom(self):
        """
        callback for change of zoom on source image

            Returns:
                None
        """
        if self.has_image:
            self.redisplay_image()

    @qc.pyqtSlot()
    def subimage_zoom(self):
        """
        callback for change of zoom on subimage image

            Returns:
                None
        """

        if self._source_label1.number_rectangles:
            self.display_subimage()

    @qc.pyqtSlot()
    def save_subimages(self):
        """
        save the selected sub-image

            Returns:
                None
        """

        if self._source_label1 is None or self._source_label1.number_rectangles < 1:
            qw.QMessageBox.information(
                self,
                'Save',
                "You have not made any subimages yet!")
            return

        options = qw.QFileDialog.Options()
        options |= qw.QFileDialog.DontUseNativeDialog
        file_name, _ = qw.QFileDialog().getSaveFileName(
            self,
            self.tr("Select File"),
            "",
            self.tr("CrystalGrowthTracker Files (*.ga);;All Files (*)"),
            options=options)

        if file_name:
            if not file_name.endswith('.ga'):
                file_name = file_name + '.ga'

            with open(file_name, 'wb') as out_f:
                for index in range(self._source_label1.number_rectangles):
                    rect = self._source_label1.get_rectangle(index)
                    # store as raw data because pickel will not export Qt objects
                    tmp = {}
                    tmp["top left (v,h)"] = (rect.left, rect.bottom)
                    tmp["source"] = self._image_source
                    tmp["image"] = self._raw_image[rect.left:rect.right, rect.top:rect.bottom]
                    pk.dump(tmp, out_f)

                qw.QMessageBox.information(
                    self,
                    self.tr('Save'),
                    self.tr("Subimages written to: {}").format(file_name))

    @qc.pyqtSlot()
    def display_subimage(self, img=None):
        """
        view and save a new subimage provided by argument 'img': else
        display the subimage currently selected by the user.

            Args:
                img (numpy.array) a new image to be displayed and stored

            Returns:
                None
        """
        if img is None:
            img = self.get_current_subimage()

        height, width = img.shape
        tmp = arr.array(
            'B',
            img.reshape(img.size))

        # use constructor with bytes per line
        image = qg.QImage(
            tmp,
            width,
            height,
            width,
            qg.QImage.Format_Grayscale8)

        pixmap = qg.QPixmap.fromImage(image)
        size = pixmap.size()
        size *= self._subimageZoomSpinBox.value()

        pixmap = pixmap.scaled(
            size,
            qc.Qt.KeepAspectRatio,
            qc.Qt.SmoothTransformation)

        self._subimage_label.setPixmap(pixmap)

        self._subimage_label.setScaledContents(True)
        self._subimage_label.setSizePolicy(
            qw.QSizePolicy.Fixed, qw.QSizePolicy.Fixed)
        self._subimage_label.setMargin(0)
        self._subScrollArea.setWidget(self._subimage_label)

    def get_current_subimage(self):
        """
        get the pixels of the subimage that is selected by the user

            Returns:
                numpy.array the pixels of the selected subimage
        """
        index = self._subimageComboBox.currentIndex()

        if index < 0:
            return None

        rect = self._source_label1.get_rectangle(index)

        return self._raw_image[rect.top:rect.bottom, rect.left:rect.right]

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

        window = CrystalGrowthTrackerMain(app)
        window.show()
        app.exec_()

    file_name = "growth_tracker.log"
    lazylogger.set_up_logging(file_name, append=True)
    inner_run()
    lazylogger.end_logging(file_name)

if __name__ == "__main__":
    run_growth_tracker()
