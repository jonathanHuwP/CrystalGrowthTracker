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

import PyQt5.QtGui as qg
import PyQt5.QtCore as qc
import pyqtgraph as pg

from cgt.gui.videobasewidget import VideoBaseWidget
from cgt.gui.Ui_videostatisticswidget import Ui_VideoStatisticsWidget

class VideoStatisticsWidget(VideoBaseWidget, Ui_VideoStatisticsWidget):
    """
    A widget intended to dispay the intensity statistics
    """
    ## font for the graphs
    label_style = {'font-weight': 'bold'}

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
        self._graph = None

        ## pointer for the vertical line identifying the frame
        self._frame_line = None

        ## the plot widget for for the histogram
        self._histogram = None

        self.make_plots()

        font = qg.QFont( "Monospace", 8, qg.QFont.DemiBold)
        self._videoNameLabel.setFont(font)

    def set_video_source(self, video_source):
        """
        override base with drawing the graphs
            video_source (VideoSource): a source of video frames
        """
        self.clear()
        super().set_video_source(video_source)

    def make_plots(self):
        """
        make the plain plots
        """
        self._graph = pg.PlotWidget(title="<b>Intensity</b>")
        self._graph.setBackground('w')
        self._graphScrollArea.setWidget(self._graph)

        self._histogram = pg.PlotWidget(title="<b>Intensity</b>")
        self._histogram.setBackground('w')
        self._histogramScrollArea.setWidget(self._histogram)

    def animate_graphs(self):
        """
        adjust graphs in step with view of video
            Args:
                frame_number (int) the current frame number
        """
        if self._frame_line is None:
            return

        self._frame_line.setPos(self._current_frame+1)
        self.plot_histogram()

    @qc.pyqtSlot()
    def display_stats(self):
        """
        draw the two graphs
        """
        if self._frame_line is not None:
            self.clear()
        self.draw_stats_graph()
        self.plot_histogram()

    def plot_histogram(self):
        """
        draw the histogram of the current frame
        """
        tick_font = qg.QFont()
        tick_font.setBold(True)

        self._histogram.clear()
        self._histogram.getAxis('left').setLabel("Counts (number)",
                                                 **VideoStatisticsWidget.label_style)
        self._histogram.getAxis('bottom').setLabel("Bins (Level)",
                                                   **VideoStatisticsWidget.label_style)
        self._histogram.getAxis('left').setTickFont(tick_font)
        self._histogram.getAxis('bottom').setTickFont(tick_font)
        self._histogram.setXRange(0, 260)

        stats = self._data_source.get_video_stats()

        # use only lower limits of bins
        plot_bins = stats.get_bins()[:len(stats.get_bins())-1]

        # visible width 7/8 of full bin width
        width = stats.get_bins()[1] - stats.get_bins()[0]
        width -= width/8.0

        self._histogram.addItem(pg.BarGraphItem(x=plot_bins,
                                                height=stats.get_frames()[self._current_frame].bin_counts,
                                                width=width,
                                                brush='g'))

    def draw_stats_graph(self):
        """
        draw the statistics graph
        """
        if self._data_source.get_project()["raw_video_path"] is None:
            text = self._data_source.get_project()["enhanced_video_no_path"]
        else:
            text = self._data_source.get_project()["raw_video_no_path"]

        self._videoNameLabel.setText(text)

        tick_font = qg.QFont()
        tick_font.setBold(True)

        levels = np.linspace(0.2, 1, 5)
        stats = self._data_source.get_video_stats()
        means = [x.mean for x in stats.get_frames()]
        std_dev = [x.std_deviation for x in stats.get_frames()]

        means_plus = []
        means_minus = []

        for i, mean in enumerate(means):
            means_plus.append(mean + std_dev[i])
            means_minus.append(mean - std_dev[i])

        self._graph.getAxis('left').setLabel("Intensity (Level)",
                                             **VideoStatisticsWidget.label_style)
        self._graph.getAxis('left').setTickFont(tick_font)
        self._graph.getAxis('bottom').setLabel("Frame (number)",
                                               **VideoStatisticsWidget.label_style)
        self._graph.getAxis('bottom').setTickFont(tick_font)
        self._graph.setYRange(0, 260)

        x_axis = range(1, len(stats.get_frames())+1)
        self._graph.addLegend()
        m_plot = self._graph.plot(x_axis, means, pen='b', name="Mean")
        up_plot = self._graph.plot(x_axis, means_plus, pen='r', name="Std Dev up")
        down_plot = self._graph.plot(x_axis, means_minus, pen='r', name="Std Dev down")

        self._graph.addItem(pg.FillBetweenItem(m_plot, up_plot, levels[3]))
        self._graph.addItem(pg.FillBetweenItem(m_plot, down_plot, levels[3]))

        self._frame_line = pg.InfiniteLine(angle=90, movable=False)
        self._frame_line.setBounds([0, len(stats.get_frames())])
        self._graph.addItem(self._frame_line)

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
        self.make_plots()
        super().clear()

    @qc.pyqtSlot()
    def make_stats(self):
        self._data_source.make_video_statistics()

    @qc.pyqtSlot(bool)
    def setEnabled(self, enabled):
        self._videoControl.setEnabled(enabled)
        self._graphicsView.setEnabled(enabled)
        self._graphScrollArea.setEnabled(enabled)
        self._histogramScrollArea.setEnabled(enabled)
        self._makeStatsButton.setEnabled(True)