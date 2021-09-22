## -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 2021

This module contains the top level graphical user interface for measuring the
growth rates of crystals observed in videos taken using an X-ray synchrotron source

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
# pylint: disable = too-many-public-methods
# pylint: disable = too-many-instance-attributes
# pylint: disable = c-extension-no-member
# pylint: disable = line-too-long
# pylint: disable = invalid-name
# pylint: disable = import-error
# pylint: disable = unnecessary-comprehension

import PyQt5.QtWidgets as qw
import PyQt5.QtCore as qc
import PyQt5.QtGui as qg

from cgt.gui.markupview import MarkUpStates
from cgt.gui.resultsstoreproxy import ResultsStoreProxy
from cgt.gui.videobasewidget import PlayStates
from cgt.util.utils import (get_region,
                            get_frame,
                            hash_marker)

# import UI
from cgt.gui.Ui_markupwidget import Ui_MarkUpWidget

class MarkUpWidget(qw.QWidget, Ui_MarkUpWidget):
    """
    The tool for marking up items identified in the video
    """

    def __init__(self, parent, data_source):
        """
        the object initalization function
            Args:
                parent (QObject): the parent QObject for this widget
                data_store (CrystalGrowthTrackeMain) the main GUI
        """
        super().__init__(parent)
        self.setupUi(self)

        # pointer to the main gui
        self._data_source = data_source

        ## a proxy for the data store
        self._results_proxy = None

        ## the current frame of the video
        self._current_frame = 0

        ## the current raw pixmap
        self._current_pixmap = None

        ## playing state of the video
        self._playing = PlayStates.MANUAL

        ## are the markers going forward or backward in time
        self._entry_forward = True

        ## has a key-frame been set for the region
        self._base_key_frame = None

        ## pointer for the help dialog
        self._help = None

        ## pointer for the video source
        self._video_source = None

        self._entryView.set_parent_and_pens(self, self._data_source.get_pens())
        self._cloneView.set_parent_and_pens(self, self._data_source.get_pens())
        self._cloneView.assign_state(MarkUpStates.CLONE_ITEM)

        self.make_connections()

        font = qg.QFont( "Monospace", 8, qg.QFont.DemiBold)
        self._frameLabel.setFont(font)
        self._frameLabel_2.setFont(font)
        self._videoNameLabel.setFont(font)

    def set_results(self, results_store):
        """
        set a new results object
            Args:
                results_store (VideoAnalysisResultsStore) the store
        """
        self._results_proxy = ResultsStoreProxy(results_store,
                                                self._entryView,
                                                self._cloneView)
        self.setup_regions_combobox()

    def setup_video_widget(self):
        """
        connect up the control widgets
        """
        self.make_connections()

    def make_connections(self):
        """
        set up the video control connections
        """
        self._entryControls.zoom_value.connect(self.entry_zoom_changed)
        self._entryControls.forwards.connect(self.play_video)
        self._entryControls.backwards.connect(self.play_reverse_video)
        self._entryControls.pause.connect(self.pause_video)
        self._entryControls.one_frame_forward.connect(self.step_video)
        self._entryControls.one_frame_backward.connect(self.step_reverse_video)
        self._entryControls.start_end.connect(self.start_or_end)
        self._entryControls.frame_changed.connect(self.display_frame)

        self._cloneControls.zoom_value.connect(self.clone_zoom_changed)
        self._cloneControls.forwards.connect(self.play_video)
        self._cloneControls.backwards.connect(self.play_reverse_video)
        self._cloneControls.pause.connect(self.pause_video)
        self._cloneControls.one_frame_forward.connect(self.step_video)
        self._cloneControls.one_frame_backward.connect(self.step_reverse_video)
        self._cloneControls.start_end.connect(self.start_or_end)
        self._cloneControls.frame_changed.connect(self.display_frame)

        self._cloneControls.disable_all_but_zoom()

    def setup_regions_combobox(self):
        """
        add list of regions to combobox
        """
        if self._results_proxy is None:
            return

        self._regionsBox.blockSignals(True)
        all_regions = self._results_proxy.get_regions()
        index = self._regionsBox.currentIndex()
        self._regionsBox.clear()

        for i in range(len(all_regions)):
            self._regionsBox.addItem(f"Region {i}")

        if index > -1:
            self._regionsBox.setCurrentIndex(index)
        self._regionsBox.blockSignals(False)

        if self._video_source is not None:
            self.region_changed()

    def get_results_proxy(self):
        """
        getter for results proxy object
            Returns:
                pointer to the results proxy object
        """
        return self._results_proxy

    @qc.pyqtSlot()
    def region_changed(self):
        """
        callback for change of regions combobox
        """
        key_frames = self._results_proxy.get_key_frames(self._regionsBox.currentIndex())
        if key_frames is not None:
            if self._entry_forward:
                self._base_key_frame = min(key_frames)
            else:
                self._base_key_frame = max(key_frames)
            self.region_changed_with_key_frames()
        else:
            self._base_key_frame = None
            self.region_changed_no_key_frames()

        self.fill_key_frame_combo()

    def region_changed_with_key_frames(self):
        """
        handel region change if the region posesses key frames
        """
        self.time_changed(self._base_key_frame)

        self._cloneControls.enable_all()
        self._entryControls.freeze()

        if self._entry_forward:
            self._cloneControls.set_range(self._video_source.get_video_data().get_frame_count(),
                                          self._base_key_frame)
        else:
            self._cloneControls.set_range(self._base_key_frame, 0)

        if self._current_pixmap is not None:
            self._results_proxy.clear()
            self.display_pixmap()

        self._results_proxy.redraw_markers(self._regionsBox.currentIndex())

    def region_changed_no_key_frames(self):
        """
        handel region change if the region posesses no key frames
        """
        if self._current_pixmap is not None:
            self._results_proxy.clear()
            self.display_pixmap()

        self._entryControls.enable_all()
        self._entryControls.set_range(self._video_source.get_video_data().get_frame_count(), 0)
        self._cloneControls.disable_all_but_zoom()
        self._cloneControls.set_range(self._video_source.get_video_data().get_frame_count(), 0)

    def display_frame(self, frame):
        """
        display a given frame
            Args:
                frame (int): the time of the frame to display (user FPS)
        """
        pixmap = self._video_source.get_pixmap(frame)
        self.display_image(pixmap, frame)

    def display_image(self, pixmap, frame_number):
        """
        callback function to display an image from a source
            Args:
                pixmap (QPixmap) the pixmap to be displayed
                frame_number (int) the frame number of the video
        """
        if self._regionsBox.count() < 1:
            return

        self._current_pixmap = pixmap
        self._current_frame = frame_number

        self.display_pixmap()
        self.set_key_frame_combo()

        # display the current time
        data = self._video_source.get_video_data()
        length = data.get_time_duration_user()
        now = data.frame_to_user_time(self._current_frame)
        message = f"Time {now:0>5.1f} of {length:0>5.1f} (Frames: {data.get_frame_count()})"
        self._frameLabel_2.setText(message)
        if self._base_key_frame is None:
            self._frameLabel.setText(message)

        self._entryControls.set_frame_currently_displayed(self._current_frame)
        self._cloneControls.set_frame_currently_displayed(self._current_frame)

        delay = self._video_source.get_video_data().get_user_time_step()
        qc.QTimer.singleShot(delay, self.next_pixmap)

    @qc.pyqtSlot()
    def next_pixmap(self):
        """
        call back for timer in display, will incrament/decrement frame as needed
        """
        if self._playing == PlayStates.PLAY_FORWARD:
            self.incrament_frame()
        elif self._playing == PlayStates.PLAY_BACKWARD:
            self.decrament_frame()

    def display_pixmap(self):
        """
        display the current pixmap
        """
        pixmap = self._current_pixmap
        regions = self._results_proxy.get_regions()
        if len(regions) > 0:
            index = self._regionsBox.currentIndex()
            region = regions[index].rect()
            pixmap = self._current_pixmap.copy(region.toRect())

        if self._base_key_frame is None:
            self._entryView.set_region_pixmap(pixmap, self._current_frame, index)
        elif self._base_key_frame == self._current_frame:
            self._entryView.set_region_pixmap(pixmap, self._base_key_frame, index)

        self._cloneView.set_region_pixmap(pixmap, self._current_frame, index)

    def redisplay(self):
        """
        emit the current frame
        """
        self.display_frame(self._current_frame)

    def set_key_frame_combo(self):
        """
        check if the current frame is a key_frame & if so change combo
        """
        if self._base_key_frame is None:
            return

        key_frames = self._results_proxy.get_key_frames(self._regionsBox.currentIndex())

        if key_frames is None:
            return

        if self._current_frame in key_frames:
            index = key_frames.index(self._current_frame)
            self._keyFrameBox.blockSignals(True)
            self._keyFrameBox.setCurrentIndex(index+1)
            self._keyFrameBox.blockSignals(False)
            return

        if not self._keyFrameBox.currentIndex() == 0:
            self._keyFrameBox.blockSignals(True)
            self._keyFrameBox.setCurrentIndex(0)
            self._keyFrameBox.blockSignals(False)

    def setEnabled(self, enabled):
        """
        enable/disable widget: on enable the source
        is connected; on disable play is paused
        """
        if enabled and self._video_source is not None:
            super().setEnabled(True)
            self.redisplay()
            self.region_changed()
        elif not enabled:
            super().setEnabled(False)
            self.play_pause()

    def set_video_source(self, video_source):
        """
        set the video_source object, set length for controls
            Args:
                video_source (VideoSource): the source object
        """
        self._video_source = video_source
        self._cloneControls.set_range(self._video_source.get_video_data().get_frame_count())
        self._entryControls.set_range(self._video_source.get_video_data().get_frame_count())

    @qc.pyqtSlot()
    def play_video(self):
        """
        callback for starting the video
        """
        self._playing = PlayStates.PLAY_FORWARD
        self.block_user_entry()
        self.incrament_frame()

    @qc.pyqtSlot()
    def step_video(self):
        """
        callback for stepping the video one frame
        """
        if self._playing == PlayStates.MANUAL:
            self.incrament_frame()

    @qc.pyqtSlot()
    def pause_video(self):
        """
        callback for calling the video
        """
        self._playing = PlayStates.MANUAL
        self.unblock_user_entry()

    @qc.pyqtSlot()
    def step_reverse_video(self):
        """
        callback for calling the video
        """
        if self._playing == PlayStates.MANUAL:
            self.decrament_frame()

    @qc.pyqtSlot()
    def play_reverse_video(self):
        """
        callback for calling the video
        """
        self._playing = PlayStates.PLAY_BACKWARD
        self.block_user_entry()
        self.decrament_frame()

    @qc.pyqtSlot(int)
    def time_changed(self, frame):
        """
        callback for the jump to a new frame
            Args:
                frame (int) the frame number for the jump
        """
        self.display_frame(frame)

    @qc.pyqtSlot(bool)
    def start_or_end(self, start):
        """
        callback for moving the video to the start or end frame
            Args:
                start (bool) if true first frame else last
        """
        if start:
            self.display_frame(self._video_source.get_video_data().get_frame_count()-1)
        else:
            self.display_frame(0)

    @qc.pyqtSlot(int)
    def jump_to_key_frame(self, index):
        """
        jump the clone view to a key-frame
            Args:
                index (int) the array index of the key frame
        """
        frame = self._keyFrameBox.itemData(index)
        if frame is not None:
            self.time_changed(frame)

    @qc.pyqtSlot(float)
    def entry_zoom_changed(self, zoom_value):
        """
        callback for change of entry controls zoom
        """
        self._entryView.set_zoom(zoom_value)

    @qc.pyqtSlot(float)
    def clone_zoom_changed(self, zoom_value):
        """
        callback for change of clone controls zoom
        """
        self._cloneView.set_zoom(zoom_value)

    @qc.pyqtSlot(qw.QAbstractButton)
    def clone_view_set_state(self, button):
        """
        callback for set state of right view
            Args:
                button (QPushButton) the button
        """
        if button == self._cloneButton:
            self._cloneView.assign_state(MarkUpStates.CLONE_ITEM)
        elif button == self._deleteCloneButton:
            self._cloneView.assign_state(MarkUpStates.DELETE_ITEM)

    @qc.pyqtSlot(int)
    def entry_view_set_marker_type(self, index):
        """
        callback for set artifact input type on right view
            Args:
                index (int) index of selected item
        """
        if index == 0:
            self._entryView.assign_state(MarkUpStates.DRAW_LINES)
        elif index == 1:
            self._entryView.assign_state(MarkUpStates.DRAW_CROSS)

    def incrament_frame(self):
        """
        emit a signal for the next frame looping at max
        """
        upper_limit = self._video_source.get_video_data().get_frame_count()
        lower_limit = 0

        if self._base_key_frame is not None:
            current_range = self._cloneControls.get_range()
            if self._entry_forward:
                lower_limit = current_range[0]
            else:
                upper_limit = current_range[1]

        if self._current_frame < upper_limit-1:
            self.display_frame(self._current_frame+1)
        else:
            self.display_frame(lower_limit)

    def decrament_frame(self):
        """
        emit a signal for the previous frame looping at min
        """
        upper_limit = self._video_source.get_video_data().get_frame_count()
        lower_limit = 0

        if self._base_key_frame is not None:
            current_range = self._cloneControls.get_range()
            if self._entry_forward:
                lower_limit = current_range[0]
            else:
                upper_limit = current_range[1]

        if self._current_frame > lower_limit:
            self.display_frame(self._current_frame-1)
        else:
            self.display_frame(upper_limit-1)

    def add_point(self, point):
        """
        add point to results asking user if a new key frame is generated
            Args:
                point (QGraphicsPathItem)
        """
        key_frame = get_frame(point)
        region = get_region(point)
        key_frames = self._results_proxy.get_key_frames(region)

        if key_frames is None:
            if self.request_start_of_key_frame():
                self.start_region_key_frame(key_frame)
                self._results_proxy.add_point(point)
            else:
                self._results_proxy.remove_item_from_views(hash_marker(point))
            return

        if key_frame in key_frames:
            self._results_proxy.add_point(point)
            return

        if self.request_start_of_key_frame():
            self._results_proxy.add_point(point)
            self.fill_key_frame_combo(key_frame)
        else:
            self._results_proxy.remove_item_from_views(hash_marker(point))

    def add_line(self, line):
        """
        add line to results asking user if a new key frame is generated
            Args:
                line (QGraphicsLineItem)
        """
        key_frame = get_frame(line)
        region = get_region(line)
        key_frames = self._results_proxy.get_key_frames(region)

        if key_frames is None:
            if self.request_start_of_key_frame():
                self.start_region_key_frame(key_frame)
                self._results_proxy.add_line(line)
            else:
                self._results_proxy.remove_item_from_views(hash_marker(line))
            return

        if key_frame in key_frames:
            self._results_proxy.add_line(line)
            return

        if self.request_start_of_key_frame():
            self._results_proxy.add_line(line)
            self.fill_key_frame_combo(key_frame)
        else:
            self._results_proxy.remove_item_from_views(hash_marker(line))

    def request_start_of_key_frame(self):
        """
        check if user wants to start a new key frame
            Returns:
                True if yes else False
        """
        reply = qw.QMessageBox.question(self,
                                        self.tr("New Key Frame?"),
                                        self.tr("Do you wish to start a new <b>key-frame</b>?"),
                                        qw.QMessageBox.Yes|qw.QMessageBox.No,
                                        qw.QMessageBox.No)

        return reply == qw.QMessageBox.Yes

    def start_region_key_frame(self, key_frame):
        """
        first key frame added to region
            Args:
                key_frame (int) the key frame
        """
        self._cloneControls.enable_all()
        self._entryControls.freeze()
        self._base_key_frame = self._current_frame

        self._keyFrameBox.blockSignals(True)
        self._keyFrameBox.clear()
        self._keyFrameBox.addItem(self.tr("None"))
        self._keyFrameBox.addItem(f"{key_frame}", key_frame)
        self._keyFrameBox.blockSignals(False)

        if self._entry_forward:
            self._cloneControls.set_range(self._video_source.get_video_data().get_frame_count(), key_frame)
        else:
            self._cloneControls.set_range(key_frame, 0)

    def fill_key_frame_combo(self, current_key_frame=-1):
        """
        start a new key frame
            Args:
                current_key_frame (int) if viewer is in a newly defined key-frame, set this frame
        """
        self._keyFrameBox.blockSignals(True)
        self._keyFrameBox.clear()
        key_frames = self._results_proxy.get_key_frames(self._regionsBox.currentIndex())
        self._keyFrameBox.addItem(self.tr("None"))

        if key_frames is None:
            return

        set_index = None
        for i, key_frame in enumerate(key_frames):
            self._keyFrameBox.addItem(f"{key_frame}", key_frame)
            if key_frame == current_key_frame:
                set_index = i

        if set_index is not None:
            self._keyFrameBox.setCurrentIndex(set_index+1)

        self._keyFrameBox.blockSignals(False)

    def add_marker(self, marker):
        """
        add marker to results asking user if a new key frame is generated
            Args:
                line (QGraphicsItem)
        """
        if self._results_proxy.check_if_marker_already_has_key_frame(marker):
            qw.QMessageBox.warning(self,
                                   self.tr("Warning no new frame"),
                                   self.tr("The selected marker is already defined in this frame!"))
            self._results_proxy.remove_item_from_views(hash_marker(marker))
            return

        key_frame = get_frame(marker)
        region = get_region(marker)
        key_frames = self._results_proxy.get_key_frames(region)

        if key_frames is None:
            self._results_proxy.add_marker(marker)
            return

        if key_frame in key_frames:
            self._results_proxy.add_marker(marker)
            return

        if self.request_start_of_key_frame():
            self._results_proxy.add_marker(marker)
            self.fill_key_frame_combo(key_frame)
        else:
            self._results_proxy.remove_item_from_views(hash_marker(marker))

    def block_user_entry(self):
        """
        stop user drawing or cloning
        """
        self._entryView.assign_state(MarkUpStates.VIEW_ONLY)
        self._cloneView.assign_state(MarkUpStates.VIEW_ONLY)
        self._regionsBox.setEnabled(False)

    def unblock_user_entry(self):
        """
        allow user to draw or clone
        """
        if self._entryComboBox.currentIndex() == 0:
            self._entryView.assign_state(MarkUpStates.DRAW_LINES)
        elif self._entryComboBox.currentIndex() == 1:
            self._entryView.assign_state(MarkUpStates.DRAW_CROSS)

        if self._cloneButtonGroup.checkedButton() == self._cloneButton:
            self._cloneView.assign_state(MarkUpStates.CLONE_ITEM)
        elif self._cloneButtonGroup.checkedButton() == self._deleteCloneButton:
            self._cloneView.assign_state(MarkUpStates.DELETE_ITEM)

        self._regionsBox.setEnabled(True)

    @qc.pyqtSlot()
    def play_pause(self):
        """
        pause the playing
        """
        self._playing = PlayStates.MANUAL

    @qc.pyqtSlot()
    def display_help(self):
        """
        pop-up help
        """
        text = """<ol>
        <li>Use the left controls to find a first frame.</li>
        <li>Draw lines and select points on the left image.</li>
        <li>Use right controls to find next frame.</li>
        <li>Select and drag lines and points on the left image.</li>
        </ol>
        """
        self._help = qw.QTextBrowser()
        self._help.setWindowFlags(qc.Qt.Window)
        self._help.setDocumentTitle(self.tr("Feature Tracking Help"))
        self._help.setText(text)
        self._help.show()

    def clear(self):
        """
        empyt scene graphs and results proxy
        """
        self._cloneView.scene().clear()
        self._entryView.scene().clear()
        self._results_proxy = None

    def grab_clone_image(self):
        """
        save what part of the clone view is visible to the user (WYSIWYG).
            Returns:
                QPixmap holding the visible part of the view
        """
        return self._cloneView.viewport().grab()

    def grab_entry_image(self):
        """
        save what part of the entry view is visible to the user (WYSIWYG).
            Returns:
                QPixmap holding the visible part of the view
        """
        return self._entryView.viewport().grab()

    def get_clone_image(self):
        """
        Save the whole clone view contents.
            Returns:
                QImage holding image of everything within the scene-graph's bounding rectangle
        """
        return self.get_scene_image(self._cloneView)

    def get_entry_image(self):
        """
        Save the whole entry view contents.
            Returns:
                QImage holding image of everything within the scene-graph's bounding rectangle
        """
        return self.get_scene_image(self._entryView)

    def update_data_display(self):
        """
        data changed reload regions
        """
        self.setup_regions_combobox()

    def save_scene(self, file_path):
        """
        save the current scene regarless of current view
            Args:
                file_path (string): the file
        """
        self._cloneView.save_scene(file_path)

    @staticmethod
    def get_scene_image(view):
        """
        get an image of a whole scene
            Args:
                view (QGraphicsView) the view holding the scene
            Returns:
                QImage holding image of everything within the scene-graph's bounding rectangle
        """
        bound_rect = view.scene().itemsBoundingRect()

        image =  qg.QImage(bound_rect.size().toSize(),
                           qg.QImage.Format_ARGB32)

        top_left = view.mapFromScene(bound_rect.toAlignedRect().topLeft())
        bottom_right = view.mapFromScene(bound_rect.toAlignedRect().bottomRight())

        image.fill(qc.Qt.white)
        painter = qg.QPainter(image)
        view.render(painter, source=qc.QRect(top_left, bottom_right))
        # avoid error if pixmap is garbage collected before painter
        del painter
        return image

    def display_video_file_name(self):
        """
        dispaly the name of the video
        """
        name = self._data_source.get_project()["enhanced_video_no_path"]
        if name is not None:
            self._videoNameLabel.setText(name)

    def change_entry_pens(self):
        """
        force redraw of view
        """
        self._entryView.change_display_pen(self._data_source.get_pens())
