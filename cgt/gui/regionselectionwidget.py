# -*- coding: utf-8 -*-
"""
Created on Fri Sept 18 2020

this widget allow the user to select regions in a video

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
# pylint: disable = too-many-instance-attributes
# pylint: disable = too-many-arguments

import sys
from collections import namedtuple

import PyQt5.QtWidgets as qw
import PyQt5.QtGui as qg
import PyQt5.QtCore as qc

from cgt.gui.regionselectionlabel import RegionSelectionLabel
from cgt.model.region import Region
from cgt.util.utils import nparray_to_qimage, qimage_to_nparray

# import UI
from cgt.gui.Ui_regionselectionwidget import Ui_RegionSelectionWidget

## a tuple representing one end of a region
##
## Args:
## rectangle the subimage in screen pixel coordinates
## frame the number of the frame
RegionEnd = namedtuple("RegionEnd", ["rectangle", "frame"])

class RegionSelectionWidget(qw.QWidget, Ui_RegionSelectionWidget):
    """
    The implementation of the GUI, all the functions and
    data-structures required to implement the intended behaviour
    """

    def __init__(self, parent=None, data_source=None):
        """
        the object initalization function

            Args:
                parent (QObject): the parent QObject for this window

            Returns:
                None
        """
        super().__init__(parent)
        ## the object that owns the widget and holds the data
        self._data_source = data_source

        self.setupUi(self)

        ## the label for displaying the current main image
        self._source_label = RegionSelectionLabel(self, self._data_source)

        self._source_label.setAlignment(qc.Qt.AlignTop | qc.Qt.AlignLeft)
        self._source_label.setSizePolicy(
            qw.QSizePolicy.Fixed, qw.QSizePolicy.Fixed)
        self._source_label.setMargin(0)
        self._source_label.new_selection.connect(self.start_new_region)
        self._source_label.set_adding()

        ## the length of the current video
        self._video_frame_count = 0

        ## the image that is being viewed
        self._current_image = None

        ## the frame number of the current image
        self._current_frame = -1

        ## storage for one end of a region in the process of being created
        self._region_end = None

        ## a user set frame rate to override video header
        self._user_frame_rate = None

        # put the label in the scroll
        self._scrollArea.setWidget(self._source_label)

        # connect up the change frame signals
        self._videoControls.frame_changed.connect(self.frame_changed)

    def clear(self):
        """
        clear the contents

            Return:
                None
        """
        self._video_frame_count = 0
        self._current_frame = -1
        self._current_image = None
        self._region_end = None
        self._user_frame_rate = None
        self._regionComboBox.clear()
        self._videoControls.clear()
        self._endImageLabel.clear()
        self._endLabel.clear()
        self._startImageLabel.clear()
        self._startLabel.clear()
        self._source_label.clear()

    @qc.pyqtSlot(int)
    def frame_changed(self, frame_number):
        """
        callback for a change of frame

            Returns:
                None
        """
        self.set_frame(frame_number)

    @property
    def current_frame(self):
        """
        get the image currently being displayed

            Returns:
                the image being displayed (numpy.ndarray)
        """
        return self._current_frame

    def get_current_video_time(self):
        """
        getter function for the time associated with the frame
        of the video currently being displayed, must be getter
        rather than property to allow use in pyqtSlots

            Returns:
                the video time in seconds (float)
                the frame number (int)
        """
        frame_rate, _ = self._data_source.get_fps_and_resolution()
        return float(self._current_frame) / float(frame_rate), self._current_frame

    def set_frame(self, frame_number):
        """
        set the frame to be displayed and display it

            Returns:
                None
        """
        if self._current_frame != frame_number:
            self._current_frame = frame_number
            self._data_source.request_video_frame(frame_number)

    def start_new_region(self):
        """
        get the current rectangle and frame number

            Returns:
                None
        """
        time, frame = self.get_current_video_time()
        img, rect = self.get_current_subimage()
        self._region_end = RegionEnd(rect, frame)

        image = nparray_to_qimage(img)

        self._startImageLabel.setPixmap(qg.QPixmap(image))
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
        time, frame = self.get_current_video_time()

        # ensure that frame has changed
        if self._region_end.frame == frame:
            self._endImageLabel.clear()
            self._endLabel.setText("End")
            return

        npimage, _ = self.get_current_subimage()

        qimage = nparray_to_qimage(npimage)

        self._endImageLabel.setPixmap(qg.QPixmap(qimage))

        self._endImageLabel.setScaledContents(True)
        self._endImageLabel.setSizePolicy(
            qw.QSizePolicy.Fixed, qw.QSizePolicy.Fixed)
        self._endImageLabel.setMargin(0)

        message = "End Time {:.2f}".format(time)
        self._endLabel.setText(message)

    def get_current_subimage(self):
        """
        get the pixels of the subimage that is selected by the user

            Returns:
                numpy.array the pixels of the selected subimage
        """
        rect = self._source_label.rectangle

        image = qg.QImage(self._source_label.pixmap())
        raw = qimage_to_nparray(image)

        return raw[rect.top:rect.bottom, rect.left:rect.right].copy(), rect

    @qc.pyqtSlot()
    def region_combobox_changed(self):
        """
        callback for changes to the region combobox

            Returns:
                None
        """
        if self._selectedButton.isChecked():
            self._source_label.repaint()

    @qc.pyqtSlot()
    def select_region(self):
        """
        complete the selctions of a region

            Returns:
                None
        """
        if self._endImageLabel.pixmap() is None:
            message = self.tr("You must select an ending for the region.")
            qw.QMessageBox.warning(self,
                                   "Warning",
                                   message)
            return

        _, frame = self.get_current_video_time()
        self.add_new_region(frame)

    def add_new_region(self, last_frame):
        """
        construct a new Region and add it to the list, reset the region end and selection label

            Args:
                last_frame (int) the frame number of the user's end point selection
        """
        # ensure that the first is the earliest frame
        first_frame = min(self._region_end.frame, last_frame)
        final_frame = max(self._region_end.frame, last_frame)

        region = Region(
            top=self._region_end.rectangle.top,
            left=self._region_end.rectangle.left,
            bottom=self._region_end.rectangle.bottom,
            right=self._region_end.rectangle.right,
            start_frame=first_frame,
            end_frame=final_frame)

        image = qg.QImage(self._startImageLabel.pixmap())
        start_image = qimage_to_nparray(image)

        image = qg.QImage(self._endImageLabel.pixmap())

        end_image = qimage_to_nparray(image)

        images = (start_image, end_image)

        self._data_source.append_region(region, images)
        results = self._data_source.get_result()
        self._regionComboBox.addItem(str(len(results.regions)-1))
        self.reset_enter_region()

    def reload_combobox(self):
        """
        clear and reload the combobox

            Returns:
                None
        """
        self._regionComboBox.clear()
        results = self._data_source.get_result()
        for index in range(len(results.regions)):
            self._regionComboBox.addItem(str(index))

    def get_selected_region(self):
        """
        get the region selected by the user
            Returns:
                the region
        """
        index = self._regionComboBox.currentIndex()

        return self._data_source.get_result().regions[index]

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
        self.display()

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

    def get_zoom(self):
        """
        getter for the level of zoom

            Returns:
                the current zoom (float)
        """
        return self._zoomSpinBox.value()

    def show_video(self):
        """
        read in a video and have it processed

            Args:
                file_name (string) the file name of the video

            Returns:
                None
        """

        self._video_frame_count = self._data_source.video_frame_count()
        self._data_source.request_video_frame(0)
        self._videoControls.set_range(0, self._video_frame_count)
        self._videoControls.enable(True)

    def display_image(self, image, frame_number):
        """
        diplay pimage with new current zoom
            Args:
                image (QImage) the image to be displayed
                frame_number (int) the frame number in the video
            Returns:
                None
        """
        self._current_image = image
        self._current_frame = frame_number
        self.display()

    def display(self):
        """
        display the current image
            Returns:
                None
        """
        if self._current_image is None or self.isHidden():
            return

        height = self._current_image.height()*self.get_zoom()
        width = self._current_image.width()*self.get_zoom()
        tmp = self._current_image.scaled(width, height)

        self._source_label.setPixmap(qg.QPixmap(tmp))
        message = "Frame {:d} of {:d}, approx {:.2f} seconds"
        time, _ = self.get_current_video_time()
        message = message.format(self._current_frame,
                                 self._video_frame_count+1,
                                 time)
        self._timeStatusLabel.setText(message)

        if self._region_end is not None:
            self.display_final_region()

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
            self._source_label.set_adding()

        elif button == "_allButton":
            # set display all regions
            self._source_label.set_display_all()

        elif button == "_allNoTimeButton":
            # set display all regions independant of time
            self._source_label.set_display_all_no_time()

        elif button == "_selectedButton":
            # only disply the selected region
            self._source_label.set_display_selected()

    def get_pixmap(self):
        """
        get a pixmap of the current image, if there is one

            Returns:
                QPixmap of image or None if no image has been set
        """
        if self._source_label is None:
            return None

        return self._source_label.grab()

    @qc.pyqtSlot()
    def showEvent(self, event):
        """
        override qwidget and ensure a safe display

            Returns:
                None
        """
        print("RSW: showEvent")
        qw.QWidget.showEvent(self, event)

        self.display()

    def get_current_frame(self):
        """
        getter for the current frame
            Returns:
                (int) the frame numer of the image currently being shown
        """
        return self._current_frame

# the main
######################

def run():
    """
    use a local function to make an isolated the QApplication object

        Returns:
            None
    """
    app = qw.QApplication(sys.argv)
    window = RegionSelectionWidget()
    window.show()
    app.exec_()

if __name__ == "__main__":
    run()
