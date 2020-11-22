'''
videooverviewwindow.py

This is a stand alone Windowed application that looks at
how the image mean value changes over the course of a video.
This is used an unprocessed (without Euler's Magnifier) video file
showing dynamic crystallisation of X-ray synchrotron videos.

Joanna Leng (an EPSRC funded Research Software Engineering Fellow (EP/R025819/1)
University of Leeds
June 2020

Copyright 2020

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at
http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

'''

import sys
import os

from datetime import timedelta
from timeit import default_timer as timer
from imageio import get_reader

from PyQt5 import QtWidgets as qw
from PyQt5 import QtGui as qg
from PyQt5 import QtCore as qc

from cgt.gui.Ui_VideoOverviewWindow import Ui_VideoOverviewWindow

from cgt.util import overviewplots
from cgt.io import readers

import cv2

class VideoOverviewWindow(qw.QMainWindow, Ui_VideoOverviewWindow):
    """
    The implementation of the GUI, all the functions and
    data-structures required to implement the intended behaviour
    """

    def __init__(self, parent=None):
        super(VideoOverviewWindow, self).__init__()
        self._parent = parent
        self.name = self.tr("VideoOverviewWindow")
        self.setupUi(self)
        self._raw_image = None
        self._frame_numbers = []
        self._frame_means = []
        self._frame_stds = []
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self._outpath = dir_path + '\\temp'
        self._in_file_name = ""
        self._frame_total = 0
        self._video_there = False


    def set_title(self):
        """
        Sets the window title.
        """
        source = self._in_file_name
        title = self.name + " - " + source
        self.setWindowTitle(title)

    @qc.pyqtSlot()
    def change_frame(self):
        """
        Gets the frame number when the FrameSlider changes its value.
        """

        print("hi from change_frame")
        value = self.FrameSlider.value()
        print(value)

        if not self._video_there:
            print("You need to load a video.")
        if self._video_there:
            print("The video is loaded.")
            print("The total number of frames is: ", self._frame_total)
            if value > self._frame_total:
                self.VideoDisplay.setPixmap(qg.QPixmap("temp/blank.png"))
                self.MeanValueGraphDisplay.setPixmap(qg.QPixmap("temp/Mean1.png"))
                self.HistogramDisplay.setPixmap(qg.QPixmap("temp/blank.png"))
            if -1 < value < self._frame_total:
                filename_frame, filename_histogram = readers.read_video_frame(value,
                                                                      self._in_file_name,
                                                                      self._outpath)
                self.VideoDisplay.setPixmap(qg.QPixmap(filename_frame))
                self.HistogramDisplay.setPixmap(qg.QPixmap(filename_histogram))





    @qc.pyqtSlot()
    def load_video(self):
        """
        Get file name from user and check if it is good.
        """

        # file types
        #image_file_type = self.tr("Image Files (*.png *.jpg)")
        video_file_type = self.tr("Video Files (*.avi)")
#        fg = self.tr("CrystalGrowthTracker Files (*.ga)")
#        fn = self.tr("CrystalGrowthTracker Subimage Files(*.pki)")
        all_file_types = self.tr("All Files (*)")

        files_all = [video_file_type, all_file_types]
        files = ";;".join(files_all)
        print(files_all)
        print(files)


        options = qw.QFileDialog.Options()
        print(options)
        options |= qw.QFileDialog.DontUseNativeDialog
        print(options)
        file_name, file_type = qw.QFileDialog.getOpenFileName(
            self,
            self.tr("Select File"),
            "",
            files,
            options=options)
        print(file_name)
        print(not file_name)
        print(file_type)


        if not file_name:
            return

        #if file_type == image_file_type:
        #    self.read_image(file_name)
        if file_type == video_file_type:
            self.read_video(file_name)
        elif file_type == all_file_types:
            if file_name.lower().endswith(".avi"):
                self.read_video(file_name)
            else:
                message = self.tr("Unused file type: {}").format(file_type)
                print(message)
                #qw.QMessageBox.warning(self,
                #                       self.NAME,
                #                       message)
            #self.read_ga_image(file_name)
        else:
            message = self.tr("Unknown file type: {}").format(file_type)
            qw.QMessageBox.warning(self,
                                   self.NAME,
                                   message)



    def read_video(self, file_name, read_type):
        ''' opens the avi input file '''

        self._in_file_name = file_name

        start = timer()

        #print("hi read_video")

        cv2.VideoCapture()
        

        try:
            video = get_reader(file_name, 'ffmpeg')
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise

        if self._frame_numbers:
            self._frame_numbers.clear()
        if self._frame_means:
            self._frame_means.clear()
        if self._frame_stds:
            self._frame_stds.clear()

        try:
            if not os.path.exists(self._outpath):
                os.makedirs(self._outpath)
        except OSError:
            sys.exit('Fatal: output directory ' + self._outpath +
                     ' does not exist and cannot be created')

        num = 0
        img = None
        for img in video.iter_data():
            self._frame_numbers.append(num)
            if num == 0:
                filename_frame = overviewplots.save_grayscale_frame(self._outpath,
                                                                    img,
                                                                    num,)
            mean = img.mean()
            std = img.std()
            if num == 0:
                filename_histogram = overviewplots.plot_histogram(self._outpath,
                                                                  img,
                                                                  num,
                                                                  mean,
                                                                  std)
            self._frame_means.append(mean)
            self._frame_stds.append(std)
            if num < 5:
                print("number: ", num, " image mean: %4.3f" % mean, "std: %4.3f" % std)
            num = num+1
            #f num is 7:
            #   break

        metadata = video.get_meta_data()
        print(metadata)

        filename_means = overviewplots.plot_means(self._outpath,
                                                  self._frame_numbers,
                                                  self._frame_means)

        self._frame_total = num

        self.initial_video_display(filename_frame, filename_histogram, filename_means)
        self._video_there = True
        end = timer()
        time = str(timedelta(seconds=(end-start)))
        print("The time to read and process the video was: ", time) # Time in seconds


    def initial_video_display(self, filename_frame, filename_histogram, filename_means):
        '''
        Displays the initial blank images.
        '''
        self.VideoDisplay.setPixmap(qg.QPixmap(filename_frame))
        self.MeanValueGraphDisplay.setPixmap(qg.QPixmap(filename_means))
        self.HistogramDisplay.setPixmap(qg.QPixmap(filename_histogram))





######################################

def get_translators(lang):
    '''
    Get translations to be displayed through the GUI.
    '''
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
    '''
    Set up the translator for the GUI so that translated versions of
    information and comments made through the GUI are possible.
    '''
    languages = ["English", "German"]

    lang = qw.QInputDialog.getItem(
        None, "Select Language", "Language", languages)

    if not lang[1]:
        return None
    return get_translators(lang[0])


def run_video_overview():
    """
    use a local function to make an isolated the QApplication object
    """
    app = qw.QApplication(sys.argv)

    translators = select_translator()
    for translator in translators:
        qc.QCoreApplication.installTranslator(translator)

    window = VideoOverviewWindow(app)
    window.show()
    app.exec_()

if __name__ == "__main__":
    run_video_overview()
