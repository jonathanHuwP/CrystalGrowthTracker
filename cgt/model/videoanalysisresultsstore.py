# -*- coding: utf-8 -*-
"""
Created on Tuesday August 18 2020

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
# pylint: disable = too-many-arguments

import PyQt5.QtCore as qc

class VideoAnalysisResultsStore:
    """
    a storage class that records the results of a video analysis
    """
    def __init__(self, regions=None):
        """
        initalize an object

            Args:
                video (video_source) description of the original video sequence

                regions ([Region]) the region objects
        """
        ## storage for the regions
        self._regions = []

        ## storage for the lines
        self._lines = []

        ## flag to indicate store has been changed
        self._changed = False

        ## association of regions to lines
        self._region_line_association = RegionLineAssociation()

        if regions is not None:
            self._regions = regions
            self._changed = True

    def has_been_changed(self):
        """
        getter for the changed status

            Returns:
                the changed flag
        """
        return self._changed

    def reset_changed(self):
        """
        make the changed status false

            Returns:
                None
        """
        self._changed = False

    def set_changed(self):
        """
        set the changed status to true

            Returns:
                None
        """
        self._changed = True

    @property
    def regions(self):
        """
        getter for the regions array

            Returns:
                regions array
        """
        return self._regions

    def reserve_regions(self, size):
        """
        set the size of the regions array, will overwrite all existing enteries

            Args:
                size (int) the desired size

            Returns:
                None
        """
        self._regions.extend(['']*size)

    def insert_region(self, region, index):
        """
        insert a region at a specified index in the regions array, will overwrite existing
            Args:
                region (Region) the region to be added
                index (int) the index at which the region is to be located
            Throws:
                IndexError if index out of range
        """
        self._regions[index] = region
        self.set_changed()

    def add_region(self, region):
        """
        add a crystal to the results
            Args:
                region (Region) the region to be added
            Reterns:
                index of the new region
        """
        index = len(self._regions)
        self._regions.append(region)
        self.set_changed()
        return index

    def replace_region(self, region, index):
        """
        replace an existing region
            Args:
                rectangle (QRect) the new region
                index (int) the list index
            Throws:
                IndexError: pop index out of range
        """
        self._regions[index] = region

    def remove_region(self, index):
        """
        remove an item
            Args:
                index (int) the index of the item to be removed
            Throws:
                IndexError: pop index out of range
        """
        self._regions.pop(index)
        self._region_line_association.removed_region(index)
        self.set_changed()

    @property
    def lines(self):
        return self._lines

    @property
    def region_lines_association(self):
        return self._region_line_association

    @property
    def number_of_regions(self):
        """
        getter for the number of regions in the store
            Returns:
                the number of regions
        """
        return len(self._regions)

    def get_lines(self, region_index):
        """
        get all the lines associated with region at region_index
            Args:
                region_index (int) the array index of the region
            Returns:
                a list of lines in the region
        """
        lines = []
        line_indices = self._region_line_association.get_lines_for_region(region_index)

        if len(line_indices) < 1:
            return lines

        for i in line_indices:
            lines.append(self._lines[i])

        return lines

    def get_lines_and_indices(self, region_index):
        """
        get all the lines, and their list indices, associated with region at region_index
            Args:
                region_index (int) the array index of the region
            Returns:
                a list of (line_index, line) of lines in the region
        """
        tmp = []
        line_indices = self._region_line_association.get_lines_for_region(region_index)

        if len(line_indices) < 1:
            return tmp

        for i in line_indices:
            tmp.append((i, self._lines[i]))

        return tmp

    def add_line(self, region_index, line):
        """
        add a line
            Args:
                region_index (int) the array index of the line
                line (Line) the line to be added
        """
        self._lines.append(line)
        line_index = len(self._lines)-1
        self._region_line_association.add_association(region_index, line_index)
        self.set_changed()

class RegionLineAssociation(list):
    """
    array of pairs associating regions, with lines, each line
    must appear only once, it the the users responsibility to
    enforce this
    """
    def __init__(self):
        pass

    def add_association(self, region_index, line_index):
        """
        add a region line association
            Args:
                region_index (int) the array index of the region
                line_index (int) the array index of the region
        """
        self.append((region_index, line_index))

    def get_region(self, line_index):
        """
        get a region given the index of the line
            Args:
                line_index (int) the array index of the line
            Returns:
                the array index of the region, or None if line is unknown
        """
        for tmp in self:
            if tmp[1] == line_index:
                return tmp[0]

        return None

    def get_lines_for_region(self, region_index):
        """
        get the lines in a region
            Args:
                region_index (int) the array index of the region
            Returns:
                a list of the the array indecies of the lines in the region
        """
        tmp = []
        for pair in self:
            if pair[0] == region_index:
                tmp.append(pair[1])

        return tmp

    def removed_region(self, index):
        """
        remove region and reduce the indices in associations with larger region indices
            Args:
                index (int) the index of the region that no longer exists
        """
        tmp = [x for x in self if x[0] == index]
        for item in tmp:
            self.remove(item)

        for i, item in enumerate(self):
            if item[0] > index:
                self[i] = (item[0]-1, item[1])

