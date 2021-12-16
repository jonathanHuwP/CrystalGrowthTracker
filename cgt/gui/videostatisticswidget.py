# -*- coding: utf-8 -*-
## @package videostatisticswidget
# the widget for displaying the pixel statistics of a video
#
# @copyright 2021 University of Leeds, Leeds, UK.
# @author j.h.pickering@leeds.ac.uk and j.leng@leeds.ac.uk
"""
Created on Wed 26 Feb 2021

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

This work was funded by Joanna Leng's EPSRC funded RSE Fellowship (EP/R025819/1)
"""
# set up linting conditions
# pylint: disable = c-extension-no-member
# pylint: disable = no-name-in-module
# pylint: disable = import-error
# pylint: disable = too-many-instance-attributes
# pylint: disable = no-member
# pylint: disable = too-many-public-methods

import PyQt5.QtGui as qg
import PyQt5.QtCore as qc
import PyQt5.QtWidgets as qw

from cgt.io.mpl import (make_mplcanvas,
                        render_graph,
                        render_prob_density,
                        update_density,
                        update_graph)

from cgt.gui.videobasewidget import VideoBaseWidget
from cgt.gui.Ui_videostatisticswidget import Ui_VideoStatisticsWidget

class VideoStatisticsWidget(VideoBaseWidget, Ui_VideoStatisticsWidget):
    """
    A widget intended to dispay the intensity statistics
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

        ## the plot widget for time series graph
        self._evolution_canvas = None

        ## the probability density curve for a single frame
        self._density_curve = None

        ## the plot widget for for the single frame
        self._single_frame_canvas = None

        ## pointer for the vertical line identifying the frame
        self._frame_line = None

        self.make_canvases()

        font = qg.QFont( "Monospace", 8, qg.QFont.DemiBold)
        self._videoNameLabel.setFont(font)

    def set_video_source(self, video_source):
        """
        override base with drawing the graphs
            video_source (VideoSource): a source of video frames
        """
        self.clear()
        super().set_video_source(video_source)

    def make_canvases(self):
        """
        make the empty plotting canvases
        """
        self.make_time_evolution_canvas()
        self.make_single_frame_canvas()

    def  make_time_evolution_canvas(self):
        """
        make the canvas for the evolution of the mean
        """
        self._evolution_canvas, toolbar = make_mplcanvas()
        layout = qw.QVBoxLayout(self._graphScrollArea)
        layout.addWidget(toolbar)
        layout.addWidget(self._evolution_canvas)
        self._graphScrollArea.setLayout(layout)

    def make_single_frame_canvas(self):
        """
        make the canvas for the distribution of the current frame
        """
        self._single_frame_canvas, toolbar = make_mplcanvas()
        layout = qw.QVBoxLayout(self._histogramScrollArea)
        layout.addWidget(toolbar)
        layout.addWidget(self._single_frame_canvas)
        self._histogramScrollArea.setLayout(layout)

    def animate_graphs(self):
        """
        display the data animating the frame line
        """
        stats = self._data_source.get_results().get_video_statistics()
        if self._density_curve is not None:
            update_density(self._single_frame_canvas,
                           self._density_curve,
                           stats,
                           self._current_frame)

        if self._frame_line is not None:
            update_graph(self._evolution_canvas, self._frame_line, self._current_frame)

    @qc.pyqtSlot()
    def display_stats(self):
        """
        draw the two graphs
        """
        stats = self._data_source.get_results().get_video_statistics()
        self._frame_line = render_graph(stats.get_frames(),
                                        self._evolution_canvas,
                                        self._current_frame)

        self._density_curve = render_prob_density(stats,
                                                  self._single_frame_canvas,
                                                  self._current_frame)

        self.redisplay()

    def display_extra(self):
        """
        location for additional code beyond displaying the video label
        """
        self.animate_graphs()

    def get_data(self):
        """
        get the data store
            Returns:
                pointer to data (SimulatedDataStore)
        """
        return self._data_source

    def clear(self):
        """
        clear the current contents
        """
        self._frame_line = None

        self._videoNameLabel.setText(self.tr("Video"))

        if self._evolution_canvas is not None:
            self._evolution_canvas.axes.clear()
            self._evolution_canvas.draw()
            self._evolution_canvas.flush_events()

        if self._single_frame_canvas is not None:
            self._single_frame_canvas.axes.clear()
            self._single_frame_canvas.draw()
            self._single_frame_canvas.flush_events()

        super().clear()

    def save_scene(self, file_path):
        """
        save the current scene regarless of current view
            Args:
                file_path (string): the file
        """
        self._graphicsView.save_scene(file_path)

    @qc.pyqtSlot()
    def make_statistics(self):
        """
        calculate the statistics for the video
        """
        print("VideoStatisticsWidget.make_statistics()")
        self._data_source.make_video_statistics()

    def enable(self, enabled):
        """
        enable/disable widget on disable play is paused
            Args:
                enabled (bool): if true connect and enable else, disable and pause
        """
        self._makeStatsButton.setEnabled(True)
        self._videoControl.setEnabled(enabled)
        self._graphicsView.setEnabled(enabled)
        self._graphScrollArea.setEnabled(enabled)
        self._histogramScrollArea.setEnabled(enabled)
        self.play_pause()
