# -*- coding: utf-8 -*-
"""
Created on Wed 03 Feb 2020

this widget allow the user to select regions in a video

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

This work was funded by Joanna Leng's EPSRC funded RSE Fellowship (EP/R025819/1)

@copyright 2021
@author: j.h.pickering@leeds.ac.uk and j.leng@leeds.ac.uk
"""
# set up linting conditions
# pylint: disable = c-extension-no-member
# pylint: disable = no-name-in-module
# pylint: disable = import-error
# pylint: disable = too-many-instance-attributes
# pylint: disable = no-member
# pylint: disable = too-many-public-methods

from enum import Enum

import PyQt5.QtWidgets as qw
import PyQt5.QtGui as qg
import PyQt5.QtCore as qc

from cgt.io.videobuffer import VideoBuffer
from cgt.util.qthreadsafequeue import QThreadSafeQueue
from cgt.util.simulateddatastore import SimulatedDataStore
from cgt.gui.regioncreationlabel import RegionCreationLabel
from cgt.gui.regioneditlabel import RegionEditLabel
from cgt.gui.regiondisplaylabel import RegionDisplayLabel

from cgt.gui.videoregionselectionwidgetstates import VideoRegionSelectionWidgetStates as states

# import UI
from cgt.gui.Ui_videoregionselectionwidget import Ui_VideoRegionSelectionWidget

class PlayStates(Enum):
    """
    enumeration of video playing states
    """
    MANUAL        = 1
    PLAY_FORWARD  = 2
    PLAY_BACKWARD = 3

class VideoRegionSelectionWidget(qw.QWidget, Ui_VideoRegionSelectionWidget):
    """
    The implementation of the GUI, all the functions and
    data-structures required to implement the intended behaviour
    """

    def __init__(self, video_file, frames_per_second, parent=None):
        """
        the object initalization function

            Args:
                video_file (string) the name of the file holding the video
                frames_per_second (int) the number of frame per second in the video
                parent (QObject): the parent QObject for this window

            Returns:
                None
        """
        super().__init__(parent)
        self.setupUi(self)

        self._data_store = SimulatedDataStore()

        ## the frame queue
        self._frame_queue = QThreadSafeQueue(self)

        ## state variable determines if video is playing
        self._playing = PlayStates.MANUAL

        ## the current image
        self._current_image = None

        ## the currently displayed frame
        self._current_frame = None

        ## the currently displayed subimage
        self._current_subimage = None

        ## the currently used subimage rectangle
        self._current_rectangle = None

        ## the current value of the zoom
        self._current_zoom = 1.0

        ## the number of frames per second
        self._frames_per_second = frames_per_second

        ## the player
        self._source = VideoBuffer(video_file, self)

        ## thread for the player
        self._video_thread = None

        ## pointer to the label currently in use
        self._current_label = None

        ## label for creating regions
        self._create_label = None

        ## label for editing regions
        self._edit_label = None

        ## label for displaying regions
        self._display_label = None

        ## label for deleting regions
        self._delete_label = None

        ## label for the subimage
        self._subimage_label = None

        ## state variable for the operating mode
        self._mode = states.CREATE

        self.set_up_subimage_label()
        self.make_create_label()

        font = qg.QFont( "Monospace", 10, qg.QFont.DemiBold)
        self._frameLabel.setFont(font)

        self.set_up_controls()
        self.request_frame(0)
        self.start_video_source()

    def start_video_source(self):
        """
        initalize the video file reader
        """
        self._video_thread = qc.QThread()

        # move sourse to the thread
        self._source.moveToThread(self._video_thread)

        # make connections
        self._video_thread.started.connect(self._source.make_frames)
        self._video_thread.finished.connect(self._video_thread.deleteLater)
        self._source.display_image.connect(self.display_image)

        # start the thread
        self._video_thread.start()

    def make_create_label(self):
        """
        set up a create label and assign to current label
        """
        self._create_label = RegionCreationLabel(self)
        self.setup_label(self._create_label)

        # connect up create's signals
        self._create_label.have_rectangle.connect(self.rectangle_drawn)
        self._create_label.rectangle_deleted.connect(self.rectangle_deleted)
        self._create_label.store_rectangle.connect(self.store_rectangle)

        tip = self.tr("Left click and drag to make/save/delete")
        self.move_label_to_main_scroll(self._create_label, tip)

        self._edit_label = None
        self._display_label = None

    def make_edit_label(self):
        """
        setup the label for editing
        """
        self._edit_label = RegionEditLabel(self)
        self.setup_label(self._edit_label)

        self._edit_label.have_rectangle.connect(self.rectangle_drawn)
        self._edit_label.rectangle_changed.connect(self.rectangle_drawn)
        self._edit_label.rectangle_changed.connect(self.rectangle_changed)

        tip = self.tr("Left click and drag on corners or centre")
        self.move_label_to_main_scroll(self._edit_label, tip)

        index = self._view_control.get_current_rectangle()

        if index > -1:
            self._edit_label.set_rectangle(self._data_store.get_region(index), index)
            self.rectangle_drawn()

        self._create_label = None
        self._display_label = None

    def make_display_label(self):
        """
        set up label for dispaly
        """
        self._display_label = RegionDisplayLabel(self)
        self.setup_label(self._display_label)
        self.move_label_to_main_scroll(self._display_label)
        self._display_label.display_rectangle(0)
        
        self._create_label = None
        self._edit_label = None

    def move_label_to_main_scroll(self, label, tooltip=None):
        """
        move a label to the main scroll area and assign it to _current_label
            Args:
                label (QLabel) the label to be assigned
                tooltip (string) the scroll area's tooltip
        """
        self._current_label = label

        self._videoScrollArea.setToolTip(tooltip)

        h_bar = self._videoScrollArea.horizontalScrollBar()
        v_bar = self._videoScrollArea.verticalScrollBar()
        dx = h_bar.value()
        dy = v_bar.value()

        self._videoScrollArea.setWidget(label)

        # when adding a widget the max of scroll bars is set to zero
        if dx > h_bar.maximum():
            h_bar.setMaximum(dx)
        
        if dy > v_bar.maximum():
            v_bar.setMaximum(dy)
        
        h_bar.setValue(dx)
        v_bar.setValue(dy)

    def setup_label(self, label):
        """
        set up a label for the main video
        """
        label.setAlignment(qc.Qt.AlignTop | qc.Qt.AlignLeft)
        label.setSizePolicy(qw.QSizePolicy.Fixed, qw.QSizePolicy.Fixed)
        label.setMargin(0)

        label.set_zoom(self._current_zoom)

    def set_up_subimage_label(self):
        """
        initalize the subimage label
        """
        self._subimage_label = qw.QLabel()
        self._regionScrollArea.setWidget(self._subimage_label)

    def set_up_controls(self):
        """
        initalize the controls
        """
        self._videoControl.set_range(self._source.get_length())
        self.connect_controls()

    def connect_controls(self):
        """
        connect the video controls to self
        """
        self._videoControl.zoom_value.connect(self.zoom_value)
        self._videoControl.frame_changed.connect(self.request_frame)
        self._videoControl.start_end.connect(self.start_end)
        self._videoControl.one_frame_forward.connect(self.step_forward)
        self._videoControl.one_frame_backward.connect(self.step_backward)
        self._videoControl.pause .connect(self.play_pause)
        self._videoControl.forwards.connect(self.play_forward)
        self._videoControl.backwards.connect(self.play_backward)

    def get_operating_mode(self):
        """
        getter for the operating mode
            Returns:
                operating mode (VideoRegionSelectionWidgetStates)
        """
        return self._mode

    @qc.pyqtSlot(int)
    def set_opertating_mode(self, mode):
        """
        callback for change of operating mode
            Args:
                mode (VideoRegionSelectionWidgetStates) the new mode
        """
        self._mode = mode

        if self._mode == states.CREATE:
            self.make_create_label()
            self.rectangle_deleted()
            self.display()
        elif self._mode == states.EDIT:
            self.make_edit_label()
            self.rectangle_drawn()
            self.display()
        elif self._mode == states.DISPLAY:
            self.make_display_label()
            self.rectangle_deleted()
            self.display()

    def display_subimage(self):
        """
        if current subimage exists display it at the current zoom
        """
        if self._current_subimage is None:
            return

        img = self.apply_zoom_to_image(self._current_subimage)
        self._subimage_label.setPixmap(qg.QPixmap(img))

    def get_frame_queue(self):
        """
        getter for the frame queue
            Returns:
                pointer to the frame queue
        """
        return self._frame_queue

    def is_playing(self):
        """
        getter for the playing status
            Returns:
                True if the widget is playing video else False
        """
        if self._playing == PlayStates.MANUAL:
            return False

        return True

    @qc.pyqtSlot(qg.QPixmap, int)
    def display_image(self, pixmap, frame_number):
        """
        display an image, the image must be a pixmap so that
        it can safely be recieved from another thread
            Args:
                pixmap (QPixmap) the image in pixmap form
                frame_number
        """
        self._current_image = qg.QImage(pixmap)
        self._current_frame = frame_number
        self._videoControl.set_frame_currently_displayed(frame_number)

        self.animate_subimage()
        self.display()

    def animate_subimage(self):
        """
        if there is a subimage copy get a new copy and display
        """
        if self._current_subimage is None:
            return

        self.rectangle_drawn()

    def display(self):
        """
        display the current image
            Returns:
                None
        """
        if self._current_image is None or self.isHidden():
            return
        # zoom and display image
        tmp = self.apply_zoom_to_image(self._current_image)
        self._current_label.setPixmap(qg.QPixmap(tmp))

        # update the controls
        self._videoControl.set_slider_value(self._current_frame)

        # display the current frame number and time
        display_number = self._current_frame+1
        time = display_number/self._frames_per_second
        message =   "Frame {:0>5d} of {:0>5d}, approx {:0>5.1f} seconds video time"
        self._frameLabel.setText(message.format(display_number,
                                                self._source.get_length(),
                                                time))
        # display any subimage
        self.display_subimage()

        if self._playing == PlayStates.PLAY_FORWARD:
            next_frame = (self._current_frame + 1)
            self.request_frame(next_frame%self._source.get_length())
        elif self._playing == PlayStates.PLAY_BACKWARD:
            next_frame = (self._current_frame - 1)
            self.request_frame(next_frame%self._source.get_length())

    def apply_zoom_to_image(self, image):
        """
        apply the current zoom to an image
            Args:
                image (Qimage) the image to be resized
            Returns
                Qimage resized by current zoom
        """
        height = image.height()*self._current_zoom
        width = image.width()*self._current_zoom
        return image.scaled(width, height)

    def clear_queue(self):
        """
        clear the video buffer queue
        """
        self._frame_queue.clear()

    @qc.pyqtSlot(bool)
    def start_end(self, end):
        """
        jump to the start or end of the video
            Args:
                end (bool) if true jump to end else start
        """
        if end:
            self.request_frame(self._source.get_length()-1)
        else:
            self.request_frame(0)

    @qc.pyqtSlot(int)
    def request_frame(self, frame_number):
        """
        a specific frame should be displayed
        """
        self._frame_queue.push(frame_number)

    @qc.pyqtSlot(float)
    def zoom_value(self, value):
        """
        a new value for the zoom has been entered
        """
        self._current_zoom = value
        if self._create_label is not None:
            self._create_label.set_zoom(value)
        elif self._edit_label is not None:
            self._edit_label.set_zoom(value)
        self.display()

    @qc.pyqtSlot()
    def step_forward(self):
        """
        advance by one frame
        """
        frame = self._current_frame + 1
        if frame < self._source.get_length():
            self.request_frame(frame)

    @qc.pyqtSlot()
    def step_backward(self):
        """
        reverse by one frame
        """
        frame = self._current_frame - 1
        if frame >= 0:
            self.request_frame(frame)

    @qc.pyqtSlot()
    def play_pause(self):
        """
        pause the playing
        """
        self.clear_queue()
        self._playing = PlayStates.MANUAL

    @qc.pyqtSlot()
    def play_forward(self):
        """
        start playing forward
        """
        self.clear_queue()
        self._playing = PlayStates.PLAY_FORWARD
        self.request_frame((self._current_frame+1)%self._source.get_length())

    @qc.pyqtSlot()
    def play_backward(self):
        """
        start playing in reverse
        """
        self.clear_queue()
        self._playing = PlayStates.PLAY_BACKWARD
        self.request_frame((self._current_frame-1)%self._source.get_length())

    @qc.pyqtSlot()
    def rectangle_drawn(self):
        """
        label has a rectangle
        """
        self._current_rectangle = self._current_label.get_rectangle()
        self._current_subimage = self._current_image.copy(self._current_rectangle)
        self.display_subimage()

    @qc.pyqtSlot()
    def rectangle_deleted(self):
        """
        rectangle deleted in label
        """
        self._subimage_label.clear()
        self.clear_subimage()

    @qc.pyqtSlot()
    def store_rectangle(self):
        """
        store the current rectangle
        """
        self._subimage_label.clear()
        index = self._data_store.append(self._current_rectangle)
        self._view_control.add_rectangle(index)
        self.clear_subimage()

    def clear_subimage(self):
        """
        remove the subimage and rectangle
        """
        self._current_subimage = None
        self._current_rectangle = None

    @qc.pyqtSlot()
    def rectangle_changed(self):
        """
        signal that a rectangle has been editied
        """
        if self._edit_label is None:
            return

        data = self._edit_label.get_rectangle_and_index()
        self._data_store.replace_region(data[0], data[1])

    @qc.pyqtSlot()
    def editing_rectangle_changed(self):
        """
        callback for a user change of the currently edited rectangle
        """
        if self._edit_label is None:
            return

        index = self._view_control.get_current_rectangle()

        if index > -1:
            self._edit_label.set_rectangle(self._data_store.get_region(index), index)

    @qc.pyqtSlot()
    def display_rectangle_changed(self):
        """
        callback for a user change of the currently edited rectangle
        """
        if self._display_label is None:
            return

        index = self._view_control.get_current_rectangle()

        if index > -1:
            self._display_label.display_rectangle(index)
            
    @qc.pyqtSlot()
    def delete_rectangle_changed(self):
        """
        callback for a user change of the currently edited rectangle
        """
        if self._delete_label is None:
            return

        index = self._view_control.get_current_rectangle()

        if index > -1:
            print(f"delete {index}")
            #self._delete_label.set_rectangle(self._data_store.get_region(index), index)
            
    def get_data(self):
        """
        get the data store
            Returns:
                pointer to data (SimulatedDataStore) 
        """
        return self._data_store
