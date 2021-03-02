# -*- coding: utf-8 -*-
"""
Created on Wed 26 Feb 2021

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
import numpy as np
from enum import Enum

import PyQt5.QtWidgets as qw
import PyQt5.QtGui as qg
import PyQt5.QtCore as qc
import PyQt5.Qt as qt
import pyqtgraph as pg
import numpy as np

from cgt.gui.regiondisplaylabel import RegionDisplayLabel

class PlayStates(Enum):
    """
    enumeration of video playing states
    """
    MANUAL        = 1
    PLAY_FORWARD  = 2
    PLAY_BACKWARD = 3

# import UI
from cgt.gui.Ui_videopropertieswidget import Ui_VideoPropertiesWidget

class VideoPropertiesWidget(qw.QWidget, Ui_VideoPropertiesWidget):
    """
    The implementation of the GUI, all the functions and
    data-structures required to implement the intended behaviour
    """

    def __init__(self, parent, data_source):
        """
        the object initalization function

            Args:
                parent (QWidget): the parent widget
                data_source (CrystalGrowthTrackerMain): the holder of the results
        """
        super().__init__(parent)
        self.setupUi(self)

        ## required as QWidget .parent() returns vanilla QWidget
        self._data_source = data_source

        ## label for showing video
        self._video_label = None

        ## the currently displayed frame
        self._current_frame = 0

        ## the current value of the zoom
        self._current_zoom = 1.0

        ## state variable determines if video is playing
        self._playing = PlayStates.MANUAL

        ## the plot widget used display
        self._graph = pg.PlotWidget(title="Intensity")
        self._graph.setBackground('w')
        self._graphScrollArea.setWidget(self._graph)

        ## the histogram widget
        self._histogram = pg.PlotWidget(title="Intensity")
        self._histogram.setBackground('w')
        self._histogramScrollArea.setWidget(self._histogram)

        font = qg.QFont( "Monospace", 10, qg.QFont.DemiBold)
        self._frameLabel.setFont(font)

        self.connect_controls()

        self.make_label()

    def make_label(self):
        """
        set up label for display
        """
        self._video_label = RegionDisplayLabel(self)
        self._video_label.setAlignment(qc.Qt.AlignTop | qc.Qt.AlignLeft)
        self._video_label.setSizePolicy(qw.QSizePolicy.Fixed, qw.QSizePolicy.Fixed)
        self._video_label.setMargin(0)

        self._video_label.set_zoom(self._current_zoom)
        self._videoScrollArea.setWidget(self._video_label)

    def redisplay(self):
        """
        get and redisplay the current frame
        """
        self.request_frame(self._current_frame)

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

        self.display()

    def animate_graphs(self):
        """
        adjust graphs in step with view of video
            Args:
                frame_number (int) the current frame number
        """
        self._frame_line.setPos(self._current_frame+1)
        self.plot_histogram()

    def plot_histogram(self):
        """
        draw the histogram of the current frame
        """
        stats = self._data_source.get_video_stats()
        counts, bins = stats[self._current_frame].histogram
        self._histogram.clear()
        self._histogram.getAxis('left').setLabel("Counts (number)")
        self._histogram.getAxis('bottom').setLabel("Bins (Level)")
        self._histogram.setXRange(0, 260)
        self._histogram.plot(bins,
                             counts,
                             stepMode=True,
                             fillLevel=0,
                             brush=(0,0,255,150))

    def draw_stats_graph(self):
        """
        draw the statistics graph
        """
        levels = np.linspace(0.2, 1, 5)
        stats = self._data_source.get_video_stats()
        means = [x.mean for x in stats]
        std_dev = [x.std_deviation for x in stats]

        means_plus = []
        means_minus = []

        for i, mean in enumerate(means):
            means_plus.append(mean + std_dev[i])
            means_minus.append(mean - std_dev[i])

        self._graph.getAxis('left').setLabel("Intensity (Level)")
        self._graph.getAxis('bottom').setLabel("Frame (number)")
        self._graph.setYRange(0, 260)

        x_axis = range(1, len(stats)+1)
        self._graph.addLegend()
        m_plot = self._graph.plot(x_axis, means, pen='b', name="Mean")
        up_plot = self._graph.plot(x_axis, means_plus, pen='r', name="Std Dev up")
        down_plot = self._graph.plot(x_axis, means_minus, pen='r', name="Std Dev down")

        self._graph.addItem(pg.FillBetweenItem(m_plot, up_plot, levels[3]))
        self._graph.addItem(pg.FillBetweenItem(m_plot, down_plot, levels[3]))

        self._frame_line = pg.InfiniteLine(angle=90, movable=False)
        self._frame_line.setBounds([0, len(stats)])
        self._graph.addItem(self._frame_line)

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
        self._video_label.setPixmap(qg.QPixmap(tmp))

        # update the line (frame+1 in common with video controls)
        self._videoControl.set_slider_value(self._current_frame)

        # display the current frame number and time
        display_number = self._current_frame+1
        fps, _ = self._data_source.get_fps_and_resolution()
        time = display_number/fps
        message =   "Frame {:0>5d} of {:0>5d}, approx {:0>5.1f} seconds video time"
        self._frameLabel.setText(message.format(display_number,
                                                self._data_source.get_video_length(),
                                                time))
        # adjust the graphs
        self.animate_graphs()

        if self._playing == PlayStates.PLAY_FORWARD:
            next_frame = (self._current_frame + 1)
            self.request_frame(next_frame%self._data_source.get_video_length())
        elif self._playing == PlayStates.PLAY_BACKWARD:
            next_frame = (self._current_frame - 1)
            self.request_frame(next_frame%self._data_source.get_video_length())

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

        transform = qt.Qt.SmoothTransformation
        if self._videoControl.use_fast_transform():
            transform = qt.Qt.FastTransformation

        return image.scaled(width, height, transformMode=transform)

    @qc.pyqtSlot(bool)
    def start_end(self, end):
        """
        jump to the start or end of the video
            Args:
                end (bool) if true jump to end else start
        """
        if end:
            self.request_frame(self._data_source.get_video_length()-1)
        else:
            self.request_frame(0)

    @qc.pyqtSlot(int)
    def request_frame(self, frame_number):
        """
        a specific frame should be displayed
        """
        self._data_source.request_video_frame(frame_number)

    @qc.pyqtSlot(float)
    def zoom_value(self, value):
        """
        a new value for the zoom has been entered
        """
        self._current_zoom = value
        self._video_label.set_zoom(value)
        self.display()

    @qc.pyqtSlot()
    def step_forward(self):
        """
        advance by one frame
        """
        frame = self._current_frame + 1
        if frame < self._data_source.get_video_length():
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
        self._data_source.clear_queue()
        self._playing = PlayStates.MANUAL

    @qc.pyqtSlot()
    def play_forward(self):
        """
        start playing forward
        """
        self._data_source.clear_queue()
        self._playing = PlayStates.PLAY_FORWARD
        self.request_frame((self._current_frame+1)%self._data_source.get_video_length())

    @qc.pyqtSlot()
    def play_backward(self):
        """
        start playing in reverse
        """
        self._data_source.clear_queue()
        self._playing = PlayStates.PLAY_BACKWARD
        self.request_frame((self._current_frame-1)%self._data_source.get_video_length())

    def get_image_copy(self):
        """
        get the current main image
            Returns:
                deep copy of current image (QImage)
        """
        return self._current_image.copy()

    def get_data(self):
        """
        get the data store
            Returns:
                pointer to data (SimulatedDataStore)
        """
        return self._data_source

    def load_video(self):
        """
        initalize the controls
        """
        self._videoControl.set_range(self._data_source.get_video_length())
