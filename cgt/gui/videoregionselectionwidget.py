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

import PyQt5.QtWidgets as qw
import PyQt5.QtGui as qg
import PyQt5.QtCore as qc

from cgt.gui.videobasewidget import VideoBaseWidget
from cgt.gui.regioncreationlabel import RegionCreationLabel
from cgt.gui.regioneditlabel import RegionEditLabel
from cgt.gui.regiondisplaylabel import RegionDisplayLabel

from cgt.gui.videoregionselectionwidgetstates import VideoRegionSelectionWidgetStates as states

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

        ## the currently displayed subimage
        self._current_subimage = None

        ## the currently used subimage rectangle
        self._current_rectangle = None

        ## pointer to the label currently in use
        self._video_label = None

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

        self._view_control.set_data_source(self)

        self.set_up_subimage_label()
        self.make_create_label()

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
            regions = self._data_source.get_results().regions
            self._edit_label.set_rectangle(regions[index], index)
            self.rectangle_drawn()

        self._create_label = None
        self._display_label = None
        self._delete_label = None

    def make_display_label(self):
        """
        set up label for display
        """
        self._display_label = RegionDisplayLabel(self)
        self.setup_label(self._display_label)
        self.move_label_to_main_scroll(self._display_label)
        index = self._view_control.get_current_rectangle()
        self._display_label.display_rectangle(index)

        self._create_label = None
        self._edit_label = None
        self._delete_label = None

    def set_zoom_in_labels(self, value):
        """
        apply the zoom to the labels in user
            Args:
                value (float) the value of the zoom
        """
        if self._create_label is not None:
            self._create_label.set_zoom(value)
        elif self._edit_label is not None:
            self._edit_label.set_zoom(value)
        elif self._display_label is not None:
            self._display_label.set_zoom(value)
        elif self._delete_label is not None:
            self._delete_label.set_zoom(value)

    def make_delete_label(self):
        """
        set up label for display
        """
        self._delete_label = RegionDisplayLabel(self)
        self.setup_label(self._delete_label)
        self.move_label_to_main_scroll(self._delete_label)
        index = self._view_control.get_current_rectangle()
        self._delete_label.display_rectangle(index)

        self._delete_label.region_selected.connect(self.selected_for_delete)

        self._create_label = None
        self._edit_label = None
        self._display_label = None

    def move_label_to_main_scroll(self, label, tooltip=None):
        """
        move a label to the main scroll area and assign it to _current_label
            Args:
                label (QLabel) the label to be assigned
                tooltip (string) the scroll area's tooltip
        """
        self._video_label = label

        self._videoScrollArea.setToolTip(tooltip)

        h_bar = self._videoScrollArea.horizontalScrollBar()
        v_bar = self._videoScrollArea.verticalScrollBar()
        old_x = h_bar.value()
        old_y = v_bar.value()

        self._videoScrollArea.setWidget(label)

        # the following is needed becaues when a widget
        # is added the max of scroll bars defaults to zero
        if old_x > h_bar.maximum():
            h_bar.setMaximum(old_x)

        if old_y > v_bar.maximum():
            v_bar.setMaximum(old_y)

        h_bar.setValue(old_x)
        v_bar.setValue(old_y)

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
            #self.rectangle_drawn()
            self.display()
        elif self._mode == states.DISPLAY:
            self.make_display_label()
            self.rectangle_deleted()
            self.display()
        elif self._mode == states.DELETE:
            self.make_delete_label()
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

    def animate_subimage(self):
        """
        if there is a subimage copy get a new copy and display
        """
        if self._current_subimage is None:
            return

        self.rectangle_drawn()

    def display_extra(self):
        """
        location for additional code beyond displaying the video label
        """
        self.animate_subimage()
        if self._current_image is None or self.isHidden():
            return
        self.display_subimage()

    @qc.pyqtSlot()
    def rectangle_drawn(self):
        """
        label has a rectangle
        """
        self._current_rectangle = self._video_label.get_rectangle()
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
        self._data_source.append_region(self._current_rectangle)
        self._view_control.data_changed()
        self.clear_subimage()

    def data_changed(self):
        """
        allow parent widget to notify controls of a change of data
        """
        self._view_control.data_changed()

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
        self._data_source.get_results().replace_region(data[0], data[1])

    @qc.pyqtSlot()
    def editing_rectangle_changed(self):
        """
        callback for a user change of the currently edited rectangle
        """
        if self._edit_label is None:
            return

        index = self._view_control.get_current_rectangle()

        if index > -1:
            results = self._data_source.get_results()
            self._edit_label.set_rectangle(results.regions[index], index)

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
            self._delete_label.display_rectangle(index)

    @qc.pyqtSlot(int)
    def selected_for_delete(self, index):
        """
        callback for the user requesing deletion of rectangle, offers pop-up question
            Args:
                index (int) the list index of the selected region
        """
        message = self.tr(f"Do you wish to remove region {index+1}. Cannot be reversed.")
        mb_reply = qw.QMessageBox.question(self,
                                           'CrystalGrowthTracker',
                                           message,
                                           qw.QMessageBox.Yes | qw.QMessageBox.No,
                                           qw.QMessageBox.No)

        if mb_reply == qw.QMessageBox.Yes:
            self._data_source.remove_region(index)
            self._view_control.data_changed()

    def get_data(self):
        """
        get the data store
            Returns:
                pointer to holder of results (CrystalGrowthTrackerMain)
        """
        return self._data_source

    def clear(self):
        """
        reset to initial conditions
        """
        self._video_label.clear()
        self._subimage_label.clear()
        super().clear()
