# -*- coding: utf-8 -*-
"""
Created on Fri Aug 08 2020

Demonstration of how to handel video

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
# imageio.reader meta data example
# plugin => ffmpeg
# nframes => inf
# ffmpeg_version => 4.2.2 built with gcc 9.2.1 (GCC) 20200122
# codec => mjpeg
# pix_fmt => yuvj420p(pc
# fps => 20.0
# source_size => (2560, 2160)
# size => (2560, 2160)
# duration => 22.0

# set up linting conditions
# pylint: disable = too-many-public-methods
# pylint: disable = c-extension-no-member
# pylint: disable = too-many-instance-attributes
# pylint: disable = too-many-arguments

import sys
from collections import namedtuple
import array as arr
from imageio import get_reader as imio_get_reader
import numpy as np
from skimage import color

import PyQt5.QtWidgets as qw
import PyQt5.QtGui as qg
import PyQt5.QtCore as qc

from regionselectionlabel import RegionSelectionLabel
from region import Region

# import UI
from Ui_video_demonstration import Ui_VideoDemo

## a tuple representing one end of a region
##
## Args:
##
## rectangle the subimage in screen pixel coordinates
##
## frame the number of the frame 
RegionEnd = namedtuple("RegionEnd", ["rectangle", "frame"])

## a tuple for the video on which the analysis is based
##
## Args:
##
## name the video file name or path
##
## frame_rate number of frames per second
##
## length the numer of frames in the video
##
## width the horizontal size of the video in pixels
##
## height the vertical size of the video in pixels
VideoSource = namedtuple("VideoSource", ["name", "frame_rate", "length", "width", "height"])

def modify_video_source(original,
                        name=None,
                        frame_rate=None,
                        length=None,
                        width=None,
                        height=None):
    """
    copy with modification an immutable VideoSource, it will return a
    copy of the original with any of the named fields in the arguments
    replacing the equivalent field in the orginal

        Args:
            original (VideoSource) the object to be modified
            name (string) new name
            frame_rate (int) the new video frames per second
            length (float) the new video duration in seconds
            width (int) the new horizontal size in pixels
            height (int) the new verticl size in pixels

        Returns:
            a modified copy of the original VideoSource
    """
    if name is None:
        name = original.name

    if frame_rate is None:
        frame_rate = original.frame_rate

    if length is None:
        length = original.length

    if width is None:
        width = original.width

    if height is None:
        height = original.height

    return VideoSource(name, frame_rate, length, width, height)


def make_video_source_imageio(file_name, imio_reader):
    """
    construct a VideoSource data-struct from a imageio.reader object's meta data

        Args:
            imio_reader (imageio.reader) a reader instanciated with a video file

        Returns:
            VideoSource object holding details of video
    """
    meta_data = imio_reader.get_meta_data()
    number_frames = int(np.round(meta_data["fps"] * (meta_data["duration"]-1)))

    return VideoSource(file_name,
                       meta_data["fps"],
                       number_frames,
                       meta_data["size"][0],
                       meta_data["size"][1])

def ndarray_to_qpixmap(data):
    """
    convert a numpy.ndarray to a qpixmap

        Args:
            data (numpy.ndarray) the numpy data

        Returns:
            a QPixmap of the data
    """
    tmp = arr.array('B', data.reshape(data.size))

    im_format = qg.QImage.Format_Grayscale8

    image = qg.QImage(tmp,
                      data.shape[1],
                      data.shape[0],
                      data.shape[1],
                      im_format)

    return qg.QPixmap.fromImage(image)

class VideoDemo(qw.QMainWindow, Ui_VideoDemo):
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
        super(VideoDemo, self).__init__()
        ## the parent object
        self._parent = parent

        self.setupUi(self)

        ## the label for displaying the current main image
        self._source_label = RegionSelectionLabel(self)
        self._source_label.setAlignment(qc.Qt.AlignTop | qc.Qt.AlignLeft)
        self._source_label.setSizePolicy(
            qw.QSizePolicy.Fixed, qw.QSizePolicy.Fixed)
        self._source_label.setMargin(0)
        self._source_label.new_selection.connect(self.start_new_region)
        self._source_label.set_adding()

        ## the reader for the video file
        self._video_reader = None

        ## data on the video
        self._video_data = None

        ## the image that is being viewed
        self._current_image = -1

        ## storage for the video frames as grayscale numpy arrays
        self._images = None

        ## the step size of the video
        self._step_size = 5
        
        ## upper limit for the display frame
        self._max_step = 0
        
        ## storage for one end of a region in the process of being created
        self._region_end = None
        
        ## storage for the regions 
        self._regions = []
        
        # put the label in the scroll
        self._scrollArea.setWidget(self._source_label)

    @property
    def current_image(self):
        """
        get the image currently being displayed

            Returns:
                the image being displayed (numpy.ndarray)
        """
        return self._current_image
        
    def get_current_original_video_frame(self):
        """
        getter for the frame number in the orginal unprocessed video
        
            Returns:
                the frame number in the unprocessed video
        """
        return self._current_image * self._step_size

    def get_current_video_time(self):
        """
        getter function for the time associated with the frame
        of the video currently being displayed, must be getter
        rather than property to allow use in pyqtSlots

            Returns:
                the time of the frame in seconds from the start of the video (float) and the original frame number (int)
        """
        original_frame = self.get_current_original_video_frame()
        return float(original_frame) / float(self._video_data.frame_rate), original_frame

    def set_frame(self, number):
        """
        set the frame to be displayed and display it

            Returns:
                None
        """
        if self._current_image != number:
            self._current_image = number
            self._imageSlider.setSliderPosition(number)

            message = "Frame {:d} of {:d}, approx {:.2f} seconds"
            time, _ = self.get_current_video_time()
            message = message.format(number+1, self._max_step+1, time)
            self._timeStatusLabel.setText(message)

            self.display_pixmap()

    #@qc.pyqtSlot()
    def start_new_region(self):
        """
        get the current rectangle and frame number

            Returns:
                None
        """
        time, frame = self.get_current_video_time()
        img, rect = self.get_current_subimage()
        self._region_end = RegionEnd(rect, frame)
        
        pixmap = ndarray_to_qpixmap(img)
        self._startImageLabel.setPixmap(pixmap)
        self._startImageLabel.setScaledContents(True)
        self._startImageLabel.setSizePolicy(
            qw.QSizePolicy.Fixed, qw.QSizePolicy.Fixed)
        self._startImageLabel.setMargin(0)

        message = "Start Time {:.2f}".format(time)
        self._startLabel.setText(message)
        
        self.enable_select_buttons(True)
        
    def display_final_region(self):
        """
        display the user's current selection of the final frame of region
        
            Returns:
                None
        """
        img, _ = self.get_current_subimage()

        pixmap = ndarray_to_qpixmap(img)

        self._endImageLabel.setPixmap(pixmap)

        self._endImageLabel.setScaledContents(True)
        self._endImageLabel.setSizePolicy(
            qw.QSizePolicy.Fixed, qw.QSizePolicy.Fixed)
        self._endImageLabel.setMargin(0)
        
        time, frame = self.get_current_video_time()
        message = "End Time {:.2f}".format(time)
        self._endLabel.setText(message) 

    #@qc.pyqtSlot()
    def get_current_subimage(self):
        """
        get the pixels of the subimage that is selected by the user

            Returns:
                numpy.array the pixels of the selected subimage
        """
        rect = self._source_label.rectangle
        img = self._images[self.current_image]

        return img[rect.top:rect.bottom, rect.left:rect.right], rect

    @qc.pyqtSlot()
    def select_region(self):
        """
        complete the selctions of a region

            Returns:
                None
        """        
        _, frame = self.get_current_video_time()
        
        self.add_new_region(frame)
        
    def get_selected_region(self):
        """
        getter for the region selected via the combo box, 
        
            Returns:
                region or None if no regions entered
        """
        
        index = self._regionComboBox.currentIndex()
        
        if len(self._regions) < 1 or index < 0:
            return None
        
        return self._regions[index]
  
    def add_new_region(self, last_frame):
        """
        construct a new Region and add it to the list, reset the region end and selection label
        
            Args:
                last_frame (int) the frame number of the user's end point selection
        """
        tlh = self._region_end.rectangle.top
        tlv = self._region_end.rectangle.left
        brh = self._region_end.rectangle.bottom
        brv = self._region_end.rectangle.right
        
        # ensure that the first is the earliest frame
        first_frame = min(self._region_end.frame, last_frame)
        final_frame = max(self._region_end.frame, last_frame)
        
        self._regions.append(Region(tlh, tlv, brh, brv, first_frame, final_frame))
        self._regionComboBox.addItem(str(len(self._regions)))
        self.reset_enter_region()
    
    @qc.pyqtSlot()
    def reset_enter_region(self):
        """
        reset the process of entering a new region
        
            Returns:
                None
        """
        self._region_end = None
        self._endLabel.setText("End")
        self._startLabel.setText("Start")
        self._endImageLabel.clear()
        self._startImageLabel.clear()
        self._source_label.reset_selection()  
        self.enable_select_buttons(False)

    @qc.pyqtSlot()
    def zoom_changed(self):
        """
        callback for a change of the level of zoom on the main image

            Returns:
                None
        """
        self.display_pixmap()

    @qc.pyqtSlot()
    def frame_jump(self):
        """
        callback for the movement of the slider, display frame changed

            Returns:
                None
        """
        frame = self._imageSlider.sliderPosition()
        self.set_frame(frame)

    @qc.pyqtSlot()
    def frame_forward(self):
        """
        callback for the click of forward button, if possible the
        display frame is advanced by one

            Returns:
                None
        """
        if self.current_image < self._max_step:
            self.set_frame(self.current_image + 1)

    @qc.pyqtSlot()
    def frame_backward(self):
        """
        callback for the click of backward button, if possible the
        display frame is decreased by one

            Returns:
                None
        """
        if self.current_image > 0:
            self.set_frame(self.current_image - 1)

    @qc.pyqtSlot()
    def open_file(self):
        """
        callback for opening a new file

            Returns:
                None
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
            self.load_video(file_name)

    @qc.pyqtSlot()
    def set_frame_rate(self):
        """
        callback for setting the video's frame rate will override file meta-data

            Returns:
                None
        """
        rate, flag = qw.QInputDialog.getDouble(
            self,
            "Set frames per second",
            "Frames per Second",
            self._video_data.frame_rate, 0, 100, 1)

        if flag:
            self._video_data = modify_video_source(self._video_data, frame_rate=rate)

    @qc.pyqtSlot()
    def set_sampeling_rate(self):
        """
        callback for setting the sampeling rate, which will be one frame
        in the number of frames entered by this function

            Returns:
                None
        """
        rate, flag = qw.QInputDialog.getInt(
            self,
            "Set number of frames per frame sampled",
            "Sample one in ",
            self._step_size, 0, 100)

        if flag:
            self._step_size = rate

    def enable_select_buttons(self, flag):
        """
        enable the selection buttons
        
            Args:
                flag (bool) if true enable, else disable

            Returns:
                None
        """
        self._selectButton.setEnabled(flag)
        self._cancelButton.setEnabled(flag)
        self._regionsGroupBox.setEnabled(not flag)
        
    def video_controls_enabled(self, flag):
        """
        enable disable video controls

            Args:
                flag (bool) if true enable, else disable

            Returns:
                None
        """
        self._actionSet_Frame_Rate.setEnabled(flag)
        self._downButton.setEnabled(flag)
        self._upButton.setEnabled(flag)
        self._imageSlider.setEnabled(flag)
        self._zoomSpinBox.setEnabled(flag)

    def get_zoom(self):
        """
        getter for the level of zoom

            Returns:
                the current zoom (float)
        """
        return self._zoomSpinBox.value()

    def load_video(self, file_name):
        """
        read in a video and have it processed

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

        self._video_data = make_video_source_imageio(file_name, self._video_reader)

        self.process_video()

        self.display_pixmap()

        self.video_controls_enabled(True)

    def display_pixmap(self):
        """
        diplay pixmap with new current zoom

            Returns:
                None
        """

        pixmap = ndarray_to_qpixmap(self._images[self.current_image])

        size = pixmap.size() * self._zoomSpinBox.value()

        pixmap = pixmap.scaled(size,
                               qc.Qt.KeepAspectRatio,
                               qc.Qt.SmoothTransformation)

        self._source_label.setPixmap(pixmap)
        
        if self._region_end is not None:
            self.display_final_region()

    def process_video(self):
        """
        convert video to qpixmaps

            Retuns:
                None
        """
        # convert 0.0 to 1.0 float to 0 to 255 unsigned int
        def to_gray(value):
            return np.uint8(np.round(value*255))

        self._timeStatusLabel.setText("Loading and processing video")
        array_size = int(np.round(self._video_data.length/self._step_size))
        self._max_step = array_size-1

        # set limiting values on text edit fram number
        self._imageSlider.setMaximum(self._max_step)

        self._images = np.empty(
            (array_size, self._video_data.height, self._video_data.width),
            dtype=np.uint8)

        progress = qw.QProgressDialog("Video Processing", "cancel", 0, 100)
        progress.setCancelButton(None)
        progress.setWindowModality(qc.Qt.WindowModal)
        progress.setValue(0)
        progress.show()

        image_count = 0
        for frame in range(0, self._video_data.length, self._step_size):
            img = color.rgb2gray(self._video_reader.get_data(frame))
            img = to_gray(img)

            self._images[image_count] = img
            image_count += 1

            if image_count%2 == 0:
                tmp = (float(frame) / float(self._video_data.length)) * 100.0
                progress.setValue(tmp)


        self.set_frame(0)
        
    #@qc.pyqtSlot()
    def region_display_mode(self):
        """
        set the mode of operation, with respect to showing the regions
        
            Returns:
                None
        """
        # get the name of the checked button, same as give in designer
        button = self._regionsButtonGroup.checkedButton().objectName()
        
        if button == "_newButton":
            # set state for entering new regions
            print("new")
            self._source_label.set_adding()
            
        elif button == "_allButton":
            # set display all regions
            print("All")
            self._source_label.set_display_all()
            
        elif button == "_allNoTimeButton":
            # set display all regions independant of time
            print("All No Time")
            self._source_label.set_display_all_no_time()
            
        elif button == "_selectedButton":
            # only disply the selected region
            print("selected {}".format(self._regionComboBox.currentText()))
            self._source_label.set_display_selected()

# the main
######################

def run():
    """
    use a local function to make an isolated the QApplication object

        Returns:
            None
    """

    def inner_run():
        app = qw.QApplication(sys.argv)
        window = VideoDemo(app)
        window.show()
        app.exec_()

    inner_run()

if __name__ == "__main__":
    run()
