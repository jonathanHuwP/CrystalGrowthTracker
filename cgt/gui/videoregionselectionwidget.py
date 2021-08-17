# -*- coding: utf-8 -*-
"""
Created on Wed 03 Feb 2021

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
import pathlib

import PyQt5.QtWidgets as qw
import PyQt5.QtCore as qc
import PyQt5.QtGui as qg

from cgt.gui.videobasewidget import VideoBaseWidget
from cgt.gui.regionselectionview import SelectStates
from cgt.util.utils import qimage_to_nparray

# import UI
from cgt.gui.Ui_videoregionselectionwidget import Ui_VideoRegionSelectionWidget

class VideoRegionSelectionWidget(VideoBaseWidget, Ui_VideoRegionSelectionWidget):
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

        ## the holder of the results data
        self._data_source = data_source

        ## the currently used subimage rectangle
        self._current_rectangle = None

        ## label for the subimage
        self._subimage_label = qw.QLabel()
        self._regionScrollArea.setWidget(self._subimage_label)

        ## state variable for the operating mode
        self._mode = SelectStates.MAKE_REGION
        self._graphicsView.set_state(self._mode)
        self._graphicsView.set_data_source(self._data_source)

        font = qg.QFont( "Monospace", 8, qg.QFont.DemiBold)
        self._videoNameLabel.setFont(font)

        ## array for holding writers used to produce region videos
        self._writers = []

    def get_operating_mode(self):
        """
        getter for the operating mode
            Returns:
                operating mode (SelectStates)
        """
        return self._mode

    @qc.pyqtSlot(int)
    def set_opertating_mode(self, mode):
        """
        callback for change of operating mode
            Args:
                mode (SelectionStates) the new mode
        """
        self._graphicsView.set_state(mode)
        self.display()

    def display_subimage(self):
        """
        if current subimage exists display it at the current zoom
        """
        if self._current_rectangle is None:
            self._subimage_label.clear()
            return

        rect = self._current_rectangle.toAlignedRect()

        pixmap = self._current_pixmap.copy(rect)
        self._subimage_label.setPixmap(pixmap)

    def display_extra(self):
        """
        location for additional code beyond displaying the video label
        """
        if self._current_pixmap is None or self.isHidden():
            return

        if self._current_rectangle is not None:
            self.display_subimage()

        if len(self._writers) == 0:
            return

        for writer in self._writers:
            self.output_frame_of_region(writer)

        if self._current_frame == self._video_source.get_length()-1:
            self.finish_writing()

    @qc.pyqtSlot(qc.QRectF)
    def show_region(self, region):
        """
        display a given region as subimage
            Args:
                region (QRectF) the region to be displayed
        """
        self._current_rectangle = region
        self.display_subimage()

    @qc.pyqtSlot()
    def stop_showing_region(self):
        """
        stop showing the current region
        """
        self._current_rectangle = None
        self.display_subimage()

    def data_changed(self):
        """
        allow parent widget to notify controls of a change of data
        """
        self._view_control.data_changed()

    def clear_subimage(self):
        """
        remove the subimage and rectangle
        """
        self._current_rectangle = None

    def get_data(self):
        """
        get the data store
            Returns:
                pointer to holder of results (CrystalGrowthTrackerMain)
        """
        return self._data_source

    def display_video_file_name(self):
        """
        force the dispaly of the video file name
        """
        name = self._data_source.get_project()["enhanced_video_no_path"]
        self._videoNameLabel.setText(name)

    def redisplay_regions(self):
        """
        force a resdisplay of the current set of regions
        """
        self._graphicsView.redisplay_regions()

    def clear(self):
        """
        reset to initial conditions
        """
        self._subimage_label.clear()
        super().clear()

    def save_videos(self, dir_name):
        """
        save videos of each region
            Args:
                dir_name (string) the directory in which to save files
        """
        results = self._data_source.get_results()
        regions = results.get_regions()
        if len(regions) < 1:
            return

        path = pathlib.Path(dir_name)
        # HACK
        # self._writers.clear()
        # fourcc = cv2.VideoWriter_fourcc(*'XVID')
        # for i, region in enumerate(regions):
        #     file = path.joinpath(f"region_{i}.avi")
        #     rect = region.rect().toAlignedRect()
        #     shape = (rect.width(), rect.height())
        #     self._writers.append((cv2.VideoWriter(str(file), fourcc, 20.0, shape), region))

        # self.write_video_files()

    def finish_writing(self):
        """
        clean up after writing video files
        """
        for writer in self._writers:
            writer[0].release()

        self._writers.clear()
        self._videoControl.enable_all()

    def write_video_files(self):
        """
        run the video and copy out the regions
        """
        self.play_pause()
        self._video_source.clear()
        frames = list(range(self._video_source.get_length()))
        self._videoControl.disable_all_but_zoom()
        self._video_source.request_frames(frames)

    def output_frame_of_region(self, writer):
        """
        output one frame of a region to a writers
            Args:
                writer ((cv2.VideoWriter, QGraphicsRectItem)) the writer and region pair
        """
        rect = writer[1].rect().toAlignedRect()
        image = qg.QImage(self._current_pixmap.copy(rect))
        array = qimage_to_nparray(image)
        # HACK
        # rgb_out = cv2.cvtColor(array, cv2.COLOR_RGBA2RGB)
        # writer[0].write(rgb_out)
