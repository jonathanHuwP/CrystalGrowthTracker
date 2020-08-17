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
import array as arr
import pickle as pk
import numpy as np
from PIL import Image
import matplotlib.image as mpimg
from skimage import color

import PyQt5.QtWidgets as qw
import PyQt5.QtGui as qg
import PyQt5.QtCore as qc

import lazylogger
from ImageLabel import ImageLabel
from PolyLineExtract import PolyLineExtract, IAParameters
from ImageEnhancer import ImageEnhancer

# set up linting conditions
# pylint: disable = too-many-public-methods
# pylint: disable = c-extension-no-member

# import UI
from Ui_CrystalGrowthTrackerMain import Ui_CrystalGrowthTrackerMain

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
    def feature_detect(self):
        """
        @brief find the outlines of any crystals in the currently selected sub-image
        @param method the number of the method to be used

            Returns:
                None
        """
        index = self._subimageComboBox.currentIndex()
        self._logger.debug("running on subimage (%s)", index)

        if index < 0:
            return

        rect = self._source_label1.get_rectangle(index)

        # line_threshold, line_length, line_gap, verts_min_distance
        params = IAParameters(10, 50, 5, 5)
        ple = PolyLineExtract(params)
        #ie = ImageEnhancer(
        #    self._raw_image[rect.top:rect.bottom, rect.left:rect.right])
        #ple.image = ie.constrast_stretch((25, 75))

        ple.image = self._raw_image[rect.top:rect.bottom, rect.left:rect.right]
        ple.find_vertices()
        ple.find_lines()

        # print("Number of vertices found: {}".format(ple.number_vertices))
        # for vert in ple.vertices:
        #     print(vert)

        # print("Number of lines found: {}".format(ple.number_lines))
        # print("Start, , End")
        # print("y, x, y, x, theta, r, length")
        # for l in ple.lines:
        #     s = "{}, {}, {}, {}, {}, {}, {}".format(
        #         l.start[0], l.start[1],
        #         l.end[0], l.end[1],
        #         l.theta, l.r, l.length)
        #     print(s)
        # print("End")

        tmp_img = ple.image_all
        self.display_subimage(tmp_img)

    @qc.pyqtSlot()
    def save_results(self):
        """
        Save the curren set of results

            Returns:
                None
        """
        csv_file = "Comma Seperated Value Files (*.csv)"
        html_file = "HTML Report (*.html)"

        options = qw.QFileDialog.Options()
        options |= qw.QFileDialog.DontUseNativeDialog
        file_name, file_type = qw.QFileDialog().getSaveFileName(
            self,
            self.tr("Select File"),
            "",
            self.tr(";;".join([csv_file, html_file])),
            options=options)

        if file_type == csv_file:
            self.save_results_csv(file_name)
        elif file_type == html_file:
            self.save_results_html(file_name)

    def save_results_csv(self, file_name):
        """
        save the results in a comma seperated file

            Returns:
                None
        """
        if not file_name.lower().endswith(".csv"):
            file_name += ".csv"

        # call csv writing package with params (self._results, file_name)

        print("{} saving results to comma seperated text file {}".format(
            self._translated_name, file_name))

    def save_results_html(self, file_name):
        """
        save the results as a report in HTML

            Returns:
                None
        """
        if not file_name.lower().endswith(".html"):
            file_name += ".html"

        # call report writing packagee with params (self._results, file_name)

        print("{}saving results to report file {}".format(self._translated_name, file_name))

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
        image_files = self.tr("Image Files (*.png *.jpg)")
        tracker_files = self.tr("CrystalGrowthTracker Files (*.ga)")
        subimage_files = self.tr("CrystalGrowthTracker Subimage Files(*.pki)")
        all_files = self.tr("All Files (*)")

        files_all = [image_files, tracker_files, subimage_files, all_files]
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

        if file_type == image_files:
            self.read_image(file_name)
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

        if self._source_label1.number_rectangles and not self._detectButton.isEnabled():
            self._detectButton.setEnabled(True)

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
